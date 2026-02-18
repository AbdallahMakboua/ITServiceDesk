# PoC Cleanup Guide

## Overview

This guide will help you clean up all resources created for the DAS Holding AI IT L1 Voice Service Desk PoC, while preserving your Amazon Connect instance and phone number.

**Date:** 2026-02-18  
**Region:** us-east-1

---

## What Will Be Deleted

The cleanup script will remove:

1. **AgentCore Gateway** (manual deletion required first)
   - Gateway: `poc-itsm-agentcore-gateway`

2. **IAM Roles (3 total)**
   - `poc-connect-ai-agent-role`
   - `poc-agentcore-gateway-role`
   - `poc-itsm-lambda-role`

3. **IAM Policies (3 total)**
   - `poc-connect-ai-agent-policy`
   - `poc-agentcore-gateway-policy`
   - `poc-itsm-lambda-policy`

4. **Secrets Manager**
   - Secret: `poc-itsm-api-key`

5. **API Gateway**
   - API: `iixw3qtwo3`
   - Endpoint: `https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc`

6. **Lambda Function**
   - Function: `poc-itsm-api-handler`

7. **DynamoDB Table**
   - Table: `poc-itsm-tickets`

8. **S3 Bucket**
   - Bucket: `poc-itsm-openapi-specs-714059461907`

9. **CloudWatch Log Groups**
   - `/aws/lambda/poc-itsm-api-handler`

---

## What Will Be Kept

These resources will NOT be deleted:

1. **Amazon Connect Instance**
   - Instance: `poc-ai-l1-support`
   - Instance ID: `c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
   - Access URL: `https://poc-ai-l1-support.my.connect.aws`

2. **Phone Number**
   - Number: +16782709241
   - Cost: ~$1/month

3. **Connect AI Agents**
   - Agent: `poc-l1-support-agent`
   - Prompt: `POC-prompt`

4. **Connect Contact Flows**
   - Flow: `poc-l1-support-flow`

5. **Connect CloudWatch Logs**
   - Log Group: `/aws/connect/poc-ai-l1-support`

---

## Cleanup Steps

### Step 1: Delete AgentCore Gateway (Manual)

**IMPORTANT:** The AgentCore Gateway must be deleted manually BEFORE running the cleanup script.

1. Open AWS Console
2. Navigate to **Amazon Bedrock** → **AgentCore Gateway**
3. Find: `poc-itsm-agentcore-gateway`
4. Select it and click **Delete**
5. Confirm deletion
6. Wait for deletion to complete (may take 1-2 minutes)

**Why manual?** AWS CLI doesn't have a direct command for AgentCore Gateway deletion yet.

### Step 2: Run the Cleanup Script

Once the AgentCore Gateway is deleted:

```bash
# Make the script executable
chmod +x cleanup-poc-resources.sh

# Run the cleanup script
bash cleanup-poc-resources.sh
```

The script will:
1. Ask for confirmation before proceeding
2. Prompt you to confirm AgentCore Gateway deletion
3. Delete all other resources automatically
4. Show progress for each deletion
5. Display a summary at the end

### Step 3: Verify Cleanup

After the script completes, verify resources are deleted:

**Via AWS Console:**
1. **IAM** → Roles → Search for "poc-" (should find none)
2. **IAM** → Policies → Search for "poc-" (should find none)
3. **Secrets Manager** → Search for "poc-itsm-api-key" (should find none)
4. **API Gateway** → APIs → Search for "poc" (should find none)
5. **Lambda** → Functions → Search for "poc-itsm-api-handler" (should find none)
6. **DynamoDB** → Tables → Search for "poc-itsm-tickets" (should find none)
7. **S3** → Buckets → Search for "poc-itsm-openapi-specs" (should find none)

**Via AWS CLI:**
```bash
# Check IAM roles
aws iam list-roles --region us-east-1 | grep poc-

# Check Lambda functions
aws lambda list-functions --region us-east-1 | grep poc-

# Check DynamoDB tables
aws dynamodb list-tables --region us-east-1 | grep poc-

# Check S3 buckets
aws s3 ls | grep poc-
```

### Step 4: Verify Connect Resources Are Intact

**Via AWS Console:**
1. **Amazon Connect** → Instances → Verify `poc-ai-l1-support` exists
2. **Phone Numbers** → Verify +16782709241 is still claimed
3. **AI Agents** → Verify `poc-l1-support-agent` exists
4. **Contact Flows** → Verify `poc-l1-support-flow` exists

**Test the phone number:**
- Call +16782709241
- Verify it still connects (even if the flow doesn't work perfectly)

---

## Cost Impact

### Before Cleanup
- **Secrets Manager:** ~$0.40/month
- **DynamoDB:** ~$0.00/month (free tier)
- **Lambda:** ~$0.00/month (free tier)
- **API Gateway:** ~$0.00/month (free tier)
- **S3:** ~$0.00/month (minimal storage)
- **Connect Phone Number:** ~$1.00/month
- **Total:** ~$1.40/month

### After Cleanup
- **Connect Phone Number:** ~$1.00/month
- **Total:** ~$1.00/month

**Savings:** ~$0.40/month

---

## Troubleshooting

### Issue: AgentCore Gateway won't delete

**Solution:**
- Check if it's still in use by Connect AI Agent
- Go to Connect → AI Agents → `poc-l1-support-agent`
- Remove the AgentCore Gateway link
- Try deleting the gateway again

### Issue: IAM role won't delete

**Error:** "Role is still in use"

**Solution:**
```bash
# List policies attached to the role
aws iam list-attached-role-policies --role-name poc-connect-ai-agent-role --region us-east-1

# Detach each policy manually
aws iam detach-role-policy \
  --role-name poc-connect-ai-agent-role \
  --policy-arn <policy-arn> \
  --region us-east-1

# Then delete the role
aws iam delete-role --role-name poc-connect-ai-agent-role --region us-east-1
```

### Issue: S3 bucket won't delete

**Error:** "Bucket not empty"

**Solution:**
```bash
# Empty the bucket first
aws s3 rm s3://poc-itsm-openapi-specs-714059461907 --recursive --region us-east-1

# Then delete the bucket
aws s3 rb s3://poc-itsm-openapi-specs-714059461907 --region us-east-1
```

### Issue: DynamoDB table won't delete

**Error:** "Table is being deleted"

**Solution:**
- Wait 1-2 minutes for the deletion to complete
- DynamoDB deletions can take time
- Check status: `aws dynamodb describe-table --table-name poc-itsm-tickets --region us-east-1`

---

## Manual Cleanup (If Script Fails)

If the script fails, you can delete resources manually:

### Delete IAM Roles and Policies

```bash
# Connect AI Agent Role
aws iam detach-role-policy --role-name poc-connect-ai-agent-role --policy-arn arn:aws:iam::714059461907:policy/poc-connect-ai-agent-policy --region us-east-1
aws iam delete-policy --policy-arn arn:aws:iam::714059461907:policy/poc-connect-ai-agent-policy --region us-east-1
aws iam delete-role --role-name poc-connect-ai-agent-role --region us-east-1

# AgentCore Gateway Role
aws iam detach-role-policy --role-name poc-agentcore-gateway-role --policy-arn arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy --region us-east-1
aws iam delete-policy --policy-arn arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy --region us-east-1
aws iam delete-role --role-name poc-agentcore-gateway-role --region us-east-1

# Lambda Role
aws iam detach-role-policy --role-name poc-itsm-lambda-role --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy --region us-east-1
aws iam delete-policy --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy --region us-east-1
aws iam delete-role --role-name poc-itsm-lambda-role --region us-east-1
```

### Delete Other Resources

```bash
# Secrets Manager
aws secretsmanager delete-secret --secret-id poc-itsm-api-key --force-delete-without-recovery --region us-east-1

# API Gateway
aws apigateway delete-rest-api --rest-api-id iixw3qtwo3 --region us-east-1

# Lambda
aws lambda delete-function --function-name poc-itsm-api-handler --region us-east-1

# DynamoDB
aws dynamodb delete-table --table-name poc-itsm-tickets --region us-east-1

# S3
aws s3 rm s3://poc-itsm-openapi-specs-714059461907 --recursive --region us-east-1
aws s3 rb s3://poc-itsm-openapi-specs-714059461907 --region us-east-1

# CloudWatch Logs
aws logs delete-log-group --log-group-name /aws/lambda/poc-itsm-api-handler --region us-east-1
```

---

## Optional: Delete Connect Resources Later

If you want to delete the Amazon Connect resources later (not recommended now):

### Delete AI Agent
1. Go to Connect admin console
2. Navigate to **AI Agents**
3. Select `poc-l1-support-agent`
4. Click **Delete**

### Delete Contact Flow
1. Go to Connect admin console
2. Navigate to **Routing** → **Contact flows**
3. Select `poc-l1-support-flow`
4. Click **Delete**

### Release Phone Number
1. Go to Connect admin console
2. Navigate to **Channels** → **Phone numbers**
3. Select +16782709241
4. Click **Release**
5. **Cost savings:** ~$1/month

### Delete Connect Instance
1. Go to AWS Console → Amazon Connect
2. Select `poc-ai-l1-support`
3. Click **Delete**
4. Type the instance name to confirm
5. **Note:** This will delete ALL Connect data, flows, agents, etc.

---

## Summary

**To clean up the PoC:**

1. Delete AgentCore Gateway manually via AWS Console
2. Run: `bash cleanup-poc-resources.sh`
3. Verify all resources are deleted
4. Keep Amazon Connect instance and phone number

**Cost after cleanup:** ~$1/month (phone number only)

**Time required:** ~5-10 minutes

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-18  
**Status:** Ready to Execute
