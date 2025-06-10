"""
R3 Engine - Rule-Based Regulatory Risk Engine
Implements compliance screening for known risks
"""

import json
import boto3
import os
from decimal import Decimal


def handler(event, context):
    """
    Main handler for R3 Engine
    Performs rule-based compliance screening
    """
    try:
        # Initialize AWS clients
        dynamodb = boto3.resource('dynamodb')
        config_table = dynamodb.Table(os.environ['CONFIG_TABLE'])
        
        # Extract transaction data
        transaction_data = event.get('transaction', {})
        transaction_id = transaction_data.get('id', 'unknown')
        
        print(f"Processing transaction {transaction_id} with R3 Engine")
        
        # Load compliance rules
        rules = load_compliance_rules(config_table)
        
        # Apply rules
        risk_flags = apply_compliance_rules(transaction_data, rules)
        
        # Calculate risk score
        risk_score = calculate_compliance_risk_score(risk_flags)
        
        result = {
            'transaction_id': transaction_id,
            'r3_risk_score': risk_score,
            'risk_flags': risk_flags,
            'compliance_status': 'HIGH_RISK' if risk_score > 0.7 else 'MEDIUM_RISK' if risk_score > 0.3 else 'LOW_RISK',
            'timestamp': context.aws_request_id
        }
        
        print(f"R3 Engine result: {result}")
        
        return {
            'statusCode': 200,
            'body': result
        }
        
    except Exception as e:
        print(f"Error in R3 Engine: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


def load_compliance_rules(config_table):
    """Load compliance rules from DynamoDB"""
    try:
        response = config_table.query(
            KeyConditionExpression='config_type = :type',
            ExpressionAttributeValues={':type': 'compliance_rules'}
        )
        
        rules = {}
        for item in response.get('Items', []):
            rules[item['config_key']] = item.get('config_value', {})
        
        return rules
    except Exception as e:
        print(f"Error loading compliance rules: {str(e)}")
        return get_default_compliance_rules()


def get_default_compliance_rules():
    """Default compliance rules"""
    return {
        'ofac_sanctions': {
            'enabled': True,
            'risk_weight': 1.0
        },
        'high_value_threshold': {
            'enabled': True,
            'threshold': 10000,
            'risk_weight': 0.3
        },
        'mixer_detection': {
            'enabled': True,
            'risk_weight': 0.8
        },
        'velocity_check': {
            'enabled': True,
            'max_transactions_per_hour': 100,
            'risk_weight': 0.4
        }
    }


def apply_compliance_rules(transaction_data, rules):
    """Apply compliance rules to transaction"""
    risk_flags = []
    
    # OFAC sanctions check
    if rules.get('ofac_sanctions', {}).get('enabled', False):
        if check_ofac_sanctions(transaction_data):
            risk_flags.append({
                'rule': 'ofac_sanctions',
                'description': 'Address appears on OFAC sanctions list',
                'risk_weight': rules['ofac_sanctions']['risk_weight']
            })
    
    # High value threshold check
    if rules.get('high_value_threshold', {}).get('enabled', False):
        threshold = rules['high_value_threshold']['threshold']
        amount = float(transaction_data.get('amount', 0))
        if amount > threshold:
            risk_flags.append({
                'rule': 'high_value_threshold',
                'description': f'Transaction amount {amount} exceeds threshold {threshold}',
                'risk_weight': rules['high_value_threshold']['risk_weight']
            })
    
    # Mixer detection
    if rules.get('mixer_detection', {}).get('enabled', False):
        if check_mixer_involvement(transaction_data):
            risk_flags.append({
                'rule': 'mixer_detection',
                'description': 'Transaction involves known mixing service',
                'risk_weight': rules['mixer_detection']['risk_weight']
            })
    
    return risk_flags


def check_ofac_sanctions(transaction_data):
    """Check if addresses are on OFAC sanctions list"""
    # Simplified check - in production would check against actual OFAC list
    sanctioned_addresses = [
        '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Example addresses
        '3FupnqxAUJ1ZmZVVkTnEPCCCQh6X8D',
    ]
    
    from_address = transaction_data.get('from_address', '')
    to_address = transaction_data.get('to_address', '')
    
    return from_address in sanctioned_addresses or to_address in sanctioned_addresses


def check_mixer_involvement(transaction_data):
    """Check if transaction involves known mixers"""
    # Simplified check - in production would check against mixer address database
    mixer_patterns = ['mix', 'tumbl', 'tornado']
    
    from_address = transaction_data.get('from_address', '').lower()
    to_address = transaction_data.get('to_address', '').lower()
    
    for pattern in mixer_patterns:
        if pattern in from_address or pattern in to_address:
            return True
    
    return False


def calculate_compliance_risk_score(risk_flags):
    """Calculate overall compliance risk score"""
    if not risk_flags:
        return 0.0
    
    # Weighted average of risk flags
    total_weight = sum(flag['risk_weight'] for flag in risk_flags)
    max_possible_weight = len(risk_flags)  # Assuming max risk weight is 1.0
    
    return min(total_weight / max_possible_weight, 1.0) if max_possible_weight > 0 else 0.0
