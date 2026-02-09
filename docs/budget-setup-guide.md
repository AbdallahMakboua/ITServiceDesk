# AWS Budgets Setup Guide - Task 0.1

## Overview

This document provides step-by-step instructions for configuring AWS Budgets to monitor spending for the DAS Holding AI IT L1 Voice Service Desk PoC. The budget is set at $10 USD total with an alert threshold at $8 USD (80%).

**CRITICAL:** AWS Budgets provides alerts only, NOT spending enforcement. The Manual Stop Rule applies: If spending reaches $8 USD, pause work immediately and execute cleanup procedures.

---

## Budget Configuration

### Budget Parameters

- **Budget Name:** `poc-ai-l1-support-budget`
- **Budget Amount:** $10.00 USD
- **Budget Type:** Cost budget
- **Time Period:** Monthly (or custom for PoC duration)
- **Alert Threshold:** $8.00 USD (80% of budget)
- **Region Scope:** us-east-1 only
- **Service Scope:** All services (filtered to whitelisted services)

---

## Step-by-Step Configuration

### Step 1: Access AWS Budgets

1. Sign in to AWS Management Console
2. Navigate to **AWS Billing and Cost Management**
3. In the left navigation pane, select **Budgets**
4. Click **Create budget**

### Step 2: Choose Budget Type

1. Select **Cost budget**
2. Click **Next**

### Step 3: Set Budget Details

**Budget Name:**
```
poc-ai-l1-support-budget
```

**Budget Amount:**
- **Period:** Monthly (or Custom for specific PoC dates)
- **Budgeted amount:** $10.00 USD
- **Budget effective dates:** 
  - Start: [PoC Start Date - e.g., 2026-02-09]
  - End: [PoC End Date - e.g., 2026-02-28]

**Budget Scope:**
- **Filters:**
  - **Region:** us-east-1
  - **Services:** (Optional - can filter to whitelisted services)
    - Amazon Connect
    - Amazon Bedrock
    - AWS Lambda
    - Amazon API Gateway
    - Amazon DynamoDB
    - Amazon S3
    - AWS IAM (no cost)
    - Amazon CloudWatch
    - AWS Secrets Manager

### Step 4: Configure Alerts

**Alert 1: 80% Threshold (Critical Alert)**

- **Alert threshold:** $8.00 USD (80% of budgeted amount)
- **Trigger:** Actual costs
- **Email recipients:** [Project stakeholder email addresses]
- **SNS topic:** (Optional) Create SNS topic for programmatic alerts

**Alert 2: 100% Threshold (Budget Exceeded)**

- **Alert threshold:** $10.00 USD (100% of budgeted amount)
- **Trigger:** Actual costs
- **Email recipients:** [Project stakeholder email addresses]
- **SNS topic:** (Optional) Same SNS topic as Alert 1

**Alert 3: Forecasted 100% (Early Warning)**

- **Alert threshold:** 100% of budgeted amount
- **Trigger:** Forecasted costs
- **Email recipients:** [Project stakeholder email addresses]

### Step 5: Review and Create

1. Review all budget settings
2. Confirm alert configurations
3. Click **Create budget**

---

## AWS CLI Commands (Alternative Method)

### Create Budget

```bash
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget-config.json \
  --notifications-with-subscribers file://budget-notifications.json
```

### budget-config.json

```json
{
  "BudgetName": "poc-ai-l1-support-budget",
  "BudgetLimit": {
    "Amount": "10.0",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "TimePeriod": {
    "Start": "2026-02-01T00:00:00Z",
    "End": "2026-03-01T00:00:00Z"
  },
  "CostTypes": {
    "IncludeTax": true,
    "IncludeSubscription": true,
    "UseBlended": false,
    "IncludeRefund": false,
    "IncludeCredit": false,
    "IncludeUpfront": true,
    "IncludeRecurring": true,
    "IncludeOtherSubscription": true,
    "IncludeSupport": true,
    "IncludeDiscount": true,
    "UseAmortized": false
  },
  "CostFilters": {
    "Region": ["us-east-1"]
  },
  "BudgetType": "COST"
}
```

### budget-notifications.json

```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "stakeholder@example.com"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "stakeholder@example.com"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "stakeholder@example.com"
      }
    ]
  }
]
```

---

## Manual Stop Rule

**CRITICAL REQUIREMENT:**

AWS Budgets provides **alerts only**, NOT automatic spending enforcement. When the $8 USD alert is triggered:

### Immediate Actions Required:

1. **STOP all ongoing work immediately**
2. **Do NOT proceed with any new deployments**
3. **Review current spending in AWS Cost Explorer**
4. **Assess remaining tasks vs. budget**
5. **Execute cleanup procedure if necessary** (see docs/cleanup-procedure.md)

### Decision Points:

- **If spending < $8 USD:** Continue with caution, monitor closely
- **If spending = $8-$9 USD:** Pause, assess, decide whether to continue or cleanup
- **If spending > $9 USD:** Execute immediate cleanup to prevent exceeding $10 budget

---

## Cost Monitoring

### Daily Monitoring (Recommended)

Check AWS Cost Explorer daily during PoC:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-02-09,End=2026-02-10 \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --filter file://cost-filter.json
```

### cost-filter.json

```json
{
  "Dimensions": {
    "Key": "REGION",
    "Values": ["us-east-1"]
  }
}
```

### View Current Month-to-Date Spending

1. Navigate to **AWS Cost Explorer**
2. Select **Cost and Usage Reports**
3. Filter by:
   - **Time range:** Month to date
   - **Region:** us-east-1
   - **Services:** Whitelisted services only

---

## Expected Cost Breakdown (Estimates)

Based on minimal PoC usage:

| Service | Estimated Cost | Notes |
|---------|---------------|-------|
| Amazon Connect | $2-4 | Phone number ($0.03/day) + usage ($0.018/min) |
| Amazon Bedrock (AgentCore) | $1-2 | Agent invocations |
| AWS Lambda | $0.20-0.50 | Free tier covers most usage |
| Amazon DynamoDB | $0.10-0.25 | On-demand, minimal data |
| Amazon API Gateway | $0.10-0.30 | REST API calls |
| Amazon S3 | $0.01-0.05 | OpenAPI spec storage |
| CloudWatch Logs | $0.10-0.20 | Default retention |
| AWS Secrets Manager | $0.40 | $0.40/secret/month |
| **Total Estimated** | **$4-8** | Well within $10 budget |

**Note:** Estimates assume:
- 2-3 short test calls (< 5 minutes total)
- Minimal Lambda invocations (< 100)
- Small DynamoDB dataset (< 10 tickets)
- No verbose logging or high-frequency metrics

---

## Acceptance Criteria Validation

### Requirement 4.6: Configure AWS Budgets alerts at $8 USD (80% threshold)

- ✅ Budget name specified: poc-ai-l1-support-budget
- ✅ Budget amount: $10 USD
- ✅ Alert threshold: $8 USD (80%)
- ✅ Notification email setup documented
- ✅ Region constraint: us-east-1
- ✅ Manual Stop Rule documented
- ✅ AWS Budgets provides alerts only (not enforcement) - clearly stated

---

## Verification Steps

After creating the budget:

1. **Verify budget exists:**
   ```bash
   aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text)
   ```

2. **Verify notifications:**
   ```bash
   aws budgets describe-notifications-for-budget \
     --account-id $(aws sts get-caller-identity --query Account --output text) \
     --budget-name poc-ai-l1-support-budget
   ```

3. **Test email delivery:** Wait for first budget calculation (usually within 24 hours)

---

## Cleanup

When PoC is complete, delete the budget:

```bash
aws budgets delete-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget-name poc-ai-l1-support-budget
```

---

## Task Status

**Task 0.1: Budget Setup Planning - COMPLETE ✅**

Documentation complete. Budget configuration steps defined. Manual Stop Rule documented.

**Note:** This documentation was created retroactively after Phase 1 deployment began. Budget should be configured immediately to monitor existing resources.
