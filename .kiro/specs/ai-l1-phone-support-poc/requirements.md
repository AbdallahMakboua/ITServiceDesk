# Requirements Document

## Introduction

This document specifies the requirements for the DAS Holding AI IT L1 Voice Service Desk Proof of Concept (PoC). The system provides an AI-driven phone support experience using Amazon Connect with Bedrock AgentCore Gateway (MCP) to handle Level 1 IT support requests. This is a non-production, cost-controlled PoC that must NOT integrate with any production ITSM systems.

## Glossary

- **AI_Agent**: The Amazon Connect AI Agent powered by Bedrock that handles voice interactions
- **AgentCore_Gateway**: The Bedrock AgentCore Gateway (MCP server) that exposes tools to the AI Agent
- **Mock_ITSM_API**: The sandbox REST API that simulates ITSM ticket operations without touching production systems
- **Connect_Flow**: The Amazon Connect contact flow that orchestrates the voice interaction
- **Caller**: The end user calling the support line
- **Ticket**: A support request record stored in the mock ITSM backend
- **PoC_Session**: The complete demonstration period with a $10 USD budget cap
- **Production_System**: Any real ManageEngine ServiceDesk Plus environment or production ITSM system
- **Escalation**: The process of transferring a call to a human agent

## Requirements

### Requirement 1: Production Safety Isolation

**User Story:** As a system administrator, I want absolute isolation from production ITSM systems, so that the PoC cannot accidentally impact real support operations.

#### Acceptance Criteria

1. THE System SHALL NOT make any API calls to ManageEngine ServiceDesk Plus production environments
2. THE System SHALL NOT store or use production ITSM credentials
3. THE System SHALL NOT create webhooks or integrations pointing to production systems
4. WHEN the PoC is deployed, THE System SHALL use only a mock ITSM backend with sandbox data
5. THE System SHALL store all PoC tickets in DynamoDB tables clearly labeled as non-production

### Requirement 2: Mock ITSM Backend API

**User Story:** As a developer, I want a minimal REST API that simulates ITSM operations, so that the AI Agent can demonstrate ticket management without production risk.

#### Acceptance Criteria

1. THE Mock_ITSM_API SHALL expose an OpenAPI specification document
2. THE Mock_ITSM_API SHALL implement a POST /tickets endpoint for ticket creation
3. THE Mock_ITSM_API SHALL implement a GET /tickets/{id} endpoint for ticket status retrieval
4. THE Mock_ITSM_API SHALL implement a POST /tickets/{id}/comments endpoint for adding comments
5. THE Mock_ITSM_API SHALL implement a GET /tickets endpoint with caller query parameter for listing recent tickets
6. THE Mock_ITSM_API SHALL NOT expose delete or privileged administrative endpoints
7. THE Mock_ITSM_API SHALL store all data in DynamoDB tables
8. WHEN a ticket is created, THE Mock_ITSM_API SHALL return a unique ticket identifier
9. WHEN a ticket is queried, THE Mock_ITSM_API SHALL return current status and metadata
10. THE Mock_ITSM_API SHALL be deployed using either API Gateway REST + Lambda or Lambda Function URL

### Requirement 3: AWS Service Whitelist Compliance

**User Story:** As a cost controller, I want the PoC to use only approved AWS services, so that we avoid unexpected charges and complexity.

#### Acceptance Criteria

1. THE System SHALL use only services from the explicit whitelist: Amazon Connect, Connect AI Agents, Amazon Q in Connect, Bedrock AgentCore Gateway, Lambda, API Gateway, DynamoDB, S3, IAM, CloudWatch, and AWS Budgets
2. THE System SHALL NOT deploy VPC resources, NAT Gateways, or Load Balancers
3. THE System SHALL NOT use EC2, EKS, ECS, OpenSearch, RDS, Aurora, Redshift, or SageMaker
4. THE System SHALL NOT use Step Functions, EventBridge, or Kinesis
5. THE System SHALL NOT integrate paid third-party services
6. THE System SHALL NOT deploy persistent always-on compute resources beyond Lambda
7. WHEN a service outside the whitelist is needed, THE System SHALL halt and request explicit approval

### Requirement 4: Cost Guardrails

**User Story:** As a budget owner, I want strict cost controls on the PoC, so that total spending does not exceed $10 USD.

#### Acceptance Criteria

1. THE System SHALL operate within a $10 USD total budget for the PoC session
2. THE System SHALL prefer AWS Free Tier services where available
3. THE System SHALL use at most ONE customer-managed KMS key, and only if required
4. THE System SHALL use default CloudWatch log retention settings to avoid excessive storage costs
5. THE System SHALL NOT enable verbose logging or high-frequency metrics that increase costs
6. WHEN budget setup is performed, THE System SHALL configure AWS Budgets alerts at $8 USD (80% threshold)

### Requirement 5: AgentCore Gateway Configuration

**User Story:** As an integration architect, I want the AgentCore Gateway properly configured with secure authentication, so that the AI Agent can safely invoke mock ITSM tools.

#### Acceptance Criteria

1. THE System SHALL deploy exactly ONE AgentCore Gateway (MCP server)
2. THE AgentCore_Gateway SHALL configure inbound authentication using the Connect OIDC discovery URL format: https://<CONNECT_ALIAS>.my.connect.aws/.well-known/openid-configuration
3. THE AgentCore_Gateway SHALL configure outbound authentication to the Mock_ITSM_API using API key authentication
4. THE AgentCore_Gateway SHALL store API keys securely using AWS Secrets Manager or Lambda environment variables with encryption
5. THE AgentCore_Gateway SHALL expose exactly four tools: create_ticket, get_ticket_status, add_ticket_comment, and list_recent_tickets
6. THE AgentCore_Gateway SHALL NOT expose any administrative or delete operations
7. WHEN the AI_Agent invokes a tool, THE AgentCore_Gateway SHALL authenticate the request and forward it to the Mock_ITSM_API
8. The list of exposed tools SHALL be static and explicitly defined.
9. Dynamic tool generation or inferred tool exposure is strictly forbidden.
10. Tool definitions MUST match the OpenAPI specification exactly.

### Requirement 6: Voice Interaction Experience

**User Story:** As a caller, I want a natural voice-first support experience, so that I can report IT issues without navigating complex menus.

#### Acceptance Criteria

1. THE Connect_Flow SHALL provide a voice-first interaction using Amazon Connect AI Agents
2. WHEN a Caller connects, THE AI_Agent SHALL greet them and ask how it can help
3. THE AI_Agent SHALL provide short, spoken-friendly responses optimized for voice
4. THE AI_Agent SHALL avoid asking for sensitive information including passwords, MFA codes, or complete device serial numbers
5. WHEN the AI_Agent gathers sufficient information, THE AI_Agent SHALL summarize the issue and ask for confirmation before creating a ticket
6. WHEN a ticket is created, THE AI_Agent SHALL provide the ticket number to the Caller
7. THE Connect_Flow SHALL include an explicit "Escalate to human" path for complex issues
8. WHEN a Caller requests human assistance, THE Connect_Flow SHALL transfer to a human agent queue or provide escalation instructions

### Requirement 7: Ticket Creation and Management

**User Story:** As a caller, I want to create support tickets and check their status, so that I can track my IT issues.

#### Acceptance Criteria

1. WHEN a Caller describes an IT issue, THE AI_Agent SHALL collect necessary information including issue description and caller identification
2. WHEN sufficient information is collected, THE AI_Agent SHALL invoke the create_ticket tool via the AgentCore_Gateway
3. WHEN a ticket is successfully created, THE AI_Agent SHALL provide the ticket ID to the Caller
4. WHEN a Caller asks about ticket status, THE AI_Agent SHALL invoke the get_ticket_status tool with the ticket ID
5. WHEN a Caller provides additional information, THE AI_Agent SHALL invoke the add_ticket_comment tool to append the information
6. WHEN a Caller asks about their recent tickets, THE AI_Agent SHALL invoke the list_recent_tickets tool with the caller identifier
7. Caller identification SHALL use a session identifier or a hashed phone number.
8. The system SHALL NOT store or process real employee IDs, usernames, or HR identifiers.

### Requirement 8: Regional Deployment Constraint

**User Story:** As a deployment engineer, I want all resources deployed to a single region, so that the PoC remains simple and cost-effective.

#### Acceptance Criteria

1. THE System SHALL deploy all AWS resources exclusively in the us-east-1 region
2. THE System SHALL NOT create cross-region replications or multi-region architectures
3. WHEN resources are provisioned, THE System SHALL verify they are created in us-east-1

### Requirement 9: Test-Driven Development and Verification

**User Story:** As a quality engineer, I want each deliverable to include tests and acceptance criteria, so that we validate functionality before proceeding.

#### Acceptance Criteria

1. WHEN a Lambda function is implemented, THE System SHALL include unit tests using pytest or equivalent
2. WHEN the Mock_ITSM_API is deployed, THE System SHALL include API contract tests verifying each endpoint
3. WHEN the Connect_Flow is configured, THE System SHALL include a smoke test checklist for voice interaction
4. THE System SHALL NOT proceed to the next implementation task until the current task passes all tests
5. WHEN end-to-end testing is performed, THE System SHALL provide a test script that validates the complete flow

### Requirement 10: Incremental Task-by-Task Delivery

**User Story:** As a project manager, I want incremental delivery with validation at each step, so that we catch issues early and maintain quality.


#### Acceptance Criteria

1. THE System SHALL follow a plan-first approach with explicit task breakdown
2. THE System SHALL deliver components in this order: task plan, OpenAPI spec, Lambda + DynamoDB implementation, AgentCore configuration, Connect AI Agent setup, end-to-end testing, cleanup steps
3. WHEN a task is completed, THE System SHALL validate acceptance criteria before proceeding
4. WHEN a task fails validation, THE System SHALL halt and request corrections
5. THE System SHALL provide checkpoint reviews between major phases

### Requirement 10A: Deployment Approval Gate

**User Story:** As a project owner, I want explicit approval gates before any AWS resources are created, so that no deployments happen unintentionally.

#### Acceptance Criteria
1. During the design phase, the system SHALL produce documentation only (no deployment commands or executed actions).
2. No AWS resources (Connect, AgentCore Gateway, API, data stores) SHALL be created without explicit approval.
3. If any step would result in deployment, the process SHALL stop and request approval first.

### Requirement 11: OpenAPI Specification for Mock API

**User Story:** As an API consumer, I want a formal OpenAPI specification for the mock ITSM API, so that the AgentCore Gateway can correctly invoke endpoints.

#### Acceptance Criteria

1. THE System SHALL create an OpenAPI 3.0 specification document for the Mock_ITSM_API
2. THE OpenAPI specification SHALL define all four endpoints: POST /tickets, GET /tickets/{id}, POST /tickets/{id}/comments, GET /tickets
3. THE OpenAPI specification SHALL define request and response schemas for each endpoint
4. THE OpenAPI specification SHALL define authentication requirements (API key)
5. THE OpenAPI specification SHALL be stored in S3 for reference by the AgentCore_Gateway
6. WHEN the specification is created, THE System SHALL validate it using an OpenAPI validator

### Requirement 12: Minimal Lambda Implementation

**User Story:** As a backend developer, I want minimal Lambda functions that handle API requests efficiently, so that we keep costs low and complexity minimal.

#### Acceptance Criteria

1. THE System SHALL implement Lambda functions using Python 3.12 or Node.js 20.x runtime
2. THE Lambda functions SHALL handle only the four required API operations
3. THE Lambda functions SHALL use DynamoDB for data persistence
4. THE Lambda functions SHALL implement proper error handling and return appropriate HTTP status codes
5. THE Lambda functions SHALL log errors to CloudWatch using default settings
6. THE Lambda functions SHALL NOT include unnecessary dependencies or libraries
7. WHEN a Lambda function is invoked, THE System SHALL complete execution within 10 seconds

### Requirement 13: DynamoDB Data Model

**User Story:** As a data architect, I want a simple DynamoDB schema for storing mock tickets, so that we can persist PoC data without complex database setup.

#### Acceptance Criteria

1. THE System SHALL create a DynamoDB table named with a clear non-production prefix (e.g., "poc-itsm-tickets")
2. THE DynamoDB table SHALL use ticket_id as the partition key
3. THE DynamoDB table SHALL store ticket attributes including: ticket_id, caller_id, issue_description, status, created_at, updated_at, and comments array
4. THE DynamoDB table SHALL use on-demand billing mode to minimize costs
5. WHEN a ticket is created, THE System SHALL generate a unique ticket_id using UUID or timestamp-based identifier
6. THE DynamoDB table SHALL support querying by caller_id using a Global Secondary Index (GSI) for list_recent_tickets operation

### Requirement 14: Security and IAM Least Privilege

**User Story:** As a security engineer, I want least-privilege IAM policies, so that components have only the permissions they need.

#### Acceptance Criteria

1. THE Lambda functions SHALL have IAM roles with permissions limited to DynamoDB operations on the specific PoC table
2. THE AgentCore_Gateway SHALL have IAM permissions limited to invoking the Mock_ITSM_API
3. THE Connect AI Agent SHALL have IAM permissions limited to invoking the AgentCore_Gateway
4. THE System SHALL NOT use wildcard (*) permissions in IAM policies
5. THE System SHALL NOT grant administrative or privileged access to any component
6. WHEN IAM roles are created, THE System SHALL follow AWS least-privilege best practices

### Requirement 15: Cleanup and Teardown

**User Story:** As a cost controller, I want clear cleanup steps to remove all PoC resources, so that we don't incur ongoing charges after the demonstration.

#### Acceptance Criteria

1. THE System SHALL provide a documented cleanup procedure listing all created resources
2. THE cleanup procedure SHALL include steps to delete: DynamoDB tables, Lambda functions, API Gateway or Function URLs, AgentCore Gateway, Connect AI Agent, Connect Flow, S3 buckets, IAM roles, and CloudWatch log groups
3. THE cleanup procedure SHALL verify that all resources are deleted and no charges continue
4. WHEN cleanup is executed, THE System SHALL confirm deletion of each resource
5. THE System SHALL provide a script or command sequence to automate cleanup where possible

### Requirement 16: End-to-End Testing

**User Story:** As a QA engineer, I want an end-to-end test that validates the complete voice interaction flow, so that we confirm the PoC works as intended.

#### Acceptance Criteria

1. THE System SHALL provide an end-to-end test script or checklist
2. THE test SHALL validate that a caller can create a ticket through voice interaction
3. THE test SHALL validate that the AI_Agent provides the ticket ID after creation
4. THE test SHALL validate that a caller can query ticket status
5. THE test SHALL validate that a caller can add comments to a ticket
6. THE test SHALL validate that a caller can list their recent tickets
7. THE test SHALL validate that the escalation path works correctly
8. WHEN the end-to-end test completes, THE System SHALL report pass/fail status for each scenario

### Requirement 17: Documentation and Deliverables

**User Story:** As a stakeholder, I want clear documentation of the PoC architecture and usage, so that I can understand and demonstrate the system.

#### Acceptance Criteria

1. THE System SHALL provide architecture documentation describing component interactions
2. THE System SHALL provide setup instructions for deploying the PoC
3. THE System SHALL provide usage instructions for testing the voice interaction
4. THE System SHALL provide troubleshooting guidance for common issues
5. THE documentation SHALL include the OpenAPI specification, Lambda code, IAM policies, and Connect Flow configuration
6. THE documentation SHALL include cost estimates and actual spending during the PoC

### Requirement 18: Amazon Q in Connect (Optional)

**User Story:** As a support agent, I want optional Amazon Q in Connect integration for knowledge assistance, so that the AI can reference documentation if needed.

#### Acceptance Criteria

1. WHERE Amazon Q in Connect is enabled, THE System SHALL configure a knowledge base with sample IT support documentation
2. WHERE Amazon Q in Connect is enabled, THE AI_Agent SHALL be able to query the knowledge base for answers
3. WHERE Amazon Q in Connect is enabled, THE System SHALL store knowledge documents in S3
4. THE Amazon Q in Connect integration SHALL be optional and not required for core PoC functionality
5. WHERE Amazon Q in Connect is not enabled, THE AI_Agent SHALL still handle ticket operations correctly

### Requirement 19: Error Handling and Resilience

**User Story:** As a system operator, I want proper error handling throughout the system, so that failures are graceful and informative.

#### Acceptance Criteria

1. WHEN the Mock_ITSM_API encounters an error, THE System SHALL return appropriate HTTP status codes (400, 404, 500)
2. WHEN a Lambda function fails, THE System SHALL log the error to CloudWatch with sufficient detail for debugging
3. WHEN the AgentCore_Gateway cannot reach the Mock_ITSM_API, THE System SHALL return an error to the AI_Agent
4. WHEN the AI_Agent encounters a tool invocation error, THE AI_Agent SHALL inform the Caller that there is a technical issue and offer escalation
5. THE System SHALL NOT expose internal error details or stack traces to the Caller
6. WHEN DynamoDB operations fail, THE Lambda functions SHALL retry with exponential backoff up to 3 attempts

### Requirement 20: Confirmation and Approval Gates

**User Story:** As a project stakeholder, I want explicit approval gates before proceeding with implementation, so that we maintain control over the PoC scope.

#### Acceptance Criteria

1. WHEN the task plan is created, THE System SHALL request approval before implementation begins
2. WHEN the OpenAPI specification is created, THE System SHALL request review and approval
3. WHEN the Lambda and DynamoDB design is complete, THE System SHALL request approval before deployment
4. WHEN the AgentCore Gateway configuration is ready, THE System SHALL request approval before connecting to Connect
5. WHEN any component requires a service outside the whitelist, THE System SHALL halt and request explicit approval before proceeding
