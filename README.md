# RAID-X: Risk Assessment and Intelligent Detection for Cryptocurrency Transactions

A comprehensive cryptocurrency fraud detection framework built on AWS using CDK.

## Architecture

The RAID-X framework consists of three main layers:

1. **R3 Engine (Rule-Based Regulatory Risk Engine)**: Compliance screening for known risks
2. **ARSM (Account Risk Scoring Model)**: Graph-based behavioral analysis 
3. **TAD-X (Transaction Anomaly Detection - Explainable)**: ML-based anomaly detection with SHAP explanations

## AWS Services Used

- Amazon Neptune: Graph database for transaction networks
- Amazon SageMaker: ML model training and inference
- AWS Lambda: Serverless compute for processing
- AWS Step Functions: Workflow orchestration
- Amazon DynamoDB: Metadata and configuration storage
- Amazon S3: Data lake for blockchain data
- AWS Glue: ETL processing
- Amazon API Gateway: REST API endpoints

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

3. Bootstrap CDK (first time only):
   ```bash
   cdk bootstrap
   ```

4. Deploy the stack:
   ```bash
   cdk deploy
   ```

## Configuration

Edit `config/config.json` to customize:
- Neptune instance types
- Lambda memory settings
- SageMaker training parameters
- Compliance rules

## Testing

Run tests with:
```bash
pytest tests/
```
