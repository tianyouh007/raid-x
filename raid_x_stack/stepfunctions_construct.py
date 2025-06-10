"""
Step Functions for RAID-X workflow orchestration
"""

import aws_cdk as cdk
from aws_cdk import (
    Duration,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct


class StepFunctionsConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, lambda_functions: dict, environment_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.lambda_functions = lambda_functions
        self.environment_name = environment_name
        self.state_machine = self._create_state_machine()

    def _create_state_machine(self):
        """Create Step Functions state machine for RAID-X pipeline"""
        
        # Define Lambda invoke tasks
        data_ingestion_task = tasks.LambdaInvoke(
            self, "DataIngestionTask",
            lambda_function=self.lambda_functions['data_ingestion'],
            result_path="$.data_ingestion_result"
        )
        
        r3_engine_task = tasks.LambdaInvoke(
            self, "R3EngineTask", 
            lambda_function=self.lambda_functions['r3_engine'],
            result_path="$.r3_result"
        )
        
        arsm_task = tasks.LambdaInvoke(
            self, "ARSMTask",
            lambda_function=self.lambda_functions['arsm'],
            result_path="$.arsm_result"
        )
        
        tad_x_task = tasks.LambdaInvoke(
            self, "TADXTask",
            lambda_function=self.lambda_functions['tad_x'],
            result_path="$.tad_x_result"
        )
        
        # Define parallel processing for R3 and ARSM
        parallel_analysis = sfn.Parallel(self, "ParallelAnalysis")
        parallel_analysis.branch(r3_engine_task)
        parallel_analysis.branch(arsm_task)
        
        # Create the workflow
        definition = data_ingestion_task.next(
            parallel_analysis.next(
                tad_x_task.next(
                    sfn.Succeed(self, "ProcessingComplete")
                )
            )
        )
        
        return sfn.StateMachine(
            self, "RaidXStateMachine",
            state_machine_name=f"raid-x-pipeline-{self.environment_name}",
            definition=definition,
            timeout=Duration.hours(2)
        )
