#!/bin/bash

# Cleanup Script for DAS Holding AI IT L1 Voice Service Desk PoC
# This script deletes all created resources EXCEPT Amazon Connect
# Region: us-east-1

set -e

REGION="us-east-1"
ACCOUNT_ID="714059461907"

echo "=========================================="
echo "PoC Cleanup Script"
echo "=========================================="
echo "This will delete all PoC resources EXCEPT Amazon Connect"
echo "Region: $REGION"
echo ""
echo "Resources to be deleted:"
echo "  - AgentCore Gateway"
echo "  - IAM Roles and Policies (3 roles)"
echo "  - Secrets Manager Secret"
echo "  - API Gateway"
echo "  - Lambda Function"
echo "  - DynamoDB Table"
echo "  - S3 Bucket"
echo "  - CloudWatch Log Groups"
echo ""
echo "Resources to be KEPT:"
echo "  - Amazon Connect Instance (poc-ai-l1-support)"
echo "  - Phone Number (+16782709241)"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup..."
echo ""

# Phase 1: Delete AgentCore Gateway
echo "Phase 1: Deleting AgentCore Gateway..."
echo "Note: AgentCore Gateway must be deleted manually via AWS Console"
echo "  1. Go to AWS Console → Amazon Bedrock → AgentCore Gateway"
echo "  2. Select: poc-itsm-agentcore-gateway"
echo "  3. Click Delete"
echo ""
read -p "Press Enter after you've deleted the AgentCore Gateway manually..."

# Phase 2: Delete IAM Roles and Policies
echo ""
echo "Phase 2: Deleting IAM Roles and Policies..."

# Connect AI Agent Role
echo "  Deleting Connect AI Agent IAM role..."
aws iam detach-role-policy \
  --role-name poc-connect-ai-agent-role \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-connect-ai-agent-policy \
  --region $REGION 2>/dev/null || echo "    Policy already detached or doesn't exist"

aws iam delete-policy \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-connect-ai-agent-policy \
  --region $REGION 2>/dev/null || echo "    Policy already deleted or doesn't exist"

aws iam delete-role \
  --role-name poc-connect-ai-agent-role \
  --region $REGION 2>/dev/null || echo "    Role already deleted or doesn't exist"

echo "  ✓ Connect AI Agent role deleted"

# AgentCore Gateway Role
echo "  Deleting AgentCore Gateway IAM role..."
aws iam detach-role-policy \
  --role-name poc-agentcore-gateway-role \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-agentcore-gateway-policy \
  --region $REGION 2>/dev/null || echo "    Policy already detached or doesn't exist"

aws iam delete-policy \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-agentcore-gateway-policy \
  --region $REGION 2>/dev/null || echo "    Policy already deleted or doesn't exist"

aws iam delete-role \
  --role-name poc-agentcore-gateway-role \
  --region $REGION 2>/dev/null || echo "    Role already deleted or doesn't exist"

echo "  ✓ AgentCore Gateway role deleted"

# Lambda Role
echo "  Deleting Lambda IAM role..."
aws iam detach-role-policy \
  --role-name poc-itsm-lambda-role \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-itsm-lambda-policy \
  --region $REGION 2>/dev/null || echo "    Policy already detached or doesn't exist"

aws iam delete-policy \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-itsm-lambda-policy \
  --region $REGION 2>/dev/null || echo "    Policy already deleted or doesn't exist"

aws iam delete-role \
  --role-name poc-itsm-lambda-role \
  --region $REGION 2>/dev/null || echo "    Role already deleted or doesn't exist"

echo "  ✓ Lambda role deleted"

# Phase 3: Delete Secrets Manager Secret
echo ""
echo "Phase 3: Deleting Secrets Manager secret..."
aws secretsmanager delete-secret \
  --secret-id poc-itsm-api-key \
  --force-delete-without-recovery \
  --region $REGION 2>/dev/null || echo "  Secret already deleted or doesn't exist"

echo "  ✓ Secret deleted"

# Phase 4: Delete API Gateway
echo ""
echo "Phase 4: Deleting API Gateway..."
aws apigateway delete-rest-api \
  --rest-api-id iixw3qtwo3 \
  --region $REGION 2>/dev/null || echo "  API Gateway already deleted or doesn't exist"

echo "  ✓ API Gateway deleted"

# Phase 5: Delete Lambda Function
echo ""
echo "Phase 5: Deleting Lambda function..."
aws lambda delete-function \
  --function-name poc-itsm-api-handler \
  --region $REGION 2>/dev/null || echo "  Lambda function already deleted or doesn't exist"

echo "  ✓ Lambda function deleted"

# Phase 6: Delete DynamoDB Table
echo ""
echo "Phase 6: Deleting DynamoDB table..."
aws dynamodb delete-table \
  --table-name poc-itsm-tickets \
  --region $REGION 2>/dev/null || echo "  DynamoDB table already deleted or doesn't exist"

echo "  ✓ DynamoDB table deleted"

# Phase 7: Delete S3 Bucket
echo ""
echo "Phase 7: Deleting S3 bucket..."
aws s3 rm s3://poc-itsm-openapi-specs-${ACCOUNT_ID} --recursive --region $REGION 2>/dev/null || echo "  Bucket already empty or doesn't exist"
aws s3 rb s3://poc-itsm-openapi-specs-${ACCOUNT_ID} --region $REGION 2>/dev/null || echo "  Bucket already deleted or doesn't exist"

echo "  ✓ S3 bucket deleted"

# Phase 8: Delete CloudWatch Log Groups
echo ""
echo "Phase 8: Deleting CloudWatch log groups..."
aws logs delete-log-group \
  --log-group-name /aws/lambda/poc-itsm-api-handler \
  --region $REGION 2>/dev/null || echo "  Lambda log group already deleted or doesn't exist"

echo "  ✓ Lambda log group deleted"
echo "  Note: Connect log group (/aws/connect/poc-ai-l1-support) kept for Connect instance"

# Summary
echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Deleted resources:"
echo "  ✓ AgentCore Gateway (manual)"
echo "  ✓ IAM Roles (3): poc-connect-ai-agent-role, poc-agentcore-gateway-role, poc-itsm-lambda-role"
echo "  ✓ IAM Policies (3): poc-connect-ai-agent-policy, poc-agentcore-gateway-policy, poc-itsm-lambda-policy"
echo "  ✓ Secrets Manager: poc-itsm-api-key"
echo "  ✓ API Gateway: iixw3qtwo3"
echo "  ✓ Lambda Function: poc-itsm-api-handler"
echo "  ✓ DynamoDB Table: poc-itsm-tickets"
echo "  ✓ S3 Bucket: poc-itsm-openapi-specs-${ACCOUNT_ID}"
echo "  ✓ CloudWatch Log Groups"
echo ""
echo "Kept resources (as requested):"
echo "  ✓ Amazon Connect Instance: poc-ai-l1-support"
echo "  ✓ Phone Number: +16782709241"
echo "  ✓ Connect AI Agents (poc-l1-support-agent, etc.)"
echo "  ✓ Connect Flows (poc-l1-support-flow, etc.)"
echo ""
echo "Note: If you want to delete Connect resources later, do it manually via Console"
echo ""
echo "Estimated cost savings: ~$0.40/month (Secrets Manager)"
echo "Remaining cost: ~$1/month (Connect phone number)"
echo ""
