# Plan of Record (POR)
# DAS Holding – AI IT L1 Voice Service Desk PoC

**Version:** 1.0  
**Date:** 2026-02-09  
**Region:** us-east-1 ONLY  
**Budget Alert:** $10 USD total, $8 USD alert threshold (AWS Budgets provides alerts only, not enforcement)  
**Deployment Mode:** PLAN-FIRST, TASK-BY-TASK, NO AUTO-DEPLOY

---

## Executive Summary

This Plan of Record defines the incremental, test-driven delivery approach for building a minimal AI-driven L1 phone support PoC using Amazon Connect with Bedrock AgentCore Gateway (MCP). The PoC is completely isolated from production ITSM systems and uses a mock backend for demonstration purposes.

**Critical Constraints:**
- NO production ManageEngine ServiceDesk Plus integration
- ONLY whitelisted AWS services (Connect, Bedrock AgentCore, Lambda, API Gateway, DynamoDB, S3, IAM, CloudWatch, Budgets)
- $10 USD total budget with alert at $8 USD (AWS Budgets provides alerts only, not spending enforcement)
- Manual Stop Rule: If spending reaches $8 USD, pause work immediately and execute cleanup
- us-east-1 region exclusively
- Explicit approval gates before ANY AWS resource creation

---

## Delivery Phases Overview

1. **Phase 0: Planning & Documentation** (Documentation only - NO deployment)
2. **Phase 1: Mock ITSM Backend** (API Gateway + Lambda + DynamoDB)
3. **Phase 2: AgentCore Gateway Configuration** (Bedrock MCP server setup)
4. **Phase 3: Amazon Connect Setup** (AI Agent + Contact Flow)
5. **Phase 4: End-to-End Testing** (Voice interaction validation)
6. **Phase 5: Cleanup & Teardown** (Resource removal)

---

## Phase 0: Planning & Documentation

**Objective:** Create all design artifacts and specifications WITHOUT deploying any AWS resources.

### Task 0.1: Budget Setup Planning

**Goal:** Document AWS Budgets configuration steps for $10 total budget with $8 alert threshold.

**Inputs:**
- Requirements.md (Requirement 4)

**Outputs:**
- `docs/budget-setup-guide.md` - Step-by-step budget configuration instructions

**Acceptance Criteria:**
- Maps to Requirement 4.6: Configure AWS Budgets alerts at $8 USD (80% threshold)
- Document includes budget name, amount ($10), alert threshold ($8), notification email setup
- Document specifies us-east-1 region constraint
- Document clarifies that AWS Budgets provides alerts only, not spending enforcement
- Manual Stop Rule documented: If spending reaches $8 USD, pause work immediately and execute cleanup

**Verification:**
- Manual review of documentation completeness
- Verify all budget parameters are specified

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.2: OpenAPI Specification Creation

**Goal:** Create formal OpenAPI 3.0 specification for the Mock ITSM API.

**Inputs:**
- Requirements.md (Requirement 2, Requirement 11)

**Outputs:**
- `specs/mock-itsm-api-openapi.yaml` - Complete OpenAPI 3.0 specification

**Acceptance Criteria:**
- Maps to Requirement 11.1-11.6: OpenAPI 3.0 spec with all four endpoints
- Defines POST /tickets (create_ticket)
- Defines GET /tickets/{id} (get_ticket_status)
- Defines POST /tickets/{id}/comments (add_ticket_comment)
- Defines GET /tickets?caller={caller_id} (list_recent_tickets)
- Includes request/response schemas for all endpoints
- Defines API key authentication mechanism
- NO delete or administrative endpoints

**Verification:**
- Validate using OpenAPI validator (e.g., `swagger-cli validate` or online validator)
- Manual review against Requirement 2 acceptance criteria
- Confirm authentication scheme is API key only

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.3: DynamoDB Schema Design

**Goal:** Document DynamoDB table schema and GSI design for mock ticket storage.

**Inputs:**
- Requirements.md (Requirement 13)

**Outputs:**
- `docs/dynamodb-schema.md` - Table design document

**Acceptance Criteria:**
- Maps to Requirement 13.1-13.6: DynamoDB schema with non-production naming
- Table name: `poc-itsm-tickets` (clear non-production prefix)
- Partition key: `ticket_id` (String)
- Attributes: ticket_id, caller_id, issue_description, status, created_at, updated_at, comments (List)
- GSI: `CallerIdIndex` with caller_id as partition key, created_at as sort key
- Billing mode: ON_DEMAND
- Region: us-east-1

**Verification:**
- Manual review of schema completeness
- Verify GSI supports list_recent_tickets query pattern
- Confirm on-demand billing mode for cost control

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.4: Lambda Function Design

**Goal:** Document Lambda function architecture, handler logic, and IAM requirements.

**Inputs:**
- Requirements.md (Requirement 12, Requirement 14)
- specs/mock-itsm-api-openapi.yaml

**Outputs:**
- `docs/lambda-design.md` - Lambda architecture document
- `docs/iam-policies.md` - IAM role and policy specifications

**Acceptance Criteria:**
- Maps to Requirement 12.1-12.7: Minimal Lambda implementation
- Runtime: Python 3.12 or Node.js 20.x
- Single Lambda function handling all four API operations OR separate functions per operation
- Error handling with appropriate HTTP status codes (400, 404, 500)
- DynamoDB retry logic with exponential backoff (up to 3 attempts)
- Execution timeout: 10 seconds maximum
- IAM policy: Least privilege, DynamoDB operations only on poc-itsm-tickets table
- Maps to Requirement 14.1: Lambda IAM role limited to specific DynamoDB table

**Verification:**
- Manual review of design against requirements
- Verify IAM policies follow least privilege (no wildcards)
- Confirm error handling covers all failure scenarios

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.5: API Gateway Design

**Goal:** Document API Gateway REST API configuration or Lambda Function URL approach.

**Inputs:**
- Requirements.md (Requirement 2.10)
- specs/mock-itsm-api-openapi.yaml

**Outputs:**
- `docs/api-gateway-design.md` - API Gateway or Function URL configuration

**Acceptance Criteria:**
- Maps to Requirement 2.10: API Gateway REST + Lambda OR Lambda Function URL
- Decision documented: API Gateway REST API vs Lambda Function URL
- API key authentication mechanism specified
- Endpoint mappings to Lambda functions defined
- CORS configuration (if needed for testing)
- Region: us-east-1

**Verification:**
- Manual review of design completeness
- Verify authentication approach aligns with AgentCore Gateway requirements
- Confirm cost implications within $10 budget

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.6: AgentCore Gateway Configuration Design

**Goal:** Document Bedrock AgentCore Gateway (MCP server) configuration including authentication and tool definitions.

**Inputs:**
- Requirements.md (Requirement 5)
- specs/mock-itsm-api-openapi.yaml

**Outputs:**
- `docs/agentcore-gateway-config.md` - AgentCore Gateway configuration specification

**Acceptance Criteria:**
- Maps to Requirement 5.1-5.10: AgentCore Gateway with secure authentication
- Exactly ONE AgentCore Gateway (MCP server)
- Inbound auth: Connect OIDC discovery URL format (https://<CONNECT_ALIAS>.my.connect.aws/.well-known/openid-configuration)
- Outbound auth: API key to Mock_ITSM_API (stored in Secrets Manager or encrypted Lambda env vars)
- Tool definitions: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- Tool definitions MUST match OpenAPI spec exactly
- NO dynamic tool generation or inferred tools
- NO administrative or delete operations exposed

**Verification:**
- Manual review against Requirement 5 acceptance criteria
- Verify tool list is static and explicitly defined
- Confirm authentication mechanisms are secure
- Verify NO production ITSM endpoints are referenced

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.7: Amazon Connect Flow Design

**Goal:** Document Amazon Connect contact flow design including AI Agent configuration and escalation paths.

**Inputs:**
- Requirements.md (Requirement 6, Requirement 7)

**Outputs:**
- `docs/connect-flow-design.md` - Contact flow architecture and AI Agent instructions

**Acceptance Criteria:**
- Maps to Requirement 6.1-6.8: Voice-first interaction with escalation
- Voice-first greeting and interaction flow
- AI Agent instructions: short, spoken-friendly responses
- NO requests for sensitive information (passwords, MFA codes, device serials)
- Confirmation step before ticket creation
- Ticket ID provided to caller after creation
- Explicit "Escalate to human" path defined
- Maps to Requirement 7.1-7.8: Ticket operations via AgentCore tools
- Caller identification using session ID or hashed phone number (NO real employee IDs)

**Verification:**
- Manual review of flow design against requirements
- Verify escalation path is clearly defined
- Confirm NO sensitive data collection
- Verify caller identification approach is privacy-safe

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.8: Test Strategy Documentation

**Goal:** Document comprehensive test strategy including unit tests, contract tests, and E2E test scenarios.

**Inputs:**
- Requirements.md (Requirement 9, Requirement 16)

**Outputs:**
- `docs/test-strategy.md` - Complete testing approach and test cases

**Acceptance Criteria:**
- Maps to Requirement 9.1-9.5: TDD with validation at each step
- Unit test plan for Lambda functions (pytest or equivalent)
- API contract test plan for all four endpoints
- Smoke test checklist for Connect flow
- Maps to Requirement 16.1-16.8: E2E test scenarios
- E2E test cases: create ticket, get status, add comment, list tickets, escalation
- Test data and expected results defined
- Pass/fail criteria for each test scenario

**Verification:**
- Manual review of test coverage completeness
- Verify test cases map to all acceptance criteria
- Confirm E2E scenarios cover all user stories

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.9: Architecture Documentation

**Goal:** Create comprehensive architecture diagram and component interaction documentation.

**Inputs:**
- All Phase 0 design documents
- Requirements.md (Requirement 17)

**Outputs:**
- `docs/architecture.md` - System architecture and component interactions
- `docs/architecture-diagram.png` or ASCII diagram

**Acceptance Criteria:**
- Maps to Requirement 17.1-17.6: Architecture and usage documentation
- Component diagram showing: Caller → Connect → AI Agent → AgentCore Gateway → Mock API → DynamoDB
- Authentication flows documented
- Data flow for each operation (create, get, comment, list)
- Cost estimates for each AWS service
- Region constraint (us-east-1) clearly indicated

**Verification:**
- Manual review of architecture completeness
- Verify all components from requirements are included
- Confirm cost estimates align with $10 budget

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 0.10: Cleanup Procedure Documentation

**Goal:** Document complete resource cleanup and teardown procedure.

**Inputs:**
- Requirements.md (Requirement 15)
- All Phase 0 design documents

**Outputs:**
- `docs/cleanup-procedure.md` - Step-by-step resource deletion guide

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Deletion steps for: DynamoDB table, Lambda functions, API Gateway/Function URL, AgentCore Gateway, Connect AI Agent, Connect Flow, S3 buckets, IAM roles, CloudWatch log groups, Secrets Manager secrets
- Verification steps to confirm deletion
- Cost verification to ensure no ongoing charges
- Automated cleanup script outline (optional)

**Verification:**
- Manual review of cleanup completeness
- Verify all created resources are included
- Confirm verification steps are adequate

**Rollback/Cleanup:**
- N/A (documentation only)

---

### 🛑 APPROVAL GATE 1: Phase 0 Documentation Review

**STOP HERE - DO NOT PROCEED WITHOUT EXPLICIT APPROVAL**

**Review Checklist:**
- [ ] All Phase 0 documentation complete and reviewed
- [ ] OpenAPI spec validated
- [ ] DynamoDB schema supports all query patterns
- [ ] Lambda design follows least privilege IAM
- [ ] AgentCore Gateway configuration is secure and isolated from production
- [ ] Connect flow design avoids sensitive data collection
- [ ] Test strategy covers all requirements
- [ ] Architecture aligns with $10 budget and us-east-1 constraint
- [ ] Cleanup procedure is comprehensive

**Approval Required From:** Project Stakeholder / Technical Lead

**Next Phase:** Phase 1 - Mock ITSM Backend Implementation

---

## Phase 1: Mock ITSM Backend Implementation

**Objective:** Deploy DynamoDB table, Lambda functions, and API Gateway to create the mock ITSM backend.

### Task 1.1: DynamoDB Table Creation

**Goal:** Create DynamoDB table with GSI for mock ticket storage.

**Inputs:**
- docs/dynamodb-schema.md
- Requirements.md (Requirement 1, Requirement 13)

**Outputs:**
- DynamoDB table: `poc-itsm-tickets` in us-east-1
- `deployment/dynamodb-creation-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 1.5: DynamoDB table clearly labeled as non-production
- Maps to Requirement 13.1-13.6: Schema with partition key and GSI
- Table name: `poc-itsm-tickets`
- Partition key: `ticket_id` (String)
- GSI: `CallerIdIndex` (caller_id as partition key, created_at as sort key)
- Billing mode: ON_DEMAND
- Region: us-east-1
- Tags: Environment=PoC, Project=AI-L1-Support

**Verification:**
- AWS CLI command to describe table and verify schema
- Verify GSI is active and queryable
- Confirm billing mode is ON_DEMAND
- Check table is in us-east-1 region

**Rollback/Cleanup:**
- Delete DynamoDB table: `aws dynamodb delete-table --table-name poc-itsm-tickets --region us-east-1`
- Verify deletion: `aws dynamodb describe-table --table-name poc-itsm-tickets` (should return error)

---

### Task 1.2: Lambda IAM Role Creation

**Goal:** Create IAM role with least-privilege policy for Lambda functions.

**Inputs:**
- docs/iam-policies.md
- Requirements.md (Requirement 14)

**Outputs:**
- IAM role: `poc-itsm-lambda-role`
- IAM policy: `poc-itsm-lambda-policy`
- `deployment/iam-creation-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 14.1: Lambda IAM role limited to DynamoDB operations on poc-itsm-tickets
- Maps to Requirement 14.4: NO wildcard (*) permissions
- Policy allows: dynamodb:PutItem, dynamodb:GetItem, dynamodb:UpdateItem, dynamodb:Query on poc-itsm-tickets table and CallerIdIndex
- Policy allows: logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents (CloudWatch logging)
- NO administrative or privileged permissions
- Trust policy allows lambda.amazonaws.com to assume role

**Verification:**
- AWS CLI command to get role policy and verify permissions
- Confirm NO wildcard permissions in policy
- Verify trust relationship is correct

**Rollback/Cleanup:**
- Detach policy from role
- Delete IAM policy: `aws iam delete-policy --policy-arn <policy-arn>`
- Delete IAM role: `aws iam delete-role --role-name poc-itsm-lambda-role`

---

### Task 1.3: Lambda Function Implementation

**Goal:** Implement Lambda function(s) to handle all four API operations.

**Inputs:**
- docs/lambda-design.md
- specs/mock-itsm-api-openapi.yaml
- Requirements.md (Requirement 12, Requirement 19)

**Outputs:**
- `src/lambda/mock_itsm_handler.py` (or .js) - Lambda function code
- `src/lambda/requirements.txt` (or package.json) - Dependencies
- `tests/test_lambda_handler.py` - Unit tests

**Acceptance Criteria:**
- Maps to Requirement 12.1-12.7: Minimal Lambda with proper error handling
- Runtime: Python 3.12 or Node.js 20.x
- Handles POST /tickets (create_ticket): Generate UUID, store in DynamoDB, return ticket_id
- Handles GET /tickets/{id} (get_ticket_status): Query DynamoDB, return ticket data or 404
- Handles POST /tickets/{id}/comments (add_ticket_comment): Update DynamoDB, append comment
- Handles GET /tickets?caller={caller_id} (list_recent_tickets): Query GSI, return tickets
- Maps to Requirement 19.1-19.6: Error handling with appropriate status codes
- Returns 400 for invalid input, 404 for not found, 500 for server errors
- DynamoDB retry with exponential backoff (up to 3 attempts)
- Execution timeout: 10 seconds
- Minimal dependencies (boto3 for Python, aws-sdk for Node.js)

**Verification:**
- Unit tests for each operation (pytest or jest)
- Test create_ticket: Verify UUID generation, DynamoDB PutItem call
- Test get_ticket_status: Verify GetItem call, 404 handling
- Test add_ticket_comment: Verify UpdateItem call, comment append
- Test list_recent_tickets: Verify Query on GSI
- Test error handling: Invalid input, DynamoDB errors, retry logic
- All unit tests must pass before proceeding

**Rollback/Cleanup:**
- Delete Lambda function (Task 1.4 rollback will handle this)
- Remove source code files if needed

---

### Task 1.4: Lambda Function Deployment

**Goal:** Deploy Lambda function with IAM role and environment configuration.

**Inputs:**
- src/lambda/mock_itsm_handler.py (or .js)
- IAM role: `poc-itsm-lambda-role`
- Requirements.md (Requirement 12)

**Outputs:**
- Lambda function: `poc-itsm-api-handler` in us-east-1
- `deployment/lambda-deployment-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 12.1-12.7: Lambda deployed with correct configuration
- Function name: `poc-itsm-api-handler`
- Runtime: Python 3.12 or Node.js 20.x
- IAM role: `poc-itsm-lambda-role`
- Environment variables: TABLE_NAME=poc-itsm-tickets, REGION=us-east-1
- Timeout: 10 seconds
- Memory: 256 MB (minimal)
- Region: us-east-1

**Verification:**
- AWS CLI command to invoke Lambda with test event (create_ticket)
- Verify Lambda execution succeeds and returns ticket_id
- Check CloudWatch logs for successful execution
- Verify DynamoDB table contains created ticket

**Rollback/Cleanup:**
- Delete Lambda function: `aws lambda delete-function --function-name poc-itsm-api-handler --region us-east-1`
- Delete CloudWatch log group: `aws logs delete-log-group --log-group-name /aws/lambda/poc-itsm-api-handler --region us-east-1`

---

### Task 1.5: API Gateway or Lambda Function URL Setup

**Goal:** Expose Lambda function via API Gateway REST API or Lambda Function URL with API key authentication.

**Inputs:**
- docs/api-gateway-design.md
- Lambda function: `poc-itsm-api-handler`
- specs/mock-itsm-api-openapi.yaml
- Requirements.md (Requirement 2)

**Outputs:**
- API Gateway REST API: `poc-itsm-api` OR Lambda Function URL
- API key for authentication
- `deployment/api-gateway-deployment-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 2.1-2.10: Mock API with four endpoints
- Endpoints exposed:
  - POST /tickets
  - GET /tickets/{id}
  - POST /tickets/{id}/comments
  - GET /tickets?caller={caller_id}
- API key authentication configured
- Lambda integration configured for all endpoints
- Stage: `poc` or `v1`
- Region: us-east-1
- NO delete or administrative endpoints

**Verification:**
- API contract tests using curl or Postman:
  - Test POST /tickets: Create ticket, verify 201 response with ticket_id
  - Test GET /tickets/{id}: Retrieve ticket, verify 200 response with ticket data
  - Test POST /tickets/{id}/comments: Add comment, verify 200 response
  - Test GET /tickets?caller={caller_id}: List tickets, verify 200 response with array
  - Test authentication: Request without API key returns 401/403
- All contract tests must pass before proceeding

**Rollback/Cleanup:**
- Delete API Gateway: `aws apigateway delete-rest-api --rest-api-id <api-id> --region us-east-1`
- OR Delete Lambda Function URL: `aws lambda delete-function-url-config --function-name poc-itsm-api-handler --region us-east-1`
- Delete API key if created

---

### Task 1.6: S3 Bucket for OpenAPI Spec Storage

**Goal:** Create S3 bucket and upload OpenAPI specification for AgentCore Gateway reference.

**Inputs:**
- specs/mock-itsm-api-openapi.yaml
- Requirements.md (Requirement 11)

**Outputs:**
- S3 bucket: `poc-itsm-openapi-specs-<account-id>` in us-east-1
- OpenAPI spec uploaded to S3
- `deployment/s3-deployment-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 11.5: OpenAPI spec stored in S3
- Bucket name: `poc-itsm-openapi-specs-<account-id>` (globally unique)
- Region: us-east-1
- Versioning: Enabled (optional for PoC)
- Public access: Blocked
- OpenAPI spec uploaded: `mock-itsm-api-openapi.yaml`
- Bucket policy allows AgentCore Gateway to read spec (if needed)

**Verification:**
- AWS CLI command to list bucket contents
- Verify OpenAPI spec file is present
- Download spec from S3 and validate it matches local version

**Rollback/Cleanup:**
- Delete objects: `aws s3 rm s3://poc-itsm-openapi-specs-<account-id> --recursive --region us-east-1`
- Delete bucket: `aws s3 rb s3://poc-itsm-openapi-specs-<account-id> --region us-east-1`

---

### 🛑 APPROVAL GATE 2: Phase 1 Backend Validation

**STOP HERE - DO NOT PROCEED WITHOUT EXPLICIT APPROVAL**

**Review Checklist:**
- [ ] DynamoDB table created and queryable
- [ ] Lambda function deployed with least-privilege IAM role
- [ ] All unit tests pass
- [ ] API Gateway or Function URL configured with API key auth
- [ ] All API contract tests pass (POST /tickets, GET /tickets/{id}, POST /tickets/{id}/comments, GET /tickets?caller=...)
- [ ] OpenAPI spec uploaded to S3
- [ ] NO production ITSM integrations present
- [ ] All resources in us-east-1
- [ ] Cost tracking shows spending within budget

**Approval Required From:** Project Stakeholder / Technical Lead

**Next Phase:** Phase 2 - AgentCore Gateway Configuration

---

## Phase 2: AgentCore Gateway Configuration

**Objective:** Configure Bedrock AgentCore Gateway (MCP server) to expose mock ITSM tools to Amazon Connect AI Agent.

### Task 2.1: API Key Storage in Secrets Manager

**Goal:** Store Mock ITSM API key securely in AWS Secrets Manager.

**Inputs:**
- API key from Task 1.5
- Requirements.md (Requirement 5)

**Outputs:**
- Secret: `poc-itsm-api-key` in Secrets Manager
- `deployment/secrets-manager-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 5.4: API keys stored securely
- Secret name: `poc-itsm-api-key`
- Secret value: API key from Mock ITSM API
- Region: us-east-1
- Encryption: Default AWS managed key (to avoid KMS costs)
- Tags: Environment=PoC, Project=AI-L1-Support

**Verification:**
- AWS CLI command to retrieve secret value
- Verify secret is encrypted
- Confirm region is us-east-1

**Rollback/Cleanup:**
- Delete secret: `aws secretsmanager delete-secret --secret-id poc-itsm-api-key --force-delete-without-recovery --region us-east-1`

---

### Task 2.2: AgentCore Gateway IAM Role Creation

**Goal:** Create IAM role for AgentCore Gateway with permissions to invoke Mock ITSM API and read secrets.

**Inputs:**
- docs/iam-policies.md
- Requirements.md (Requirement 14)

**Outputs:**
- IAM role: `poc-agentcore-gateway-role`
- IAM policy: `poc-agentcore-gateway-policy`
- `deployment/agentcore-iam-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 14.2: AgentCore Gateway IAM limited to invoking Mock API
- Maps to Requirement 14.4: NO wildcard (*) permissions
- Policy allows: secretsmanager:GetSecretValue on poc-itsm-api-key
- IF using API Gateway: Policy allows execute-api:Invoke scoped to the specific API/stage
- IF using Lambda Function URL: No Lambda invoke permissions required (Function URL is HTTPS + API key); only secretsmanager:GetSecretValue and logging permissions required
- Policy allows: logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents (if logging is required)
- Trust policy allows bedrock.amazonaws.com to assume role

**Verification:**
- AWS CLI command to get role policy and verify permissions
- Confirm NO wildcard permissions
- Verify trust relationship is correct

**Rollback/Cleanup:**
- Detach policy from role
- Delete IAM policy
- Delete IAM role

---

### Task 2.3: AgentCore Gateway Tool Definitions

**Goal:** Create static tool definitions for the four ITSM operations that match the OpenAPI spec exactly.

**Inputs:**
- specs/mock-itsm-api-openapi.yaml
- docs/agentcore-gateway-config.md
- Requirements.md (Requirement 5)

**Outputs:**
- `config/agentcore-tools.json` - Tool definitions for AgentCore Gateway

**Acceptance Criteria:**
- Maps to Requirement 5.5-5.10: Four tools matching OpenAPI spec exactly
- Tool 1: `create_ticket`
  - Input: caller_id (string), issue_description (string)
  - Output: ticket_id (string), status (string), created_at (string)
- Tool 2: `get_ticket_status`
  - Input: ticket_id (string)
  - Output: ticket object with all fields
- Tool 3: `add_ticket_comment`
  - Input: ticket_id (string), comment (string)
  - Output: success (boolean), updated_at (string)
- Tool 4: `list_recent_tickets`
  - Input: caller_id (string)
  - Output: tickets array
- Tool definitions are STATIC and explicitly defined (NO dynamic generation)
- NO administrative or delete operations

**Verification:**
- Manual review of tool definitions against OpenAPI spec
- Verify input/output schemas match API contracts
- Confirm NO delete or admin tools are defined
- Validate JSON syntax

**Rollback/Cleanup:**
- N/A (configuration file only)

---

### Task 2.4: AgentCore Gateway Deployment

**Goal:** Deploy Bedrock AgentCore Gateway (MCP server) with authentication and tool configurations.

**Inputs:**
- config/agentcore-tools.json
- IAM role: `poc-agentcore-gateway-role`
- Secret: `poc-itsm-api-key`
- docs/agentcore-gateway-config.md
- Requirements.md (Requirement 5)

**Outputs:**
- AgentCore Gateway: `poc-itsm-agentcore-gateway` in us-east-1
- `deployment/agentcore-deployment-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 5.1-5.10: AgentCore Gateway with secure authentication
- Gateway name: `poc-itsm-agentcore-gateway`
- Region: us-east-1
- Inbound authentication: Connect OIDC (placeholder URL until Connect is created)
- Outbound authentication: API key from Secrets Manager (poc-itsm-api-key)
- Tools configured: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- IAM role: `poc-agentcore-gateway-role`
- Mock ITSM API endpoint configured

**Verification:**
- AWS CLI or Console to verify AgentCore Gateway is active
- Test tool invocation (if possible via CLI or test harness):
  - Invoke create_ticket with test data
  - Verify ticket is created in DynamoDB
  - Invoke get_ticket_status with ticket_id
  - Verify ticket data is returned
- Check CloudWatch logs for successful tool invocations

**Rollback/Cleanup:**
- Delete AgentCore Gateway via AWS Console (Bedrock AgentCore) or the officially supported CLI/API for AgentCore Gateway (to be confirmed during implementation)
- Placeholder: “Exact CLI command to be confirmed during implementation”.
- Verify deletion in Console

---

### 🛑 APPROVAL GATE 3: Phase 2 AgentCore Gateway Validation

**STOP HERE - DO NOT PROCEED WITHOUT EXPLICIT APPROVAL**

**Review Checklist:**
- [ ] API key stored securely in Secrets Manager
- [ ] AgentCore Gateway IAM role follows least privilege
- [ ] Tool definitions match OpenAPI spec exactly
- [ ] AgentCore Gateway deployed and active
- [ ] Tool invocation tests pass (create_ticket, get_ticket_status)
- [ ] NO production ITSM endpoints configured
- [ ] All resources in us-east-1
- [ ] Cost tracking shows spending within budget

**Approval Required From:** Project Stakeholder / Technical Lead

**Next Phase:** Phase 3 - Amazon Connect Setup

---

## Phase 3: Amazon Connect Setup

**Objective:** Configure Amazon Connect instance, AI Agent, and contact flow for voice-first L1 support experience.

### Task 3.1: Amazon Connect Instance Creation

**Goal:** Create Amazon Connect instance for PoC voice interactions.

**Inputs:**
- Requirements.md (Requirement 6, Requirement 8)

**Outputs:**
- Connect instance: `poc-ai-l1-support` in us-east-1
- Connect instance alias and OIDC discovery URL
- `deployment/connect-instance-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 6.1: Voice-first interaction using Connect AI Agents
- Maps to Requirement 8.1-8.3: All resources in us-east-1
- Instance name: `poc-ai-l1-support`
- Region: us-east-1
- Identity management: Store users in Amazon Connect (minimal setup)
- Data storage: Default settings (call recordings disabled to save costs)
- Telephony: Claim the cheapest available DID; keep test calls minimal (2-3 short calls); release number immediately after tests

**Verification:**
- AWS CLI or Console to verify Connect instance is active
- Note Connect instance alias (e.g., `poc-ai-l1-support`)
- Note OIDC discovery URL: `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
- Test phone number by calling it (should reach default flow)

**Rollback/Cleanup:**
- Release phone number
- Delete Connect instance (via Console or CLI)

---

### Task 3.2: Connect AI Agent IAM Role Creation

**Goal:** Create IAM role for Connect AI Agent with permissions to invoke AgentCore Gateway.

**Inputs:**
- docs/iam-policies.md
- Requirements.md (Requirement 14)

**Outputs:**
- IAM role: `poc-connect-ai-agent-role`
- IAM policy: `poc-connect-ai-agent-policy`
- `deployment/connect-ai-agent-iam-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 14.3: Connect AI Agent IAM limited to invoking AgentCore Gateway
- Maps to Requirement 14.4: NO wildcard (*) permissions
- Policy allows: bedrock:InvokeAgent on poc-itsm-agentcore-gateway
- Policy allows: logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents
- Trust policy allows connect.amazonaws.com to assume role

**Verification:**
- AWS CLI command to get role policy and verify permissions
- Confirm NO wildcard permissions
- Verify trust relationship is correct

**Rollback/Cleanup:**
- Detach policy from role
- Delete IAM policy
- Delete IAM role

---

### Task 3.3: AgentCore Gateway OIDC Configuration Update

**Goal:** Update AgentCore Gateway inbound authentication with Connect OIDC discovery URL.

**Inputs:**
- Connect instance OIDC URL from Task 3.1
- AgentCore Gateway: `poc-itsm-agentcore-gateway`
- Requirements.md (Requirement 5)

**Outputs:**
- Updated AgentCore Gateway configuration
- `deployment/agentcore-oidc-update-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 5.2: Inbound auth using Connect OIDC discovery URL
- OIDC discovery URL configured: `https://<CONNECT_ALIAS>.my.connect.aws/.well-known/openid-configuration`
- AgentCore Gateway accepts authenticated requests from Connect AI Agent

**Verification:**
- AWS CLI or Console to verify OIDC configuration
- Test authentication flow (if possible via test harness)

**Rollback/Cleanup:**
- Revert OIDC configuration to placeholder or remove

---

### Task 3.4: Connect AI Agent Creation

**Goal:** Create Amazon Connect AI Agent with instructions and AgentCore Gateway integration.

**Inputs:**
- docs/connect-flow-design.md
- AgentCore Gateway: `poc-itsm-agentcore-gateway`
- IAM role: `poc-connect-ai-agent-role`
- Requirements.md (Requirement 6, Requirement 7)

**Outputs:**
- Connect AI Agent: `poc-l1-support-agent`
- AI Agent instructions document
- `deployment/connect-ai-agent-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 6.2-6.6: Voice-first interaction with confirmation
- Maps to Requirement 7.1-7.8: Ticket operations via tools
- Agent name: `poc-l1-support-agent`
- Agent instructions:
  - Greet caller: "Hello, I'm your AI IT support assistant. How can I help you today?"
  - Collect issue description and caller identification (session ID or hashed phone)
  - Avoid asking for passwords, MFA codes, or device serials
  - Summarize issue and ask for confirmation before creating ticket
  - Provide ticket ID after creation
  - Offer escalation option for complex issues
  - Keep responses short and spoken-friendly
- AgentCore Gateway integration: poc-itsm-agentcore-gateway
- IAM role: `poc-connect-ai-agent-role`
- Tools available: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets

**Verification:**
- AWS CLI or Console to verify AI Agent is active
- Review AI Agent instructions for compliance with requirements
- Verify AgentCore Gateway is linked
- Verify NO sensitive data collection in instructions

**Rollback/Cleanup:**
- Delete Connect AI Agent

---

### Task 3.5: Connect Contact Flow Creation

**Goal:** Create Amazon Connect contact flow with AI Agent integration and escalation path.

**Inputs:**
- docs/connect-flow-design.md
- Connect AI Agent: `poc-l1-support-agent`
- Requirements.md (Requirement 6)

**Outputs:**
- Contact flow: `poc-l1-support-flow`
- Contact flow JSON export
- `deployment/connect-flow-log.md` - Deployment record

**Acceptance Criteria:**
- Maps to Requirement 6.1-6.8: Voice-first with escalation path
- Flow name: `poc-l1-support-flow`
- Flow steps:
  1. Play greeting prompt (optional)
  2. Invoke AI Agent: `poc-l1-support-agent`
  3. Handle AI Agent response
  4. Escalation path: Transfer to queue or play escalation message
  5. End call
- Escalation trigger: Caller says "speak to a human" or "escalate" or AI Agent determines issue is complex
- Escalation action: Transfer to basic queue OR play message "I'll transfer you to a human agent" (for PoC, can be simulated)

**Verification:**
- Export contact flow JSON and review structure
- Verify AI Agent is invoked in flow
- Verify escalation path exists
- Smoke test checklist (manual):
  - [ ] Call phone number and hear greeting
  - [ ] AI Agent responds to "I need help with my laptop"
  - [ ] Escalation path works when saying "speak to a human"

**Rollback/Cleanup:**
- Delete contact flow

---

### Task 3.6: Phone Number Assignment to Flow

**Goal:** Assign claimed phone number to the contact flow for testing.

**Inputs:**
- Phone number from Task 3.1
- Contact flow: `poc-l1-support-flow`

**Outputs:**
- Phone number assigned to flow
- `deployment/phone-number-assignment-log.md` - Deployment record

**Acceptance Criteria:**
- Phone number routes to `poc-l1-support-flow`
- Inbound calls trigger AI Agent interaction

**Verification:**
- Call phone number and verify flow executes
- Verify AI Agent responds

**Rollback/Cleanup:**
- Unassign phone number from flow

---

### 🛑 APPROVAL GATE 4: Phase 3 Connect Setup Validation

**STOP HERE - DO NOT PROCEED WITHOUT EXPLICIT APPROVAL**

**Review Checklist:**
- [ ] Connect instance created in us-east-1
- [ ] Connect AI Agent IAM role follows least privilege
- [ ] AgentCore Gateway OIDC configuration updated
- [ ] Connect AI Agent created with proper instructions
- [ ] AI Agent instructions avoid sensitive data collection
- [ ] Contact flow created with escalation path
- [ ] Phone number assigned to flow
- [ ] Smoke test: Call phone number and interact with AI Agent
- [ ] Cost tracking shows spending within budget

**Approval Required From:** Project Stakeholder / Technical Lead

**Next Phase:** Phase 4 - End-to-End Testing

---

## Phase 4: End-to-End Testing

**Objective:** Validate complete voice interaction flow and all ticket operations.

### Task 4.1: E2E Test Script Creation

**Goal:** Create comprehensive end-to-end test script with test cases and expected results.

**Inputs:**
- docs/test-strategy.md
- Requirements.md (Requirement 16)

**Outputs:**
- `tests/e2e-test-script.md` - End-to-end test scenarios and checklist

**Acceptance Criteria:**
- Maps to Requirement 16.1-16.8: E2E test validating complete flow
- Test scenarios:
  1. Create ticket via voice interaction
  2. Query ticket status via voice
  3. Add comment to ticket via voice
  4. List recent tickets via voice
  5. Escalation path via voice
- Each scenario includes:
  - Test steps (what to say to AI Agent)
  - Expected AI Agent responses
  - Expected backend state (DynamoDB records)
  - Pass/fail criteria

**Verification:**
- Manual review of test script completeness
- Verify all user stories are covered

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 4.2: E2E Test Execution - Create Ticket

**Goal:** Execute end-to-end test for ticket creation via voice interaction.

**Inputs:**
- tests/e2e-test-script.md
- Phone number for Connect instance

**Outputs:**
- `tests/e2e-test-results.md` - Test execution results

**Acceptance Criteria:**
- Maps to Requirement 16.2-16.3: Validate ticket creation and ticket ID provision
- Test steps:
  1. Call phone number
  2. Say: "I need help with my laptop. It won't turn on."
  3. Caller identity is derived from session identifier or hashed phone number; if AI Agent asks for identification, provide a non-sensitive PoC alias (e.g., "poc-user-01")
  4. Confirm ticket creation when AI Agent asks
  5. Note ticket ID provided by AI Agent
- Expected results:
  - AI Agent summarizes issue and asks for confirmation
  - AI Agent provides ticket ID (e.g., "Your ticket number is 12345")
  - DynamoDB contains ticket with correct issue_description and caller_id
- Pass criteria: Ticket created in DynamoDB with correct data, ticket ID provided to caller

**Verification:**
- Query DynamoDB for created ticket
- Verify ticket_id, caller_id, issue_description, status, created_at fields
- Confirm ticket ID matches what AI Agent provided

**Rollback/Cleanup:**
- N/A (test data can remain in PoC table)

---

### Task 4.3: E2E Test Execution - Query Ticket Status

**Goal:** Execute end-to-end test for querying ticket status via voice interaction.

**Inputs:**
- tests/e2e-test-script.md
- Ticket ID from Task 4.2

**Outputs:**
- Updated `tests/e2e-test-results.md`

**Acceptance Criteria:**
- Maps to Requirement 16.4: Validate ticket status query
- Test steps:
  1. Call phone number
  2. Say: "I want to check the status of my ticket"
  3. Provide ticket ID when asked (e.g., "Ticket 12345")
- Expected results:
  - AI Agent retrieves ticket status from DynamoDB
  - AI Agent provides status information (e.g., "Your ticket 12345 is currently open")
- Pass criteria: AI Agent correctly retrieves and reports ticket status

**Verification:**
- Verify AI Agent response matches DynamoDB ticket status
- Confirm ticket ID is correctly parsed and used

**Rollback/Cleanup:**
- N/A (test data can remain in PoC table)

---

### Task 4.4: E2E Test Execution - Add Comment

**Goal:** Execute end-to-end test for adding comment to ticket via voice interaction.

**Inputs:**
- tests/e2e-test-script.md
- Ticket ID from Task 4.2

**Outputs:**
- Updated `tests/e2e-test-results.md`

**Acceptance Criteria:**
- Maps to Requirement 16.5: Validate adding comments to ticket
- Test steps:
  1. Call phone number
  2. Say: "I want to add information to my ticket"
  3. Provide ticket ID when asked
  4. Say: "I tried restarting the laptop but it still doesn't work"
- Expected results:
  - AI Agent adds comment to ticket in DynamoDB
  - AI Agent confirms comment was added (e.g., "I've added your comment to ticket 12345")
- Pass criteria: Comment appears in DynamoDB ticket's comments array

**Verification:**
- Query DynamoDB for ticket
- Verify comments array contains new comment
- Verify updated_at timestamp is updated

**Rollback/Cleanup:**
- N/A (test data can remain in PoC table)

---

### Task 4.5: E2E Test Execution - List Recent Tickets

**Goal:** Execute end-to-end test for listing recent tickets via voice interaction.

**Inputs:**
- tests/e2e-test-script.md
- Caller ID from Task 4.2

**Outputs:**
- Updated `tests/e2e-test-results.md`

**Acceptance Criteria:**
- Maps to Requirement 16.6: Validate listing recent tickets
- Test steps:
  1. Call phone number
  2. Say: "Show me my recent tickets"
  3. Caller identity is derived from session identifier or hashed phone number; if AI Agent asks for identification, provide a non-sensitive PoC alias (e.g., "poc-user-01")
- Expected results:
  - AI Agent queries DynamoDB GSI by caller_id
  - AI Agent lists recent tickets (e.g., "You have 1 ticket: Ticket 12345 about laptop issue")
- Pass criteria: AI Agent correctly retrieves and reports caller's tickets

**Verification:**
- Verify AI Agent response includes ticket(s) created in previous tests
- Confirm GSI query is working correctly

**Rollback/Cleanup:**
- N/A (test data can remain in PoC table)

---

### Task 4.6: E2E Test Execution - Escalation Path

**Goal:** Execute end-to-end test for escalation to human agent via voice interaction.

**Inputs:**
- tests/e2e-test-script.md

**Outputs:**
- Updated `tests/e2e-test-results.md`

**Acceptance Criteria:**
- Maps to Requirement 16.7: Validate escalation path
- Test steps:
  1. Call phone number
  2. Say: "I need to speak to a human agent"
  3. OR describe a complex issue that AI Agent cannot handle
- Expected results:
  - AI Agent recognizes escalation request
  - Contact flow transfers to human queue OR plays escalation message
  - For PoC: Acceptable to play message "I'll transfer you to a human agent" without actual transfer
- Pass criteria: Escalation path is triggered and caller is informed

**Verification:**
- Verify escalation trigger works
- Confirm contact flow handles escalation correctly

**Rollback/Cleanup:**
- N/A (test data can remain in PoC table)

---

### Task 4.7: E2E Test Results Documentation

**Goal:** Compile all E2E test results and provide pass/fail summary.

**Inputs:**
- tests/e2e-test-results.md (from Tasks 4.2-4.6)
- Requirements.md (Requirement 16)

**Outputs:**
- Final `tests/e2e-test-results.md` with pass/fail summary

**Acceptance Criteria:**
- Maps to Requirement 16.8: Report pass/fail status for each scenario
- Summary includes:
  - Test scenario name
  - Pass/fail status
  - Notes on any issues or deviations
  - Overall PoC validation status
- All test scenarios must pass for PoC to be considered successful

**Verification:**
- Manual review of test results
- Confirm all acceptance criteria are met

**Rollback/Cleanup:**
- N/A (documentation only)

---

### 🛑 APPROVAL GATE 5: Phase 4 E2E Testing Validation

**STOP HERE - DO NOT PROCEED WITHOUT EXPLICIT APPROVAL**

**Review Checklist:**
- [ ] E2E test script created and reviewed
- [ ] Create ticket test passed
- [ ] Query ticket status test passed
- [ ] Add comment test passed
- [ ] List recent tickets test passed
- [ ] Escalation path test passed
- [ ] All test results documented
- [ ] PoC demonstrates complete voice-first L1 support flow
- [ ] NO production ITSM integration present
- [ ] Cost tracking shows spending within $10 budget (manual stop at $8 alert)

**Approval Required From:** Project Stakeholder / Technical Lead

**Next Phase:** Phase 5 - Cleanup & Teardown

---

## Phase 5: Cleanup & Teardown

**Objective:** Remove all PoC resources to prevent ongoing charges and document final costs.

### Task 5.1: Cost Analysis and Documentation

**Goal:** Document actual AWS spending during PoC and verify budget compliance.

**Inputs:**
- AWS Cost Explorer or Billing Dashboard
- Requirements.md (Requirement 4, Requirement 17)

**Outputs:**
- `docs/cost-analysis.md` - Final cost breakdown and analysis

**Acceptance Criteria:**
- Maps to Requirement 4.1: Total spending within $10 USD budget (with manual stop at $8 USD alert)
- Maps to Requirement 17.6: Cost estimates and actual spending
- Document includes:
  - Cost breakdown by service (Connect, Bedrock, Lambda, API Gateway, DynamoDB, S3, etc.)
  - Total actual spending
  - Comparison to $10 budget (with $8 alert threshold)
  - Any budget alerts triggered
  - Recommendations for cost optimization if PoC were to continue

**Verification:**
- Review AWS billing dashboard
- Confirm total spending is within budget
- Verify no unexpected charges

**Rollback/Cleanup:**
- N/A (documentation only)

---

### Task 5.2: Amazon Connect Resource Cleanup

**Goal:** Remove Amazon Connect instance, AI Agent, contact flow, and phone number.

**Inputs:**
- docs/cleanup-procedure.md
- Connect instance: `poc-ai-l1-support`

**Outputs:**
- `deployment/cleanup-log.md` - Resource deletion record

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Delete or release phone number
- Delete contact flow: `poc-l1-support-flow`
- Delete AI Agent: `poc-l1-support-agent`
- Delete Connect instance: `poc-ai-l1-support`
- Verify all Connect resources are removed

**Verification:**
- AWS CLI or Console to verify Connect instance is deleted
- Verify phone number is released
- Confirm no ongoing Connect charges

**Rollback/Cleanup:**
- N/A (this is the cleanup task)

---

### Task 5.3: AgentCore Gateway Cleanup

**Goal:** Remove Bedrock AgentCore Gateway and associated IAM resources.

**Inputs:**
- docs/cleanup-procedure.md
- AgentCore Gateway: `poc-itsm-agentcore-gateway`

**Outputs:**
- Updated `deployment/cleanup-log.md`

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Delete AgentCore Gateway: `poc-itsm-agentcore-gateway`
- Delete IAM role: `poc-agentcore-gateway-role`
- Delete IAM policy: `poc-agentcore-gateway-policy`
- Delete IAM role: `poc-connect-ai-agent-role`
- Delete IAM policy: `poc-connect-ai-agent-policy`
- Verify all AgentCore and Connect IAM resources are removed

**Verification:**
- Delete AgentCore Gateway via AWS Console (Bedrock AgentCore) or the officially supported CLI/API for AgentCore Gateway (to be confirmed during implementation)
- AWS CLI to verify IAM roles and policies are deleted
- Confirm no ongoing Bedrock charges

**Rollback/Cleanup:**
- N/A (this is the cleanup task)

---

### Task 5.4: Mock ITSM Backend Cleanup

**Goal:** Remove API Gateway, Lambda functions, DynamoDB table, and associated IAM resources.

**Inputs:**
- docs/cleanup-procedure.md
- API Gateway or Function URL
- Lambda function: `poc-itsm-api-handler`
- DynamoDB table: `poc-itsm-tickets`

**Outputs:**
- Updated `deployment/cleanup-log.md`

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Delete API Gateway: `poc-itsm-api` OR Lambda Function URL
- Delete API key (if created)
- Delete Lambda function: `poc-itsm-api-handler`
- Delete CloudWatch log group: `/aws/lambda/poc-itsm-api-handler`
- Delete DynamoDB table: `poc-itsm-tickets` (including GSI)
- Delete IAM role: `poc-itsm-lambda-role`
- Delete IAM policy: `poc-itsm-lambda-policy`
- Verify all backend resources are removed

**Verification:**
- AWS CLI to verify API Gateway is deleted
- AWS CLI to verify Lambda function is deleted
- AWS CLI to verify DynamoDB table is deleted
- AWS CLI to verify IAM roles and policies are deleted
- Confirm no ongoing Lambda, API Gateway, or DynamoDB charges

**Rollback/Cleanup:**
- N/A (this is the cleanup task)

---

### Task 5.5: S3 and Secrets Manager Cleanup

**Goal:** Remove S3 bucket and Secrets Manager secret.

**Inputs:**
- docs/cleanup-procedure.md
- S3 bucket: `poc-itsm-openapi-specs-<account-id>`
- Secret: `poc-itsm-api-key`

**Outputs:**
- Updated `deployment/cleanup-log.md`

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Delete all objects in S3 bucket: `poc-itsm-openapi-specs-<account-id>`
- Delete S3 bucket: `poc-itsm-openapi-specs-<account-id>`
- Delete secret: `poc-itsm-api-key` (force delete without recovery)
- Verify all S3 and Secrets Manager resources are removed

**Verification:**
- AWS CLI to verify S3 bucket is deleted
- AWS CLI to verify secret is deleted
- Confirm no ongoing S3 or Secrets Manager charges

**Rollback/Cleanup:**
- N/A (this is the cleanup task)

---

### Task 5.6: CloudWatch Logs Cleanup

**Goal:** Remove CloudWatch log groups to prevent ongoing storage charges.

**Inputs:**
- docs/cleanup-procedure.md

**Outputs:**
- Updated `deployment/cleanup-log.md`

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Delete CloudWatch log groups:
  - `/aws/lambda/poc-itsm-api-handler`
  - `/aws/connect/poc-ai-l1-support` (if exists)
  - Any AgentCore Gateway log groups
- Verify all log groups are removed

**Verification:**
- AWS CLI to list and verify log groups are deleted
- Confirm no ongoing CloudWatch Logs charges

**Rollback/Cleanup:**
- N/A (this is the cleanup task)

---

### Task 5.7: AWS Budgets Cleanup

**Goal:** Remove AWS Budget alert to clean up billing configuration.

**Inputs:**
- docs/cleanup-procedure.md
- Budget name from Task 0.1

**Outputs:**
- Updated `deployment/cleanup-log.md`

**Acceptance Criteria:**
- Maps to Requirement 15.1-15.5: Documented cleanup with verification
- Delete AWS Budget: `poc-ai-l1-support-budget` (or configured name)
- Verify budget is removed

**Verification:**
- AWS CLI or Console to verify budget is deleted
- Confirm no budget alerts remain

**Rollback/Cleanup:**
- N/A (this is the cleanup task)

---

### Task 5.8: Final Verification and Documentation

**Goal:** Verify all resources are deleted and document final PoC status.

**Inputs:**
- deployment/cleanup-log.md
- docs/cost-analysis.md

**Outputs:**
- `docs/poc-final-report.md` - Final PoC summary and lessons learned

**Acceptance Criteria:**
- Maps to Requirement 15.3-15.5: Verify deletion and no ongoing charges
- Final report includes:
  - PoC objectives and outcomes
  - All test results summary
  - Final cost analysis
  - Lessons learned
  - Recommendations for production implementation (if applicable)
  - Confirmation that all resources are deleted
  - Confirmation that no ongoing charges exist
- Verify AWS billing shows no active resources for PoC

**Verification:**
- Review AWS Console for any remaining PoC resources
- Check AWS billing for next billing cycle to confirm no charges
- Manual review of final report

**Rollback/Cleanup:**
- N/A (this is the final task)

---

### 🛑 APPROVAL GATE 6: Phase 5 Cleanup Validation

**STOP HERE - FINAL REVIEW**

**Review Checklist:**
- [ ] Cost analysis documented and within $10 budget (manual stop at $8 alert)
- [ ] All Amazon Connect resources deleted
- [ ] All AgentCore Gateway resources deleted
- [ ] All Mock ITSM backend resources deleted (API Gateway, Lambda, DynamoDB)
- [ ] All S3 and Secrets Manager resources deleted
- [ ] All CloudWatch log groups deleted
- [ ] AWS Budget deleted
- [ ] Final verification confirms no ongoing charges
- [ ] Final PoC report completed
- [ ] All documentation archived for future reference

**Approval Required From:** Project Stakeholder / Technical Lead

**PoC Status:** COMPLETE

---

## Appendix A: Service Whitelist Compliance Matrix

| AWS Service | Usage | Requirement | Compliance |
|------------|-------|-------------|------------|
| Amazon Connect | Voice interaction, AI Agent hosting | Req 6, 7 | ✅ Whitelisted |
| Amazon Connect AI Agents | AI-driven voice support | Req 6 | ✅ Whitelisted |
| Amazon Q in Connect | Optional knowledge base (not implemented in minimal PoC) | Req 18 | ✅ Whitelisted (Optional) |
| Amazon Bedrock AgentCore Gateway | MCP server for tool exposure | Req 5 | ✅ Whitelisted |
| AWS Lambda | Mock ITSM API handlers | Req 12 | ✅ Whitelisted |
| Amazon API Gateway | REST API exposure (or Function URL) | Req 2 | ✅ Whitelisted |
| Amazon DynamoDB | Mock ticket storage | Req 13 | ✅ Whitelisted |
| Amazon S3 | OpenAPI spec storage | Req 11 | ✅ Whitelisted |
| AWS IAM | Least-privilege roles and policies | Req 14 | ✅ Whitelisted |
| Amazon CloudWatch | Default logging | Req 12, 19 | ✅ Whitelisted |
| AWS Budgets | Cost alerts | Req 4 | ✅ Whitelisted |
| AWS Secrets Manager | API key storage | Req 5 | ✅ Whitelisted |

**Forbidden Services (NOT USED):**
- ManageEngine ServiceDesk Plus (production ITSM) ❌
- VPC, NAT Gateway, Load Balancers ❌
- EC2, EKS, ECS ❌
- OpenSearch, RDS, Aurora, Redshift ❌
- SageMaker ❌
- Step Functions, EventBridge, Kinesis ❌
- Any paid third-party services ❌

---

## Appendix B: Requirements Traceability Matrix

| Requirement ID | Requirement Name | Tasks Addressing |
|---------------|------------------|------------------|
| Req 1 | Production Safety Isolation | 0.2, 0.6, 1.1, All phases |
| Req 2 | Mock ITSM Backend API | 0.2, 1.3, 1.4, 1.5 |
| Req 3 | AWS Service Whitelist Compliance | All tasks (verified in Appendix A) |
| Req 4 | Cost Guardrails | 0.1, 5.1 |
| Req 5 | AgentCore Gateway Configuration | 0.6, 2.1, 2.2, 2.3, 2.4, 3.3 |
| Req 6 | Voice Interaction Experience | 0.7, 3.1, 3.4, 3.5 |
| Req 7 | Ticket Creation and Management | 0.7, 3.4, 4.2, 4.3, 4.4, 4.5 |
| Req 8 | Regional Deployment Constraint | All deployment tasks (us-east-1) |
| Req 9 | Test-Driven Development | 1.3, 1.5, 4.1-4.7 |
| Req 10 | Incremental Task-by-Task Delivery | All phases (approval gates) |
| Req 10A | Deployment Approval Gate | Approval Gate 1 (before Phase 1) |
| Req 11 | OpenAPI Specification | 0.2, 1.6 |
| Req 12 | Minimal Lambda Implementation | 0.4, 1.3, 1.4 |
| Req 13 | DynamoDB Data Model | 0.3, 1.1 |
| Req 14 | Security and IAM Least Privilege | 0.4, 1.2, 2.2, 3.2 |
| Req 15 | Cleanup and Teardown | 0.10, 5.1-5.8 |
| Req 16 | End-to-End Testing | 0.8, 4.1-4.7 |
| Req 17 | Documentation and Deliverables | 0.9, 5.8 |
| Req 18 | Amazon Q in Connect (Optional) | Not implemented in minimal PoC |
| Req 19 | Error Handling and Resilience | 1.3, 1.5 |
| Req 20 | Confirmation and Approval Gates | Approval Gates 1-6 |

---

## Appendix C: Risk Mitigation Strategies

### Risk 1: Budget Overrun
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:**
- AWS Budget alert at $8 USD (80% threshold) - note that AWS Budgets provides alerts only, not spending enforcement
- Manual Stop Rule: If spending reaches $8 USD, pause work immediately and execute cleanup
- Use on-demand billing for DynamoDB (pay per request)
- Minimal Lambda memory allocation (256 MB)
- Default CloudWatch log retention (no extended retention)
- Claim cheapest available DID for Connect; keep test calls minimal (2-3 short calls); release number immediately after tests
- Monitor costs daily during PoC
- Immediate cleanup if approaching budget limit

### Risk 2: Production System Contamination
**Likelihood:** Low  
**Impact:** Critical  
**Mitigation:**
- NO production ITSM credentials stored anywhere
- Mock ITSM backend with clear "poc-" naming prefix
- Code review to verify NO production endpoints
- Separate AWS account for PoC (recommended)
- Documentation review at each approval gate

### Risk 3: AgentCore Gateway Misconfiguration
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:**
- Static tool definitions (NO dynamic generation)
- Tool definitions validated against OpenAPI spec
- OIDC authentication properly configured
- Test tool invocations before Connect integration
- Approval gate before Connect setup

### Risk 4: Connect AI Agent Collects Sensitive Data
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:**
- AI Agent instructions explicitly avoid passwords, MFA codes, device serials
- Use session ID or hashed phone number for caller identification
- NO real employee IDs or HR identifiers
- Review AI Agent instructions at approval gate
- Test interactions to verify NO sensitive data requests

### Risk 5: Incomplete Cleanup Leading to Ongoing Charges
**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Comprehensive cleanup procedure (Task 5.1-5.8)
- Verification steps for each resource deletion
- Final billing check after cleanup
- Automated cleanup script (optional)
- Documentation of all created resources

### Risk 6: Regional Constraint Violation
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- All AWS CLI commands include `--region us-east-1`
- Verification steps check resource region
- Console access defaults to us-east-1
- Documentation emphasizes region constraint

---

## Appendix D: Estimated Timeline

| Phase | Tasks | Estimated Duration | Dependencies |
|-------|-------|-------------------|--------------|
| Phase 0: Planning & Documentation | 0.1 - 0.10 | 2-3 days | Requirements.md |
| Approval Gate 1 | Review | 1 day | Phase 0 complete |
| Phase 1: Mock ITSM Backend | 1.1 - 1.6 | 2-3 days | Approval Gate 1 |
| Approval Gate 2 | Review | 0.5 days | Phase 1 complete |
| Phase 2: AgentCore Gateway | 2.1 - 2.4 | 1-2 days | Approval Gate 2 |
| Approval Gate 3 | Review | 0.5 days | Phase 2 complete |
| Phase 3: Amazon Connect Setup | 3.1 - 3.6 | 2-3 days | Approval Gate 3 |
| Approval Gate 4 | Review | 0.5 days | Phase 3 complete |
| Phase 4: End-to-End Testing | 4.1 - 4.7 | 1-2 days | Approval Gate 4 |
| Approval Gate 5 | Review | 0.5 days | Phase 4 complete |
| Phase 5: Cleanup & Teardown | 5.1 - 5.8 | 1 day | Approval Gate 5 |
| Approval Gate 6 | Final Review | 0.5 days | Phase 5 complete |
| **Total Estimated Duration** | | **11-17 days** | |

**Note:** Timeline assumes sequential task execution with approval gates. Actual duration may vary based on:
- AWS service provisioning time
- Testing and debugging requirements
- Approval gate review duration
- Team availability

---

## Appendix E: Success Criteria Summary

The PoC will be considered successful if ALL of the following criteria are met:

### Functional Success Criteria
✅ Mock ITSM API operational with all four endpoints (create, get, comment, list)  
✅ AgentCore Gateway exposes exactly four tools to AI Agent  
✅ Amazon Connect AI Agent handles voice interactions naturally  
✅ Caller can create ticket via voice and receive ticket ID  
✅ Caller can query ticket status via voice  
✅ Caller can add comments to ticket via voice  
✅ Caller can list recent tickets via voice  
✅ Escalation path works correctly  

### Non-Functional Success Criteria
✅ NO production ITSM integration present  
✅ Total cost within $10 USD budget (with manual stop at $8 USD alert threshold)  
✅ All resources deployed in us-east-1 only  
✅ All IAM policies follow least privilege (no wildcards)  
✅ NO sensitive data collected (passwords, MFA codes, device serials)  
✅ All unit tests pass  
✅ All API contract tests pass  
✅ All E2E tests pass  
✅ Complete cleanup with no ongoing charges  

### Documentation Success Criteria
✅ OpenAPI specification validated  
✅ Architecture documentation complete  
✅ Test strategy and results documented  
✅ Cost analysis documented  
✅ Cleanup procedure documented and executed  
✅ Final PoC report complete  

---

## Document Control

**Document Version:** 1.0  
**Last Updated:** 2026-02-09  
**Author:** AI L1 Support PoC Team  
**Approvers:** Project Stakeholder, Technical Lead  

**Change History:**
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-09 | Initial Plan of Record | PoC Team |

---

**END OF PLAN OF RECORD**

🛑 **STOP - AWAITING APPROVAL TO PROCEED WITH PHASE 1 IMPLEMENTATION**
