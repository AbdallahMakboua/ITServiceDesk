# Lambda Function Design - Task 0.4

## Overview

This document defines the architecture and design for the Lambda function(s) that implement the Mock ITSM API for the DAS Holding AI L1 Voice Service Desk PoC. The design follows AWS best practices for serverless applications with a focus on minimal complexity, cost efficiency, and least-privilege security.

---

## Architecture Decision: Single Lambda Function

### Design Choice

**Single Lambda function** handling all four API operations (create, get, comment, list).

### Rationale

**Advantages:**
- Simpler deployment and management (one function vs. four)
- Shared code and dependencies (no duplication)
- Single IAM role to manage
- Lower cold start overhead (one function stays warm)
- Easier debugging and logging (all operations in one log group)
- Cost-effective for low-volume PoC

**Trade-offs:**
- Slightly larger deployment package (still minimal)
- All operations share same timeout/memory settings
- Cannot scale operations independently (not needed for PoC)

**Conclusion:** Single function is optimal for PoC scope and budget constraints.

---

## Function Configuration

### Function Name
```
poc-itsm-api-handler
```

### Runtime
```
Python 3.12
```

**Rationale:**
- Latest stable Python runtime
- Excellent AWS SDK (boto3) support
- Fast cold starts
- Familiar language for most developers
- Good error handling capabilities

**Alternative Considered:** Node.js 20.x (also acceptable)

### Handler
```
mock_itsm_handler.lambda_handler
```

### Timeout
```
10 seconds
```

**Rationale:**
- DynamoDB operations complete in milliseconds
- Allows time for retries (up to 3 attempts)
- Prevents runaway executions
- Well within typical API response time expectations

### Memory
```
256 MB
```

**Rationale:**
- Minimal memory allocation
- Sufficient for boto3 and JSON processing
- Cost-effective ($0.0000000021 per 100ms at 256MB)
- Can be increased if needed (unlikely)

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `TABLE_NAME` | `poc-itsm-tickets` | DynamoDB table name |
| `REGION` | `us-east-1` | AWS region |

---

## Handler Logic

### Request Routing

The Lambda handler routes requests based on HTTP method and path:

```python
def lambda_handler(event, context):
    http_method = event.get('httpMethod')
    path = event.get('path')
    
    if http_method == 'POST' and path == '/tickets':
        return create_ticket(body_data)
    elif http_method == 'GET' and path.startswith('/tickets/'):
        return get_ticket_status(ticket_id)
    elif http_method == 'POST' and path.endswith('/comments'):
        return add_ticket_comment(ticket_id, body_data)
    elif http_method == 'GET' and path == '/tickets':
        return list_recent_tickets(caller_id)
    else:
        return error_response(404, "Endpoint not found")
```

### Event Structure

Lambda receives events from API Gateway or Function URL:

```json
{
  "httpMethod": "POST",
  "path": "/tickets",
  "pathParameters": {"id": "ticket-uuid"},
  "queryStringParameters": {"caller": "user-id"},
  "body": "{\"caller_id\": \"user-001\", \"issue_description\": \"...\"}"
}
```

---

## Operation Implementations

### 1. Create Ticket (POST /tickets)

**Input Validation:**
- Verify `caller_id` is present and non-empty
- Verify `issue_description` is present and non-empty
- Return 400 if validation fails

**Processing:**
1. Generate UUID for `ticket_id`
2. Get current timestamp (ISO 8601 format)
3. Create ticket item with all required fields
4. Call DynamoDB `PutItem` with retry logic
5. Return 201 with ticket_id, status, created_at

**DynamoDB Operation:**
```python
table.put_item(Item={
    'ticket_id': str(uuid.uuid4()),
    'caller_id': caller_id,
    'issue_description': issue_description,
    'status': 'open',
    'created_at': timestamp,
    'updated_at': timestamp,
    'comments': []
})
```

**Response:**
```json
{
  "statusCode": 201,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"ticket_id\": \"...\", \"status\": \"open\", \"created_at\": \"...\"}"
}
```

### 2. Get Ticket Status (GET /tickets/{id})

**Input Validation:**
- Verify `ticket_id` is present in path parameters
- Return 400 if missing

**Processing:**
1. Extract ticket_id from path parameters
2. Call DynamoDB `GetItem` with retry logic
3. Return 404 if ticket not found
4. Return 200 with full ticket data

**DynamoDB Operation:**
```python
response = table.get_item(Key={'ticket_id': ticket_id})
if 'Item' not in response:
    return error_response(404, f"Ticket {ticket_id} not found")
```

**Response:**
```json
{
  "statusCode": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"ticket_id\": \"...\", \"caller_id\": \"...\", ...}"
}
```

### 3. Add Comment (POST /tickets/{id}/comments)

**Input Validation:**
- Verify `ticket_id` is present in path parameters
- Verify `comment` is present in body and non-empty
- Return 400 if validation fails

**Processing:**
1. Extract ticket_id from path parameters
2. Extract comment from request body
3. Get current timestamp
4. Create comment object
5. Call DynamoDB `UpdateItem` to append comment
6. Return 200 with success and updated_at

**DynamoDB Operation:**
```python
table.update_item(
    Key={'ticket_id': ticket_id},
    UpdateExpression='SET comments = list_append(if_not_exists(comments, :empty_list), :comment), updated_at = :timestamp',
    ExpressionAttributeValues={
        ':comment': [{'comment_text': comment_text, 'added_at': timestamp}],
        ':timestamp': timestamp,
        ':empty_list': []
    }
)
```

**Response:**
```json
{
  "statusCode": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"success\": true, \"updated_at\": \"...\"}"
}
```

### 4. List Recent Tickets (GET /tickets?caller={caller_id})

**Input Validation:**
- Verify `caller` query parameter is present
- Return 400 if missing

**Processing:**
1. Extract caller_id from query parameters
2. Call DynamoDB `Query` on GSI with retry logic
3. Sort by created_at descending (newest first)
4. Limit to 10 tickets
5. Return 200 with tickets array (empty if none found)

**DynamoDB Operation:**
```python
response = table.query(
    IndexName='CallerIdIndex',
    KeyConditionExpression='caller_id = :caller_id',
    ExpressionAttributeValues={':caller_id': caller_id},
    ScanIndexForward=False,  # Descending order
    Limit=10
)
```

**Response:**
```json
{
  "statusCode": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"tickets\": [...]}"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Success (GET, comment added) | Ticket retrieved successfully |
| 201 | Created (POST /tickets) | Ticket created successfully |
| 400 | Bad Request (invalid input) | Missing required field |
| 404 | Not Found | Ticket does not exist |
| 500 | Internal Server Error | DynamoDB error, unexpected exception |

### Error Response Format

```json
{
  "statusCode": 400,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"error\": \"Missing required fields: caller_id and issue_description\"}"
}
```

### Error Logging

All errors logged to CloudWatch with:
- Error message
- Stack trace (for 500 errors)
- Request context (method, path)
- NO sensitive data (passwords, tokens)

```python
print(f"Error creating ticket: {str(e)}")
```

---

## Retry Logic with Exponential Backoff

### DynamoDB Throttling Handling

**Retry Conditions:**
- `ProvisionedThroughputExceededException`
- `ThrottlingException`

**Retry Strategy:**
- Maximum attempts: 3
- Backoff: Exponential (0.1s, 0.2s, 0.4s)
- Total max retry time: ~0.7 seconds

**Implementation:**
```python
def retry_dynamodb_operation(operation, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return operation()
        except ClientError as e:
            if e.response['Error']['Code'] in ['ProvisionedThroughputExceededException', 'ThrottlingException']:
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) * 0.1
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise
```

---

## Dependencies

### Runtime Dependencies

**requirements.txt:**
```
boto3>=1.34.0
```

**Rationale:**
- boto3 is the only required dependency
- Pre-installed in Lambda Python runtime (but version may vary)
- Explicitly including ensures consistent version

**Package Size:** ~50 KB (boto3 is already in Lambda runtime layer)

### No External Libraries

- No web frameworks (Flask, FastAPI) - unnecessary overhead
- No ORM libraries - direct boto3 calls are simpler
- No validation libraries - manual validation is sufficient for 4 endpoints

---

## Security Considerations

### Input Validation

- All required fields checked before processing
- String length limits enforced (max 1000 chars for descriptions)
- No SQL injection risk (NoSQL database)
- No command injection risk (no shell commands)

### Output Sanitization

- Error messages do not expose internal details
- Stack traces not returned to client (logged only)
- No sensitive data in responses

### IAM Permissions

See `docs/iam-policies.md` for detailed IAM role design.

**Principle:** Least privilege
- DynamoDB operations scoped to specific table
- CloudWatch logging scoped to specific log group
- No wildcard permissions

---

## Performance Characteristics

### Cold Start

- **Estimated:** 200-400ms for Python 3.12 with boto3
- **Mitigation:** Single function reduces cold start frequency
- **Impact:** Acceptable for PoC (not production-critical)

### Warm Execution

- **Estimated:** 10-50ms per request
- **DynamoDB latency:** Single-digit milliseconds
- **Total response time:** < 100ms typical

### Concurrency

- **Expected:** 1-5 concurrent executions for PoC
- **Lambda default:** 1000 concurrent executions (more than sufficient)
- **No throttling expected**

---

## Monitoring and Logging

### CloudWatch Logs

**Log Group:** `/aws/lambda/poc-itsm-api-handler`  
**Retention:** Default (never expire) - acceptable for short PoC  
**Log Level:** INFO (errors and key operations)

**Logged Events:**
- Function invocations
- DynamoDB operations
- Errors and exceptions
- Retry attempts

### CloudWatch Metrics (Automatic)

- Invocations
- Duration
- Errors
- Throttles
- Concurrent executions

---

## Testing Strategy

### Unit Tests

**Framework:** pytest  
**Coverage:** All four operations + error handling + retry logic

**Test Categories:**
1. **Happy path tests** - Valid inputs, successful operations
2. **Validation tests** - Missing fields, invalid inputs
3. **Error handling tests** - DynamoDB errors, exceptions
4. **Retry logic tests** - Throttling scenarios

**Test File:** `tests/test_lambda_handler.py`

### Integration Tests

**Approach:** Invoke Lambda with test events, verify DynamoDB state

**Test Cases:**
1. Create ticket → Verify in DynamoDB
2. Get ticket → Verify response matches DynamoDB
3. Add comment → Verify comment appended
4. List tickets → Verify GSI query works

---

## Deployment Package

### Structure

```
lambda-package.zip
├── mock_itsm_handler.py  (main handler)
└── (boto3 already in Lambda runtime)
```

### Size

- **Uncompressed:** ~7 KB
- **Compressed:** ~2 KB
- **Well within Lambda limits** (50 MB compressed, 250 MB uncompressed)

### Deployment Command

```bash
zip -j deployment/lambda-package.zip src/lambda/mock_itsm_handler.py

aws lambda create-function \
  --function-name poc-itsm-api-handler \
  --runtime python3.12 \
  --role arn:aws:iam::ACCOUNT_ID:role/poc-itsm-lambda-role \
  --handler mock_itsm_handler.lambda_handler \
  --zip-file fileb://deployment/lambda-package.zip \
  --timeout 10 \
  --memory-size 256 \
  --environment Variables="{TABLE_NAME=poc-itsm-tickets,REGION=us-east-1}" \
  --region us-east-1
```

---

## Cost Estimates

### Lambda Pricing (us-east-1)

- **Requests:** $0.20 per 1 million requests
- **Duration:** $0.0000000021 per 100ms at 256MB

### Estimated PoC Costs

**Assumptions:**
- 100 total invocations
- Average duration: 50ms
- Memory: 256MB

**Calculation:**
- Requests: 100 × $0.20 / 1,000,000 = $0.00002
- Duration: 100 × 0.5 × $0.0000000021 = $0.000000105
- **Total:** < $0.01

**Free Tier:** 1 million requests + 400,000 GB-seconds per month (covers PoC entirely)

---

## Acceptance Criteria Validation

### Requirement 12.1-12.7: Minimal Lambda Implementation

- ✅ Runtime: Python 3.12
- ✅ Single Lambda function handling all four API operations
- ✅ Error handling with appropriate HTTP status codes (400, 404, 500)
- ✅ DynamoDB retry logic with exponential backoff (up to 3 attempts)
- ✅ Execution timeout: 10 seconds maximum
- ✅ IAM policy: Least privilege, DynamoDB operations only on poc-itsm-tickets table
- ✅ Minimal dependencies (boto3 only)

### Requirement 14.1: Lambda IAM Role Limited to Specific DynamoDB Table

- ✅ IAM role design documented (see iam-policies.md)
- ✅ Permissions scoped to poc-itsm-tickets table only
- ✅ No wildcard permissions

---

## Task Status

**Task 0.4: Lambda Function Design - COMPLETE ✅**

Lambda function architecture and design documented:
- Single function approach justified
- All four operations designed
- Error handling strategy defined
- Retry logic specified
- Security considerations addressed
- Testing strategy outlined
- Cost estimates provided

**Note:** This design was implemented in Task 1.3 (Lambda Function Implementation) and deployed in Task 1.4 (Lambda Function Deployment). This document provides the design rationale that should have existed before implementation.
