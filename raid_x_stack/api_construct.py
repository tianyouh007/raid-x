"""
API Gateway for RAID-X
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
)
from constructs import Construct


class ApiConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, orchestrator_function: lambda_.Function, 
                 step_function: sfn.StateMachine, environment_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.orchestrator_function = orchestrator_function
        self.step_function = step_function
        self.environment_name = environment_name
        self.api = self._create_api()

    def _create_api(self):
        """Create API Gateway with endpoints"""
        api = apigateway.RestApi(
            self, "RaidXApi",
            rest_api_name=f"raid-x-api-{self.environment_name}",
            description="RAID-X Cryptocurrency Risk Assessment API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # Create Lambda integration
        orchestrator_integration = apigateway.LambdaIntegration(
            self.orchestrator_function,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        # Add resources and methods
        analyze_resource = api.root.add_resource("analyze")
        analyze_resource.add_method("POST", orchestrator_integration)
        
        status_resource = api.root.add_resource("status")
        status_resource.add_method("GET", orchestrator_integration)
        
        # Grant permissions
        self.step_function.grant_start_execution(self.orchestrator_function)
        
        return api
