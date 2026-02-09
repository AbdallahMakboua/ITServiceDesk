# AgentCore Gateway Manual Configuration Guide - Task 2.4

## ⚠️ IMPORTANT: Configuration Timing

**DO NOT configure AgentCore Gateway yet!**

**Correct Timing:** Configure AgentCore Gateway **AFTER** completing Task 3.1 (Amazon Connect Instance Creation).

**Reason:** AgentCore Gateway requires the Amazon Connect OIDC discovery URL for inbound authentication. This URL is only available after the Connect instance is created.

**Workflow:**
1. ✅ Complete Phase 2 Tasks 2.1-2.3 (DONE)
2. ➡️ Proceed to Phase 3 Task 3.1: Create Amazon Connect Instance
3. ➡️ Note the Connect OIDC discovery URL from Task 3.1
4. ➡️ **THEN** return here to configure AgentCore Gateway
5. ➡️ Complete remaining Phase 3 tasks

---

## Prerequisites (Already Complete)

Before configuring AgentCore Gateway, ensure these are complete:

- ✅ **Task 2.1:** API key stored in Secrets Manager
  - Secret: `poc-itsm-api-key`
  - ARN: `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7`

- ✅ **Task 2.2:** IAM role created
  - Role: `poc-agentcore-gateway-role`
  - ARN: `arn:aws:iam::714059461907:role/poc-agentcore-gateway-role`

- ✅ **Task 2.3:** Tool definitions created
  - File: `config/agentcore-tools.json`
  - Tools: 4 (create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets)

- ⏳ **Task 3.1:** Amazon Connect instance (TO BE COMPLETED NEXT)
  - Instance: `poc-ai-l1-support`
  - OIDC URL: `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`

---

## Configuration Information

### Gateway Details
- **Name:** `poc-itsm-agentcore-gateway`
- **Region:** us-east-1
- **Type:** MCP Server (Model Context Protocol)
- **IAM Role:** `arn:aws:iam::714059461907:role/poc-agentcore-gateway-role`

### API Endpoint
- **Base URL:** `https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc`
- **API ID:** iixw3qtwo3
- **Stage:** poc

### Authentication Configuration

#### Inbound Authentication (Connect → AgentCore)
- **Type:** OIDC (OpenID Connect)
- **Provider:** Amazon Connect
- **Discovery URL:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
  - ⚠️ **Note:** Replace `poc-ai-l1-support` with actual Connect instance alias from Task 3.1

#### Outbound Authentication (AgentCore → Mock API)
- **Type:** API Key
- **Header Name:** `x-api-key`
- **Secret ARN:** `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7`
- **Secret Name:** `poc-itsm-api-key`

---

## Manual Configuration Steps

### Step 1: Access AWS Console

1. Log in to AWS Console
2. Navigate to **Amazon Bedrock** service
3. Select region: **us-east-1** (top-right corner)
4. In the left navigation, find **Agents** section
5. Look for **AgentCore Gateway** or **MCP Servers** option

**Note:** If AgentCore Gateway is not visible in the Console, it may be in preview or require enablement. Contact AWS Support or check Bedrock documentation.

---

### Step 2: Create AgentCore Gateway

1. Click **Create Gateway** or **Create MCP Server**
2. Enter gateway configuration:

**Basic Configuration:**
- **Gateway Name:** `poc-itsm-agentcore-gateway`
- **Description:** `PoC AgentCore Gateway for Mock ITSM API - AI L1 Support`
- **Region:** us-east-1

**IAM Role:**
- **Execution Role:** Select existing role
- **Role ARN:** `arn:aws:iam::714059461907:role/poc-agentcore-gateway-role`

---

### Step 3: Configure Inbound Authentication (Connect → AgentCore)

**Authentication Type:** OIDC (OpenID Connect)

**OIDC Configuration:**
- **Provider:** Amazon Connect
- **Discovery URL:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
  - ⚠️ **IMPORTANT:** Use the actual Connect instance alias from Task 3.1
  - Format: `https://<CONNECT_ALIAS>.my.connect.aws/.well-known/openid-configuration`

**Token Validation:**
- **Validate Issuer:** Yes
- **Validate Audience:** Yes
- **Token Expiration:** Enforce

**Example OIDC Configuration (JSON format if required):**
```json
{
  "type": "OIDC",
  "discoveryUrl": "https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration",
  "validateIssuer": true,
  "validateAudience": true,
  "enforceExpiration": true
}
```

---

### Step 4: Configure Outbound Authentication (AgentCore → Mock API)

**Authentication Type:** API Key

**API Key Configuration:**
- **Header Name:** `x-api-key`
- **Secret Source:** AWS Secrets Manager
- **Secret ARN:** `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7`
- **Secret Name:** `poc-itsm-api-key` (alternative if ARN not accepted)

**Example API Key Configuration (JSON format if required):**
```json
{
  "type": "apiKey",
  "headerName": "x-api-key",
  "secretArn": "arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-thEbs7"
}
```

---

### Step 5: Configure API Endpoint

**Base URL:** `https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc`

**API Configuration:**
- **Protocol:** HTTPS
- **Endpoint:** `https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc`
- **Timeout:** 30 seconds (default)
- **Retry Policy:** Exponential backoff (default)

---

### Step 6: Import Tool Definitions

**Option A: Upload JSON File**
1. Click **Import Tools** or **Add Tools**
2. Select **Upload JSON**
3. Choose file: `config/agentcore-tools.json`
4. Click **Import**

**Option B: Manual Entry**

If file upload is not available, enter each tool manually:

#### Tool 1: create_ticket
```json
{
  "name": "create_ticket",
  "description": "Create a new IT support ticket. Use this when the caller describes an IT issue that needs to be tracked.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "caller_id": {
        "type": "string",
        "description": "Identifier for the caller (session ID or hashed phone number)"
      },
      "issue_description": {
        "type": "string",
        "description": "Clear description of the IT issue the caller is experiencing"
      }
    },
    "required": ["caller_id", "issue_description"]
  },
  "apiMapping": {
    "method": "POST",
    "endpoint": "/tickets",
    "bodyTemplate": {
      "caller_id": "{{caller_id}}",
      "issue_description": "{{issue_description}}"
    }
  }
}
```

#### Tool 2: get_ticket_status
```json
{
  "name": "get_ticket_status",
  "description": "Retrieve the current status and details of an existing ticket. Use this when the caller asks about a ticket they previously created.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "ticket_id": {
        "type": "string",
        "description": "The unique ticket identifier (UUID format)"
      }
    },
    "required": ["ticket_id"]
  },
  "apiMapping": {
    "method": "GET",
    "endpoint": "/tickets/{{ticket_id}}",
    "pathParameters": {
      "ticket_id": "{{ticket_id}}"
    }
  }
}
```

#### Tool 3: add_ticket_comment
```json
{
  "name": "add_ticket_comment",
  "description": "Add additional information or updates to an existing ticket. Use this when the caller provides more details about their issue.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "ticket_id": {
        "type": "string",
        "description": "The unique ticket identifier"
      },
      "comment": {
        "type": "string",
        "description": "The additional information or update to add to the ticket"
      }
    },
    "required": ["ticket_id", "comment"]
  },
  "apiMapping": {
    "method": "POST",
    "endpoint": "/tickets/{{ticket_id}}/comments",
    "pathParameters": {
      "ticket_id": "{{ticket_id}}"
    },
    "bodyTemplate": {
      "comment": "{{comment}}"
    }
  }
}
```

#### Tool 4: list_recent_tickets
```json
{
  "name": "list_recent_tickets",
  "description": "List recent tickets for a specific caller. Use this when the caller asks to see their previous tickets or ticket history.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "caller_id": {
        "type": "string",
        "description": "Identifier for the caller"
      }
    },
    "required": ["caller_id"]
  },
  "apiMapping": {
    "method": "GET",
    "endpoint": "/tickets",
    "queryParameters": {
      "caller": "{{caller_id}}"
    }
  }
}
```

---

### Step 7: Configure Logging (Optional but Recommended)

**CloudWatch Logs:**
- **Enable Logging:** Yes
- **Log Group:** `/aws/bedrock/agentcore/poc-itsm-agentcore-gateway`
- **Log Level:** INFO
- **Log Events:**
  - Tool invocations
  - API requests/responses
  - Authentication events
  - Errors

---

### Step 8: Add Tags

**Tags:**
- **Environment:** PoC
- **Project:** AI-L1-Support
- **ManagedBy:** Manual

---

### Step 9: Review and Create

1. Review all configuration settings
2. Verify:
   - ✅ Gateway name: `poc-itsm-agentcore-gateway`
   - ✅ IAM role: `poc-agentcore-gateway-role`
   - ✅ OIDC URL: Connect instance OIDC discovery URL
   - ✅ API key: From Secrets Manager
   - ✅ API endpoint: API Gateway URL
   - ✅ Tools: 4 tools imported
3. Click **Create Gateway** or **Deploy**

---

## Verification Steps

### Step 1: Verify Gateway Status

1. Navigate to AgentCore Gateway in Console
2. Check status: Should be **Active** or **Available**
3. Note the Gateway ARN (will be needed for Connect AI Agent configuration)

**Expected Gateway ARN Format:**
```
arn:aws:bedrock:us-east-1:714059461907:agent-gateway/poc-itsm-agentcore-gateway
```

### Step 2: Test Tool Invocation (if available in Console)

**Test 1: create_ticket**
```json
{
  "tool": "create_ticket",
  "parameters": {
    "caller_id": "test-user-manual",
    "issue_description": "Manual test - printer not working"
  }
}
```

**Expected Response:**
```json
{
  "ticket_id": "<UUID>",
  "status": "open",
  "created_at": "<ISO 8601 timestamp>"
}
```

**Test 2: get_ticket_status**
```json
{
  "tool": "get_ticket_status",
  "parameters": {
    "ticket_id": "<UUID from Test 1>"
  }
}
```

**Expected Response:**
```json
{
  "ticket_id": "<UUID>",
  "caller_id": "test-user-manual",
  "issue_description": "Manual test - printer not working",
  "status": "open",
  ...
}
```

### Step 3: Verify CloudWatch Logs

1. Navigate to CloudWatch → Log Groups
2. Find log group: `/aws/bedrock/agentcore/poc-itsm-agentcore-gateway`
3. Check for log streams
4. Verify log events show tool invocations

### Step 4: Verify IAM Role Permissions

1. Navigate to IAM → Roles → `poc-agentcore-gateway-role`
2. Check **Trust relationships** tab
3. Verify bedrock.amazonaws.com is trusted principal
4. Check **Permissions** tab
5. Verify `poc-agentcore-gateway-policy` is attached

---

## Troubleshooting

### Issue: Gateway Creation Fails

**Possible Causes:**
1. IAM role doesn't exist or has incorrect trust policy
2. Secrets Manager secret not accessible
3. API Gateway endpoint not reachable
4. OIDC discovery URL incorrect

**Solutions:**
1. Verify IAM role exists: `aws iam get-role --role-name poc-agentcore-gateway-role`
2. Verify secret exists: `aws secretsmanager describe-secret --secret-id poc-itsm-api-key --region us-east-1`
3. Test API Gateway: `curl -X GET https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets?caller=test -H "x-api-key: <API_KEY>"`
4. Verify OIDC URL format matches Connect instance alias

### Issue: Tool Invocation Fails

**Possible Causes:**
1. API key not retrieved from Secrets Manager
2. API Gateway endpoint incorrect
3. Tool definition doesn't match API contract

**Solutions:**
1. Check CloudWatch logs for authentication errors
2. Verify API Gateway URL is correct
3. Compare tool definitions with OpenAPI spec

### Issue: Authentication Fails

**Possible Causes:**
1. OIDC discovery URL incorrect
2. Connect instance not created yet
3. IAM role permissions insufficient

**Solutions:**
1. Verify Connect instance exists and OIDC URL is correct
2. Complete Task 3.1 before configuring AgentCore Gateway
3. Verify IAM role has secretsmanager:GetSecretValue permission

---

## Configuration Summary

After successful configuration, document the following:

**Gateway Information:**
- Gateway Name: `poc-itsm-agentcore-gateway`
- Gateway ARN: `<ARN from Console>`
- Status: Active
- Region: us-east-1

**Authentication:**
- Inbound: OIDC (Connect)
- Outbound: API Key (Secrets Manager)

**Tools:**
- create_ticket ✅
- get_ticket_status ✅
- add_ticket_comment ✅
- list_recent_tickets ✅

**API Endpoint:**
- URL: `https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc`

---

## Next Steps After Configuration

Once AgentCore Gateway is configured:

1. ✅ Note the Gateway ARN
2. ➡️ Proceed to Task 3.2: Connect AI Agent IAM Role Creation
3. ➡️ Proceed to Task 3.3: AgentCore Gateway OIDC Configuration Update (if needed)
4. ➡️ Proceed to Task 3.4: Connect AI Agent Creation (will reference this Gateway)

---

## Rollback Instructions

If you need to delete the AgentCore Gateway:

### Via Console:
1. Navigate to Amazon Bedrock → Agents → AgentCore Gateway
2. Select `poc-itsm-agentcore-gateway`
3. Click **Delete**
4. Confirm deletion

### Verification:
1. Check that gateway no longer appears in Console
2. Verify CloudWatch log group is deleted (or delete manually)

**Note:** Deleting the gateway does NOT delete:
- IAM role (poc-agentcore-gateway-role)
- Secrets Manager secret (poc-itsm-api-key)
- API Gateway
- Lambda function
- DynamoDB table

These resources must be deleted separately if needed.

---

## Task Status

**Task 2.4: AgentCore Gateway Deployment - MANUAL CONFIGURATION REQUIRED ⚠️**

**Status:** Documentation complete, awaiting manual configuration

**Prerequisites Complete:**
- ✅ Task 2.1: API key in Secrets Manager
- ✅ Task 2.2: IAM role created
- ✅ Task 2.3: Tool definitions created

**Blocking Dependency:**
- ⏳ Task 3.1: Amazon Connect instance (needed for OIDC URL)

**Action Required:**
1. Complete Task 3.1 (Amazon Connect Instance Creation)
2. Note the Connect OIDC discovery URL
3. Return to this guide and follow manual configuration steps
4. Document Gateway ARN in `deployment/agentcore-deployment-log.md`

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-09  
**Configuration Guide Version:** 1.0
