#!/bin/bash

# RAID-X Destroy Script

set -e

echo "🗑️  Destroying RAID-X Framework..."

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Destroy the stack
echo "🔥 Destroying CDK stack..."
cdk destroy --force

echo "✅ RAID-X Framework destroyed successfully!"
