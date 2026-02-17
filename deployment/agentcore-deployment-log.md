# AgentCore Gateway Deployment Log - Task 2.4

## Status: COMPLETE ✅

**Completed:** 2026-02-18  
**Gateway ARN:** `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`

---

## Configuration Guide

**See:** `deployment/agentcore-deployment-manual-guide.md` for detailed step-by-step instructions.

---

## Prerequisites (Complete)

- ✅ **Task 2.1:** API key stored in Secrets Manager
  - Secret: `poc-itsm-api-key`
  - ARN: `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7`

- ✅ **Task 2.2:** IAM role created
  - Role: `poc-agentcore-gateway-role`
  - ARN: `arn:aws:iam::714059461907:role/poc-agentcore-gateway-role`

- ✅ **Task 2.3:** Tool definitions created
  - File: `config/agentcore-tools.json`
  - Tools: 4 (create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets)

---

## Configuration Information (Ready to Use)

### Gateway Details
- **Name:** `poc-itsm-agentcore-gateway`
- **Region:** us-east-1
- **Type:** MCP Server
- **IAM Role ARN:** `arn:aws:iam::714059461907:role/poc-agentcore-gateway-role`

### API Endpoint
- **Base URL:** `https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc`
- **API ID:** iixw3qtwo3
- **Stage:** poc

### Inbound Authentication (Connect → AgentCore)
- **Type:** JWT (JSON Web Tokens)
- **Discovery URL:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
- **Allowed Audiences:** `arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
- **Allowed Clients:** `c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`

### Outbound Authentication (AgentCore → Mock API)
- **Type:** API Key
- **Header:** `x-api-key`
- **API Key Value:** `h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa` (stored as OAuth client in AgentCore)
- **Secret ARN:** `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7`

### Target
- **Target Type:** API Gateway
- **API:** `poc-itsm-api` (ID: `iixw3qtwo3`)
- **Stage:** `poc`
- **Operations:** 4/4 selected (all with name overrides)

### Tools (4 total)
1. create_ticket
2. get_ticket_status
3. add_ticket_comment
4. list_recent_tickets

---

## Manual Configuration Steps

**See:** `deployment/agentcore-deployment-manual-guide.md`

**Summary:**
1. Access AWS Console → Amazon Bedrock → AgentCore Gateway
2. Create gateway: `poc-itsm-agentcore-gateway`
3. Configure IAM role: `poc-agentcore-gateway-role`
4. Configure OIDC inbound auth (Connect OIDC URL from Task 3.1)
5. Configure API key outbound auth (Secrets Manager)
6. Import tool definitions from `config/agentcore-tools.json`
7. Configure API endpoint
8. Enable CloudWatch logging
9. Add tags
10. Create and verify

---

## Configuration Results

### Gateway Information
- **Gateway Name:** `poc-itsm-agentcore-gateway`
- **Gateway ARN:** `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`
- **Gateway ID:** `poc-itsm-agentcore-gateway-9ygtgj9qzu`
- **Status:** Active
- **Created Date:** 2026-02-18
- **Region:** us-east-1

### Configuration Verification
- [x] Gateway status: Active
- [x] IAM role attached: `poc-agentcore-gateway-role`
- [x] JWT inbound authentication configured (Connect OIDC)
- [x] API key outbound authentication configured
- [x] All 4 API operations selected with name overrides
- [x] Target type: API Gateway (`poc-itsm-api`, stage `poc`)
- [x] Allowed audience: Connect instance ARN
- [x] Allowed client: Connect instance ID

### Name Overrides Applied
| API Operation | Name Override |
|---|---|
| `/tickets - GET` | `list_recent_tickets` |
| `/tickets - POST` | `create_ticket` |
| `/tickets/{id} - GET` | `get_ticket_status` |
| `/tickets/{id}/comments - POST` | `add_ticket_comment` |

---

## Acceptance Criteria (To Be Verified After Configuration)

### Requirement 5.1-5.10: AgentCore Gateway with Secure Authentication

- [x] Gateway name: `poc-itsm-agentcore-gateway`
- [x] Region: us-east-1
- [x] Inbound auth: JWT with Connect OIDC discovery URL
- [x] Outbound auth: API key (`x-api-key` header)
- [x] Tools configured: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- [x] IAM role: `poc-agentcore-gateway-role`
- [x] Target: API Gateway (`poc-itsm-api`, stage `poc`)
- [ ] Tool invocation tests: to be verified during E2E testing (Phase 4)

---

## Rollback Commands

If rollback is needed after configuration:

### Via Console:
1. Navigate to Amazon Bedrock → Agents → AgentCore Gateway
2. Select `poc-itsm-agentcore-gateway`
3. Click **Delete**
4. Confirm deletion

### Verify Deletion:
- Check that gateway no longer appears in Console
- Verify CloudWatch log group is deleted (or delete manually)

**Note:** Gateway deletion does NOT delete IAM role, Secrets Manager secret, API Gateway, Lambda, or DynamoDB. These must be deleted separately if needed.

---

## Task Status

**Task 2.4: AgentCore Gateway Deployment - COMPLETE ✅**

**Completion Summary:**
- ✅ Prerequisites complete (Tasks 2.1, 2.2, 2.3)
- ✅ Amazon Connect instance created (Task 3.1)
- ✅ Gateway created via AWS Console (manual configuration)
- ✅ JWT inbound auth configured with Connect OIDC URL
- ✅ API key outbound auth configured
- ✅ All 4 API operations configured with name overrides
- ✅ Target: API Gateway (`poc-itsm-api`, stage `poc`)
- ✅ Gateway ARN documented

**Gateway ARN (Required for Task 3.2 and Task 3.4):**
```
arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu
```

**Next Steps:**
1. ➡️ Task 3.2: Create Connect AI Agent IAM Role
2. ➡️ Task 3.3: AgentCore Gateway OIDC Configuration Update (if needed)
3. ➡️ Task 3.4: Create Connect AI Agent (references this Gateway ARN)

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-18  
**Status:** COMPLETE ✅
