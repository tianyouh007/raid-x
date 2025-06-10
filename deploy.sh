#!/bin/bash

# RAID-X Deployment Script

set -e

echo "🚀 Deploying RAID-X Framework..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install dev dependencies for testing
pip install -r requirements-dev.txt

# Run basic tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Bootstrap CDK (only needed once per account/region)
echo "🎯 Bootstrapping CDK..."
cdk bootstrap || echo "CDK already bootstrapped or bootstrap failed"

# Synthesize CloudFormation template
echo "🔧 Synthesizing CDK template..."
cdk synth

# Deploy the stack
echo "🚀 Deploying stack..."
cdk deploy --require-approval never

echo "✅ RAID-X Framework deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Check the AWS Console for deployed resources"
echo "2. Test the API endpoints"
echo "3. Upload sample data for processing"
echo "4. Monitor CloudWatch logs"
