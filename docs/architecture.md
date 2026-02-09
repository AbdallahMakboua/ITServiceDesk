# Architecture Documentation - Task 0.9

## Overview

This document provides comprehensive architecture documentation for the DAS Holding AI L1 Voice Service Desk PoC, including component interactions, data flows, authentication mechanisms, and cost estimates.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CALLER (Phone)                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Voice Call
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                    Amazon Connect Instance                           │
│                    (poc-ai-l1-support)                              │
│                    Region: us-east-1                                │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Contact Flow (poc-l1-support-flow)                 │  │
│  │                                                              │  │
│  │  1. Play Greeting (optional)                                │  │
│  │  2. Invoke AI Agent                                         │  │
│  │  3. Handle Escalation                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ OIDC Authentication
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│              Amazon Connect AI Agent                                 │
│              (poc-l1-support-agent)                                 │
│              Powered by Amazon Bedrock                              │
│                                                                      │
│  Tools Available:                                                   │
│  - create_ticket                                                    │
│  - get_ticket_status                                                │
│  - add_ticket_comment                                               │
│  - list_recent_tickets                                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Tool Invocations
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│         Bedrock AgentCore Gateway (MCP Server)                      │
│         (poc-itsm-agentcore-gateway)                                │
│         Region: us-east-1                                           │
│                                                                      │
│  Inbound Auth:  OIDC (from Connect)                                │
│  Outbound Auth: API Key (from Secrets Manager)                     │
│  IAM Role:      poc-agentcore-gateway-role                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTPS + API Key
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│              Amazon API Gateway (REST API)                          │
│              (poc-itsm-api)                                         │
│              Stage: poc                                             │
│              Region: us-east-1                                      │
│                                                                      │
│  Endpoints:                                                         │
│  - POST   /tickets                                                  │
│  - GET    /tickets/{id}                                             │
│  - POST   /tickets/{id}/comments                                    │
│  - GET    /tickets?caller={caller_id}                               │
│                                                                      │
│  Authentication: API Key (x-api-key header)                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Lambda Proxy Integration
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│              AWS Lambda Function                                     │
│              (poc-itsm-api-handler)                                 │
│              Runtime: Python 3.12                                   │
│              Memory: 256 MB                                         │
│              Timeout: 10 seconds                                    │
│              IAM Role: poc-itsm-lambda-role                         │
│                                                                      │
│  Environment Variables:                                             │
│  - TABLE_NAME: poc-itsm-tickets                                     │
│  - REGION: us-east-1                                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ DynamoDB Operations
                                 │ (PutItem, GetItem, UpdateItem, Query)
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│              Amazon DynamoDB Table                                   │
│              (poc-itsm-tickets)                                     │
│              Billing: PAY_PER_REQUEST (On-Demand)                   │
│              Region: us-east-1                                      │
│                                                                      │
│  Primary Key: ticket_id (String)                                    │
│  GSI: CallerIdIndex (caller_id + created_at)                        │
│                                                                      │
│  Attributes:                                                        │
│  - ticket_id, caller_id, issue_description                          │
│  - status, created_at, updated_at, comments[]                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Supporting Services                               │
├─────────────────────────────────────────────────────────────────────┤
│  AWS Secrets Manager:  poc-itsm-api-key (API key storage)          │
│  Amazon S3:            poc-itsm-openapi-specs-* (OpenAPI spec)      │
│  CloudWatch Logs:      /aws/lambda/poc-itsm-api-handler            │
│  CloudWatch Logs:      /aws/apigateway/poc-itsm-api                │
│  CloudWatch Logs:      /aws/connect/poc-ai-l1-support              │
│  AWS Budgets:          poc-ai-l1-support-budget ($10, alert at $8) │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. Caller (End User)

**Description:** Person calling the IT support line  
**Interface:** Phone (PSTN or VoIP)  
**Interaction:** Voice conversation with AI Agent

### 2. Amazon Connect Instance

**Name:** `poc-ai-l1-support`  
**Purpose:** Cloud contact center for voice interactions  
**Components:**
- Phone number (DID)
- Contact flow (call routing logic)
- AI Agent integration

**Key Features:**
- Voice-first interaction
- Natural language understanding
- Escalation to human agents

### 3. Amazon Connect AI Agent

**Name:** `poc-l1-support-agent`  
**Purpose:** AI-powered conversational agent for L1 support  
**Powered By:** Amazon Bedrock  
**Capabilities:**
- Natural language conversation
- Tool invocation (4 ITSM tools)
- Context retention during call
- Escalation detection

### 4. Bedrock AgentCore Gateway (MCP Server)

**Name:** `poc-itsm-agentcore-gateway`  
**Purpose:** Secure bridge between AI Agent and Mock ITSM API  
**Protocol:** Model Context Protocol (MCP)  
**Key Features:**
- OIDC authentication (inbound from Connect)
- API key authentication (outbound to API)
- Static tool definitions (4 tools)
- Request/response transformation

### 5. Amazon API Gateway

**Name:** `poc-itsm-api`  
**Type:** REST API  
**Purpose:** Expose Lambda function as HTTP API  
**Key Features:**
- API key authentication
- Usage plans and throttling
- Request routing
- Lambda proxy integration

### 6. AWS Lambda Function

**Name:** `poc-itsm-api-handler`  
**Purpose:** Business logic for ITSM operations  
**Runtime:** Python 3.12  
**Key Features:**
- Single function handling all 4 operations
- DynamoDB integration
- Error handling with retry logic
- Input validation

### 7. Amazon DynamoDB Table

**Name:** `poc-itsm-tickets`  
**Purpose:** Persistent storage for mock tickets  
**Key Features:**
- On-demand billing
- Global Secondary Index for caller queries
- Single-digit millisecond latency
- Automatic scaling

### 8. Supporting Services

**AWS Secrets Manager:** Secure API key storage  
**Amazon S3:** OpenAPI specification storage  
**CloudWatch Logs:** Centralized logging  
**AWS Budgets:** Cost monitoring and alerts

---

## Data Flow Diagrams

### Flow 1: Create Ticket

```
1. Caller describes issue via phone
   ↓
2. Connect AI Agent processes speech
   ↓
3. AI Agent invokes create_ticket tool
   ↓
4. AgentCore Gateway receives tool invocation
   ↓
5. AgentCore Gateway retrieves API key from Secrets Manager
   ↓
6. AgentCore Gateway calls POST /tickets with API key
   ↓
7. API Gateway validates API key
   ↓
8. API Gateway invokes Lambda function
   ↓
9. Lambda generates UUID for ticket_id
   ↓
10. Lambda calls DynamoDB PutItem
   ↓
11. DynamoDB stores ticket
   ↓
12. Lambda returns 201 with ticket_id
   ↓
13. API Gateway returns response to AgentCore
   ↓
14. AgentCore returns result to AI Agent
   ↓
15. AI Agent speaks ticket number to caller
```

### Flow 2: Get Ticket Status

```
1. Caller provides ticket number via phone
   ↓
2. AI Agent invokes get_ticket_status tool
   ↓
3. AgentCore Gateway calls GET /tickets/{id}
   ↓
4. API Gateway invokes Lambda
   ↓
5. Lambda calls DynamoDB GetItem
   ↓
6. DynamoDB returns ticket data
   ↓
7. Lambda returns 200 with ticket details
   ↓
8. AI Agent speaks ticket status to caller
```

### Flow 3: Add Comment

```
1. Caller provides additional information via phone
   ↓
2. AI Agent invokes add_ticket_comment tool
   ↓
3. AgentCore Gateway calls POST /tickets/{id}/comments
   ↓
4. API Gateway invokes Lambda
   ↓
5. Lambda calls DynamoDB UpdateItem (list_append)
   ↓
6. DynamoDB appends comment to comments array
   ↓
7. Lambda returns 200 with success
   ↓
8. AI Agent confirms comment added to caller
```

### Flow 4: List Recent Tickets

```
1. Caller asks for recent tickets via phone
   ↓
2. AI Agent invokes list_recent_tickets tool
   ↓
3. AgentCore Gateway calls GET /tickets?caller={id}
   ↓
4. API Gateway invokes Lambda
   ↓
5. Lambda calls DynamoDB Query on CallerIdIndex GSI
   ↓
6. DynamoDB returns tickets (sorted by created_at desc, limit 10)
   ↓
7. Lambda returns 200 with tickets array
   ↓
8. AI Agent reads ticket list to caller
```

---

## Authentication Flows

### Authentication Flow 1: Connect → AgentCore Gateway

```
1. Connect AI Agent initiates tool invocation
   ↓
2. Connect generates JWT token
   ↓
3. Connect includes JWT in request to AgentCore Gateway
   ↓
4. AgentCore Gateway retrieves Connect's OIDC discovery URL
   ↓
5. AgentCore Gateway fetches Connect's public keys
   ↓
6. AgentCore Gateway validates JWT signature
   ↓
7. AgentCore Gateway validates JWT claims (issuer, audience, expiration)
   ↓
8. If valid: Process request
   If invalid: Return 401 Unauthorized
```

### Authentication Flow 2: AgentCore Gateway → API Gateway

```
1. AgentCore Gateway needs to call Mock ITSM API
   ↓
2. AgentCore Gateway retrieves API key from Secrets Manager
   (using IAM role: poc-agentcore-gateway-role)
   ↓
3. AgentCore Gateway includes API key in x-api-key header
   ↓
4. API Gateway receives request
   ↓
5. API Gateway validates API key against usage plan
   ↓
6. If valid: Forward to Lambda
   If invalid: Return 403 Forbidden
```

### Authentication Flow 3: Lambda → DynamoDB

```
1. Lambda function needs to access DynamoDB
   ↓
2. Lambda uses IAM role: poc-itsm-lambda-role
   ↓
3. AWS STS validates IAM role permissions
   ↓
4. IAM policy allows specific DynamoDB operations on poc-itsm-tickets
   ↓
5. If authorized: Execute DynamoDB operation
   If unauthorized: Return AccessDeniedException
```

---

## Cost Estimates by Service

### Amazon Connect

**Components:**
- Phone number: $0.03/day
- Inbound minutes: $0.018/minute
- AI Agent usage: Included in Bedrock charges

**PoC Estimate:**
- Phone number (3 days): $0.09
- Test calls (6 minutes): $0.108
- **Total: ~$0.20**

### Amazon Bedrock (AgentCore Gateway)

**Pricing:** Variable based on model and usage  
**PoC Estimate:** $1-2 for minimal testing

### AWS Lambda

**Pricing:**
- Requests: $0.20 per 1M requests
- Duration: $0.0000000021 per 100ms at 256MB

**PoC Estimate:**
- 100 invocations: < $0.01
- **Total: < $0.01** (covered by free tier)

### Amazon API Gateway

**Pricing:**
- REST API: $3.50 per 1M requests
- Data transfer: $0.09 per GB

**PoC Estimate:**
- 100 requests: $0.00035
- Data transfer: $0.00001
- **Total: < $0.01** (covered by free tier)

### Amazon DynamoDB

**Pricing:**
- Write requests: $1.25 per 1M WRUs
- Read requests: $0.25 per 1M RRUs
- Storage: $0.25 per GB-month

**PoC Estimate:**
- 30 writes: $0.0000375
- 70 reads: $0.0000175
- Storage (< 1 MB): $0.00025
- **Total: < $0.01**

### AWS Secrets Manager

**Pricing:** $0.40 per secret per month

**PoC Estimate:**
- 1 secret (prorated for 3 days): $0.04
- **Total: $0.04**

### Amazon S3

**Pricing:**
- Storage: $0.023 per GB-month
- Requests: $0.005 per 1K PUT, $0.0004 per 1K GET

**PoC Estimate:**
- Storage (< 1 MB): < $0.01
- Requests: < $0.01
- **Total: < $0.01**

### CloudWatch Logs

**Pricing:**
- Ingestion: $0.50 per GB
- Storage: $0.03 per GB-month

**PoC Estimate:**
- Ingestion (< 10 MB): < $0.01
- Storage: < $0.01
- **Total: < $0.01**

### AWS Budgets

**Pricing:** First 2 budgets free, $0.02 per budget per day after

**PoC Estimate:** $0 (first 2 budgets free)

---

## Total Cost Estimate

| Service | Estimated Cost |
|---------|---------------|
| Amazon Connect | $0.20 |
| Amazon Bedrock (AgentCore) | $1.50 |
| AWS Lambda | < $0.01 |
| Amazon API Gateway | < $0.01 |
| Amazon DynamoDB | < $0.01 |
| AWS Secrets Manager | $0.04 |
| Amazon S3 | < $0.01 |
| CloudWatch Logs | < $0.01 |
| AWS Budgets | $0.00 |
| **TOTAL ESTIMATED** | **$1.75 - $2.00** |

**Budget:** $10.00 USD  
**Alert Threshold:** $8.00 USD  
**Estimated Usage:** 17.5% - 20% of budget  
**Safety Margin:** 80% remaining

---

## Region Constraint

**All resources deployed in:** `us-east-1`

**Rationale:**
- Simplifies architecture
- Reduces latency (single region)
- Avoids cross-region data transfer costs
- Meets PoC requirements

**Verification:**
- All AWS CLI commands include `--region us-east-1`
- All resource ARNs contain `us-east-1`
- No cross-region replication configured

---

## Security Architecture

### Network Security

- **HTTPS Only:** All API communication encrypted in transit
- **No Public Endpoints:** DynamoDB not publicly accessible
- **VPC Not Required:** Serverless services use AWS backbone

### Authentication & Authorization

- **Multi-Layer Auth:**
  1. Connect → AgentCore: OIDC (JWT tokens)
  2. AgentCore → API Gateway: API Key
  3. Lambda → DynamoDB: IAM roles

- **Least Privilege IAM:**
  - Lambda: DynamoDB operations only on poc-itsm-tickets
  - AgentCore: API Gateway invoke + Secrets Manager read
  - Connect AI Agent: Bedrock invoke only

### Data Security

- **At Rest:** DynamoDB encrypted by default (AWS managed keys)
- **In Transit:** TLS 1.2+ for all connections
- **Secrets:** API keys stored in Secrets Manager (encrypted)
- **No Sensitive Data:** No passwords, MFA codes, or PII stored

### Production Isolation

- **Clear Naming:** All resources prefixed with `poc-`
- **No Production Endpoints:** Only mock API configured
- **Separate Account Recommended:** Isolate PoC from production

---

## Scalability Considerations

### Current PoC Scale

- **Concurrent Calls:** 1-2
- **API Requests:** < 100 total
- **DynamoDB Items:** < 20 tickets
- **Lambda Concurrency:** 1-2

### Production Scale Potential

**If scaled to production:**
- **Concurrent Calls:** 100+
- **API Requests:** 10K+ per day
- **DynamoDB Items:** Millions
- **Lambda Concurrency:** 100+

**Scaling Approach:**
- Lambda: Automatic scaling (up to 1000 concurrent)
- DynamoDB: On-demand scales automatically
- API Gateway: Handles 10K requests/second
- Connect: Scales to thousands of concurrent calls

---

## Monitoring and Observability

### CloudWatch Dashboards

**Recommended Metrics:**
- Lambda invocations, errors, duration
- API Gateway 4XX/5XX errors, latency
- DynamoDB consumed capacity, throttles
- Connect call volume, AI Agent success rate

### Alarms

**Critical Alarms:**
- Lambda error rate > 5%
- API Gateway 5XX errors > 1%
- DynamoDB throttling events
- Budget exceeds $8 USD

### Logging

**Log Groups:**
- `/aws/lambda/poc-itsm-api-handler`
- `/aws/apigateway/poc-itsm-api`
- `/aws/connect/poc-ai-l1-support`
- `/aws/bedrock/agentcore/poc-itsm-agentcore-gateway`

**Log Retention:** Default (never expire) - acceptable for short PoC

---

## Acceptance Criteria Validation

### Requirement 17.1-17.6: Architecture and Usage Documentation

- ✅ Component diagram showing: Caller → Connect → AI Agent → AgentCore Gateway → Mock API → DynamoDB
- ✅ Authentication flows documented (OIDC, API Key, IAM)
- ✅ Data flow for each operation (create, get, comment, list)
- ✅ Cost estimates for each AWS service
- ✅ Region constraint (us-east-1) clearly indicated
- ✅ Total estimated cost: $1.75-$2.00 (well within $10 budget)

---

## Task Status

**Task 0.9: Architecture Documentation - COMPLETE ✅**

Comprehensive architecture documented:
- System architecture diagram (ASCII art)
- Component descriptions (8 components)
- Data flow diagrams (4 operations)
- Authentication flows (3 layers)
- Cost estimates by service (total: $1.75-$2.00)
- Region constraint (us-east-1)
- Security architecture
- Scalability considerations
- Monitoring and observability

**Note:** This architecture has been partially implemented in Phase 1 (Tasks 1.1-1.4). This document provides the complete architecture view for all phases.
