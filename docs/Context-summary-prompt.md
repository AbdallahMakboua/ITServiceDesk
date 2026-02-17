# Context Summary - DAS Holding AI IT L1 Voice Service Desk PoC

**Last Updated:** 2026-02-18  
**Current Phase:** Phase 2 Complete, Phase 3 Active - Proceeding with Task 3.2  
**Status:** ACTIVE  
**Next Action:** Task 3.2 (Connect AI Agent IAM Role Creation)

---

## Project Overview

**Project:** DAS Holding AI IT L1 Voice Service Desk PoC  
**Purpose:** AI-driven phone support using Amazon Connect with Bedrock AgentCore Gateway (MCP)  
**Budget:** $10 USD total, $8 USD alert threshold (manual stop rule)  
**Region:** us-east-1 ONLY  
**Critical Constraint:** NO production ITSM integration - mock backend only

---

## Current Status: Phase 3 Active, Phone Number Claimed

**Phase 1: Mock ITSM Backend Implementation - COMPLETE ✅**

All 6 tasks in Phase 1 have been successfully completed and verified. The mock ITSM backend is fully operational with DynamoDB storage, Lambda function, API Gateway REST API, and S3 bucket for OpenAPI specification.

**Phase 2: AgentCore Gateway Configuration - COMPLETE ✅**

All 4 tasks (2.1-2.4) are complete. AgentCore Gateway `poc-itsm-agentcore-gateway` is deployed and active.

**Phase 3: Amazon Connect Setup - IN PROGRESS ⏳**

Task 3.1 (Amazon Connect Instance Creation) is complete. Phone number +16782709241 has been claimed. Proceeding with remaining tasks.

### ✅ Phone Number Quota RESOLVED

**Phone Number:** +16782709241  
**Type:** DID (Direct Inward Dialing)  
**Country:** United States (+1)  
**Claimed Date:** 2026-02-18  
**Cost:** ~$0.03/day (~$1/month)  
**Status:** Active and assigned to poc-ai-l1-support instance

### Completed Tasks

#### ✅ Task 1.1: DynamoDB Table Creation
- **Table:** poc-itsm-tickets
- **Status:** ACTIVE
- **Partition Key:** ticket_id (String)
- **GSI:** CallerIdIndex (caller_id + created_at)
- **Billing:** ON_DEMAND
- **Region:** us-east-1
- **Documentation:** `deployment/dynamodb-creation-log.md`

#### ✅ Task 1.2: Lambda IAM Role Creation
- **Role:** poc-itsm-lambda-role
- **Policy:** poc-itsm-lambda-policy
- **Permissions:** DynamoDB operations on poc-itsm-tickets only, CloudWatch Logs
- **NO wildcard permissions** (least privilege enforced)
- **Documentation:** `deployment/iam-creation-log.md`

#### ✅ Task 1.3: Lambda Function Implementation
- **Code:** `src/lambda/mock_itsm_handler.py`
- **Runtime:** Python 3.12
- **Operations:** create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- **Unit Tests:** 18/18 passing (pytest)
- **Error Handling:** HTTP 200, 201, 400, 404, 500
- **Retry Logic:** Exponential backoff (3 attempts: 0.1s, 0.2s, 0.4s)
- **Documentation:** `deployment/lambda-implementation-log.md`

#### ✅ Task 1.4: Lambda Function Deployment
- **Function:** poc-itsm-api-handler
- **ARN:** arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler
- **State:** Active
- **Timeout:** 10 seconds
- **Memory:** 256 MB
- **Environment:** TABLE_NAME=poc-itsm-tickets, REGION=us-east-1
- **Verification:** Successfully created test ticket in DynamoDB
- **Documentation:** `deployment/lambda-deployment-log.md`

#### ✅ Task 1.5: API Gateway Setup
- **API:** poc-itsm-api (REST API)
- **API ID:** iixw3qtwo3
- **Endpoint:** https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc
- **Stage:** poc
- **Authentication:** API Key (x-api-key header)
- **API Key:** h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa
- **API Key ID:** r3k6upsgse
- **Usage Plan:** poc-itsm-usage-plan (100 req/s burst, 50 req/s rate, 10K req/month quota)
- **Endpoints:**
  - POST /tickets (create ticket)
  - GET /tickets/{id} (get ticket status)
  - POST /tickets/{id}/comments (add comment)
  - GET /tickets?caller={caller_id} (list tickets)
- **Contract Tests:** 5/5 passing
- **Documentation:** `deployment/api-gateway-deployment-log.md`

#### ✅ Task 1.6: S3 Bucket for OpenAPI Spec Storage
- **Bucket:** poc-itsm-openapi-specs-714059461907
- **Region:** us-east-1
- **Public Access:** Blocked (all 4 settings)
- **OpenAPI Spec:** s3://poc-itsm-openapi-specs-714059461907/mock-itsm-api-openapi.yaml
- **File Size:** 13,307 bytes
- **Integrity:** Verified (downloaded file matches local version)
- **Documentation:** `deployment/s3-deployment-log.md`

---

## Phase 2: AgentCore Gateway Configuration (Tasks 2.1-2.3 Complete)

### ✅ Task 2.1: API Key Storage in Secrets Manager
- **Status:** COMPLETE
- **Secret:** poc-itsm-api-key
- **ARN:** arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7
- **Value:** API key from Task 1.5 (h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa)
- **Encryption:** Default AWS managed key
- **Region:** us-east-1
- **Documentation:** `deployment/secrets-manager-log.md`

### ✅ Task 2.2: AgentCore Gateway IAM Role Creation
- **Status:** COMPLETE
- **Role:** poc-agentcore-gateway-role
- **Role ARN:** arn:aws:iam::714059461907:role/poc-agentcore-gateway-role
- **Policy:** poc-agentcore-gateway-policy
- **Policy ARN:** arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
- **Permissions:**
  - secretsmanager:GetSecretValue (poc-itsm-api-key)
  - execute-api:Invoke (API Gateway iixw3qtwo3/poc)
  - CloudWatch Logs (write)
- **Trust Policy:** bedrock.amazonaws.com
- **NO wildcard permissions in actions** ✅
- **Documentation:** `deployment/agentcore-iam-log.md`

### ✅ Task 2.3: AgentCore Gateway Tool Definitions
- **Status:** COMPLETE
- **File:** `config/agentcore-tools.json`
- **Tool Count:** 4 (exactly as required)
- **Tools:**
  1. create_ticket (POST /tickets)
  2. get_ticket_status (GET /tickets/{id})
  3. add_ticket_comment (POST /tickets/{id}/comments)
  4. list_recent_tickets (GET /tickets?caller={caller_id})
- **Verification:** All tools match OpenAPI spec exactly ✅
- **Static definitions:** NO dynamic generation ✅
- **NO delete or administrative operations** ✅
- **Documentation:** `deployment/agentcore-tools-verification.md`

### ✅ Task 2.4: AgentCore Gateway Deployment
- **Status:** COMPLETE
- **Completed:** 2026-02-18
- **Gateway Name:** `poc-itsm-agentcore-gateway`
- **Gateway ARN:** `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`
- **Gateway ID:** `poc-itsm-agentcore-gateway-9ygtgj9qzu`
- **Target Type:** API Gateway (`poc-itsm-api`, stage `poc`)
- **Inbound Auth:** JWT with Connect OIDC
  - Discovery URL: `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
  - Audience: Connect instance ARN
  - Client: Connect instance ID (`c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`)
- **Outbound Auth:** API Key (`x-api-key` header)
- **Operations:** create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- **Deployment Log:** `deployment/agentcore-deployment-log.md`

---

## Key Resources

### AgentCore Gateway (NEW - Task 2.4)
- **Name:** poc-itsm-agentcore-gateway
- **ARN:** arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu
- **Gateway ID:** poc-itsm-agentcore-gateway-9ygtgj9qzu

### API Gateway
- **API ID:** iixw3qtwo3
- **Endpoint:** https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc
- **API Key:** h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa
- **API Key ID:** r3k6upsgse

### Lambda Function
- **Name:** poc-itsm-api-handler
- **ARN:** arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler

### S3 Bucket
- **Bucket:** poc-itsm-openapi-specs-714059461907
- **OpenAPI Spec URI:** s3://poc-itsm-openapi-specs-714059461907/mock-itsm-api-openapi.yaml

### DynamoDB
- **Table:** poc-itsm-tickets
- **ARN:** arn:aws:dynamodb:us-east-1:714059461907:table/poc-itsm-tickets

### Amazon Connect
- **Instance:** poc-ai-l1-support
- **Instance ID:** c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- **Instance ARN:** arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- **Phone Number:** +16782709241

### Account
- **Account ID:** 714059461907
- **Region:** us-east-1

---

## Phase 0: Documentation (Previously Completed)

All Phase 0 documentation tasks (0.1-0.10) were completed retroactively after user identified they were skipped:

- ✅ Task 0.1: Budget Setup Guide (`docs/budget-setup-guide.md`)
- ✅ Task 0.2: OpenAPI Specification (`specs/mock-itsm-api-openapi.yaml`)
- ✅ Task 0.3: DynamoDB Schema Design (`docs/dynamodb-schema.md`)
- ✅ Task 0.4: Lambda Function Design (`docs/lambda-design.md`, `docs/iam-policies.md`)
- ✅ Task 0.5: API Gateway Design (`docs/api-gateway-design.md`)
- ✅ Task 0.6: AgentCore Gateway Config Design (`docs/agentcore-gateway-config.md`)
- ✅ Task 0.7: Amazon Connect Flow Design (`docs/connect-flow-design.md`)
- ✅ Task 0.8: Test Strategy Documentation (`docs/test-strategy.md`)
- ✅ Task 0.9: Architecture Documentation (`docs/architecture.md`)
- ✅ Task 0.10: Cleanup Procedure Documentation (`docs/cleanup-procedure.md`)

---

## Phase 3: Amazon Connect Setup (In Progress)

### ✅ Task 3.1: Amazon Connect Instance Creation (COMPLETE)
- **Status:** COMPLETE ✅
- **Instance:** poc-ai-l1-support
- **Instance ID:** c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- **Instance ARN:** arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- **Region:** us-east-1 ✅ (compliant with Plan of Record)
- **Access URL:** https://poc-ai-l1-support.my.connect.aws
- **OIDC Discovery URL:** https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
- **OIDC Verified:** ✅ Accessible and returns valid JSON
- **Phone Number:** ✅ +16782709241 (DID, claimed 2026-02-18)
- **Documentation:** `deployment/connect-instance-log.md`

**Region Compliance Note:** Instance was initially created in us-west-2 by mistake, then deleted and recreated in us-east-1 to comply with Plan of Record requirements.

**Phone Number Quota Issue: RESOLVED** ✅  
Quota increase approved by AWS Support. Phone number +16782709241 claimed on 2026-02-18.

### ⏳ Task 3.2: Connect AI Agent IAM Role Creation (PENDING)
- Create IAM role: poc-connect-ai-agent-role
- Permissions: bedrock:InvokeAgent (scoped to AgentCore Gateway)
- Trust policy: connect.amazonaws.com
- **Can be completed while waiting for quota**

### ⏳ Task 3.3: AgentCore Gateway OIDC Configuration Update (PENDING)
- Update AgentCore Gateway with Connect OIDC URL from Task 3.1
- **Note:** This may be done as part of Task 2.4 manual configuration
- **Can be completed while waiting for quota**

### ⏳ Task 3.4: Connect AI Agent Creation (READY)
- Create AI Agent: poc-l1-support-agent
- Configure AI Agent instructions (voice-first, short responses)
- Link to AgentCore Gateway
- Configure escalation path
- **Phone number available:** +16782709241

---

## Budget Status

**Total Budget:** $10.00  
**Alert Threshold:** $8.00  
**Estimated Spent (Phase 1+2+3.1):** ~$0.46  
**Phone Number Daily Cost:** ~$0.03/day  
**Remaining:** ~$9.54  
**Status:** WELL WITHIN BUDGET ✅

### Cost Breakdown
**Phase 1:**
- DynamoDB: < $0.01 (ON_DEMAND, minimal usage)
- Lambda: < $0.01 (256 MB, < 100 invocations)
- API Gateway: < $0.01 (< 100 requests, Free Tier covers)
- S3: < $0.0001 (13 KB file, Free Tier covers)

**Phase 2:**
- Secrets Manager: ~$0.40/month (30-day free trial may apply)
- IAM: Free
- AgentCore Gateway: TBD (pricing to be confirmed after manual configuration)

**Phase 3 (Task 3.1):**
- Amazon Connect Instance: $0.00 (no charge for idle instance)
- Phone Number: ~$0.03/day (~$1/month) - DID +16782709241 claimed 2026-02-18

### Idle Resource Costs While Waiting for Quota
**Daily Cost:** ~$0.015/day (~$0.45/month)
- Secrets Manager: ~$0.013/day
- S3: ~$0.0007/day
- CloudWatch Logs: ~$0.001/day
- All other resources: $0.00 (no charges when idle)

**Cost Projections:**
- Wait 7 days: ~$0.11 additional (~$0.54 total)
- Wait 30 days: ~$0.45 additional (~$0.88 total)
- **Still well within $10 budget** ✅

---

## Testing Summary

### Unit Tests (Task 1.3)
- **Framework:** pytest
- **Results:** 18/18 tests passing ✅
- **Coverage:** All 4 operations + error handling + retry logic

### Contract Tests (Task 1.5)
- **Framework:** curl + jq
- **Results:** 5/5 tests passing ✅
- **Tests:**
  1. POST /tickets: 201 + ticket_id ✅
  2. GET /tickets/{id}: 200 + ticket data ✅
  3. POST /tickets/{id}/comments: 200 + success ✅
  4. GET /tickets?caller={caller_id}: 200 + array ✅
  5. Authentication: 403 without API key ✅

---

## Architecture (Phase 1)

```
External Client (curl/AgentCore Gateway)
    │
    │ HTTPS + x-api-key header
    ↓
API Gateway REST API (poc-itsm-api)
    │ - POST /tickets
    │ - GET /tickets/{id}
    │ - POST /tickets/{id}/comments
    │ - GET /tickets?caller={caller_id}
    │ - API Key Authentication
    │
    │ Lambda Proxy Integration (AWS_PROXY)
    ↓
Lambda Function (poc-itsm-api-handler)
    │ - Python 3.12
    │ - Error Handling + Retry Logic
    │
    │ DynamoDB API (boto3)
    ↓
DynamoDB Table (poc-itsm-tickets)
    │ - Partition Key: ticket_id
    │ - GSI: CallerIdIndex

S3 Bucket (poc-itsm-openapi-specs-714059461907)
    │ - OpenAPI Spec: mock-itsm-api-openapi.yaml
    │ - For AgentCore Gateway reference
```

---

## Important Notes

### User Corrections and Instructions

1. **Phase 0 was skipped:** User correctly identified that Phase 0 (documentation) should have been completed before Phase 1 (deployment). All Phase 0 tasks were completed retroactively.

2. **DynamoDB tags format:** User corrected the create-table command - DynamoDB --tags must be JSON objects list, not Key=Value pairs. Fixed format: `"[{\"Key\": \"Environment\", \"Value\": \"PoC\"}]"`

3. **Task execution order:** Execute ONE task at a time, STOP after each for approval. Do NOT proceed to next task without explicit approval.

4. **Error verification:** User asked for clarification on Task 1.4 errors. Confirmed errors were non-critical permission issues (monitoring/debugging only), not operational failures.

5. **Follow Plan of Record strictly:** All tasks must follow `.kiro/specs/ai-l1-phone-support-poc/plan-of-record.md`

6. **Budget constraint:** $10 total, $8 alert threshold with manual stop rule. AWS Budgets provides alerts only, not enforcement.

7. **Region constraint:** ALL resources in us-east-1 ONLY

8. **Production isolation:** NO production ITSM integration - mock backend only with clear "poc-" naming

---

## Files to Read for Phase 3

**Critical for Phase 3:**
- `.kiro/specs/ai-l1-phone-support-poc/plan-of-record.md` (Task 3.1-3.4 details, lines 750-900)
- `docs/connect-flow-design.md` (Connect flow and AI Agent design)
- `deployment/agentcore-deployment-manual-guide.md` (for Task 2.4 after Task 3.1)

**Context files:**
- `.kiro/specs/ai-l1-phone-support-poc/requirements.md` (requirements reference)
- `docs/iam-policies.md` (IAM policy templates)
- `deployment/phase-2-summary.md` (Phase 2 status and next steps)

---

## Deployment Artifacts

### Phase 1 Documentation
- `deployment/dynamodb-creation-log.md`
- `deployment/iam-creation-log.md`
- `deployment/lambda-implementation-log.md`
- `deployment/lambda-deployment-log.md`
- `deployment/api-gateway-deployment-log.md`
- `deployment/s3-deployment-log.md`
- `deployment/phase-1-completion-summary.md`

### Phase 2 Documentation
- `deployment/secrets-manager-log.md` (Task 2.1)
- `deployment/agentcore-iam-log.md` (Task 2.2)
- `deployment/agentcore-tools-verification.md` (Task 2.3)
- `deployment/agentcore-deployment-manual-guide.md` (Task 2.4 guide)
- `deployment/agentcore-deployment-log.md` (Task 2.4 - COMPLETE ✅)
- `deployment/phase-2-summary.md`

### Code
- `src/lambda/mock_itsm_handler.py`
- `src/lambda/requirements.txt`
- `tests/test_lambda_handler.py`
- `tests/requirements.txt`

### Configuration Files
- `deployment/iam-policy-lambda.json`
- `deployment/iam-trust-policy-lambda.json`
- `deployment/iam-policy-agentcore.json` (Phase 2)
- `deployment/iam-trust-policy-agentcore.json` (Phase 2)
- `config/agentcore-tools.json` (Phase 2)
- `deployment/lambda-package.zip`
- `deployment/test-event-create-ticket.json`

---

## How to Resume Work

Project is now ACTIVE. Phone number quota resolved, +16782709241 claimed.

1. **Current status:** Phase 3 active, phone number claimed
2. **OIDC URL available:** https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
3. **Phone Number:** +16782709241
4. **Next actions (in order):**
   - ➡️ Task 2.4: Configure AgentCore Gateway with OIDC URL (manual configuration)
   - ➡️ Task 3.2: Create Connect AI Agent IAM role
   - ➡️ Task 3.3: Update AgentCore Gateway OIDC configuration (if needed)
   - ➡️ Task 3.4: Create Connect AI Agent and contact flow
   - ➡️ Task 3.5: Create Connect Contact Flow
   - ➡️ Phase 4: End-to-End Testing
5. **Verify budget status** before proceeding (currently ~$0.46 spent, ~$9.54 remaining)
6. **Execute tasks one at a time** with approval gates

---

## Quick Reference Commands

### Verify Phase 1 Resources
```bash
# DynamoDB table
aws dynamodb describe-table --table-name poc-itsm-tickets --region us-east-1

# Lambda function
aws lambda get-function --function-name poc-itsm-api-handler --region us-east-1

# API Gateway
aws apigateway get-rest-api --rest-api-id iixw3qtwo3 --region us-east-1

# S3 bucket
aws s3 ls s3://poc-itsm-openapi-specs-714059461907/ --region us-east-1
```

### Test API Gateway
```bash
# Create ticket
curl -X POST \
  https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets \
  -H "x-api-key: h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "test-user", "issue_description": "Test issue"}'
```

---

## Critical Workflow Note

**✅ CURRENT STATUS: ACTIVE - Phone Number Claimed, Resuming Work**

**Completed Tasks:**
1. ✅ Phase 1 Tasks 1.1-1.6 (COMPLETE)
2. ✅ Phase 2 Tasks 2.1-2.3 (COMPLETE)
3. ✅ Phase 3 Task 3.1 - Amazon Connect Instance Created (COMPLETE)
4. ✅ Phone number +16782709241 claimed (2026-02-18)
5. ✅ Connect OIDC URL obtained and verified

**Next Tasks:**
1. ➡️ Task 3.2 - Create Connect AI Agent IAM role
2. ➡️ Task 3.3 - Update AgentCore Gateway OIDC configuration (if needed)
3. ➡️ Task 3.4 - Create Connect AI Agent
4. ➡️ Task 3.5 - Create Connect Contact Flow
5. ➡️ Phase 4 - End-to-End Testing

**Configuration Guide for Task 2.4:** `deployment/agentcore-deployment-manual-guide.md`  
**OIDC URL for Task 2.4:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`  
**Phone Number:** +16782709241

---

**Status:** Phase 3 Active, Phone Number Claimed, Proceeding with Task 3.2  
**Next Action:** Task 3.2 - Create Connect AI Agent IAM Role  
**Last Updated:** 2026-02-18
