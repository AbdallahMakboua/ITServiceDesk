# AgentCore Gateway Configuration Design - Task 0.6

## Overview

This document defines the Bedrock AgentCore Gateway (MCP server) configuration for the DAS Holding AI L1 Voice Service Desk PoC. The AgentCore Gateway acts as a secure bridge between the Amazon Connect AI Agent and the Mock ITSM API, exposing exactly four tools that match the OpenAPI specification.

**CRITICAL:** This gateway is completely isolated from production ITSM systems and only connects to the mock API.

---

## Architecture Overview

```
Amazon Connect AI Agent
        ↓ (OIDC Authentication)
Bedrock AgentCore Gateway (MCP Server)
        ↓ (API Key Authentication)
Mock ITSM API (API Gateway + Lambda)
        ↓
DynamoDB (poc-itsm-tickets)
```

---

## AgentCore Gateway Configuration

### Gateway Name
```
poc-itsm-agentcore-gateway
```

### Region
```
us-east-1
```

### Gateway Type
```
MCP Server (Model Context Protocol)
```

---

## Authentication Configuration

### Inbound Authentication (Connect → AgentCore)

**Method:** OIDC (OpenID Connect)  
**Provider:** Amazon Connect  
**Discovery URL Format:**
```
https://<CONNECT_ALIAS>.my.connect.aws/.well-known/openid-configuration
```

**Example:**
```
https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
```

**Configuration Steps:**
1. Create Amazon Connect instance (Task 3.1)
2. Note the Connect instance alias (e.g., `poc-ai-l1-support`)
3. Configure AgentCore Gateway with OIDC discovery URL
4. AgentCore Gateway validates JWT tokens from Connect

**Security:**
- Only requests from the specific Connect instance are accepted
- JWT tokens validated against Connect's public keys
- Token expiration enforced

### Outbound Authentication (AgentCore → Mock API)

**Method:** API Key  
**Header:** `x-api-key`  
**Storage:** AWS Secrets Manager

**Secret Configuration:**
- **Secret Name:** `poc-itsm-api-key`
- **Secret Value:** API key from Task 1.5 (API Gateway)
- **Region:** us-east-1
- **Encryption:** AWS managed key (default)

**AgentCore Configuration:**
```json
{
  "outboundAuth": {
    "type": "apiKey",
    "headerName": "x-api-key",
    "secretArn": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:poc-itsm-api-key-XXXXX"
  }
}
```

**Security:**
- API key never exposed in code or logs
- AgentCore Gateway retrieves key from Secrets Manager at runtime
- IAM role controls access to secret

---

## Tool Definitions

### Critical Requirements

1. **Exactly FOUR tools** - no more, no less
2. **Static definitions** - NO dynamic tool generation
3. **Match OpenAPI spec exactly** - input/output schemas must align
4. **NO administrative operations** - no delete, no privileged actions
5. **NO production endpoints** - only mock API

### Tool 1: create_ticket

**Purpose:** Create a new support ticket

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "caller_id": {
      "type": "string",
      "description": "Identifier for the caller (session ID or hashed phone number)",
      "minLength": 1,
      "maxLength": 100
    },
    "issue_description": {
      "type": "string",
      "description": "Description of the IT issue",
      "minLength": 1,
      "maxLength": 1000
    }
  },
  "required": ["caller_id", "issue_description"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the created ticket"
    },
    "status": {
      "type": "string",
      "enum": ["open"],
      "description": "Initial status of the ticket"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of ticket creation"
    }
  }
}
```

**API Mapping:**
- **Method:** POST
- **Endpoint:** `/tickets`
- **Request Body:** `{"caller_id": "...", "issue_description": "..."}`

### Tool 2: get_ticket_status

**Purpose:** Retrieve the current status and details of a ticket

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique ticket identifier"
    }
  },
  "required": ["ticket_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_id": {"type": "string", "format": "uuid"},
    "caller_id": {"type": "string"},
    "issue_description": {"type": "string"},
    "status": {"type": "string", "enum": ["open", "in_progress", "resolved", "closed"]},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "comments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "comment_text": {"type": "string"},
          "added_at": {"type": "string", "format": "date-time"}
        }
      }
    }
  }
}
```

**API Mapping:**
- **Method:** GET
- **Endpoint:** `/tickets/{ticket_id}`
- **Path Parameter:** `ticket_id`

### Tool 3: add_ticket_comment

**Purpose:** Add a comment to an existing ticket

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique ticket identifier"
    },
    "comment": {
      "type": "string",
      "description": "Comment text to add",
      "minLength": 1,
      "maxLength": 1000
    }
  },
  "required": ["ticket_id", "comment"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Indicates if the comment was added successfully"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of the update"
    }
  }
}
```

**API Mapping:**
- **Method:** POST
- **Endpoint:** `/tickets/{ticket_id}/comments`
- **Path Parameter:** `ticket_id`
- **Request Body:** `{"comment": "..."}`

### Tool 4: list_recent_tickets

**Purpose:** List recent tickets for a specific caller

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "caller_id": {
      "type": "string",
      "description": "Caller identifier to filter tickets"
    }
  },
  "required": ["caller_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "tickets": {
      "type": "array",
      "description": "List of tickets for the caller",
      "items": {
        "type": "object",
        "properties": {
          "ticket_id": {"type": "string", "format": "uuid"},
          "caller_id": {"type": "string"},
          "issue_description": {"type": "string"},
          "status": {"type": "string"},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"},
          "comments": {"type": "array"}
        }
      }
    }
  }
}
```

**API Mapping:**
- **Method:** GET
- **Endpoint:** `/tickets?caller={caller_id}`
- **Query Parameter:** `caller`

---

## Tool Configuration File

### AgentCore Tools JSON

**File:** `config/agentcore-tools.json`

```json
{
  "tools": [
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
    },
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
    },
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
    },
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
  ]
}
```

---

## IAM Role Configuration

### Role Name
```
poc-agentcore-gateway-role
```

### Permissions Required

See `docs/iam-policies.md` for complete IAM configuration.

**Summary:**
- `secretsmanager:GetSecretValue` on `poc-itsm-api-key`
- `execute-api:Invoke` on Mock ITSM API (if using API Gateway)
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` for CloudWatch

---

## Deployment Configuration

### AgentCore Gateway Creation

**Note:** Exact CLI commands for AgentCore Gateway creation will be confirmed during implementation (Task 2.4), as the service may use Console-based configuration or specific Bedrock APIs.

**Placeholder Configuration:**
```bash
# Create AgentCore Gateway (exact command TBD)
aws bedrock create-agent-gateway \
  --gateway-name poc-itsm-agentcore-gateway \
  --region us-east-1 \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/poc-agentcore-gateway-role \
  --inbound-auth-config file://config/inbound-oidc-config.json \
  --outbound-auth-config file://config/outbound-apikey-config.json \
  --tools file://config/agentcore-tools.json
```

### Configuration Files

**inbound-oidc-config.json:**
```json
{
  "type": "OIDC",
  "discoveryUrl": "https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration"
}
```

**outbound-apikey-config.json:**
```json
{
  "type": "apiKey",
  "headerName": "x-api-key",
  "secretArn": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:poc-itsm-api-key-XXXXX"
}
```

---

## Security Considerations

### Production Isolation

✅ **NO production ITSM endpoints configured**  
✅ **Only mock API endpoint** (API Gateway URL)  
✅ **Clear naming** (poc- prefix on all resources)  
✅ **Separate AWS account recommended** (if possible)

### Authentication Security

✅ **Inbound:** OIDC from Connect (JWT validation)  
✅ **Outbound:** API key from Secrets Manager (encrypted)  
✅ **No credentials in code or logs**  
✅ **IAM least privilege** (specific resource ARNs only)

### Tool Exposure Control

✅ **Static tool list** (no dynamic generation)  
✅ **Exactly 4 tools** (no more, no less)  
✅ **NO delete operations**  
✅ **NO administrative operations**  
✅ **Input validation** (schema enforcement)

---

## Error Handling

### Tool Invocation Errors

**Scenario:** API returns 404 (ticket not found)  
**AgentCore Behavior:** Return error to AI Agent  
**AI Agent Response:** "I couldn't find that ticket. Please verify the ticket number."

**Scenario:** API returns 500 (server error)  
**AgentCore Behavior:** Return error to AI Agent  
**AI Agent Response:** "I'm experiencing technical difficulties. Let me escalate you to a human agent."

**Scenario:** Authentication failure (invalid API key)  
**AgentCore Behavior:** Log error, return generic error  
**AI Agent Response:** "I'm unable to access the ticketing system right now. Please try again later."

---

## Monitoring and Logging

### CloudWatch Logs

**Log Group:** `/aws/bedrock/agentcore/poc-itsm-agentcore-gateway`  
**Log Events:**
- Tool invocations
- API requests/responses
- Authentication events
- Errors and exceptions

### CloudWatch Metrics

- Tool invocation count
- Tool invocation latency
- Error rate
- Authentication failures

---

## Testing Strategy

### Tool Invocation Tests

**Test 1: Create Ticket**
```json
Input: {
  "tool": "create_ticket",
  "parameters": {
    "caller_id": "test-user-001",
    "issue_description": "Test issue - laptop not working"
  }
}

Expected Output: {
  "ticket_id": "<UUID>",
  "status": "open",
  "created_at": "<ISO 8601 timestamp>"
}
```

**Test 2: Get Ticket Status**
```json
Input: {
  "tool": "get_ticket_status",
  "parameters": {
    "ticket_id": "<UUID from Test 1>"
  }
}

Expected Output: {
  "ticket_id": "<UUID>",
  "caller_id": "test-user-001",
  "issue_description": "Test issue - laptop not working",
  "status": "open",
  ...
}
```

**Test 3: Add Comment**
```json
Input: {
  "tool": "add_ticket_comment",
  "parameters": {
    "ticket_id": "<UUID from Test 1>",
    "comment": "Additional information: tried restarting"
  }
}

Expected Output: {
  "success": true,
  "updated_at": "<ISO 8601 timestamp>"
}
```

**Test 4: List Tickets**
```json
Input: {
  "tool": "list_recent_tickets",
  "parameters": {
    "caller_id": "test-user-001"
  }
}

Expected Output: {
  "tickets": [
    {
      "ticket_id": "<UUID>",
      "caller_id": "test-user-001",
      ...
    }
  ]
}
```

---

## Acceptance Criteria Validation

### Requirement 5.1-5.10: AgentCore Gateway with Secure Authentication

- ✅ Exactly ONE AgentCore Gateway (MCP server)
- ✅ Inbound auth: Connect OIDC discovery URL format
- ✅ Outbound auth: API key to Mock_ITSM_API (stored in Secrets Manager)
- ✅ Exactly four tools: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- ✅ NO administrative or delete operations
- ✅ Tool definitions STATIC and explicitly defined (NO dynamic generation)
- ✅ Tool definitions match OpenAPI spec exactly
- ✅ NO production ITSM endpoints configured

---

## Task Status

**Task 0.6: AgentCore Gateway Configuration Design - COMPLETE ✅**

AgentCore Gateway configuration documented:
- Authentication mechanisms (OIDC inbound, API key outbound)
- All four tool definitions with schemas
- API mappings for each tool
- Security considerations
- IAM role requirements
- Testing strategy
- Error handling approach

**Note:** This configuration will be implemented in Phase 2 (Tasks 2.1-2.4). This document provides the design that should exist before implementation.
