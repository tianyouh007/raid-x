#!/usr/bin/env python3
"""
RAID-X: Risk Assessment and Intelligent Detection for Cryptocurrency Transactions
Main CDK application entry point
"""

import aws_cdk as cdk
from raid_x_stack.raid_x_stack import RaidXStack

app = cdk.App()

# Environment configuration
account = app.node.try_get_context("account")
region = app.node.try_get_context("region") or "us-east-1"
environment_name = app.node.try_get_context("environment") or "dev"

env = cdk.Environment(account=account, region=region)

RaidXStack(
    app, 
    f"RaidX-{environment_name}",
    env=env,
    environment_name=environment_name,
    description="RAID-X Cryptocurrency Risk Assessment Framework"
)

app.synth()
