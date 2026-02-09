# AgentCore Gateway Deployment Log - Task 2.4

## Status: PENDING MANUAL CONFIGURATION ⚠️

**Configuration Timing:** Configure AFTER Task 3.1 (Amazon Connect Instance Creation)

**Reason:** AgentCore Gateway requires Amazon Connect OIDC discovery URL, which is only available after Connect instance is created.

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

## Blocking Dependency

- ⏳ **Task 3.1:** Amazon Connect Instance Creation (NEXT TASK)
  - Instance: `poc-ai-l1-support`
  - OIDC URL: `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
  - **Action:** Complete Task 3.1 first, then return here

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
- **Type:** OIDC
- **Discovery URL:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
  - ⚠️ Replace `poc-ai-l1-support` with actual Connect instance alias from Task 3.1

### Outbound Authentication (AgentCore → Mock API)
- **Type:** API Key
- **Header:** `x-api-key`
- **Secret ARN:** `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7`

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

## Post-Configuration: Complete This Section

**After manual configuration, document the following:**

### Gateway Information
- **Gateway Name:** poc-itsm-agentcore-gateway
- **Gateway ARN:** `<TO BE FILLED AFTER CREATION>`
- **Status:** `<TO BE FILLED AFTER CREATION>`
- **Created Date:** `<TO BE FILLED AFTER CREATION>`
- **Region:** us-east-1

### Configuration Verification
- [ ] Gateway status: Active
- [ ] IAM role attached correctly
- [ ] OIDC authentication configured
- [ ] API key authentication configured
- [ ] All 4 tools imported
- [ ] API endpoint configured
- [ ] CloudWatch logging enabled
- [ ] Tags applied

### Test Results
- [ ] Test 1: create_ticket - PASS/FAIL
- [ ] Test 2: get_ticket_status - PASS/FAIL
- [ ] Test 3: add_ticket_comment - PASS/FAIL
- [ ] Test 4: list_recent_tickets - PASS/FAIL

### CloudWatch Logs
- **Log Group:** `/aws/bedrock/agentcore/poc-itsm-agentcore-gateway`
- **Log Streams:** `<TO BE FILLED AFTER CREATION>`
- **Sample Log Events:** `<TO BE FILLED AFTER TESTING>`

---

## Acceptance Criteria (To Be Verified After Configuration)

### Requirement 5.1-5.10: AgentCore Gateway with Secure Authentication

- [ ] Gateway name: `poc-itsm-agentcore-gateway`
- [ ] Region: us-east-1
- [ ] Inbound auth: Connect OIDC (placeholder URL until Connect is created)
- [ ] Outbound auth: API key from Secrets Manager (poc-itsm-api-key)
- [ ] Tools configured: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- [ ] IAM role: `poc-agentcore-gateway-role`
- [ ] Mock ITSM API endpoint configured
- [ ] Tool invocation tests pass
- [ ] CloudWatch logs show successful tool invocations

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

**Task 2.4: AgentCore Gateway Deployment - PENDING MANUAL CONFIGURATION ⚠️**

**Current Status:**
- ✅ Prerequisites complete (Tasks 2.1, 2.2, 2.3)
- ✅ Configuration documentation complete
- ⏳ Awaiting Task 3.1 (Amazon Connect Instance Creation)
- ⏳ Manual configuration pending

**Next Steps:**
1. Proceed to Task 3.1: Amazon Connect Instance Creation
2. Note the Connect OIDC discovery URL
3. Return to this task and follow manual configuration guide
4. Complete this deployment log with actual Gateway ARN and verification results

**Configuration Guide:** `deployment/agentcore-deployment-manual-guide.md`

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-09  
**Status:** Awaiting manual configuration after Task 3.1
