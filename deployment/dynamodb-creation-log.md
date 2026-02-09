# DynamoDB Table Creation Log - Task 1.1

## Deployment Information

**Timestamp:** 2026-02-09T16:03:43.353000+04:00  
**Region:** us-east-1  
**Table Name:** poc-itsm-tickets  
**Table ARN:** arn:aws:dynamodb:us-east-1:714059461907:table/poc-itsm-tickets  
**Table ID:** d9128297-87c6-46ae-a1fd-3b8aff77e14b

---

## Commands Executed

### 1. Create Table
```bash
aws dynamodb create-table \
  --table-name poc-itsm-tickets \
  --attribute-definitions \
    AttributeName=ticket_id,AttributeType=S \
    AttributeName=caller_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
  --key-schema \
    AttributeName=ticket_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[{
      \"IndexName\": \"CallerIdIndex\",
      \"KeySchema\": [
        {\"AttributeName\": \"caller_id\", \"KeyType\": \"HASH\"},
        {\"AttributeName\": \"created_at\", \"KeyType\": \"RANGE\"}
      ],
      \"Projection\": {\"ProjectionType\": \"ALL\"}
    }]" \
  --tags \
    "[{\"Key\": \"Environment\", \"Value\": \"PoC\"}, {\"Key\": \"Project\", \"Value\": \"AI-L1-Support\"}]" \
  --region us-east-1
```

### 2. Wait for Table to Become Active
```bash
aws dynamodb wait table-exists --table-name poc-itsm-tickets --region us-east-1
```

### 3. Describe Table
```bash
aws dynamodb describe-table --table-name poc-itsm-tickets --region us-east-1
```

### 4. Query GSI Status
```bash
aws dynamodb describe-table --table-name poc-itsm-tickets --region us-east-1 --query 'Table.GlobalSecondaryIndexes[0].[IndexName,IndexStatus,KeySchema]'
```

### 5. List Tags
```bash
aws dynamodb list-tags-of-resource --resource-arn arn:aws:dynamodb:us-east-1:714059461907:table/poc-itsm-tickets --region us-east-1
```

---

## Verification Results

### Table Status
- **TableStatus:** ACTIVE ✅
- **BillingMode:** PAY_PER_REQUEST ✅
- **Region:** us-east-1 ✅

### Primary Key Schema
- **Partition Key:** ticket_id (String) ✅

### Global Secondary Index
- **IndexName:** CallerIdIndex ✅
- **IndexStatus:** ACTIVE ✅
- **Partition Key:** caller_id (String) ✅
- **Sort Key:** created_at (String) ✅
- **Projection:** ALL ✅

### Tags
- **Environment:** PoC ✅
- **Project:** AI-L1-Support ✅

### Attribute Definitions
- ticket_id (String) ✅
- caller_id (String) ✅
- created_at (String) ✅

---

## Acceptance Criteria Validation

✅ Maps to Requirement 1.5: DynamoDB table clearly labeled as non-production (poc-itsm-tickets prefix)  
✅ Maps to Requirement 13.1: Table name with clear non-production prefix  
✅ Maps to Requirement 13.2: Partition key is ticket_id (String)  
✅ Maps to Requirement 13.4: Billing mode is ON_DEMAND (PAY_PER_REQUEST)  
✅ Maps to Requirement 13.6: GSI CallerIdIndex with caller_id (partition) and created_at (sort key)  
✅ Region: us-east-1  
✅ Tags: Environment=PoC, Project=AI-L1-Support  

---

## Rollback Command

If rollback is needed, execute:

```bash
aws dynamodb delete-table --table-name poc-itsm-tickets --region us-east-1
```

Verify deletion:
```bash
aws dynamodb describe-table --table-name poc-itsm-tickets --region us-east-1
```
Expected: ResourceNotFoundException error

---

## Task Status

**Task 1.1: DynamoDB Table Creation - COMPLETE ✅**

All acceptance criteria met. Table is active and ready for use.
