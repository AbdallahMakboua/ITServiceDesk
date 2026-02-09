# API Gateway Design - Task 0.5

## Overview

This document defines the API Gateway configuration for exposing the Mock ITSM Lambda function as a REST API. The design evaluates two approaches: API Gateway REST API vs. Lambda Function URL, and provides the recommended configuration for the PoC.

---

## Architecture Decision: API Gateway REST API vs Lambda Function URL

### Option 1: API Gateway REST API

**Advantages:**
- Full REST API features (request validation, transformation)
- API key management built-in
- Usage plans and throttling
- Custom domain support
- Request/response mapping
- CORS configuration
- Better for production-like setup

**Disadvantages:**
- More complex setup
- Higher cost ($3.50 per million requests + $0.09/GB data transfer)
- Requires more configuration steps

**Cost Estimate (PoC):**
- 100 requests: $0.00035
- Data transfer: ~$0.001
- **Total: ~$0.001**

### Option 2: Lambda Function URL

**Advantages:**
- Simpler setup (one command)
- Lower cost (no API Gateway charges)
- Direct HTTPS endpoint
- Sufficient for PoC
- Faster cold starts (no API Gateway hop)

**Disadvantages:**
- No built-in API key management (must implement in Lambda)
- No request validation at gateway level
- No usage plans or throttling
- Limited monitoring compared to API Gateway

**Cost Estimate (PoC):**
- Lambda invocations only: < $0.01
- **Total: < $0.01**

### Recommendation: API Gateway REST API

**Decision:** Use **API Gateway REST API** for this PoC.

**Rationale:**
1. **AgentCore Gateway Integration:** API Gateway provides better integration patterns for AgentCore Gateway
2. **API Key Management:** Built-in API key authentication aligns with requirements
3. **Production-Like:** Better demonstrates real-world architecture
4. **Cost Difference Negligible:** < $0.01 difference for PoC scope
5. **OpenAPI Integration:** Can import OpenAPI spec directly

**Trade-off Accepted:** Slightly more complex setup is worth the benefits for demonstration purposes.

---

## API Gateway Configuration

### API Type
```
REST API (not HTTP API)
```

**Rationale:**
- Full feature set including API keys
- Better for demonstrating enterprise patterns
- OpenAPI import support

### API Name
```
poc-itsm-api
```

### Region
```
us-east-1
```

### Endpoint Type
```
Regional
```

**Rationale:**
- All resources in us-east-1
- No need for edge-optimized (CloudFront) for PoC
- Lower latency for regional access
- Cost-effective

---

## Resource and Method Configuration

### Resources and Methods

```
/tickets
  ├── POST (create_ticket)
  └── GET (list_recent_tickets)

/tickets/{id}
  ├── GET (get_ticket_status)
  └── /comments
      └── POST (add_ticket_comment)
```

### Method Details

#### POST /tickets (Create Ticket)

**Integration Type:** Lambda Function (proxy integration)  
**Lambda Function:** poc-itsm-api-handler  
**Authorization:** API Key Required  
**Request Validation:** None (handled in Lambda)

**Integration Request:**
```json
{
  "httpMethod": "POST",
  "path": "/tickets",
  "body": "$input.body"
}
```

#### GET /tickets (List Recent Tickets)

**Integration Type:** Lambda Function (proxy integration)  
**Lambda Function:** poc-itsm-api-handler  
**Authorization:** API Key Required  
**Query Parameters:** `caller` (required)

**Integration Request:**
```json
{
  "httpMethod": "GET",
  "path": "/tickets",
  "queryStringParameters": {
    "caller": "$input.params('caller')"
  }
}
```

#### GET /tickets/{id} (Get Ticket Status)

**Integration Type:** Lambda Function (proxy integration)  
**Lambda Function:** poc-itsm-api-handler  
**Authorization:** API Key Required  
**Path Parameters:** `id` (ticket UUID)

**Integration Request:**
```json
{
  "httpMethod": "GET",
  "path": "/tickets/{id}",
  "pathParameters": {
    "id": "$input.params('id')"
  }
}
```

#### POST /tickets/{id}/comments (Add Comment)

**Integration Type:** Lambda Function (proxy integration)  
**Lambda Function:** poc-itsm-api-handler  
**Authorization:** API Key Required  
**Path Parameters:** `id` (ticket UUID)

**Integration Request:**
```json
{
  "httpMethod": "POST",
  "path": "/tickets/{id}/comments",
  "pathParameters": {
    "id": "$input.params('id')"
  },
  "body": "$input.body"
}
```

---

## Authentication: API Key

### API Key Configuration

**Method:** API Key in header  
**Header Name:** `x-api-key`  
**Key Name:** `poc-itsm-api-key`

### API Key Creation

```bash
aws apigateway create-api-key \
  --name poc-itsm-api-key \
  --description "API key for PoC Mock ITSM API" \
  --enabled \
  --region us-east-1
```

### Usage Plan

**Name:** `poc-itsm-usage-plan`  
**Throttle:** 100 requests per second (more than sufficient)  
**Quota:** 10,000 requests per month (more than sufficient)

**Rationale:**
- Prevents accidental runaway costs
- Sufficient for PoC testing
- Can be increased if needed

### Associate API Key with Usage Plan

```bash
aws apigateway create-usage-plan \
  --name poc-itsm-usage-plan \
  --throttle burstLimit=100,rateLimit=50 \
  --quota limit=10000,period=MONTH \
  --api-stages apiId=<API_ID>,stage=poc

aws apigateway create-usage-plan-key \
  --usage-plan-id <USAGE_PLAN_ID> \
  --key-id <API_KEY_ID> \
  --key-type API_KEY
```

---

## Stage Configuration

### Stage Name
```
poc
```

### Stage Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `lambdaAlias` | `$LATEST` | Lambda version to invoke |

### Deployment

```bash
aws apigateway create-deployment \
  --rest-api-id <API_ID> \
  --stage-name poc \
  --description "PoC deployment for Mock ITSM API"
```

### Stage URL Format

```
https://<API_ID>.execute-api.us-east-1.amazonaws.com/poc
```

**Example:**
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/poc/tickets
```

---

## CORS Configuration

### CORS Headers (if needed for testing)

**Enabled Methods:** GET, POST, OPTIONS  
**Allowed Origins:** `*` (for PoC testing only)  
**Allowed Headers:** `Content-Type, x-api-key`

**Note:** CORS may not be needed if AgentCore Gateway is the only client.

### OPTIONS Method (Preflight)

If CORS is enabled, add OPTIONS method to each resource:

```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key"
  }
}
```

---

## Lambda Integration

### Integration Type
```
AWS_PROXY (Lambda Proxy Integration)
```

**Rationale:**
- Simplest integration pattern
- Lambda receives full request context
- Lambda controls response format
- No request/response mapping needed

### Lambda Permission

Grant API Gateway permission to invoke Lambda:

```bash
aws lambda add-permission \
  --function-name poc-itsm-api-handler \
  --statement-id apigateway-invoke-permission \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:ACCOUNT_ID:API_ID/*/*/*"
```

---

## Request/Response Flow

### Request Flow

```
Client
  ↓ (HTTPS + x-api-key header)
API Gateway
  ↓ (Validate API key)
API Gateway
  ↓ (Route to resource/method)
Lambda Function (poc-itsm-api-handler)
  ↓ (Process request)
DynamoDB (poc-itsm-tickets)
  ↓ (Return data)
Lambda Function
  ↓ (Format response)
API Gateway
  ↓ (Return to client)
Client
```

### Response Flow

Lambda returns:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"ticket_id\": \"...\"}"
}
```

API Gateway forwards response to client with API Gateway headers added.

---

## Monitoring and Logging

### CloudWatch Logs

**Log Group:** `/aws/apigateway/poc-itsm-api`  
**Log Level:** INFO  
**Log Format:** JSON

**Logged Data:**
- Request ID
- HTTP method and path
- Status code
- Response latency
- Integration latency
- Errors

### CloudWatch Metrics (Automatic)

- **Count:** Number of API calls
- **4XXError:** Client errors
- **5XXError:** Server errors
- **Latency:** End-to-end latency
- **IntegrationLatency:** Lambda execution time

### X-Ray Tracing (Optional)

**Recommendation:** Enable for PoC to visualize request flow

```bash
aws apigateway update-stage \
  --rest-api-id <API_ID> \
  --stage-name poc \
  --patch-operations op=replace,path=/tracingEnabled,value=true
```

---

## Deployment Steps

### Step 1: Create REST API

```bash
aws apigateway create-rest-api \
  --name poc-itsm-api \
  --description "Mock ITSM API for AI L1 Support PoC" \
  --endpoint-configuration types=REGIONAL \
  --region us-east-1
```

### Step 2: Import OpenAPI Specification (Alternative)

```bash
aws apigateway import-rest-api \
  --body file://specs/mock-itsm-api-openapi.yaml \
  --region us-east-1
```

**Note:** OpenAPI import creates resources, methods, and integrations automatically.

### Step 3: Configure Lambda Integration

For each method, set integration:

```bash
aws apigateway put-integration \
  --rest-api-id <API_ID> \
  --resource-id <RESOURCE_ID> \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:ACCOUNT_ID:function:poc-itsm-api-handler/invocations"
```

### Step 4: Create API Key and Usage Plan

See "Authentication: API Key" section above.

### Step 5: Deploy to Stage

```bash
aws apigateway create-deployment \
  --rest-api-id <API_ID> \
  --stage-name poc
```

### Step 6: Test API

```bash
curl -X POST \
  https://<API_ID>.execute-api.us-east-1.amazonaws.com/poc/tickets \
  -H "x-api-key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "test-user", "issue_description": "Test issue"}'
```

---

## Cost Estimates

### API Gateway Pricing (us-east-1)

- **REST API Requests:** $3.50 per million requests (first 333 million)
- **Data Transfer Out:** $0.09 per GB

### Estimated PoC Costs

**Assumptions:**
- 100 API calls
- Average response size: 1 KB
- Total data transfer: 0.0001 GB

**Calculation:**
- Requests: 100 × $3.50 / 1,000,000 = $0.00035
- Data transfer: 0.0001 × $0.09 = $0.000009
- **Total: ~$0.0004 (less than $0.01)**

**Free Tier:** 1 million API calls per month for 12 months (covers PoC entirely)

---

## Security Considerations

### API Key Security

- API keys stored in AWS (not in code)
- Keys can be rotated without code changes
- Keys can be disabled instantly if compromised

### HTTPS Only

- All traffic encrypted in transit
- No HTTP endpoint exposed

### IAM Permissions

- API Gateway has permission to invoke Lambda only
- No other AWS service access

### Rate Limiting

- Usage plan prevents abuse
- Throttling protects backend from overload

---

## Alternative: Lambda Function URL

If API Gateway is deemed too complex, Lambda Function URL is a valid alternative:

### Lambda Function URL Configuration

```bash
aws lambda create-function-url-config \
  --function-name poc-itsm-api-handler \
  --auth-type NONE \
  --cors AllowOrigins="*",AllowMethods="GET,POST"
```

**URL Format:**
```
https://<FUNCTION_ID>.lambda-url.us-east-1.on.aws/
```

### API Key Implementation in Lambda

If using Function URL, implement API key check in Lambda:

```python
def lambda_handler(event, context):
    api_key = event.get('headers', {}).get('x-api-key')
    expected_key = os.environ.get('API_KEY')
    
    if api_key != expected_key:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    # Continue with normal processing
```

**Trade-offs:**
- Simpler setup
- Lower cost
- Less production-like
- Manual API key management

---

## Acceptance Criteria Validation

### Requirement 2.10: API Gateway REST + Lambda OR Lambda Function URL

- ✅ Decision documented: API Gateway REST API (recommended)
- ✅ Alternative documented: Lambda Function URL
- ✅ API key authentication mechanism specified
- ✅ Endpoint mappings to Lambda functions defined
- ✅ CORS configuration documented (optional)
- ✅ Region: us-east-1
- ✅ Cost implications within $10 budget (< $0.01)

---

## Task Status

**Task 0.5: API Gateway Design - COMPLETE ✅**

API Gateway configuration documented:
- Architecture decision: REST API vs Function URL
- Recommendation: API Gateway REST API
- All resources and methods defined
- API key authentication configured
- Lambda integration specified
- Deployment steps provided
- Cost estimates included
- Alternative approach documented

**Note:** This design will be implemented in Task 1.5 (API Gateway or Lambda Function URL Setup). This document provides the design rationale that should exist before implementation.
