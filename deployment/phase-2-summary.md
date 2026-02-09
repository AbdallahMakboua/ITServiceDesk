# Phase 2 Summary - AgentCore Gateway Configuration

**Date:** 2026-02-09  
**Phase:** Phase 2 - AgentCore Gateway Configuration  
**Status:** TASKS 2.1-2.3 COMPLETE, TASK 2.4 PENDING MANUAL CONFIGURATION

---

## Phase 2 Overview

Phase 2 configures the Bedrock AgentCore Gateway (MCP server) to act as a secure bridge between Amazon Connect AI Agent and the Mock ITSM API.

---

## Completed Tasks

### ✅ Task 2.1: API Key Storage in Secrets Manager
- **Status:** COMPLETE
- **Secret:** poc-itsm-api-key
- **ARN:** arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7
- **Value:** API key from Task 1.5 (API Gateway)
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
  - execute-api:Invoke (API Gateway)
  - CloudWatch Logs (write)
- **Trust Policy:** bedrock.amazonaws.com
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
- **Verification:** All tools match OpenAPI spec exactly
- **Documentation:** `deployment/agentcore-tools-verification.md`

### ⏳ Task 2.4: AgentCore Gateway Deployment
- **Status:** PENDING MANUAL CONFIGURATION
- **Reason:** Requires Amazon Connect OIDC URL (available after Task 3.1)
- **Configuration Guide:** `deployment/agentcore-deployment-manual-guide.md`
- **Deployment Log:** `deployment/agentcore-deployment-log.md` (to be completed)

---

## Configuration Timing: IMPORTANT ⚠️

**DO NOT configure AgentCore Gateway yet!**

**Correct Workflow:**
1. ✅ Complete Phase 2 Tasks 2.1-2.3 (DONE)
2. ➡️ **NEXT:** Proceed to Phase 3 Task 3.1 (Amazon Connect Instance Creation)
3. ➡️ Note the Connect OIDC discovery URL from Task 3.1
4. ➡️ **THEN:** Return to Task 2.4 and configure AgentCore Gateway manually
5. ➡️ Complete remaining Phase 3 tasks

**Why This Order:**
- AgentCore Gateway requires Connect OIDC URL for inbound authentication
- Connect OIDC URL format: `https://<CONNECT_ALIAS>.my.connect.aws/.well-known/openid-configuration`
- This URL is only available after Connect instance is created

---

## Ready for Manual Configuration

All prerequisites for AgentCore Gateway configuration are complete:

### Configuration Information
- **Gateway Name:** poc-itsm-agentcore-gateway
- **Region:** us-east-1
- **IAM Role:** arn:aws:iam::714059461907:role/poc-agentcore-gateway-role
- **API Endpoint:** https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc
- **API Key Secret:** arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7
- **Tool Definitions:** config/agentcore-tools.json (4 tools)

### Missing Information (from Task 3.1)
- **Connect OIDC URL:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
  - ⚠️ Replace `poc-ai-l1-support` with actual Connect instance alias

---

## Phase 2 Architecture

```
Amazon Connect AI Agent
    │
    │ OIDC Authentication
    │ (JWT token validation)
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Bedrock AgentCore Gateway (MCP Server)                     │
│  - Name: poc-itsm-agentcore-gateway                         │
│  - IAM Role: poc-agentcore-gateway-role                     │
│  - Inbound Auth: OIDC (Connect)                             │
│  - Outbound Auth: API Key (Secrets Manager)                 │
│  - Tools: 4 (create, get, comment, list)                    │
└─────────────────────────────────────────────────────────────┘
    │
    │ API Key Authentication
    │ (x-api-key header from Secrets Manager)
    ↓
API Gateway REST API (poc-itsm-api)
    │
    │ Lambda Proxy Integration
    ↓
Lambda Function (poc-itsm-api-handler)
    │
    │ DynamoDB API
    ↓
DynamoDB Table (poc-itsm-tickets)
```

---

## Security Summary

### Authentication Chain
1. **Connect → AgentCore:** OIDC (JWT validation)
2. **AgentCore → API Gateway:** API Key (from Secrets Manager)
3. **API Gateway → Lambda:** Lambda Proxy Integration
4. **Lambda → DynamoDB:** IAM role permissions

### Least Privilege Enforcement
- ✅ AgentCore IAM role: Only Secrets Manager read, API Gateway invoke, CloudWatch Logs
- ✅ NO wildcard permissions in actions
- ✅ Resource ARNs scoped to specific resources
- ✅ NO administrative or delete operations

### Tool Exposure Control
- ✅ Exactly 4 tools (no more, no less)
- ✅ Static tool definitions (NO dynamic generation)
- ✅ NO delete operations
- ✅ NO administrative operations

---

## Testing Strategy (After Configuration)

### Tool Invocation Tests

**Test 1: create_ticket**
```json
Input: {
  "caller_id": "test-user-001",
  "issue_description": "Test issue - laptop not working"
}
Expected: {
  "ticket_id": "<UUID>",
  "status": "open",
  "created_at": "<ISO 8601>"
}
```

**Test 2: get_ticket_status**
```json
Input: {
  "ticket_id": "<UUID from Test 1>"
}
Expected: Full ticket object with all fields
```

**Test 3: add_ticket_comment**
```json
Input: {
  "ticket_id": "<UUID from Test 1>",
  "comment": "Additional information"
}
Expected: {
  "success": true,
  "updated_at": "<ISO 8601>"
}
```

**Test 4: list_recent_tickets**
```json
Input: {
  "caller_id": "test-user-001"
}
Expected: {
  "tickets": [<array of tickets>]
}
```

---

## Budget Status

**Phase 2 Costs:**
- Secrets Manager: ~$0.40/month (30-day free trial may apply)
- IAM: Free
- Tool definitions: Free
- AgentCore Gateway: TBD (pricing to be confirmed)

**Total Phase 1+2:** < $0.50

**Budget Status:**
- Total Budget: $10.00
- Alert Threshold: $8.00
- Estimated Spent: < $0.50
- Remaining: > $9.50
- **Status: WELL WITHIN BUDGET ✅**

---

## Next Steps

### Immediate Next Step
**Proceed to Phase 3 Task 3.1: Amazon Connect Instance Creation**

### After Task 3.1
1. Note the Connect instance alias (e.g., `poc-ai-l1-support`)
2. Note the OIDC discovery URL
3. Return to Task 2.4
4. Follow manual configuration guide: `deployment/agentcore-deployment-manual-guide.md`
5. Configure AgentCore Gateway in AWS Console
6. Test tool invocations
7. Document Gateway ARN in `deployment/agentcore-deployment-log.md`

### After Task 2.4 Manual Configuration
- Proceed to Task 3.2: Connect AI Agent IAM Role Creation
- Proceed to Task 3.3: AgentCore Gateway OIDC Configuration Update (if needed)
- Proceed to Task 3.4: Connect AI Agent Creation

---

## Documentation Files

### Phase 2 Documentation
- `deployment/secrets-manager-log.md` - Task 2.1 deployment log
- `deployment/agentcore-iam-log.md` - Task 2.2 deployment log
- `deployment/agentcore-tools-verification.md` - Task 2.3 verification
- `deployment/agentcore-deployment-manual-guide.md` - Task 2.4 configuration guide
- `deployment/agentcore-deployment-log.md` - Task 2.4 deployment log (pending)
- `deployment/phase-2-summary.md` - This file

### Configuration Files
- `config/agentcore-tools.json` - Tool definitions
- `deployment/iam-trust-policy-agentcore.json` - IAM trust policy
- `deployment/iam-policy-agentcore.json` - IAM permissions policy

---

## Key Information for Phase 3

### AgentCore Gateway (After Manual Configuration)
- **Name:** poc-itsm-agentcore-gateway
- **ARN:** `<TO BE FILLED AFTER MANUAL CONFIGURATION>`
- **Region:** us-east-1

### IAM Role
- **Role:** poc-agentcore-gateway-role
- **ARN:** arn:aws:iam::714059461907:role/poc-agentcore-gateway-role

### API Endpoint
- **URL:** https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc
- **API Key:** Stored in Secrets Manager (poc-itsm-api-key)

### Tools
- create_ticket
- get_ticket_status
- add_ticket_comment
- list_recent_tickets

---

**Status:** Phase 2 Tasks 2.1-2.3 Complete, Task 2.4 Pending Manual Configuration  
**Next Action:** Proceed to Phase 3 Task 3.1 (Amazon Connect Instance Creation)  
**Last Updated:** 2026-02-09
