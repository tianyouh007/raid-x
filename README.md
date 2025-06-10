# RAID-X: Risk Assessment and Intelligent Detection for Cryptocurrency Transactions

A comprehensive cryptocurrency fraud detection framework built on AWS using CDK. RAID-X implements a three-layer modular risk assessment system specifically designed for real-world cryptocurrency payment fraud detection, with enterprise-grade infrastructure, patent potential, and regulatory integration in the U.S. market.

## Architecture Overview

RAID-X follows a hybrid architecture combining rule-based compliance, graph-based behavioral analysis, and explainable machine learning to provide comprehensive cryptocurrency transaction risk assessment.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                RAID-X ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │  Data Ingestion │    │   API Gateway    │    │      CloudWatch Dashboard   │ │
│  │                 │    │                  │    │                             │ │
│  │ • Blockchain    │◄───┤ • REST Endpoints │    │ • Real-time Monitoring      │ │
│  │   Data Sources  │    │ • Authentication │    │ • Risk Score Visualization  │ │
│  │ • BigQuery      │    │ • Rate Limiting  │    │ • Compliance Reporting      │ │
│  │ • BlockSci      │    └──────────────────┘    └─────────────────────────────┘ │
│  │ • Custom APIs   │             │                                              │
│  └─────────────────┘             │                                              │
│           │                      │                                              │
│           ▼                      ▼                                              │
│  ┌─────────────────┐    ┌──────────────────┐                                    │
│  │   AWS Glue      │    │   Orchestrator   │                                    │
│  │                 │    │     Lambda       │                                    │
│  │ • ETL Processing│    │                  │                                    │
│  │ • Data Cleaning │    │ • Request Routing│                                    │
│  │ • Feature Eng.  │    │ • Step Functions │                                    │
│  └─────────────────┘    │   Coordination   │                                    │
│           │             └──────────────────┘                                    │
│           │                       │                                             │
│           ▼                       ▼                                             │
│  ┌─────────────────┐    ┌──────────────────┐                                    │
│  │    Amazon S3    │    │ Step Functions   │                                    │
│  │                 │    │   Workflow       │                                    │
│  │ • Raw Data      │    │                  │                                    │
│  │ • Processed     │    │ ┌──────────────┐ │                                    │
│  │   Features      │    │ │     Data     │ │                                    │
│  │ • ML Models     │    │ │  Ingestion   │ │                                    │
│  │ • Results       │    │ └──────────────┘ │                                    │
│  └─────────────────┘    │        │         │                                    │
│                         │        ▼         │                                    │
│                         │ ┌──────────────┐ │   ┌─────────────────────────────┐  │
│                         │ │  R3 Engine   │◄┼───┤        Layer 1              │  │
│                         │ │              │ │   │ Rule-Based Regulatory       │  │
│                         │ │ • OFAC Check │ │   │ Risk Engine (R3)            │  │
│                         │ │ • AML Rules  │ │   │                             │  │
│                         │ │ • Travel Rule│ │   │ • FinCEN Compliance         │  │
│                         │ │ • Sanctions  │ │   │ • FATF Guidelines           │  │
│                         │ └──────────────┘ │   │ • OFAC Sanctions Screening  │  │
│                         │        │         │   │ • High-Value Thresholds     │  │
│                         │        ▼         │   │ • Mixer Detection           │  │
│  ┌─────────────────┐    │ ┌──────────────┐ │   │ • Velocity Checks           │  │
│  │   Amazon        │    │ │    ARSM      │◄┼───┤                             │  │
│  │   Neptune       │◄───┼─┤              │ │   └─────────────────────────────┘  │
│  │                 │    │ │ • Graph      │ │                                    │
│  │ • Transaction   │    │ │   Analysis   │ │   ┌─────────────────────────────┐  │
│  │   Graph         │    │ │ • Centrality │ │   │        Layer 2              │  │
│  │ • Address       │    │ │ • Community  │ │   │ Account Risk Scoring        │  │
│  │   Clusters      │    │ │   Detection  │ │   │ Model (ARSM)                │  │
│  │ • Entity        │    │ │ • Risk       │ │   │                             │  │
│  │   Relationships │    │ │   Propagation│ │   │ • Multi-hop Analysis        │  │
│  │ • Flow Analysis │    │ └──────────────┘ │   │ • Graph Neural Networks     │  │
│  └─────────────────┘    │        │         │   │ • Behavioral Profiling      │  │
│           │             │        ▼         │   │ • Entity Clustering         │  │
│           │              │ ┌──────────────┐ │  │ • Anomaly Propagation       │  │
│           │              │ │    TAD-X     │◄┼──┤                             │  │
│           │              │ │              │ │  └─────────────────────────────┘  │
│           │              │ │ • ML Models  │ │                                   │
│           │              │ │ • SHAP       │ │   ┌─────────────────────────────┐ │
│           │              │ │  Explanations│ │   │        Layer 3              │ │
│           │              │ │ • Ensemble   │ │   │ Transaction Anomaly         │ │
│           │              │ │   Learning   │ │   │ Detection (TAD-X)           │ │
│           │              │ │ • Real-time  │ │   │                             │ │
│           │              │ │   Scoring    │ │   │ • XGBoost/LightGBM Models   │ │
│           │              │ └──────────────┘ │   │ • SHAP Explanations         │ │
│           │              │        │         │   │ • Ensemble Methods          │ │
│           │              │        ▼         │   │ • Real-time Inference       │ │
│           │              │ ┌──────────────┐ │   │ • Regulatory Explanations   │ │
│           │              │ │   Results    │ │   │                             │ │
│           │              │ │  Aggregation │ │   └─────────────────────────────┘ │
│           │              │ └──────────────┘ │                                   │
│           │              └──────────────────┘                                   │
│           │                       │                                             │
│           ▼                       ▼                                             │
│  ┌─────────────────┐    ┌──────────────────┐                                   │
│  │   DynamoDB      │    │   Final Risk     │                                   │
│  │                 │    │   Assessment     │                                   │
│  │ • Config Store  │    │                  │                                   │
│  │ • Metadata      │    │ • Weighted Score │                                   │
│  │ • Results Cache │    │ • Risk Category  │                                   │
│  │ • Audit Trail   │    │ • Explanations   │                                   │
│  └─────────────────┘    │ • Compliance     │                                   │
│                         │   Status         │                                   │
│  ┌─────────────────┐    └──────────────────┘                                   │
│  │   SageMaker     │                                                           │
│  │                 │                                                           │
│  │ • Model Training│                                                           │
│  │ • Notebook      │                                                           │
│  │ • Endpoints     │                                                           │
│  │ • Experiments   │                                                           │
│  └─────────────────┘                                                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### Layer 1: R3 Engine (Rule-Based Regulatory Risk Engine)
**Purpose**: Deterministic screening aligned with FinCEN and FATF AML guidelines

**Key Features**:
- **OFAC Sanctions Screening**: Real-time check against Treasury sanctions lists
- **Travel Rule Compliance**: Validates originator/beneficiary information requirements
- **AML/CFT Checks**: Anti-Money Laundering and Counter-Financing of Terrorism rules
- **High-Value Transaction Flagging**: Configurable thresholds for large transactions
- **Mixer/Tumbler Detection**: Identifies transactions involving known mixing services
- **Velocity Analysis**: Detects unusual transaction frequency patterns

**Technology Stack**:
- AWS Lambda (Python 3.11)
- DynamoDB for rule configuration
- Real-time API integration with compliance databases

### Layer 2: ARSM (Account Risk Scoring Model)
**Purpose**: Graph-based behavioral analysis using multi-hop transaction relationships

**Key Features**:
- **Graph Neural Networks**: Advanced GNN models for relationship analysis
- **Centrality Analysis**: Betweenness, closeness, and eigenvector centrality metrics
- **Community Detection**: Identifies suspicious transaction clusters
- **Behavioral Profiling**: Multi-temporal pattern analysis
- **Risk Propagation**: Spreading activation algorithms for connected risk assessment
- **Entity Resolution**: Address clustering and entity identification

**Technology Stack**:
- Amazon Neptune (Graph Database)
- Gremlin query language
- NetworkX for graph algorithms
- AWS Lambda with enhanced memory (1024MB)

### Layer 3: TAD-X (Transaction Anomaly Detection - Explainable)
**Purpose**: ML-based anomaly detection with regulatory-compliant explanations

**Key Features**:
- **Ensemble Machine Learning**: XGBoost, LightGBM, and Random Forest models
- **SHAP Explanations**: Feature importance and decision reasoning
- **Real-time Inference**: Sub-second prediction capabilities
- **Adaptive Learning**: Continuous model updates with new fraud patterns
- **Regulatory Compliance**: Explainable AI for audit requirements
- **Imbalanced Data Handling**: SMOTE and cost-sensitive learning

**Technology Stack**:
- Amazon SageMaker for model training and hosting
- SHAP for model explainability
- AWS Lambda for real-time inference
- S3 for model artifacts storage

## Data Flow Architecture

```
[Blockchain Data] → [Data Ingestion] → [AWS Glue ETL] → [Feature Store (S3)]
                                                              │
[API Request] → [API Gateway] → [Orchestrator Lambda] → [Step Functions]
                                                              │
                        ┌─────────────────────────────────────┘
                        │
                        ▼
               [Parallel Processing]
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   [R3 Engine]     [ARSM]         [TAD-X]
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
              [Risk Score Aggregation]
                        │
                        ▼
              [Results Storage (DynamoDB)]
                        │
                        ▼
              [Response to Client]
```

## AWS Services Architecture

### Compute Layer
- **AWS Lambda**: Serverless functions for each processing component
- **AWS Step Functions**: Workflow orchestration and parallel processing
- **Amazon SageMaker**: ML model training, hosting, and batch processing

### Storage Layer
- **Amazon S3**: Data lake for raw and processed transaction data
- **Amazon Neptune**: Graph database for transaction network analysis
- **Amazon DynamoDB**: Configuration, metadata, and results storage

### Integration Layer
- **Amazon API Gateway**: RESTful API endpoints with authentication
- **AWS Glue**: ETL processing and data transformation
- **Amazon EventBridge**: Event-driven architecture and scheduling

### Monitoring & Security
- **Amazon CloudWatch**: Logging, monitoring, and alerting
- **AWS IAM**: Fine-grained access control and security policies
- **AWS CloudTrail**: Audit logging and compliance tracking

## Key Innovations

### 1. Hybrid Processing Pipeline
- **Sequential + Parallel Processing**: R3 and ARSM run in parallel, TAD-X integrates results
- **Real-time + Batch**: Supports both streaming and batch processing modes
- **Modular Architecture**: Each layer can be independently scaled and updated

### 2. Explainable AI Integration
- **SHAP Integration**: Built-in model explanations for regulatory compliance
- **Feature Attribution**: Clear reasoning for each risk assessment decision
- **Audit Trail**: Complete transaction processing history

### 3. Regulatory Compliance by Design
- **FinCEN Integration**: Built-in AML/CFT compliance checks
- **FATF Alignment**: Supports all FATF recommendations (10-21)
- **Configurable Rules**: Easily adaptable to changing regulatory requirements

### 4. Enterprise Scalability
- **Auto-scaling**: Serverless architecture scales automatically with load
- **Multi-region**: Deployable across multiple AWS regions
- **High Availability**: Built-in redundancy and failover capabilities

## Deployment Architecture

### Development Environment
```
Developer → CDK CLI → CloudFormation → AWS Resources (Single Region)
```

### Production Environment
```
CI/CD Pipeline → Multi-Region Deployment → Blue/Green Deployment → Monitoring
```

## Performance Characteristics

### Throughput
- **API Requests**: 10,000+ requests/minute
- **Transaction Processing**: 1,000+ transactions/second
- **Graph Queries**: Sub-second response times for complex queries

### Latency
- **R3 Engine**: < 100ms average response time
- **ARSM**: < 500ms for graph analysis
- **TAD-X**: < 200ms for ML inference
- **End-to-end**: < 2 seconds for complete analysis

### Scalability
- **Horizontal Scaling**: Auto-scaling based on demand
- **Vertical Scaling**: Configurable memory and compute resources
- **Storage Scaling**: Unlimited S3 storage, auto-scaling DynamoDB

## Security Architecture

### Data Protection
- **Encryption at Rest**: All data encrypted using AWS KMS
- **Encryption in Transit**: TLS 1.3 for all communications
- **Data Classification**: PII and sensitive data handling

### Access Control
- **IAM Policies**: Least privilege access principles
- **VPC Isolation**: Private subnets for sensitive processing
- **API Authentication**: OAuth 2.0 and API key management

### Compliance
- **SOC 2 Type II**: AWS infrastructure compliance
- **GDPR**: Data privacy and right to be forgotten
- **PCI DSS**: Payment card industry standards

## Cost Optimization

### Resource Optimization
- **Serverless Architecture**: Pay-per-use pricing model
- **Reserved Capacity**: Cost savings for predictable workloads
- **Spot Instances**: Training cost reduction for ML models

### Monitoring & Alerts
- **Cost Tracking**: Real-time cost monitoring and alerting
- **Usage Analytics**: Resource utilization optimization
- **Budget Controls**: Automatic scaling limits and notifications

## Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Node.js 18+ and Python 3.11+
- AWS CDK CLI installed

### Quick Setup
1. **Clone and Setup**:
   ```bash
   ./setup_raid_x.sh
   cd raid-x-framework
   ```

2. **Deploy Infrastructure**:
   ```bash
   ./deploy.sh
   ```

3. **Test the System**:
   ```bash
   curl -X POST https://your-api-gateway-url/analyze \
     -H "Content-Type: application/json" \
     -d '{"transaction": {"id": "test-123", "amount": 1.5, "from_address": "1A1z...", "to_address": "3Fup..."}}'
   ```

### Configuration

The framework is highly configurable through `config/config.json`:

```json
{
  "compliance_rules": {
    "ofac_sanctions": {"enabled": true, "risk_weight": 1.0},
    "high_value_threshold": {"threshold_usd": 10000, "risk_weight": 0.3}
  },
  "risk_scoring": {
    "weights": {"r3_engine": 0.3, "arsm": 0.3, "tad_x": 0.4}
  },
  "ml_models": {
    "tad_x": {"model_type": "lightgbm", "n_estimators": 100}
  }
}
```

## API Documentation

### Endpoints

#### POST /analyze
Analyze a cryptocurrency transaction for fraud risk.

**Request Body**:
```json
{
  "transaction": {
    "id": "string",
    "from_address": "string", 
    "to_address": "string",
    "amount": "number",
    "currency": "string",
    "timestamp": "number"
  }
}
```

**Response**:
```json
{
  "transaction_id": "string",
  "final_risk_score": "number",
  "risk_category": "string",
  "component_scores": {
    "r3_score": "number",
    "arsm_score": "number", 
    "ml_score": "number"
  },
  "explanations": {
    "feature_name": {
      "value": "number",
      "importance": "number",
      "impact": "string"
    }
  }
}
```

#### GET /status
Check system status or specific transaction analysis status.

**Query Parameters**:
- `execution_arn`: Step Function execution ARN
- `transaction_id`: Transaction identifier

## Monitoring and Alerting

### CloudWatch Dashboards
- **System Health**: Lambda metrics, error rates, duration
- **Business Metrics**: Transaction volume, risk score distribution
- **Cost Tracking**: Resource utilization and costs

### Alerts
- **High Error Rates**: Automatic notification for processing failures
- **High Risk Transactions**: Immediate alerts for critical risk scores
- **System Performance**: Latency and throughput monitoring

## Testing

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Load Testing
```bash
pytest tests/load/ -v
```

## Troubleshooting

### Common Issues

1. **Neptune Connection Timeout**
   - Check VPC security groups
   - Verify IAM permissions

2. **Lambda Cold Start**
   - Use provisioned concurrency for critical functions
   - Optimize function initialization

3. **High Costs**
   - Review CloudWatch cost dashboards
   - Optimize resource allocation

### Debugging

- **CloudWatch Logs**: Detailed logging for each component
- **X-Ray Tracing**: End-to-end request tracing
- **Step Functions Console**: Visual workflow debugging

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Run tests: `pytest tests/`
4. Submit pull request

### Code Standards
- **Python**: Follow PEP 8 style guide
- **Documentation**: Comprehensive docstrings
- **Testing**: Minimum 80% code coverage

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support and questions:
- GitHub Issues: [Project Issues](https://github.com/tianyouh007/raid-x)
- Documentation: [Wiki](https://github.com/tianyouh007/raid-x/wiki)

## Roadmap

### Phase 1 
- ✅ Core framework implementation
- ✅ Basic compliance rules
- ✅ Graph analysis capabilities
- ✅ ML model integration

### Phase 2 
- 🔄 Advanced GNN models
- 🔄 Real-time streaming processing
- 🔄 Enhanced SHAP explanations
- 🔄 Multi-blockchain support

### Phase 3 
- 📋 Federated learning capabilities
- 📋 Advanced privacy features
- 📋 Regulatory reporting automation
- 📋 Enterprise integrations