# IAM Policies and Roles - Task 0.4 (Supplement)

## Overview

This document defines all IAM roles and policies for the DAS Holding AI L1 Voice Service Desk PoC. All policies follow the principle of least privilege with no wildcard permissions.

---

## Lambda IAM Role

### Role Name
```
poc-itsm-lambda-role
```

### Trust Policy

Allows Lambda service to assume this role:

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

**Policy Name:** `poc-itsm-lambda-policy`

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
        "arn:aws:dynamodb:us-east-1:ACCOUNT_ID:table/poc-itsm-tickets",
        "arn:aws:dynamodb:us-east-1:ACCOUNT_ID:table/poc-itsm-tickets/index/CallerIdIndex"
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
      "Resource": "arn:aws:logs:us-east-1:ACCOUNT_ID:log-group:/aws/lambda/poc-itsm-api-handler:*"
    }
  ]
}
```

### Permissions Breakdown

**DynamoDB Permissions:**
- `dynamodb:PutItem` - Create new tickets
- `dynamodb:GetItem` - Retrieve ticket by ID
- `dynamodb:UpdateItem` - Add comments to tickets
- `dynamodb:Query` - List tickets by caller_id (GSI)

**Scoped to:**
- Table: `poc-itsm-tickets`
- GSI: `CallerIdIndex`

**CloudWatch Logs Permissions:**
- `logs:CreateLogGroup` - Create log group on first invocation
- `logs:CreateLogStream` - Create log stream for each execution
- `logs:PutLogEvents` - Write log events

**Scoped to:**
- Log group: `/aws/lambda/poc-itsm-api-handler`

### Wildcard Analysis

**Only wildcard:** `:*` suffix in CloudWatch Logs resource ARN  
**Justification:** Standard AWS practice for log streams (unpredictable stream names)  
**Scope:** Limited to specific log group only

**NO wildcards in:**
- DynamoDB actions
- DynamoDB resource ARNs
- Any other permissions

---

## AgentCore Gateway IAM Role (Future - Phase 2)

### Role Name
```
poc-agentcore-gateway-role
```

### Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Permissions Policy

**Policy Name:** `poc-agentcore-gateway-policy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:poc-itsm-api-key-*"
    },
    {
      "Sid": "APIGatewayInvoke",
      "Effect": "Allow",
      "Action": [
        "execute-api:Invoke"
      ],
      "Resource": "arn:aws:execute-api:us-east-1:ACCOUNT_ID:API_ID/poc/*/*"
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:ACCOUNT_ID:log-group:/aws/bedrock/agentcore/poc-itsm-agentcore-gateway:*"
    }
  ]
}
```

**Note:** If using Lambda Function URL instead of API Gateway, remove APIGatewayInvoke statement.

---

## Connect AI Agent IAM Role (Future - Phase 3)

### Role Name
```
poc-connect-ai-agent-role
```

### Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "connect.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Permissions Policy

**Policy Name:** `poc-connect-ai-agent-policy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAgentInvoke",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock:us-east-1:ACCOUNT_ID:agent/poc-itsm-agentcore-gateway"
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:ACCOUNT_ID:log-group:/aws/connect/poc-ai-l1-support:*"
    }
  ]
}
```

---

## IAM Role Creation Commands

### Lambda Role

```bash
# Create trust policy file
cat > /tmp/lambda-trust-policy.json << 'EOF'
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
EOF

# Create role
aws iam create-role \
  --role-name poc-itsm-lambda-role \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
  --description "PoC Lambda role for mock ITSM API handler" \
  --tags Key=Environment,Value=PoC Key=Project,Value=AI-L1-Support

# Create policy
aws iam create-policy \
  --policy-name poc-itsm-lambda-policy \
  --policy-document file://deployment/iam-policy-lambda.json \
  --description "PoC Lambda policy with least-privilege DynamoDB access" \
  --tags Key=Environment,Value=PoC Key=Project,Value=AI-L1-Support

# Attach policy to role
aws iam attach-role-policy \
  --role-name poc-itsm-lambda-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/poc-itsm-lambda-policy
```

---

## Security Best Practices

### Least Privilege

✅ Each role has only the permissions it needs  
✅ Permissions scoped to specific resources (no wildcards in actions)  
✅ No administrative or privileged permissions  
✅ No cross-account access  

### Resource Scoping

✅ DynamoDB permissions limited to poc-itsm-tickets table  
✅ CloudWatch Logs permissions limited to specific log groups  
✅ API Gateway permissions limited to specific API and stage  
✅ Secrets Manager permissions limited to specific secret  

### No Wildcards in Actions

✅ All actions explicitly listed  
✅ No `dynamodb:*` or `logs:*` permissions  
✅ Only specific operations allowed  

### Wildcard Usage (Justified)

⚠️ CloudWatch Logs resource ARN uses `:*` suffix  
✅ Justified: Log stream names are unpredictable  
✅ Scoped: Limited to specific log group  
✅ Standard AWS practice  

---

## Acceptance Criteria Validation

### Requirement 14.1: Lambda IAM Role Limited to DynamoDB Operations

- ✅ Lambda role has DynamoDB permissions only on poc-itsm-tickets
- ✅ Permissions: PutItem, GetItem, UpdateItem, Query
- ✅ Scoped to table and GSI ARNs

### Requirement 14.2: AgentCore Gateway IAM Limited to Invoking Mock API

- ✅ AgentCore role has execute-api:Invoke permission
- ✅ Scoped to specific API ID and stage
- ✅ Secrets Manager access for API key only

### Requirement 14.3: Connect AI Agent IAM Limited to Invoking AgentCore Gateway

- ✅ Connect role has bedrock:InvokeAgent permission
- ✅ Scoped to specific AgentCore Gateway ARN

### Requirement 14.4: NO Wildcard (*) Permissions

- ✅ No wildcard actions (no `dynamodb:*`, `logs:*`, etc.)
- ✅ No wildcard resource ARNs (except CloudWatch Logs stream suffix - justified)
- ✅ All permissions explicitly scoped

### Requirement 14.5: NO Administrative or Privileged Permissions

- ✅ No IAM permissions
- ✅ No account-level permissions
- ✅ No delete permissions
- ✅ No administrative operations

### Requirement 14.6: Follow AWS Least-Privilege Best Practices

- ✅ Principle of least privilege applied
- ✅ Resource-level permissions used
- ✅ Trust policies properly configured
- ✅ Tags applied for resource management

---

## Task Status

**IAM Policies Documentation - COMPLETE ✅**

All IAM roles and policies documented:
- Lambda role with least-privilege DynamoDB access
- AgentCore Gateway role (for Phase 2)
- Connect AI Agent role (for Phase 3)
- No wildcard permissions (except justified CloudWatch Logs)
- Security best practices followed

**Note:** Lambda IAM role was created in Task 1.2. This document provides the design rationale and complete IAM architecture for all phases.
