"""
Infrastructure resources for RAID-X
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
)
from aws_cdk.aws_neptune_alpha import (
    DatabaseCluster as NeptuneCluster,
    InstanceType as NeptuneInstanceType,
)
from constructs import Construct


class InfrastructureConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, environment_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.environment_name = environment_name
        
        # Create VPC
        self.vpc = self._create_vpc()
        
        # Create S3 buckets
        self.data_bucket, self.model_bucket, self.logs_bucket = self._create_s3_buckets()
        
        # Create DynamoDB tables
        self.config_table, self.metadata_table, self.results_table = self._create_dynamodb_tables()
        
        # Create Neptune cluster
        self.neptune_cluster = self._create_neptune_cluster()
        
        # Create IAM roles
        self.lambda_role, self.sagemaker_role, self.glue_role = self._create_iam_roles()

    def _create_vpc(self):
        """Create VPC with public and private subnets"""
        return ec2.Vpc(
            self, "RaidXVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

    def _create_s3_buckets(self):
        """Create S3 buckets for data, models, and logs"""
        data_bucket = s3.Bucket(
            self, "RaidXDataBucket",
            bucket_name=f"raid-x-data-{self.environment_name}-{cdk.Aws.ACCOUNT_ID}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        model_bucket = s3.Bucket(
            self, "RaidXModelBucket",
            bucket_name=f"raid-x-models-{self.environment_name}-{cdk.Aws.ACCOUNT_ID}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        logs_bucket = s3.Bucket(
            self, "RaidXLogsBucket",
            bucket_name=f"raid-x-logs-{self.environment_name}-{cdk.Aws.ACCOUNT_ID}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        return data_bucket, model_bucket, logs_bucket

    def _create_dynamodb_tables(self):
        """Create DynamoDB tables for configuration and metadata"""
        config_table = dynamodb.Table(
            self, "RaidXConfigTable",
            table_name=f"raid-x-config-{self.environment_name}",
            partition_key=dynamodb.Attribute(
                name="config_type",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="config_key",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        metadata_table = dynamodb.Table(
            self, "RaidXMetadataTable",
            table_name=f"raid-x-metadata-{self.environment_name}",
            partition_key=dynamodb.Attribute(
                name="entity_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        results_table = dynamodb.Table(
            self, "RaidXResultsTable",
            table_name=f"raid-x-results-{self.environment_name}",
            partition_key=dynamodb.Attribute(
                name="transaction_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="processed_timestamp",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        return config_table, metadata_table, results_table

    def _create_neptune_cluster(self):
        """Create Neptune cluster for graph database"""
        neptune_sg = ec2.SecurityGroup(
            self, "NeptuneSecurityGroup",
            vpc=self.vpc,
            description="Security group for Neptune cluster",
            allow_all_outbound=True
        )
        
        neptune_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(8182),
            description="Neptune port"
        )
        
        return NeptuneCluster(
            self, "RaidXNeptuneCluster",
            vpc=self.vpc,
            instance_type=NeptuneInstanceType.R5_LARGE,
            cluster_identifier=f"raid-x-neptune-{self.environment_name}",
            security_groups=[neptune_sg],
            iam_authentication=True,
            removal_policy=RemovalPolicy.DESTROY
        )

    def _create_iam_roles(self):
        """Create IAM roles for different services"""
        # Lambda execution role
        lambda_role = iam.Role(
            self, "RaidXLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
            ]
        )
        
        # Add permissions for AWS services
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:GetObject", "s3:PutObject", "s3:DeleteObject",
                "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query", "dynamodb:Scan",
                "neptune-db:*",
                "sagemaker:InvokeEndpoint",
                "states:SendTaskSuccess", "states:SendTaskFailure",
                "glue:StartJobRun", "glue:GetJobRun"
            ],
            resources=["*"]
        ))
        
        # SageMaker execution role
        sagemaker_role = iam.Role(
            self, "RaidXSageMakerRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )
        
        sagemaker_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:*"],
            resources=[
                self.data_bucket.bucket_arn,
                f"{self.data_bucket.bucket_arn}/*",
                self.model_bucket.bucket_arn,
                f"{self.model_bucket.bucket_arn}/*"
            ]
        ))
        
        # Glue execution role
        glue_role = iam.Role(
            self, "RaidXGlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ]
        )
        
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:*", "neptune-db:*"],
            resources=["*"]
        ))
        
        return lambda_role, sagemaker_role, glue_role
