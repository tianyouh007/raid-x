"""
Glue ETL script for processing cryptocurrency transaction data
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import *
import boto3

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_bucket'])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

def process_transactions():
    """Main ETL processing function"""
    
    # Read transaction data from S3
    input_path = f"s3://{args['input_path']}"
    
    # Create dynamic frame from S3
    transactions_df = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [input_path],
            "recurse": True
        },
        format="json"
    ).toDF()
    
    # Data transformations
    processed_df = transactions_df.select(
        F.col("id").alias("transaction_id"),
        F.col("from_address"),
        F.col("to_address"),
        F.col("amount").cast(DoubleType()),
        F.col("timestamp").cast(LongType()),
        F.col("currency"),
        F.col("amount_usd").cast(DoubleType()),
        F.col("size_category"),
        F.col("hour_of_day").cast(IntegerType()),
        F.col("day_of_week").cast(IntegerType())
    )
    
    # Add derived features
    processed_df = processed_df.withColumn(
        "log_amount", F.log10(F.col("amount") + 1)
    ).withColumn(
        "is_weekend", F.when(F.col("day_of_week").isin([5, 6]), 1).otherwise(0)
    ).withColumn(
        "is_night", F.when(F.col("hour_of_day").between(22, 6), 1).otherwise(0)
    )
    
    # Write processed data back to S3
    output_path = f"s3://{args['output_bucket']}/processed-transactions/"
    
    processed_df.write.mode("append").partitionBy("currency").parquet(output_path)
    
    # Update Neptune with transaction graph
    update_neptune_graph(processed_df)
    
    print(f"Processed {processed_df.count()} transactions")

def update_neptune_graph(df):
    """Update Neptune graph with transaction data"""
    try:
        # Collect small sample for Neptune update
        sample_transactions = df.limit(100).collect()
        
        # Here you would connect to Neptune and update the graph
        # For now, just log the operation
        print(f"Would update Neptune with {len(sample_transactions)} transactions")
        
    except Exception as e:
        print(f"Error updating Neptune: {str(e)}")

# Run the ETL process
if __name__ == "__main__":
    process_transactions()
    job.commit()
