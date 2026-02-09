# API Gateway Deployment Log - Task 1.5

## Deployment Information

**Timestamp:** 2026-02-09T14:03:25+00:00  
**API Name:** poc-itsm-api  
**API ID:** iixw3qtwo3  
**Region:** us-east-1  
**Endpoint Type:** REGIONAL  
**Stage:** poc  
**API URL:** https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc

---

## Commands Executed

### 1. Create REST API
```bash
aws apigateway create-rest-api \
  --name poc-itsm-api \
  --description "Mock ITSM API for AI L1 Support PoC" \
  --endpoint-configuration types=REGIONAL \
  --region us-east-1
```

**Result:**
- API ID: iixw3qtwo3
- Root Resource ID: lybkfynx8i

### 2. Create Resources

#### Create /tickets resource
```bash
aws apigateway create-resource \
  --rest-api-id iixw3qtwo3 \
  --parent-id lybkfynx8i \
  --path-part tickets \
  --region us-east-1
```
**Resource ID:** tadn90

#### Create /tickets/{id} resource
```bash
aws apigateway create-resource \
  --rest-api-id iixw3qtwo3 \
  --parent-id tadn90 \
  --path-part '{id}' \
  --region us-east-1
```
**Resource ID:** 1wsnva

#### Create /tickets/{id}/comments resource
```bash
aws apigateway create-resource \
  --rest-api-id iixw3qtwo3 \
  --parent-id 1wsnva \
  --path-part comments \
  --region us-east-1
```
**Resource ID:** o0iy3s

### 3. Create Methods and Integrations

#### POST /tickets (Create Ticket)
```bash
# Create method
aws apigateway put-method \
  --rest-api-id iixw3qtwo3 \
  --resource-id tadn90 \
  --http-method POST \
  --authorization-type NONE \
  --api-key-required \
  --region us-east-1

# Create integration
aws apigateway put-integration \
  --rest-api-id iixw3qtwo3 \
  --resource-id tadn90 \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler/invocations" \
  --region us-east-1

# Create method response
aws apigateway put-method-response \
  --rest-api-id iixw3qtwo3 \
  --resource-id tadn90 \
  --http-method POST \
  --status-code 200 \
  --region us-east-1
```

#### GET /tickets (List Recent Tickets)
```bash
# Create method
aws apigateway put-method \
  --rest-api-id iixw3qtwo3 \
  --resource-id tadn90 \
  --http-method GET \
  --authorization-type NONE \
  --api-key-required \
  --request-parameters method.request.querystring.caller=true \
  --region us-east-1

# Create integration
aws apigateway put-integration \
  --rest-api-id iixw3qtwo3 \
  --resource-id tadn90 \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler/invocations" \
  --region us-east-1

# Create method response
aws apigateway put-method-response \
  --rest-api-id iixw3qtwo3 \
  --resource-id tadn90 \
  --http-method GET \
  --status-code 200 \
  --region us-east-1
```

#### GET /tickets/{id} (Get Ticket Status)
```bash
# Create method
aws apigateway put-method \
  --rest-api-id iixw3qtwo3 \
  --resource-id 1wsnva \
  --http-method GET \
  --authorization-type NONE \
  --api-key-required \
  --request-parameters method.request.path.id=true \
  --region us-east-1

# Create integration
aws apigateway put-integration \
  --rest-api-id iixw3qtwo3 \
  --resource-id 1wsnva \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler/invocations" \
  --region us-east-1

# Create method response
aws apigateway put-method-response \
  --rest-api-id iixw3qtwo3 \
  --resource-id 1wsnva \
  --http-method GET \
  --status-code 200 \
  --region us-east-1
```

#### POST /tickets/{id}/comments (Add Comment)
```bash
# Create method
aws apigateway put-method \
  --rest-api-id iixw3qtwo3 \
  --resource-id o0iy3s \
  --http-method POST \
  --authorization-type NONE \
  --api-key-required \
  --request-parameters method.request.path.id=true \
  --region us-east-1

# Create integration
aws apigateway put-integration \
  --rest-api-id iixw3qtwo3 \
  --resource-id o0iy3s \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler/invocations" \
  --region us-east-1

# Create method response
aws apigateway put-method-response \
  --rest-api-id iixw3qtwo3 \
  --resource-id o0iy3s \
  --http-method POST \
  --status-code 200 \
  --region us-east-1
```

### 4. Grant Lambda Permission
```bash
aws lambda add-permission \
  --function-name poc-itsm-api-handler \
  --statement-id apigateway-invoke-permission \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:714059461907:iixw3qtwo3/*/*/*" \
  --region us-east-1
```

### 5. Create API Key
```bash
aws apigateway create-api-key \
  --name poc-itsm-api-key \
  --description "API key for PoC Mock ITSM API" \
  --enabled \
  --region us-east-1
```

**Result:**
- API Key ID: r3k6upsgse
- API Key Value: h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa

### 6. Deploy to Stage
```bash
aws apigateway create-deployment \
  --rest-api-id iixw3qtwo3 \
  --stage-name poc \
  --description "PoC deployment for Mock ITSM API" \
  --region us-east-1
```

**Deployment ID:** sgpgqf

### 7. Create Usage Plan
```bash
aws apigateway create-usage-plan \
  --name poc-itsm-usage-plan \
  --description "Usage plan for PoC Mock ITSM API" \
  --throttle burstLimit=100,rateLimit=50 \
  --quota limit=10000,period=MONTH \
  --api-stages apiId=iixw3qtwo3,stage=poc \
  --region us-east-1
```

**Usage Plan ID:** 4ym2fl

### 8. Associate API Key with Usage Plan
```bash
aws apigateway create-usage-plan-key \
  --usage-plan-id 4ym2fl \
  --key-id r3k6upsgse \
  --key-type API_KEY \
  --region us-east-1
```

---

## API Configuration

### Endpoints

| Method | Path | Operation | Resource ID |
|--------|------|-----------|-------------|
| POST | /tickets | create_ticket | tadn90 |
| GET | /tickets | list_recent_tickets | tadn90 |
| GET | /tickets/{id} | get_ticket_status | 1wsnva |
| POST | /tickets/{id}/comments | add_ticket_comment | o0iy3s |

### Authentication
- **Type:** API Key
- **Header:** x-api-key
- **Key Name:** poc-itsm-api-key
- **Key ID:** r3k6upsgse
- **Key Value:** h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa

### Usage Plan
- **Name:** poc-itsm-usage-plan
- **Throttle:** 100 burst limit, 50 requests/second rate limit
- **Quota:** 10,000 requests per month

### Lambda Integration
- **Function:** poc-itsm-api-handler
- **Function ARN:** arn:aws:lambda:us-east-1:714059461907:function:poc-itsm-api-handler
- **Integration Type:** AWS_PROXY (Lambda Proxy Integration)

---

## Contract Test Results

### Test 1: POST /tickets (Create Ticket)
```bash
curl -X POST \
  https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets \
  -H "x-api-key: h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "poc-user-contract-test", "issue_description": "Contract Test 1: Create ticket via API Gateway"}'
```

**Response (HTTP 201):**
```json
{
  "ticket_id": "4f05f225-bdcf-4074-a035-56164295af00",
  "status": "open",
  "created_at": "2026-02-09T14:10:48.662958Z"
}
```
**Result:** ✅ PASS

### Test 2: GET /tickets/{id} (Get Ticket Status)
```bash
curl -X GET \
  "https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets/4f05f225-bdcf-4074-a035-56164295af00" \
  -H "x-api-key: h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa"
```

**Response (HTTP 200):**
```json
{
  "issue_description": "Contract Test 1: Create ticket via API Gateway",
  "updated_at": "2026-02-09T14:10:48.662958Z",
  "ticket_id": "4f05f225-bdcf-4074-a035-56164295af00",
  "created_at": "2026-02-09T14:10:48.662958Z",
  "status": "open",
  "comments": [],
  "caller_id": "poc-user-contract-test"
}
```
**Result:** ✅ PASS

### Test 3: POST /tickets/{id}/comments (Add Comment)
```bash
curl -X POST \
  "https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets/4f05f225-bdcf-4074-a035-56164295af00/comments" \
  -H "x-api-key: h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa" \
  -H "Content-Type: application/json" \
  -d '{"comment": "Contract Test: Adding a comment via API Gateway"}'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "updated_at": "2026-02-09T14:11:16.011681Z"
}
```
**Result:** ✅ PASS

### Test 4: GET /tickets?caller={caller_id} (List Recent Tickets)
```bash
curl -X GET \
  "https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets?caller=poc-user-contract-test" \
  -H "x-api-key: h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa"
```

**Response (HTTP 200):**
```json
{
  "tickets": [
    {
      "caller_id": "poc-user-contract-test",
      "created_at": "2026-02-09T14:10:48.662958Z",
      "issue_description": "Contract Test 1: Create ticket via API Gateway",
      "status": "open",
      "ticket_id": "4f05f225-bdcf-4074-a035-56164295af00",
      "updated_at": "2026-02-09T14:11:16.011681Z",
      "comments": [
        {
          "comment_text": "Contract Test: Adding a comment via API Gateway",
          "added_at": "2026-02-09T14:11:16.011681Z"
        }
      ]
    }
  ]
}
```
**Result:** ✅ PASS

### Test 5: Authentication Test (No API Key)
```bash
curl -X POST \
  https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc/tickets \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "test", "issue_description": "Should fail"}'
```

**Response (HTTP 403):**
```json
{
  "message": "Forbidden"
}
```
**Result:** ✅ PASS (Correctly rejects requests without API key)

---

## Acceptance Criteria Validation

### Requirement 2.1-2.10: Mock API with Four Endpoints
- ✅ POST /tickets endpoint exposed
- ✅ GET /tickets/{id} endpoint exposed
- ✅ POST /tickets/{id}/comments endpoint exposed
- ✅ GET /tickets?caller={caller_id} endpoint exposed
- ✅ API key authentication configured (x-api-key header)
- ✅ Lambda integration configured for all endpoints (AWS_PROXY)
- ✅ Stage: poc
- ✅ Region: us-east-1
- ✅ NO delete or administrative endpoints

### Contract Test Results
- ✅ POST /tickets: Create ticket returns 201 with ticket_id
- ✅ GET /tickets/{id}: Retrieve ticket returns 200 with ticket data
- ✅ POST /tickets/{id}/comments: Add comment returns 200 with success
- ✅ GET /tickets?caller={caller_id}: List tickets returns 200 with array
- ✅ Authentication: Request without API key returns 403

**All 5 contract tests PASSED ✅**

---

## Rollback Commands

If rollback is needed, execute in this order:

### 1. Delete Usage Plan Key Association
```bash
aws apigateway delete-usage-plan-key \
  --usage-plan-id 4ym2fl \
  --key-id r3k6upsgse \
  --region us-east-1
```

### 2. Delete Usage Plan
```bash
aws apigateway delete-usage-plan \
  --usage-plan-id 4ym2fl \
  --region us-east-1
```

### 3. Delete API Key
```bash
aws apigateway delete-api-key \
  --api-key-id r3k6upsgse \
  --region us-east-1
```

### 4. Remove Lambda Permission
```bash
aws lambda remove-permission \
  --function-name poc-itsm-api-handler \
  --statement-id apigateway-invoke-permission \
  --region us-east-1
```

### 5. Delete API Gateway
```bash
aws apigateway delete-rest-api \
  --rest-api-id iixw3qtwo3 \
  --region us-east-1
```

### Verification
```bash
aws apigateway get-rest-api --rest-api-id iixw3qtwo3 --region us-east-1
```
Expected: NotFoundException error

---

## Task Status

**Task 1.5: API Gateway or Lambda Function URL Setup - COMPLETE ✅**

All acceptance criteria met:
- API Gateway REST API created with 4 endpoints
- API key authentication configured and working
- Lambda proxy integration configured for all methods
- Usage plan with throttling and quota limits
- All 5 contract tests passed (4 operations + authentication test)
- NO delete or administrative endpoints exposed
- All resources in us-east-1

**API Endpoint:** https://iixw3qtwo3.execute-api.us-east-1.amazonaws.com/poc  
**API Key:** h8IwZBHEEd5FLaeY6QsnS2SlsJ7tdyN23FQEEJUa

Ready for Task 1.6: S3 Bucket for OpenAPI Spec Storage.
