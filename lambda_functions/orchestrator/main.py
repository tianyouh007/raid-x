"""
Orchestrator Lambda
Handles API requests and orchestrates Step Functions execution
"""

import json
import boto3
import os
import uuid
import time


def handler(event, context):
    """
    Main handler for orchestrator
    Routes API requests and manages workflow execution
    """
    try:
        print(f"Orchestrator event: {json.dumps(event, indent=2)}")
        
        # Determine the operation based on the API path
        http_method = event.get('httpMethod', 'POST')
        path = event.get('path', '/analyze')
        
        if http_method == 'POST' and path == '/analyze':
            return handle_analyze_request(event, context)
        elif http_method == 'GET' and path == '/status':
            return handle_status_request(event, context)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Endpoint not found'})
            }
        
    except Exception as e:
        print(f"Error in orchestrator: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }


def handle_analyze_request(event, context):
    """Handle transaction analysis request"""
    try:
        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            request_data = json.loads(body)
        else:
            request_data = body
        
        # Extract or generate transaction data
        transaction_data = request_data.get('transaction', {})
        
        if not transaction_data:
            # Generate sample transaction for testing
            transaction_data = {
                'id': str(uuid.uuid4()),
                'from_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'to_address': '3FupnqxAUJ1ZmZVVkTnEPCCCQh6X8D',
                'amount': 0.5,
                'timestamp': int(time.time()),
                'currency': 'BTC'
            }
        
        # Start Step Functions execution
        stepfunctions = boto3.client('stepfunctions')
        
        execution_input = {
            'transaction': transaction_data,
            'request_id': context.aws_request_id,
            'timestamp': int(time.time())
        }
        
        response = stepfunctions.start_execution(
            stateMachineArn=os.environ.get('STEP_FUNCTION_ARN'),
            name=f"raid-x-{transaction_data['id']}-{int(time.time())}",
            input=json.dumps(execution_input)
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Analysis started',
                'execution_arn': response['executionArn'],
                'transaction_id': transaction_data['id'],
                'status': 'RUNNING'
            })
        }
        
    except Exception as e:
        print(f"Error handling analyze request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }


def handle_status_request(event, context):
    """Handle status check request"""
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        execution_arn = query_params.get('execution_arn')
        transaction_id = query_params.get('transaction_id')
        
        if execution_arn:
            # Check specific execution status
            return check_execution_status(execution_arn)
        elif transaction_id:
            # Look up execution by transaction ID
            return lookup_transaction_status(transaction_id)
        else:
            # Return general system status
            return get_system_status()
            
    except Exception as e:
        print(f"Error handling status request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }


def check_execution_status(execution_arn):
    """Check Step Functions execution status"""
    try:
        stepfunctions = boto3.client('stepfunctions')
        
        response = stepfunctions.describe_execution(
            executionArn=execution_arn
        )
        
        status = response['status']
        
        result_data = {
            'execution_arn': execution_arn,
            'status': status,
            'started_at': response['startDate'].isoformat(),
        }
        
        if status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'ABORTED']:
            result_data['stopped_at'] = response.get('stopDate', '').isoformat() if response.get('stopDate') else None
            
            if status == 'SUCCEEDED' and 'output' in response:
                try:
                    output = json.loads(response['output'])
                    result_data['result'] = output
                except:
                    result_data['result'] = {'raw_output': response['output']}
            elif status == 'FAILED':
                result_data['error'] = response.get('error', 'Unknown error')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result_data)
        }
        
    except Exception as e:
        print(f"Error checking execution status: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }


def lookup_transaction_status(transaction_id):
    """Look up transaction status from DynamoDB"""
    try:
        # This would query DynamoDB for transaction results
        # For now, return a mock response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'transaction_id': transaction_id,
                'status': 'COMPLETED',
                'message': 'Transaction analysis completed',
                'risk_score': 0.3,
                'risk_category': 'LOW'
            })
        }
        
    except Exception as e:
        print(f"Error looking up transaction: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }


def get_system_status():
    """Get general system status"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'system': 'RAID-X',
            'status': 'OPERATIONAL',
            'version': '1.0.0',
            'environment': os.environ.get('ENVIRONMENT', 'dev'),
            'timestamp': int(time.time())
        })
    }
