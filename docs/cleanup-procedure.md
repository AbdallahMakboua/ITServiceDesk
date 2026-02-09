# Cleanup Procedure Documentation - Task 0.10

## Overview

This document provides step-by-step instructions for completely removing all PoC resources to prevent ongoing charges. The cleanup procedure must be executed when the PoC is complete or if the $8 USD budget alert is triggered.

**CRITICAL:** Follow the order specified to avoid dependency errors.

---

## Cleanup Checklist

Use this checklist to track cleanup progress:

- [ ] 1. Cost analysis and documentation
- [ ] 2. Amazon Connect resources (phone number, AI Agent, flow, instance)
- [ ] 3. Bedrock AgentCore Gateway
- [ ] 4. AgentCore Gateway IAM resources
- [ ] 5. Connect AI Agent IAM resources
- [ ] 6. API Gateway or Lambda Function URL
- [ ] 7. Lambda function
- [ ] 8. Lambda IAM resources
- [ ] 9. DynamoDB table
- [ ] 10. S3 bucket and objects
- [ ] 11. AWS Secrets Manager secret
- [ ] 12. CloudWatch log groups
- [ ] 13. AWS Budget
- [ ] 14. Final verification

---

## Pre-Cleanup: Cost Analysis

### Step 1: Document Final Costs

**Purpose:** Record actual spending before cleanup

**Actions:**
1. Navigate to AWS Cost Explorer
2. Filter by date range (PoC start to end)
3. Filter by region (us-east-1)
4. Export cost breakdown by service
5. Document in `docs/cost-analysis.md`

**AWS CLI:**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-02-09,End=2026-02-12 \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter file://cost-filter.json \
  --output json > final-costs.json
```

**cost-filter.json:**
```json
{
  "Dimensions": {
    "Key": "REGION",
    "Values": ["us-east-1"]
  }
}
```

**Verification:**
- [ ] Total cost documented
- [ ] Cost breakdown by service recorded
- [ ] Comparison to $10 budget noted

---

## Phase 3 Cleanup: Amazon Connect Resources

### Step 2: Release Phone Number

**Purpose:** Stop daily phone number charges

**Console:**
1. Navigate to Amazon Connect console
2. Select instance: `poc-ai-l1-support`
3. Go to **Channels** → **Phone numbers**
4. Select the claimed phone number
5. Click **Release**
6. Confirm release

**Verification:**
```bash
# List phone numbers (should be empty)
aws connect list-phone-numbers \
  --instance-id <INSTANCE_ID> \
  --region us-east-1
```

**Expected:** Empty list or phone number not associated with instance

### Step 3: Delete Contact Flow

**Purpose:** Remove call routing logic

**Console:**
1. Navigate to Amazon Connect console
2. Select instance: `poc-ai-l1-support`
3. Go to **Routing** → **Contact flows**
4. Find flow: `poc-l1-support-flow`
5. Click **Delete**
6. Confirm deletion

**Verification:**
- [ ] Contact flow no longer appears in list

### Step 4: Delete AI Agent

**Purpose:** Remove AI Agent configuration

**Console:**
1. Navigate to Amazon Connect console
2. Select instance: `poc-ai-l1-support`
3. Go to **Agent experiences** → **AI Agents**
4. Find agent: `poc-l1-support-agent`
5. Click **Delete**
6. Confirm deletion

**Verification:**
- [ ] AI Agent no longer appears in list

### Step 5: Delete Connect Instance

**Purpose:** Remove Connect instance and stop all charges

**Console:**
1. Navigate to Amazon Connect console
2. Find instance: `poc-ai-l1-support`
3. Click **Delete**
4. Type instance alias to confirm
5. Click **Delete**

**Note:** Instance deletion may take several minutes

**Verification:**
```bash
# List Connect instances (should not include poc-ai-l1-support)
aws connect list-instances --region us-east-1
```

**Expected:** Instance not in list or status = DELETING

---

## Phase 2 Cleanup: AgentCore Gateway

### Step 6: Delete AgentCore Gateway

**Purpose:** Remove MCP server and stop Bedrock charges

**Console:**
1. Navigate to Amazon Bedrock console
2. Go to **AgentCore** → **Gateways**
3. Find gateway: `poc-itsm-agentcore-gateway`
4. Click **Delete**
5. Confirm deletion

**CLI (if available):**
```bash
# Exact command TBD - depends on Bedrock AgentCore CLI support
aws bedrock delete-agent-gateway \
  --gateway-id <GATEWAY_ID> \
  --region us-east-1
```

**Verification:**
- [ ] Gateway no longer appears in Bedrock console

### Step 7: Delete AgentCore Gateway IAM Role

**Purpose:** Remove IAM role and policy

**Commands:**
```bash
# Detach policy from role
aws iam detach-role-policy \
  --role-name poc-agentcore-gateway-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-agentcore-gateway-policy

# Delete policy
aws iam delete-policy \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-agentcore-gateway-policy

# Delete role
aws iam delete-role \
  --role-name poc-agentcore-gateway-role
```

**Verification:**
```bash
# Should return NoSuchEntity error
aws iam get-role --role-name poc-agentcore-gateway-role
```

**Expected:** Error: NoSuchEntity

### Step 8: Delete Connect AI Agent IAM Role

**Purpose:** Remove Connect AI Agent IAM resources

**Commands:**
```bash
# Detach policy from role
aws iam detach-role-policy \
  --role-name poc-connect-ai-agent-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-connect-ai-agent-policy

# Delete policy
aws iam delete-policy \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-connect-ai-agent-policy

# Delete role
aws iam delete-role \
  --role-name poc-connect-ai-agent-role
```

**Verification:**
```bash
# Should return NoSuchEntity error
aws iam get-role --role-name poc-connect-ai-agent-role
```

**Expected:** Error: NoSuchEntity

---

## Phase 1 Cleanup: Mock ITSM Backend

### Step 9: Delete API Gateway

**Purpose:** Remove REST API and stop API Gateway charges

**Commands:**
```bash
# Get API ID
aws apigateway get-rest-apis --region us-east-1 --query 'items[?name==`poc-itsm-api`].id' --output text

# Delete API Gateway
aws apigateway delete-rest-api \
  --rest-api-id <API_ID> \
  --region us-east-1
```

**Alternative (if using Lambda Function URL):**
```bash
# Delete Function URL
aws lambda delete-function-url-config \
  --function-name poc-itsm-api-handler \
  --region us-east-1
```

**Verification:**
```bash
# Should not include poc-itsm-api
aws apigateway get-rest-apis --region us-east-1
```

**Expected:** API not in list

### Step 10: Delete Lambda Function

**Purpose:** Remove Lambda function and stop compute charges

**Commands:**
```bash
# Delete Lambda function
aws lambda delete-function \
  --function-name poc-itsm-api-handler \
  --region us-east-1
```

**Verification:**
```bash
# Should return ResourceNotFoundException
aws lambda get-function \
  --function-name poc-itsm-api-handler \
  --region us-east-1
```

**Expected:** Error: ResourceNotFoundException

### Step 11: Delete Lambda IAM Role

**Purpose:** Remove Lambda IAM resources

**Commands:**
```bash
# Detach policy from role
aws iam detach-role-policy \
  --role-name poc-itsm-lambda-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-itsm-lambda-policy

# Delete policy
aws iam delete-policy \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-itsm-lambda-policy

# Delete role
aws iam delete-role \
  --role-name poc-itsm-lambda-role
```

**Verification:**
```bash
# Should return NoSuchEntity error
aws iam get-role --role-name poc-itsm-lambda-role
```

**Expected:** Error: NoSuchEntity

### Step 12: Delete DynamoDB Table

**Purpose:** Remove table and stop storage charges

**Commands:**
```bash
# Delete DynamoDB table
aws dynamodb delete-table \
  --table-name poc-itsm-tickets \
  --region us-east-1
```

**Note:** Table deletion may take a few minutes

**Verification:**
```bash
# Should return ResourceNotFoundException
aws dynamodb describe-table \
  --table-name poc-itsm-tickets \
  --region us-east-1
```

**Expected:** Error: ResourceNotFoundException

### Step 13: Delete S3 Bucket

**Purpose:** Remove OpenAPI spec storage and stop S3 charges

**Commands:**
```bash
# Get bucket name
BUCKET_NAME=$(aws s3 ls | grep poc-itsm-openapi-specs | awk '{print $3}')

# Delete all objects in bucket
aws s3 rm s3://${BUCKET_NAME} --recursive --region us-east-1

# Delete bucket
aws s3 rb s3://${BUCKET_NAME} --region us-east-1
```

**Verification:**
```bash
# Should not include poc-itsm-openapi-specs
aws s3 ls
```

**Expected:** Bucket not in list

### Step 14: Delete Secrets Manager Secret

**Purpose:** Remove API key and stop Secrets Manager charges

**Commands:**
```bash
# Force delete secret (no recovery period)
aws secretsmanager delete-secret \
  --secret-id poc-itsm-api-key \
  --force-delete-without-recovery \
  --region us-east-1
```

**Verification:**
```bash
# Should return ResourceNotFoundException
aws secretsmanager describe-secret \
  --secret-id poc-itsm-api-key \
  --region us-east-1
```

**Expected:** Error: ResourceNotFoundException

---

## Supporting Services Cleanup

### Step 15: Delete CloudWatch Log Groups

**Purpose:** Remove logs and stop storage charges

**Commands:**
```bash
# Delete Lambda log group
aws logs delete-log-group \
  --log-group-name /aws/lambda/poc-itsm-api-handler \
  --region us-east-1

# Delete API Gateway log group (if exists)
aws logs delete-log-group \
  --log-group-name /aws/apigateway/poc-itsm-api \
  --region us-east-1

# Delete Connect log group (if exists)
aws logs delete-log-group \
  --log-group-name /aws/connect/poc-ai-l1-support \
  --region us-east-1

# Delete AgentCore log group (if exists)
aws logs delete-log-group \
  --log-group-name /aws/bedrock/agentcore/poc-itsm-agentcore-gateway \
  --region us-east-1
```

**Verification:**
```bash
# List log groups (should not include poc-* groups)
aws logs describe-log-groups --region us-east-1 --query 'logGroups[?contains(logGroupName, `poc`)].logGroupName'
```

**Expected:** Empty list

### Step 16: Delete AWS Budget

**Purpose:** Remove budget alert

**Commands:**
```bash
# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Delete budget
aws budgets delete-budget \
  --account-id ${ACCOUNT_ID} \
  --budget-name poc-ai-l1-support-budget
```

**Verification:**
```bash
# Should not include poc-ai-l1-support-budget
aws budgets describe-budgets --account-id ${ACCOUNT_ID}
```

**Expected:** Budget not in list

---

## Final Verification

### Step 17: Verify All Resources Deleted

**Check each service:**

**1. Amazon Connect:**
```bash
aws connect list-instances --region us-east-1
```
Expected: No poc-ai-l1-support instance

**2. Lambda:**
```bash
aws lambda list-functions --region us-east-1 --query 'Functions[?contains(FunctionName, `poc`)].FunctionName'
```
Expected: Empty list

**3. API Gateway:**
```bash
aws apigateway get-rest-apis --region us-east-1 --query 'items[?contains(name, `poc`)].name'
```
Expected: Empty list

**4. DynamoDB:**
```bash
aws dynamodb list-tables --region us-east-1 --query 'TableNames[?contains(@, `poc`)]'
```
Expected: Empty list

**5. S3:**
```bash
aws s3 ls | grep poc
```
Expected: No results

**6. Secrets Manager:**
```bash
aws secretsmanager list-secrets --region us-east-1 --query 'SecretList[?contains(Name, `poc`)].Name'
```
Expected: Empty list

**7. IAM Roles:**
```bash
aws iam list-roles --query 'Roles[?contains(RoleName, `poc`)].RoleName'
```
Expected: Empty list

**8. IAM Policies:**
```bash
aws iam list-policies --scope Local --query 'Policies[?contains(PolicyName, `poc`)].PolicyName'
```
Expected: Empty list

**9. CloudWatch Log Groups:**
```bash
aws logs describe-log-groups --region us-east-1 --query 'logGroups[?contains(logGroupName, `poc`)].logGroupName'
```
Expected: Empty list

### Step 18: Verify No Ongoing Charges

**Actions:**
1. Wait 24-48 hours for final billing cycle
2. Check AWS Cost Explorer for us-east-1
3. Verify no new charges after cleanup date
4. Confirm all services show $0.00 for current period

**Verification Checklist:**
- [ ] No Connect charges
- [ ] No Bedrock charges
- [ ] No Lambda charges
- [ ] No API Gateway charges
- [ ] No DynamoDB charges
- [ ] No S3 charges
- [ ] No Secrets Manager charges
- [ ] No CloudWatch charges

---

## Automated Cleanup Script

### cleanup-all.sh

**Purpose:** Automate cleanup process

**Script:**
```bash
#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "=== PoC Cleanup Script ==="
echo "Region: $REGION"
echo "Account: $ACCOUNT_ID"
echo ""

read -p "Are you sure you want to delete ALL PoC resources? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Step 1: Deleting API Gateway..."
API_ID=$(aws apigateway get-rest-apis --region $REGION --query 'items[?name==`poc-itsm-api`].id' --output text)
if [ -n "$API_ID" ]; then
    aws apigateway delete-rest-api --rest-api-id $API_ID --region $REGION
    echo "✅ API Gateway deleted"
else
    echo "⚠️  API Gateway not found"
fi

echo ""
echo "Step 2: Deleting Lambda function..."
aws lambda delete-function --function-name poc-itsm-api-handler --region $REGION 2>/dev/null && echo "✅ Lambda deleted" || echo "⚠️  Lambda not found"

echo ""
echo "Step 3: Deleting Lambda IAM role..."
aws iam detach-role-policy --role-name poc-itsm-lambda-role --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-itsm-lambda-policy 2>/dev/null
aws iam delete-policy --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/poc-itsm-lambda-policy 2>/dev/null
aws iam delete-role --role-name poc-itsm-lambda-role 2>/dev/null && echo "✅ Lambda IAM deleted" || echo "⚠️  Lambda IAM not found"

echo ""
echo "Step 4: Deleting DynamoDB table..."
aws dynamodb delete-table --table-name poc-itsm-tickets --region $REGION 2>/dev/null && echo "✅ DynamoDB deleted" || echo "⚠️  DynamoDB not found"

echo ""
echo "Step 5: Deleting S3 bucket..."
BUCKET_NAME=$(aws s3 ls | grep poc-itsm-openapi-specs | awk '{print $3}')
if [ -n "$BUCKET_NAME" ]; then
    aws s3 rm s3://${BUCKET_NAME} --recursive --region $REGION
    aws s3 rb s3://${BUCKET_NAME} --region $REGION
    echo "✅ S3 bucket deleted"
else
    echo "⚠️  S3 bucket not found"
fi

echo ""
echo "Step 6: Deleting Secrets Manager secret..."
aws secretsmanager delete-secret --secret-id poc-itsm-api-key --force-delete-without-recovery --region $REGION 2>/dev/null && echo "✅ Secret deleted" || echo "⚠️  Secret not found"

echo ""
echo "Step 7: Deleting CloudWatch log groups..."
aws logs delete-log-group --log-group-name /aws/lambda/poc-itsm-api-handler --region $REGION 2>/dev/null && echo "✅ Lambda logs deleted" || echo "⚠️  Lambda logs not found"
aws logs delete-log-group --log-group-name /aws/apigateway/poc-itsm-api --region $REGION 2>/dev/null && echo "✅ API Gateway logs deleted" || echo "⚠️  API Gateway logs not found"

echo ""
echo "Step 8: Deleting AWS Budget..."
aws budgets delete-budget --account-id ${ACCOUNT_ID} --budget-name poc-ai-l1-support-budget 2>/dev/null && echo "✅ Budget deleted" || echo "⚠️  Budget not found"

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Delete Amazon Connect instance via Console (poc-ai-l1-support)"
echo "2. Delete Bedrock AgentCore Gateway via Console (poc-itsm-agentcore-gateway)"
echo "3. Delete AgentCore IAM role: poc-agentcore-gateway-role"
echo "4. Delete Connect AI Agent IAM role: poc-connect-ai-agent-role"
echo ""
echo "Run final verification in 24-48 hours to confirm no ongoing charges."
```

**Usage:**
```bash
chmod +x cleanup-all.sh
./cleanup-all.sh
```

---

## Emergency Cleanup (Budget Alert Triggered)

If the $8 USD budget alert is triggered:

### Immediate Actions

1. **STOP all work immediately**
2. **Execute cleanup script:** `./cleanup-all.sh`
3. **Manually delete Connect instance** (highest cost)
4. **Manually delete AgentCore Gateway** (second highest cost)
5. **Verify deletions in AWS Console**
6. **Monitor costs for next 24 hours**

### Priority Order (Highest Cost First)

1. Amazon Connect instance (phone number + usage)
2. Bedrock AgentCore Gateway
3. Lambda function
4. API Gateway
5. All other resources

---

## Acceptance Criteria Validation

### Requirement 15.1-15.5: Documented Cleanup with Verification

- ✅ Cleanup procedure lists all created resources
- ✅ Deletion steps for: DynamoDB, Lambda, API Gateway, AgentCore, Connect, S3, IAM, CloudWatch, Secrets Manager
- ✅ Verification steps to confirm deletion
- ✅ Cost verification to ensure no ongoing charges
- ✅ Automated cleanup script provided

---

## Task Status

**Task 0.10: Cleanup Procedure Documentation - COMPLETE ✅**

Comprehensive cleanup procedure documented:
- Step-by-step deletion instructions (18 steps)
- Cleanup checklist for tracking progress
- Verification commands for each step
- Automated cleanup script (cleanup-all.sh)
- Emergency cleanup procedure (budget alert)
- Final verification checklist
- Priority order for cost reduction

**Note:** This cleanup procedure will be executed in Phase 5 (Tasks 5.1-5.8) or immediately if budget alert is triggered.
