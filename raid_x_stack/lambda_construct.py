"""
Lambda functions for RAID-X
"""

import aws_cdk as cdk
from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
)
from constructs import Construct


class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, infrastructure, environment_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.infrastructure = infrastructure
        self.environment_name = environment_name
        self.functions = self._create_lambda_functions()

    def _create_lambda_functions(self):
        """Create Lambda functions for each component"""
        functions = {}
        
        # R3 Engine Lambda
        functions['r3_engine'] = lambda_.Function(
            self, "R3EngineFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset("lambda_functions/r3_engine"),
            role=self.infrastructure.lambda_role,
            vpc=self.infrastructure.vpc,
            timeout=Duration.minutes(5),
            memory_size=512,
            environment={
                "CONFIG_TABLE": self.infrastructure.config_table.table_name,
                "ENVIRONMENT": self.environment_name
            }
        )
        
        # ARSM Lambda
        functions['arsm'] = lambda_.Function(
            self, "ARSMFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset("lambda_functions/arsm"),
            role=self.infrastructure.lambda_role,
            vpc=self.infrastructure.vpc,
            timeout=Duration.minutes(15),
            memory_size=1024,
            environment={
                "NEPTUNE_ENDPOINT": self.infrastructure.neptune_cluster.cluster_endpoint.socket_address,
                "METADATA_TABLE": self.infrastructure.metadata_table.table_name,
                "ENVIRONMENT": self.environment_name
            }
        )
        
        # TAD-X Lambda
        functions['tad_x'] = lambda_.Function(
            self, "TADXFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset("lambda_functions/tad_x"),
            role=self.infrastructure.lambda_role,
            vpc=self.infrastructure.vpc,
            timeout=Duration.minutes(10),
            memory_size=2048,
            environment={
                "MODEL_BUCKET": self.infrastructure.model_bucket.bucket_name,
                "RESULTS_TABLE": self.infrastructure.results_table.table_name,
                "ENVIRONMENT": self.environment_name
            }
        )
        
        # Data Ingestion Lambda
        functions['data_ingestion'] = lambda_.Function(
            self, "DataIngestionFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset("lambda_functions/data_ingestion"),
            role=self.infrastructure.lambda_role,
            vpc=self.infrastructure.vpc,
            timeout=Duration.minutes(15),
            memory_size=1024,
            environment={
                "DATA_BUCKET": self.infrastructure.data_bucket.bucket_name,
                "GLUE_JOB_NAME": f"raid-x-etl-{self.environment_name}",
                "ENVIRONMENT": self.environment_name
            }
        )
        
        # Orchestrator Lambda
        functions['orchestrator'] = lambda_.Function(
            self, "OrchestratorFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset("lambda_functions/orchestrator"),
            role=self.infrastructure.lambda_role,
            timeout=Duration.minutes(5),
            memory_size=512,
            environment={
                "ENVIRONMENT": self.environment_name
            }
        )
        
        return functions
