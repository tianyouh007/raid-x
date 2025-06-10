"""
RAID-X Main CDK Stack
"""

import aws_cdk as cdk
from constructs import Construct
from .infrastructure import InfrastructureConstruct
from .lambda_construct import LambdaConstruct
from .stepfunctions_construct import StepFunctionsConstruct
from .api_construct import ApiConstruct


class RaidXStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, environment_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.environment_name = environment_name
        
        # Create infrastructure resources
        self.infrastructure = InfrastructureConstruct(
            self, "Infrastructure",
            environment_name=environment_name
        )
        
        # Create Lambda functions
        self.lambda_construct = LambdaConstruct(
            self, "LambdaFunctions",
            infrastructure=self.infrastructure,
            environment_name=environment_name
        )
        
        # Create Step Functions
        self.stepfunctions = StepFunctionsConstruct(
            self, "StepFunctions",
            lambda_functions=self.lambda_construct.functions,
            environment_name=environment_name
        )
        
        # Create API Gateway
        self.api = ApiConstruct(
            self, "ApiGateway",
            orchestrator_function=self.lambda_construct.functions['orchestrator'],
            step_function=self.stepfunctions.state_machine,
            environment_name=environment_name
        )
        
        # Update orchestrator with step function ARN
        self.lambda_construct.functions['orchestrator'].add_environment(
            "STEP_FUNCTION_ARN", 
            self.stepfunctions.state_machine.state_machine_arn
        )
