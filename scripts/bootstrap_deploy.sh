#!/bin/bash

# Workaround script for AWS Need to perform AWS calls for account XXX, but no credentials have been configured
# Need to pass in AWS_PROFILE and AWS_REGION as arguments
# Need to run aws configure and load variables from ~/.aws/credentials

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Move to the infra directory (one level up from scripts)
cd "$SCRIPT_DIR/../infra"

# Check for environment variables first, then fall back to command line arguments
AWS_PROFILE=${AWS_PROFILE:-${1:-default}}
AWS_REGION=${AWS_REGION:-${2:-us-east-1}}

# Export AWS credentials and bootstrap CDK
export AWS_PROFILE=$AWS_PROFILE
export AWS_REGION=$AWS_REGION

echo "bootstrapping..."
# Export AWS credentials and bootstrap CDK
export $(aws configure export-credentials --format env | xargs) && cdk bootstrap


echo "AWS_PROFILE: $AWS_PROFILE"
echo "AWS_REGION: $AWS_REGION"


echo "deploying..."
# Deploy CDK stack
export $(aws configure export-credentials --format env | xargs) && cdk deploy --require-approval never