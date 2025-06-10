"""
Data Ingestion Lambda
Handles blockchain data ingestion and preprocessing
"""

import json
import boto3
import os
import time


def handler(event, context):
    """
    Main handler for data ingestion
    Processes incoming blockchain transaction data
    """
    try:
        # Initialize clients
        s3 = boto3.client('s3')
        glue = boto3.client('glue')
        
        # Extract transaction data from event
        transaction_data = event.get('transaction', {})
        
        # If no transaction data, use sample transaction
        if not transaction_data:
            transaction_data = generate_sample_transaction()
        
        print(f"Processing transaction data: {transaction_data}")
        
        # Validate transaction data
        validated_data = validate_transaction_data(transaction_data)
        
        # Enrich transaction data
        enriched_data = enrich_transaction_data(validated_data)
        
        # Store raw data in S3
        s3_key = store_raw_data(s3, enriched_data)
        
        # Trigger Glue ETL job if needed
        glue_job_result = trigger_etl_processing(glue, s3_key)
        
        result = {
            'transaction': enriched_data,
            's3_location': s3_key,
            'glue_job': glue_job_result,
            'status': 'success',
            'timestamp': context.aws_request_id
        }
        
        print(f"Data ingestion result: {result}")
        
        return {
            'statusCode': 200,
            'body': result
        }
        
    except Exception as e:
        print(f"Error in data ingestion: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


def generate_sample_transaction():
    """Generate sample transaction for testing"""
    import random
    import uuid
    
    return {
        'id': str(uuid.uuid4()),
        'from_address': f"1{''.join(random.choices('0123456789ABCDEFabcdef', k=33))}",
        'to_address': f"3{''.join(random.choices('0123456789ABCDEFabcdef', k=33))}",
        'amount': round(random.uniform(0.001, 100.0), 8),
        'timestamp': int(time.time()),
        'block_height': random.randint(700000, 800000),
        'gas_price': random.randint(20, 200),
        'gas_used': random.randint(21000, 100000),
        'currency': 'BTC'
    }


def validate_transaction_data(transaction_data):
    """Validate and normalize transaction data"""
    validated = {}
    
    # Required fields
    validated['id'] = transaction_data.get('id', 'unknown')
    validated['from_address'] = transaction_data.get('from_address', '').strip()
    validated['to_address'] = transaction_data.get('to_address', '').strip()
    validated['amount'] = float(transaction_data.get('amount', 0))
    validated['timestamp'] = int(transaction_data.get('timestamp', time.time()))
    
    # Optional fields with defaults
    validated['block_height'] = int(transaction_data.get('block_height', 0))
    validated['gas_price'] = int(transaction_data.get('gas_price', 0))
    validated['gas_used'] = int(transaction_data.get('gas_used', 0))
    validated['currency'] = transaction_data.get('currency', 'BTC').upper()
    
    # Validation checks
    if not validated['from_address'] or not validated['to_address']:
        raise ValueError("Missing required address fields")
    
    if validated['amount'] <= 0:
        raise ValueError("Invalid transaction amount")
    
    if len(validated['from_address']) < 26 or len(validated['to_address']) < 26:
        raise ValueError("Invalid address format")
    
    return validated


def enrich_transaction_data(transaction_data):
    """Enrich transaction data with additional metadata"""
    enriched = transaction_data.copy()
    
    # Add processing metadata
    enriched['processed_at'] = int(time.time())
    enriched['processing_id'] = f"proc_{int(time.time())}"
    
    # Add derived features
    enriched['amount_usd'] = estimate_usd_value(
        enriched['amount'], 
        enriched['currency']
    )
    
    enriched['hour_of_day'] = (enriched['timestamp'] % 86400) // 3600
    enriched['day_of_week'] = ((enriched['timestamp'] // 86400) + 4) % 7  # 0=Monday
    
    # Add address classifications
    enriched['from_address_type'] = classify_address(enriched['from_address'])
    enriched['to_address_type'] = classify_address(enriched['to_address'])
    
    # Add transaction size category
    enriched['size_category'] = categorize_transaction_size(enriched['amount_usd'])
    
    return enriched


def estimate_usd_value(amount, currency):
    """Estimate USD value of transaction"""
    # Mock exchange rates - in production would use real-time rates
    exchange_rates = {
        'BTC': 45000,
        'ETH': 3000,
        'LTC': 100,
        'BCH': 300,
        'XRP': 0.6
    }
    
    rate = exchange_rates.get(currency, 1)
    return round(amount * rate, 2)


def classify_address(address):
    """Classify address type based on patterns"""
    if address.startswith('1'):
        return 'P2PKH'  # Pay to Public Key Hash
    elif address.startswith('3'):
        return 'P2SH'   # Pay to Script Hash
    elif address.startswith('bc1'):
        return 'BECH32' # Bech32
    elif address.startswith('0x'):
        return 'ETH'    # Ethereum
    else:
        return 'UNKNOWN'


def categorize_transaction_size(usd_amount):
    """Categorize transaction by USD amount"""
    if usd_amount < 100:
        return 'MICRO'
    elif usd_amount < 1000:
        return 'SMALL'
    elif usd_amount < 10000:
        return 'MEDIUM'
    elif usd_amount < 100000:
        return 'LARGE'
    else:
        return 'WHALE'


def store_raw_data(s3_client, transaction_data):
    """Store raw transaction data in S3"""
    try:
        bucket = os.environ['DATA_BUCKET']
        
        # Create S3 key with partitioning
        timestamp = transaction_data['timestamp']
        year = time.strftime('%Y', time.gmtime(timestamp))
        month = time.strftime('%m', time.gmtime(timestamp))
        day = time.strftime('%d', time.gmtime(timestamp))
        
        s3_key = f"raw-transactions/year={year}/month={month}/day={day}/{transaction_data['id']}.json"
        
        # Store data
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json.dumps(transaction_data, indent=2),
            ContentType='application/json'
        )
        
        print(f"Stored transaction data at s3://{bucket}/{s3_key}")
        return s3_key
        
    except Exception as e:
        print(f"Error storing data in S3: {str(e)}")
        return None


def trigger_etl_processing(glue_client, s3_key):
    """Trigger Glue ETL job for data processing"""
    try:
        job_name = os.environ.get('GLUE_JOB_NAME')
        
        if not job_name:
            print("No Glue job configured")
            return {'status': 'skipped', 'reason': 'no_job_configured'}
        
        # Check if job should be triggered (e.g., batch processing)
        if should_trigger_etl():
            response = glue_client.start_job_run(
                JobName=job_name,
                Arguments={
                    '--input_path': s3_key,
                    '--job_bookmark_option': 'job-bookmark-enable'
                }
            )
            
            return {
                'status': 'triggered',
                'job_run_id': response['JobRunId']
            }
        else:
            return {
                'status': 'skipped',
                'reason': 'batch_threshold_not_met'
            }
            
    except Exception as e:
        print(f"Error triggering Glue job: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


def should_trigger_etl():
    """Determine if ETL job should be triggered"""
    # Simple logic - in production would check batch size, timing, etc.
    import random
    return random.random() < 0.1  # 10% chance for demo
