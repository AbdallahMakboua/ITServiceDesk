# Task 3.1 Summary - Amazon Connect Instance Creation

**Date:** 2026-02-09  
**Task:** 3.1 - Amazon Connect Instance Creation  
**Status:** MANUAL CONFIGURATION REQUIRED ⚠️

---

## Overview

Task 3.1 requires creating an Amazon Connect instance through the AWS Console. This cannot be fully automated via CLI due to the interactive setup wizard and phone number claiming process.

---

## What Has Been Prepared

### ✅ Comprehensive Configuration Guide
**File:** `deployment/connect-instance-manual-guide.md`

**Contents:**
- Step-by-step Console instructions
- All configuration choices with recommendations
- Cost optimization tips
- OIDC URL format and location
- Phone number claiming instructions
- Verification steps
- Troubleshooting guide
- Rollback instructions

### ✅ Deployment Log Template
**File:** `deployment/connect-instance-log.md`

**Purpose:** Document actual configuration values after manual setup

**To be filled:**
- Instance alias
- Instance ARN
- OIDC discovery URL (CRITICAL for Task 2.4)
- Phone number
- Verification results
- Cost tracking

---

## Configuration Parameters (Ready to Use)

### Instance Configuration
- **Instance Alias:** `poc-ai-l1-support`
- **Region:** us-east-1
- **Identity Management:** Store users in Amazon Connect
- **Administrator:** poc-admin
- **Telephony:** Incoming and outgoing calls enabled
- **Data Storage:** All disabled (cost optimization)

### Phone Number
- **Type:** DID (Direct Inward Dialing)
- **Country:** United States (+1)
- **Selection:** Cheapest available number
- **Cost:** ~$0.03 per day (~$1/month)

### Cost Optimization
- ✅ Call recordings: Disabled
- ✅ Chat transcripts: Disabled
- ✅ Exported reports: Disabled
- ✅ Live media streaming: Disabled
- ✅ DID number (not toll-free)

---

## Critical Information Needed

After manual configuration, you MUST document:

### 1. Instance Alias
**Example:** `poc-ai-l1-support`

**Used for:** OIDC URL construction

### 2. OIDC Discovery URL (MOST IMPORTANT)
**Format:** `https://<INSTANCE_ALIAS>.my.connect.aws/.well-known/openid-configuration`

**Example:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`

**Why critical:** This URL is required for Task 2.4 (AgentCore Gateway configuration)

### 3. Phone Number
**Example:** `+1-555-123-4567`

**Used for:** Testing voice interactions

### 4. Instance ARN
**Format:** `arn:aws:connect:us-east-1:<ACCOUNT_ID>:instance/<INSTANCE_ID>`

**Used for:** IAM policies and Connect AI Agent configuration

---

## Workflow After Task 3.1

**Correct order:**

1. ✅ Complete Task 3.1 (Create Connect instance) - **YOU ARE HERE**
2. ✅ Note OIDC discovery URL
3. ➡️ **RETURN TO TASK 2.4:** Configure AgentCore Gateway with OIDC URL
   - Guide: `deployment/agentcore-deployment-manual-guide.md`
   - Use OIDC URL from Task 3.1
4. ➡️ Proceed to Task 3.2: Connect AI Agent IAM Role Creation
5. ➡️ Proceed to Task 3.4: Connect AI Agent Creation

**Why this order:**
- AgentCore Gateway (Task 2.4) needs Connect OIDC URL
- Connect OIDC URL is only available after Connect instance is created (Task 3.1)
- Therefore: Task 3.1 → Task 2.4 → Task 3.2 → Task 3.4

---

## Estimated Costs

### Task 3.1 Costs
- **Phone Number:** ~$0.03/day × 7 days = ~$0.21
- **Test Calls:** $0.018/min × 5 min = ~$0.09
- **Total Task 3.1:** ~$0.30

### Cumulative PoC Costs
- **Phase 1:** < $0.03
- **Phase 2:** ~$0.40
- **Phase 3 (Task 3.1):** ~$0.30
- **Total so far:** ~$0.73
- **Remaining:** ~$9.27 (of $10.00 budget)
- **Status:** WELL WITHIN BUDGET ✅

---

## Cost Optimization Reminders

1. ✅ Claim cheapest DID number (not toll-free)
2. ✅ Disable all data storage options
3. ⚠️ Keep test calls SHORT (2-3 minutes max)
4. ⚠️ Limit to 2-3 test calls total
5. ⚠️ **Release phone number immediately after testing**
6. ⚠️ **Delete Connect instance after PoC completion**

---

## Manual Configuration Steps (Summary)

1. **Access AWS Console** → Amazon Connect (us-east-1)
2. **Create instance:**
   - Alias: `poc-ai-l1-support`
   - Identity: Store users in Amazon Connect
   - Admin: poc-admin
   - Telephony: Incoming and outgoing enabled
   - Data storage: All disabled
3. **Claim phone number:**
   - Type: DID
   - Country: United States (+1)
   - Select cheapest available
4. **Test phone number:**
   - Call the number
   - Verify default message plays
5. **Document OIDC URL:**
   - Format: `https://<ALIAS>.my.connect.aws/.well-known/openid-configuration`
   - Save for Task 2.4

**Detailed guide:** `deployment/connect-instance-manual-guide.md`

---

## Verification Checklist

After manual configuration, verify:

- [ ] Instance status: Active
- [ ] Instance region: us-east-1
- [ ] Instance alias documented
- [ ] OIDC URL documented and accessible
- [ ] Phone number claimed
- [ ] Phone number tested (call connects)
- [ ] Default message plays
- [ ] Call disconnects properly
- [ ] All values documented in `deployment/connect-instance-log.md`

---

## Next Actions

### Immediate (After Manual Setup)
1. Complete `deployment/connect-instance-log.md` with actual values
2. Test phone number to verify it works
3. Verify OIDC URL is accessible: `curl https://<ALIAS>.my.connect.aws/.well-known/openid-configuration`

### Then
1. **Return to Task 2.4:** Configure AgentCore Gateway
   - Use OIDC URL from this task
   - Follow guide: `deployment/agentcore-deployment-manual-guide.md`
2. **Proceed to Task 3.2:** Create Connect AI Agent IAM role
3. **Proceed to Task 3.4:** Create Connect AI Agent

---

## Documentation Files

- **Configuration Guide:** `deployment/connect-instance-manual-guide.md` (complete)
- **Deployment Log:** `deployment/connect-instance-log.md` (template - to be filled)
- **Task Summary:** `deployment/task-3.1-summary.md` (this file)

---

## Task Status

**Task 3.1: Amazon Connect Instance Creation - MANUAL CONFIGURATION REQUIRED ⚠️**

**Status:** Configuration guide complete, awaiting manual setup

**Action Required:**
1. Follow guide: `deployment/connect-instance-manual-guide.md`
2. Create Connect instance via AWS Console
3. Claim phone number
4. Test phone number
5. Document OIDC URL
6. Complete deployment log: `deployment/connect-instance-log.md`
7. **THEN:** Return to Task 2.4 to configure AgentCore Gateway

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-09  
**Status:** Awaiting manual configuration
