# Test Strategy Documentation - Task 0.8

## Overview

This document defines the comprehensive testing strategy for the DAS Holding AI L1 Voice Service Desk PoC. The strategy follows a test-driven development (TDD) approach with validation at each implementation step, covering unit tests, API contract tests, integration tests, and end-to-end tests.

---

## Testing Principles

### Test-Driven Development (TDD)

**Approach:**
1. Write tests before implementation
2. Implement minimal code to pass tests
3. Refactor while keeping tests green
4. Validate acceptance criteria before proceeding

**Benefits:**
- Catches bugs early
- Ensures requirements are met
- Provides regression protection
- Documents expected behavior

### Test Pyramid

```
        /\
       /E2E\         (Few - High-level scenarios)
      /------\
     /Integr.\      (Some - Component interactions)
    /----------\
   /   Unit     \   (Many - Individual functions)
  /--------------\
```

---

## Unit Tests (Lambda Functions)

### Framework
```
pytest (Python)
```

### Test File
```
tests/test_lambda_handler.py
```

### Coverage Requirements

**Minimum Coverage:** 80% code coverage  
**Target Coverage:** 90%+ code coverage

### Test Categories

#### 1. Happy Path Tests

**Purpose:** Verify correct behavior with valid inputs

**Tests:**
- `test_create_ticket_success` - Valid ticket creation
- `test_get_ticket_success` - Retrieve existing ticket
- `test_add_comment_success` - Add comment to ticket
- `test_list_tickets_success` - List tickets for caller

**Example:**
```python
def test_create_ticket_success(mock_table):
    """Test successful ticket creation"""
    mock_table.put_item.return_value = {}
    
    event = {
        'httpMethod': 'POST',
        'path': '/tickets',
        'body': json.dumps({
            'caller_id': 'user-001',
            'issue_description': 'Laptop not turning on'
        })
    }
    
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'ticket_id' in body
    assert body['status'] == 'open'
```

#### 2. Validation Tests

**Purpose:** Verify input validation and error handling

**Tests:**
- `test_create_ticket_missing_caller_id` - Returns 400
- `test_create_ticket_missing_issue_description` - Returns 400
- `test_create_ticket_invalid_json` - Returns 400
- `test_get_ticket_missing_id` - Returns 400
- `test_add_comment_missing_comment` - Returns 400
- `test_list_tickets_missing_caller` - Returns 400

**Example:**
```python
def test_create_ticket_missing_caller_id(mock_table):
    """Test ticket creation with missing caller_id"""
    event = {
        'httpMethod': 'POST',
        'path': '/tickets',
        'body': json.dumps({
            'issue_description': 'Laptop not turning on'
        })
    }
    
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
```

#### 3. Not Found Tests

**Purpose:** Verify 404 handling for non-existent resources

**Tests:**
- `test_get_ticket_not_found` - Ticket doesn't exist
- `test_add_comment_ticket_not_found` - Ticket doesn't exist

**Example:**
```python
def test_get_ticket_not_found(mock_table):
    """Test ticket retrieval when ticket doesn't exist"""
    mock_table.get_item.return_value = {}
    
    event = {
        'httpMethod': 'GET',
        'path': '/tickets/nonexistent',
        'pathParameters': {'id': 'nonexistent'}
    }
    
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 404
```

#### 4. Error Handling Tests

**Purpose:** Verify graceful handling of DynamoDB errors

**Tests:**
- `test_create_ticket_dynamodb_error` - DynamoDB failure
- `test_retry_on_throttling` - Throttling with retry
- `test_retry_max_attempts_exceeded` - Max retries exceeded
- `test_unexpected_exception` - Unexpected errors

**Example:**
```python
def test_create_ticket_dynamodb_error(mock_table):
    """Test ticket creation with DynamoDB error"""
    from botocore.exceptions import ClientError
    
    mock_table.put_item.side_effect = ClientError(
        {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}},
        'PutItem'
    )
    
    event = {
        'httpMethod': 'POST',
        'path': '/tickets',
        'body': json.dumps({
            'caller_id': 'user-001',
            'issue_description': 'Test issue'
        })
    }
    
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 500
```

#### 5. Retry Logic Tests

**Purpose:** Verify exponential backoff retry mechanism

**Tests:**
- `test_retry_on_throttling` - Retries on throttling
- `test_retry_max_attempts_exceeded` - Fails after 3 attempts

**Example:**
```python
def test_retry_on_throttling(mock_table):
    """Test retry logic on throttling exception"""
    from botocore.exceptions import ClientError
    
    # First two calls fail, third succeeds
    mock_table.put_item.side_effect = [
        ClientError({'Error': {'Code': 'ProvisionedThroughputExceededException'}}, 'PutItem'),
        ClientError({'Error': {'Code': 'ThrottlingException'}}, 'PutItem'),
        {}
    ]
    
    event = {
        'httpMethod': 'POST',
        'path': '/tickets',
        'body': json.dumps({
            'caller_id': 'user-001',
            'issue_description': 'Test issue'
        })
    }
    
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 201
    assert mock_table.put_item.call_count == 3
```

### Running Unit Tests

```bash
# Install dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/test_lambda_handler.py -v

# Run with coverage
pytest tests/test_lambda_handler.py --cov=src/lambda --cov-report=html

# Run specific test
pytest tests/test_lambda_handler.py::TestCreateTicket::test_create_ticket_success -v
```

### Expected Results

**All 18 unit tests must pass:**
- 5 Create Ticket tests ✅
- 3 Get Ticket Status tests ✅
- 3 Add Comment tests ✅
- 3 List Recent Tickets tests ✅
- 2 Retry Logic tests ✅
- 2 Error Handling tests ✅

---

## API Contract Tests

### Purpose

Verify that the deployed API conforms to the OpenAPI specification.

### Framework
```
curl + bash scripts OR Postman/Newman
```

### Test File
```
tests/api-contract-tests.sh
```

### Test Cases

#### Test 1: POST /tickets (Create Ticket)

**Request:**
```bash
curl -X POST \
  https://<API_URL>/poc/tickets \
  -H "x-api-key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": "test-user-001",
    "issue_description": "Test ticket - Laptop not working"
  }'
```

**Expected Response:**
```json
{
  "ticket_id": "<UUID>",
  "status": "open",
  "created_at": "<ISO 8601 timestamp>"
}
```

**Assertions:**
- Status code: 201
- Response contains ticket_id (UUID format)
- Response contains status = "open"
- Response contains created_at (ISO 8601 format)

#### Test 2: GET /tickets/{id} (Get Ticket Status)

**Request:**
```bash
curl -X GET \
  https://<API_URL>/poc/tickets/<TICKET_ID> \
  -H "x-api-key: <API_KEY>"
```

**Expected Response:**
```json
{
  "ticket_id": "<UUID>",
  "caller_id": "test-user-001",
  "issue_description": "Test ticket - Laptop not working",
  "status": "open",
  "created_at": "<ISO 8601 timestamp>",
  "updated_at": "<ISO 8601 timestamp>",
  "comments": []
}
```

**Assertions:**
- Status code: 200
- Response contains all ticket fields
- ticket_id matches request
- comments is an array

#### Test 3: POST /tickets/{id}/comments (Add Comment)

**Request:**
```bash
curl -X POST \
  https://<API_URL>/poc/tickets/<TICKET_ID>/comments \
  -H "x-api-key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Tried restarting the laptop but still not working"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "updated_at": "<ISO 8601 timestamp>"
}
```

**Assertions:**
- Status code: 200
- Response contains success = true
- Response contains updated_at

#### Test 4: GET /tickets?caller={caller_id} (List Tickets)

**Request:**
```bash
curl -X GET \
  "https://<API_URL>/poc/tickets?caller=test-user-001" \
  -H "x-api-key: <API_KEY>"
```

**Expected Response:**
```json
{
  "tickets": [
    {
      "ticket_id": "<UUID>",
      "caller_id": "test-user-001",
      "issue_description": "Test ticket - Laptop not working",
      "status": "open",
      "created_at": "<ISO 8601 timestamp>",
      "updated_at": "<ISO 8601 timestamp>",
      "comments": [...]
    }
  ]
}
```

**Assertions:**
- Status code: 200
- Response contains tickets array
- Array contains at least one ticket
- Ticket matches previously created ticket

#### Test 5: Authentication (Missing API Key)

**Request:**
```bash
curl -X POST \
  https://<API_URL>/poc/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": "test-user-001",
    "issue_description": "Test"
  }'
```

**Expected Response:**
```json
{
  "message": "Forbidden"
}
```

**Assertions:**
- Status code: 401 or 403
- Request is rejected

### Running Contract Tests

```bash
# Set environment variables
export API_URL="https://abc123.execute-api.us-east-1.amazonaws.com"
export API_KEY="your-api-key-here"

# Run contract tests
bash tests/api-contract-tests.sh

# Expected output:
# ✅ Test 1: POST /tickets - PASSED
# ✅ Test 2: GET /tickets/{id} - PASSED
# ✅ Test 3: POST /tickets/{id}/comments - PASSED
# ✅ Test 4: GET /tickets?caller=... - PASSED
# ✅ Test 5: Authentication - PASSED
```

---

## Integration Tests

### Purpose

Verify that Lambda function correctly integrates with DynamoDB.

### Approach

**Option 1:** Use moto library to mock DynamoDB  
**Option 2:** Use actual DynamoDB table (PoC approach)

### Test Cases

#### Test 1: End-to-End Ticket Creation

**Steps:**
1. Invoke Lambda with create_ticket event
2. Verify Lambda returns 201 with ticket_id
3. Query DynamoDB directly to verify ticket exists
4. Verify all fields are correct

**Verification:**
```bash
# Invoke Lambda
aws lambda invoke \
  --function-name poc-itsm-api-handler \
  --payload file://test-event.json \
  response.json

# Verify DynamoDB
aws dynamodb get-item \
  --table-name poc-itsm-tickets \
  --key '{"ticket_id": {"S": "<TICKET_ID>"}}'
```

#### Test 2: Comment Append

**Steps:**
1. Create ticket via Lambda
2. Add comment via Lambda
3. Query DynamoDB to verify comment is appended
4. Verify updated_at is updated

#### Test 3: GSI Query

**Steps:**
1. Create multiple tickets for same caller
2. Query via list_recent_tickets
3. Verify tickets are returned in descending order
4. Verify limit of 10 is enforced

---

## Smoke Tests (Connect Flow)

### Purpose

Quick manual tests to verify Amazon Connect flow works.

### Test Checklist

#### Test 1: Basic Call Flow
- [ ] Call phone number
- [ ] Hear greeting (if configured)
- [ ] AI Agent responds with greeting
- [ ] Can have basic conversation
- [ ] Call ends gracefully

#### Test 2: Create Ticket via Voice
- [ ] Call phone number
- [ ] Say: "I need help with my laptop. It won't turn on."
- [ ] AI Agent summarizes issue
- [ ] Confirm ticket creation
- [ ] AI Agent provides ticket number
- [ ] Verify ticket in DynamoDB

#### Test 3: Check Ticket Status via Voice
- [ ] Call phone number
- [ ] Say: "I want to check my ticket status"
- [ ] Provide ticket number when asked
- [ ] AI Agent retrieves and reads status
- [ ] Information is accurate

#### Test 4: Add Comment via Voice
- [ ] Call phone number
- [ ] Say: "I want to add information to my ticket"
- [ ] Provide ticket number
- [ ] Provide additional information
- [ ] AI Agent confirms comment added
- [ ] Verify comment in DynamoDB

#### Test 5: List Tickets via Voice
- [ ] Call phone number
- [ ] Say: "Show me my recent tickets"
- [ ] AI Agent lists tickets
- [ ] Information is accurate

#### Test 6: Escalation Path
- [ ] Call phone number
- [ ] Say: "I want to speak to a human agent"
- [ ] AI Agent acknowledges escalation
- [ ] Transfer occurs (or escalation message plays)
- [ ] Call ends appropriately

---

## End-to-End (E2E) Test Scenarios

### Test Scenario 1: Complete Ticket Lifecycle

**Objective:** Verify full ticket creation, update, and retrieval flow

**Steps:**
1. **Create Ticket:**
   - Call Connect phone number
   - Describe issue: "My email isn't working in Outlook"
   - Confirm ticket creation
   - Note ticket ID provided by AI Agent

2. **Verify Ticket Created:**
   - Query DynamoDB for ticket
   - Verify all fields are correct
   - Verify status is "open"

3. **Add Comment:**
   - Call Connect phone number again
   - Say: "I want to add information to ticket <TICKET_ID>"
   - Provide comment: "I tried restarting Outlook but it didn't help"
   - Confirm comment added

4. **Verify Comment Added:**
   - Query DynamoDB for ticket
   - Verify comment is in comments array
   - Verify updated_at is updated

5. **Check Status:**
   - Call Connect phone number again
   - Say: "What's the status of ticket <TICKET_ID>?"
   - Verify AI Agent reads correct status and details

6. **List Tickets:**
   - Call Connect phone number again
   - Say: "Show me my recent tickets"
   - Verify ticket appears in list

**Pass Criteria:**
- All steps complete without errors
- Data is consistent across all operations
- AI Agent provides accurate information

### Test Scenario 2: Multiple Tickets for Same Caller

**Objective:** Verify GSI query works correctly

**Steps:**
1. Create 3 tickets via voice calls
2. Call and ask to list recent tickets
3. Verify all 3 tickets are returned
4. Verify tickets are in descending order (newest first)

**Pass Criteria:**
- All tickets returned
- Correct order
- Limit of 10 enforced (if more than 10 exist)

### Test Scenario 3: Error Handling

**Objective:** Verify graceful error handling

**Steps:**
1. **Invalid Ticket ID:**
   - Call and ask for status of non-existent ticket
   - Verify AI Agent says ticket not found
   - Verify no crash or error exposure

2. **Missing Information:**
   - Call and try to create ticket without describing issue
   - Verify AI Agent asks for more information
   - Verify ticket not created until sufficient info provided

**Pass Criteria:**
- Errors handled gracefully
- No internal error details exposed
- AI Agent provides helpful messages

### Test Scenario 4: Escalation

**Objective:** Verify escalation path works

**Steps:**
1. Call phone number
2. Say: "This is urgent, I need to speak to someone now"
3. Verify AI Agent acknowledges urgency
4. Verify escalation occurs (transfer or message)

**Pass Criteria:**
- Escalation trigger recognized
- Appropriate action taken
- Caller informed of escalation

---

## Test Data Management

### Test Data

**Caller IDs:**
- `test-user-001`
- `test-user-002`
- `poc-caller-alpha`

**Issue Descriptions:**
- "Laptop not turning on"
- "Email not working in Outlook"
- "Cannot access shared drive"
- "Printer not responding"

### Cleanup

After testing, optionally clean up test data:

```bash
# Delete test tickets
aws dynamodb delete-item \
  --table-name poc-itsm-tickets \
  --key '{"ticket_id": {"S": "<TEST_TICKET_ID>"}}'
```

**Note:** For PoC, cleanup is optional as table will be deleted in Phase 5.

---

## Test Execution Schedule

### Phase 1: Mock ITSM Backend

**After Task 1.3 (Lambda Implementation):**
- ✅ Run all unit tests (18 tests must pass)

**After Task 1.4 (Lambda Deployment):**
- ✅ Run integration test (create ticket, verify in DynamoDB)

**After Task 1.5 (API Gateway Setup):**
- ✅ Run all API contract tests (5 tests must pass)

### Phase 2: AgentCore Gateway

**After Task 2.4 (AgentCore Deployment):**
- ✅ Test tool invocations (4 tools)
- ✅ Verify tickets created via tools appear in DynamoDB

### Phase 3: Amazon Connect Setup

**After Task 3.6 (Phone Number Assignment):**
- ✅ Run all smoke tests (6 tests)

### Phase 4: End-to-End Testing

**Tasks 4.2-4.6:**
- ✅ Execute all E2E test scenarios (4 scenarios)
- ✅ Document results in `tests/e2e-test-results.md`

---

## Acceptance Criteria Validation

### Requirement 9.1-9.5: TDD with Validation at Each Step

- ✅ Lambda functions include unit tests using pytest
- ✅ Mock_ITSM_API includes API contract tests verifying each endpoint
- ✅ Connect_Flow includes smoke test checklist for voice interaction
- ✅ System does not proceed to next task until current task passes all tests
- ✅ End-to-end testing provides test script validating complete flow

### Requirement 16.1-16.8: E2E Test Scenarios

- ✅ E2E test script/checklist provided
- ✅ Test validates caller can create ticket through voice interaction
- ✅ Test validates AI_Agent provides ticket ID after creation
- ✅ Test validates caller can query ticket status
- ✅ Test validates caller can add comments to ticket
- ✅ Test validates caller can list recent tickets
- ✅ Test validates escalation path works correctly
- ✅ Test reports pass/fail status for each scenario

---

## Task Status

**Task 0.8: Test Strategy Documentation - COMPLETE ✅**

Comprehensive test strategy documented:
- Unit tests (18 tests with pytest)
- API contract tests (5 tests with curl)
- Integration tests (Lambda + DynamoDB)
- Smoke tests (6 manual tests for Connect)
- E2E test scenarios (4 complete scenarios)
- Test execution schedule
- Pass/fail criteria for each test type

**Note:** Tests have been implemented and executed for Phase 1 (Tasks 1.3-1.4). This document provides the complete test strategy for all phases.
