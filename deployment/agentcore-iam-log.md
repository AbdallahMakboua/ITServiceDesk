# AgentCore Gateway IAM Role Deployment Log - Task 2.2

## Deployment Information

**Timestamp:** 2026-02-09T15:45:35+00:00  
**Role Name:** poc-agentcore-gateway-role  
**Role ARN:** arn:aws:iam::714059461907:role/poc-agentcore-gateway-role  
**Role ID:** AROA2MQKCWUJSAOSZRS2C  
**Policy Name:** poc-agentcore-gateway-policy  
**Policy ARN:** arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy  
**Policy ID:** ANPA2MQKCWUJ2DMWAXJRN

---

## Commands Executed

### 1. Create Trust Policy File
```bash
cat > deployment/iam-trust-policy-agentcore.json << 'EOF'
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
EOF
```

### 2. Create Permissions Policy File
```bash
cat > deployment/iam-policy-agentcore.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-*"
    },
    {
      "Sid": "APIGatewayInvoke",
      "Effect": "Allow",
      "Action": [
        "execute-api:Invoke"
      ],
      "Resource": "arn:aws:execute-api:us-east-1:714059461907:iixw3qtwo3/poc/*/*"
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:714059461907:log-group:/aws/bedrock/agentcore/poc-itsm-agentcore-gateway:*"
    }
  ]
}
EOF
```

### 3. Create IAM Role
```bash
aws iam create-role \
  --role-name poc-agentcore-gateway-role \
  --assume-role-policy-document file://deployment/iam-trust-policy-agentcore.json \
  --description "PoC AgentCore Gateway role for invoking Mock ITSM API" \
  --tags Key=Environment,Value=PoC Key=Project,Value=AI-L1-Support
```

**Result:**
- Role Name: poc-agentcore-gateway-role
- Role ARN: arn:aws:iam::714059461907:role/poc-agentcore-gateway-role
- Role ID: AROA2MQKCWUJSAOSZRS2C

### 4. Create IAM Policy
```bash
aws iam create-policy \
  --policy-name poc-agentcore-gateway-policy \
  --policy-document file://deployment/iam-policy-agentcore.json \
  --description "PoC AgentCore Gateway policy with least-privilege API Gateway and Secrets Manager access" \
  --tags Key=Environment,Value=PoC Key=Project,Value=AI-L1-Support
```

**Result:**
- Policy Name: poc-agentcore-gateway-policy
- Policy ARN: arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
- Policy ID: ANPA2MQKCWUJ2DMWAXJRN

### 5. Attach Policy to Role
```bash
aws iam attach-role-policy \
  --role-name poc-agentcore-gateway-role \
  --policy-arn arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
```

---

## IAM Role Configuration

### Role Details
- **Name:** poc-agentcore-gateway-role
- **ARN:** arn:aws:iam::714059461907:role/poc-agentcore-gateway-role
- **Role ID:** AROA2MQKCWUJSAOSZRS2C
- **Description:** PoC AgentCore Gateway role for invoking Mock ITSM API
- **Max Session Duration:** 3600 seconds (1 hour)
- **Path:** /

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

**Trust Relationship:**
- Allows: bedrock.amazonaws.com to assume this role ✅
- Enables: AgentCore Gateway to use this role for API calls

### Tags
| Key | Value |
|-----|-------|
| Environment | PoC |
| Project | AI-L1-Support |

---

## IAM Policy Configuration

### Policy Details
- **Name:** poc-agentcore-gateway-policy
- **ARN:** arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
- **Policy ID:** ANPA2MQKCWUJ2DMWAXJRN
- **Description:** PoC AgentCore Gateway policy with least-privilege API Gateway and Secrets Manager access
- **Version:** v1 (default)
- **Attachable:** Yes
- **Attachment Count:** 1 (attached to poc-agentcore-gateway-role)

### Permissions Policy
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
      "Resource": "arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-*"
    },
    {
      "Sid": "APIGatewayInvoke",
      "Effect": "Allow",
      "Action": [
        "execute-api:Invoke"
      ],
      "Resource": "arn:aws:execute-api:us-east-1:714059461907:iixw3qtwo3/poc/*/*"
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:714059461907:log-group:/aws/bedrock/agentcore/poc-itsm-agentcore-gateway:*"
    }
  ]
}
```

### Permissions Breakdown

#### 1. Secrets Manager Access
**Action:** `secretsmanager:GetSecretValue`  
**Resource:** `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-*`

**Purpose:** Retrieve Mock ITSM API key from Secrets Manager  
**Scope:** Limited to poc-itsm-api-key secret only  
**Wildcard:** `-*` suffix required (Secrets Manager adds random suffix to secret ARN)

#### 2. API Gateway Invoke
**Action:** `execute-api:Invoke`  
**Resource:** `arn:aws:execute-api:us-east-1:714059461907:iixw3qtwo3/poc/*/*`

**Purpose:** Invoke Mock ITSM API via API Gateway  
**Scope:** Limited to specific API (iixw3qtwo3) and stage (poc)  
**Wildcards:** `/*/*` for HTTP method and resource path (standard pattern for API Gateway)

#### 3. CloudWatch Logs Access
**Actions:** `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`  
**Resource:** `arn:aws:logs:us-east-1:714059461907:log-group:/aws/bedrock/agentcore/poc-itsm-agentcore-gateway:*`

**Purpose:** Write logs for AgentCore Gateway operations  
**Scope:** Limited to specific log group for this gateway  
**Wildcard:** `:*` suffix for log streams (unpredictable stream names)

---

## Wildcard Analysis

### NO Wildcards in Actions ✅
- ✅ All actions explicitly listed
- ✅ NO `secretsmanager:*`
- ✅ NO `execute-api:*`
- ✅ NO `logs:*`
- ✅ NO administrative or privileged permissions

### Wildcards in Resource ARNs (Justified)

#### Secrets Manager Resource
**Pattern:** `arn:aws:secretsmanager:us-east-1:714059461907:secret:poc-itsm-api-key-*`

**Wildcard:** `-*` suffix  
**Justification:** Secrets Manager automatically appends random suffix to secret ARNs  
**Example:** `poc-itsm-api-key-thEbs7`  
**Scope:** Limited to secrets starting with `poc-itsm-api-key` prefix ✅

#### API Gateway Resource
**Pattern:** `arn:aws:execute-api:us-east-1:714059461907:iixw3qtwo3/poc/*/*`

**Wildcards:** `/*/*` for HTTP method and resource path  
**Justification:** Standard AWS pattern for API Gateway permissions (allows all methods and paths)  
**Scope:** Limited to specific API ID (iixw3qtwo3) and stage (poc) ✅  
**Alternative:** Could specify exact paths, but would require 4 separate resource ARNs

#### CloudWatch Logs Resource
**Pattern:** `arn:aws:logs:us-east-1:714059461907:log-group:/aws/bedrock/agentcore/poc-itsm-agentcore-gateway:*`

**Wildcard:** `:*` suffix for log streams  
**Justification:** Log stream names are unpredictable (timestamps, execution IDs)  
**Scope:** Limited to specific log group ✅  
**Standard Practice:** AWS best practice for CloudWatch Logs permissions

---

## Verification Results

### Role Verification
```bash
aws iam get-role --role-name poc-agentcore-gateway-role
```

**Result:** ✅ Role created successfully
- Role ARN: arn:aws:iam::714059461907:role/poc-agentcore-gateway-role
- Trust policy: bedrock.amazonaws.com ✅
- Tags: Environment=PoC, Project=AI-L1-Support ✅

### Policy Verification
```bash
aws iam get-policy-version \
  --policy-arn arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy \
  --version-id v1
```

**Result:** ✅ Policy created successfully
- Policy ARN: arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
- Version: v1 (default)
- Permissions: Secrets Manager, API Gateway, CloudWatch Logs ✅

### Policy Attachment Verification
```bash
aws iam list-attached-role-policies --role-name poc-agentcore-gateway-role
```

**Result:** ✅ Policy attached successfully
- Attached Policy: poc-agentcore-gateway-policy
- Attachment Count: 1

### Wildcard Verification
**Actions:** ✅ NO wildcards in actions  
**Resources:** ✅ Wildcards justified and scoped appropriately

---

## Acceptance Criteria Validation

### Requirement 14.2: AgentCore Gateway IAM Limited to Invoking Mock API
- ✅ Policy allows: secretsmanager:GetSecretValue on poc-itsm-api-key
- ✅ Policy allows: execute-api:Invoke scoped to API Gateway (iixw3qtwo3/poc)
- ✅ Policy allows: CloudWatch Logs operations for debugging
- ✅ NO other permissions granted

### Requirement 14.4: NO Wildcard (*) Permissions
- ✅ NO wildcard actions (all actions explicitly listed)
- ✅ Resource wildcards justified:
  - Secrets Manager: Required for secret suffix
  - API Gateway: Standard pattern for methods/paths
  - CloudWatch Logs: Required for log streams
- ✅ All wildcards scoped to specific resources

### Trust Policy Verification
- ✅ Trust policy allows bedrock.amazonaws.com to assume role
- ✅ NO other principals allowed
- ✅ Correct service for AgentCore Gateway

### Tags Verification
- ✅ Environment: PoC
- ✅ Project: AI-L1-Support

---

## Security Best Practices

### Least Privilege ✅
- Only permissions needed for AgentCore Gateway operations
- Secrets Manager: Read-only access to specific secret
- API Gateway: Invoke-only access to specific API and stage
- CloudWatch Logs: Write-only access to specific log group

### Resource Scoping ✅
- Secrets Manager: Scoped to poc-itsm-api-key prefix
- API Gateway: Scoped to specific API ID (iixw3qtwo3) and stage (poc)
- CloudWatch Logs: Scoped to specific log group

### No Administrative Permissions ✅
- NO IAM permissions
- NO delete permissions
- NO account-level permissions
- NO cross-account access

### Trust Policy Security ✅
- Only bedrock.amazonaws.com can assume role
- NO wildcard principals
- NO cross-account trust relationships

---

## Usage for AgentCore Gateway

### Role ARN for AgentCore Gateway Configuration
```
arn:aws:iam::714059461907:role/poc-agentcore-gateway-role
```

### Permissions Granted
1. **Retrieve API Key:** Read poc-itsm-api-key from Secrets Manager
2. **Invoke API:** Call Mock ITSM API via API Gateway (iixw3qtwo3/poc)
3. **Write Logs:** Create log groups, streams, and write log events

### What AgentCore Gateway Can Do
- ✅ Get API key from Secrets Manager
- ✅ Invoke POST /tickets (create ticket)
- ✅ Invoke GET /tickets/{id} (get ticket status)
- ✅ Invoke POST /tickets/{id}/comments (add comment)
- ✅ Invoke GET /tickets?caller={caller_id} (list tickets)
- ✅ Write logs to CloudWatch

### What AgentCore Gateway CANNOT Do
- ❌ Access other secrets
- ❌ Invoke other APIs
- ❌ Delete or modify API Gateway configuration
- ❌ Delete or modify DynamoDB tables
- ❌ Access Lambda functions directly
- ❌ Perform any administrative operations

---

## Rollback Commands

If rollback is needed, execute in this order:

### 1. Detach Policy from Role
```bash
aws iam detach-role-policy \
  --role-name poc-agentcore-gateway-role \
  --policy-arn arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
```

### 2. Delete IAM Policy
```bash
aws iam delete-policy \
  --policy-arn arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy
```

### 3. Delete IAM Role
```bash
aws iam delete-role \
  --role-name poc-agentcore-gateway-role
```

### Verification
```bash
aws iam get-role --role-name poc-agentcore-gateway-role
```
Expected: NoSuchEntity error

---

## Task Status

**Task 2.2: AgentCore Gateway IAM Role Creation - COMPLETE ✅**

All acceptance criteria met:
- IAM role created: poc-agentcore-gateway-role
- IAM policy created: poc-agentcore-gateway-policy
- Policy attached to role
- Permissions: Secrets Manager (GetSecretValue), API Gateway (Invoke), CloudWatch Logs
- NO wildcard permissions in actions
- Resource wildcards justified and scoped
- Trust policy: bedrock.amazonaws.com
- Tags: Environment=PoC, Project=AI-L1-Support

**Role ARN:** arn:aws:iam::714059461907:role/poc-agentcore-gateway-role  
**Policy ARN:** arn:aws:iam::714059461907:policy/poc-agentcore-gateway-policy

Ready for Task 2.3: AgentCore Gateway Tool Definitions.
