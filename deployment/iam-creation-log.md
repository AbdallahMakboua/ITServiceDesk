# IAM Role and Policy Creation Log - Task 1.2

## Deployment Information

**Timestamp:** 2026-02-09T12:10:15+00:00  
**Role Name:** poc-itsm-lambda-role  
**Role ARN:** arn:aws:iam::714059461907:role/poc-itsm-lambda-role  
**Role ID:** AROA2MQKCWUJU7P56FQC3  
**Policy Name:** poc-itsm-lambda-policy  
**Policy ARN:** arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy  
**Policy ID:** ANPA2MQKCWUJQUFT3FATR

---

## Commands Executed

### 1. Create IAM Role
```bash
aws iam create-role \
  --role-name poc-itsm-lambda-role \
  --assume-role-policy-document file://deployment/iam-trust-policy-lambda.json \
  --description "PoC Lambda role for mock ITSM API handler with least-privilege DynamoDB access" \
  --tags Key=Environment,Value=PoC Key=Project,Value=AI-L1-Support
```

### 2. Create IAM Policy
```bash
aws iam create-policy \
  --policy-name poc-itsm-lambda-policy \
  --policy-document file://deployment/iam-policy-lambda.json \
  --description "PoC Lambda policy with least-privilege access to DynamoDB table poc-itsm-tickets and CloudWatch Logs" \
  --tags Key=Environment,Value=PoC Key=Project,Value=AI-L1-Support
```

### 3. Attach Policy to Role
```bash
aws iam attach-role-policy \
  --role-name poc-itsm-lambda-role \
  --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy
```

### 4. Verify Role
```bash
aws iam get-role --role-name poc-itsm-lambda-role
```

### 5. Verify Attached Policies
```bash
aws iam list-attached-role-policies --role-name poc-itsm-lambda-role
```

### 6. Verify Policy Document
```bash
aws iam get-policy-version --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy --version-id v1
```

---

## IAM Policy Document

### Trust Policy (AssumeRole)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Permissions Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBTableAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:714059461907:table/poc-itsm-tickets",
        "arn:aws:dynamodb:us-east-1:714059461907:table/poc-itsm-tickets/index/CallerIdIndex"
      ]
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:714059461907:log-group:/aws/lambda/poc-itsm-api-handler:*"
    }
  ]
}
```

---

## Verification Results

### Role Configuration
- **Role Name:** poc-itsm-lambda-role ✅
- **Trust Policy:** lambda.amazonaws.com can assume role ✅
- **Tags:** Environment=PoC, Project=AI-L1-Support ✅

### Policy Configuration
- **Policy Name:** poc-itsm-lambda-policy ✅
- **Attached to Role:** Yes ✅
- **Tags:** Environment=PoC, Project=AI-L1-Support ✅

### Permissions Analysis
**DynamoDB Permissions:**
- ✅ dynamodb:PutItem (for creating tickets)
- ✅ dynamodb:GetItem (for retrieving ticket by ID)
- ✅ dynamodb:UpdateItem (for adding comments)
- ✅ dynamodb:Query (for listing tickets by caller_id via GSI)
- ✅ Scoped to specific table: poc-itsm-tickets
- ✅ Scoped to specific GSI: CallerIdIndex

**CloudWatch Logs Permissions:**
- ✅ logs:CreateLogGroup
- ✅ logs:CreateLogStream
- ✅ logs:PutLogEvents
- ✅ Scoped to specific log group: /aws/lambda/poc-itsm-api-handler

### Wildcard Permission Check
- ✅ NO wildcard (*) permissions in Action fields
- ✅ NO wildcard (*) permissions in DynamoDB Resource ARNs
- ✅ CloudWatch Logs uses `:*` suffix for log streams (standard AWS practice, scoped to specific log group)

---

## Acceptance Criteria Validation

✅ Maps to Requirement 14.1: Lambda IAM role limited to DynamoDB operations on poc-itsm-tickets  
✅ Maps to Requirement 14.4: NO wildcard (*) permissions in actions or DynamoDB resources  
✅ Policy allows: dynamodb:PutItem, GetItem, UpdateItem, Query on poc-itsm-tickets table and CallerIdIndex  
✅ Policy allows: logs:CreateLogGroup, CreateLogStream, PutLogEvents (CloudWatch logging)  
✅ NO administrative or privileged permissions  
✅ Trust policy allows lambda.amazonaws.com to assume role  
✅ Least-privilege principle followed  

---

## Rollback Commands

If rollback is needed, execute in this order:

### 1. Detach Policy from Role
```bash
aws iam detach-role-policy \
  --role-name poc-itsm-lambda-role \
  --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy
```

### 2. Delete IAM Policy
```bash
aws iam delete-policy \
  --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy
```

### 3. Delete IAM Role
```bash
aws iam delete-role \
  --role-name poc-itsm-lambda-role
```

### Verification
```bash
aws iam get-role --role-name poc-itsm-lambda-role
```
Expected: NoSuchEntity error

```bash
aws iam get-policy --policy-arn arn:aws:iam::714059461907:policy/poc-itsm-lambda-policy
```
Expected: NoSuchEntity error

---

## Task Status

**Task 1.2: Lambda IAM Role Creation - COMPLETE ✅**

All acceptance criteria met. IAM role and policy created with least-privilege permissions. Ready for Lambda function deployment.
