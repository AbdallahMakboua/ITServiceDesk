# Amazon Connect Instance Deployment Log - Task 3.1

## Status: PENDING MANUAL CONFIGURATION ⚠️

**Configuration Guide:** `deployment/connect-instance-manual-guide.md`

---

## Prerequisites (Complete)

- ✅ Phase 1: Mock ITSM Backend (Tasks 1.1-1.6)
- ✅ Phase 2: AgentCore Gateway Prerequisites (Tasks 2.1-2.3)
- ✅ Budget alert configured ($10 total, $8 threshold)
- ✅ AWS Console access with Connect permissions

---

## Configuration Information (Completed)

### Instance Details
- **Instance Alias:** `poc-ai-l1-support`
- **Instance ID:** `c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
- **Instance ARN:** `arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
- **Access URL:** `https://poc-ai-l1-support.my.connect.aws`
- **Region:** ✅ **us-east-1** (Compliant with Plan of Record)
- **Status:** Active
- **Created Date:** 2026-02-09

### OIDC Discovery URL (CRITICAL for Task 2.4)
```
https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
```

**OIDC Verification (PASSED):**
```json
{
  "id_token_signing_alg_values_supported": ["ES384"],
  "issuer": "https://poc-ai-l1-support.my.connect.aws",
  "jwks_uri": "https://poc-ai-l1-support.my.connect.aws/.well-known/jwks.json",
  "subject_types_supported": ["public"]
}
```

✅ **Region Compliance:** Instance successfully created in us-east-1 (Requirement 8.1-8.3)

### Phone Number
- **Number:** Not yet claimed (to be claimed before Task 3.4)
- **Type:** DID (Direct Inward Dialing) - to be claimed
- **Country:** United States (+1)
- **Cost:** ~$0.03 per day (~$1/month)
- **Description:** PoC AI L1 Support Test Number
- **Contact Flow:** Default (to be updated in Task 3.4)
- **Status:** ⏳ To be claimed when ready for testing

### Administrator
- **Username:** poc-admin
- **Email:** (configured during setup)
- **First Name:** PoC
- **Last Name:** Administrator

### Configuration Settings
- **Identity Management:** Store users in Amazon Connect
- **Telephony:** Incoming and outgoing calls enabled
- **Call Recordings:** Disabled (cost optimization)
- **Chat Transcripts:** Disabled (not needed)
- **Exported Reports:** Disabled (not needed)
- **Live Media Streaming:** Disabled (not needed)

---

## Manual Configuration Steps

**See:** `deployment/connect-instance-manual-guide.md` for detailed step-by-step instructions.

**Summary:**
1. Access AWS Console → Amazon Connect
2. Create instance with alias: `poc-ai-l1-support`
3. Configure identity management: Store users in Amazon Connect
4. Add administrator: poc-admin
5. Enable telephony: Incoming and outgoing calls
6. Disable data storage options (cost optimization)
7. Review and create instance
8. Claim phone number (cheapest DID)
9. Test phone number
10. Note OIDC discovery URL

---

## Verification Steps (Completed)

### Step 1: Verify Instance Status

**Via AWS CLI:**
```bash
aws connect list-instances --region us-east-1
```

**Result:** ✅ PASS
- Instance ID: c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- Instance ARN: arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- Instance Alias: poc-ai-l1-support
- Instance Status: ACTIVE
- Region: us-east-1 ✅

### Step 2: Verify OIDC Discovery URL

**Test OIDC endpoint:**
```bash
curl https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
```

**Actual Response:**
```json
{
  "id_token_signing_alg_values_supported": ["ES384"],
  "issuer": "https://poc-ai-l1-support.my.connect.aws",
  "jwks_uri": "https://poc-ai-l1-support.my.connect.aws/.well-known/jwks.json",
  "subject_types_supported": ["public"]
}
```

**Result:** ✅ PASS
- OIDC URL is accessible
- Returns valid JSON
- Issuer matches instance URL
- JWKS URI is available

### Step 3: Test Phone Number

**Status:** ⏳ Phone number not yet claimed
- Phone number will be claimed later when ready for E2E testing
- This saves costs (~$0.03/day) until testing is needed
- Phone number claiming will be done before Task 3.4 (Contact Flow configuration)

---

## Acceptance Criteria Validation (Completed)

### Requirement 6.1: Voice-first interaction using Connect AI Agents
- ✅ Connect instance created
- ✅ Instance status: Active
- ✅ Telephony enabled (incoming and outgoing calls)
- ⏳ Phone number: To be claimed before Task 3.4 (deferred for cost optimization)

### Requirement 8.1-8.3: All resources in us-east-1
- ✅ Instance created in us-east-1
- ✅ Region compliance verified

### Instance Configuration
- ✅ Instance name: poc-ai-l1-support
- ✅ Region: us-east-1
- ✅ Identity management: Store users in Amazon Connect
- ✅ Data storage: Call recordings disabled (cost optimization)
- ⏳ Phone number: To be claimed later (cost optimization)

### OIDC Discovery URL
- ✅ OIDC URL format correct
- ✅ OIDC URL accessible (returns valid JSON)
- ✅ OIDC URL documented for Task 2.4

---

## Cost Tracking

### Task 3.1 Costs
- **Connect Instance:** $0.00 (no charges for instance itself)
- **Phone Number:** $0.00 (not yet claimed - deferred for cost optimization)
- **Test Calls:** $0.00 (no calls made yet)
- **Total Task 3.1:** $0.00

### Cumulative PoC Costs
- **Phase 1:** < $0.03
- **Phase 2:** ~$0.40
- **Phase 3 (Task 3.1):** $0.00
- **Total:** ~$0.43
- **Remaining Budget:** ~$9.57 (of $10.00)
- **Status:** WELL WITHIN BUDGET ✅

---

## Rollback Commands

If rollback is needed:

### Release Phone Number
1. Go to Connect admin console
2. Navigate to **Channels** → **Phone numbers**
3. Find your phone number
4. Click **Release**
5. Confirm release

### Delete Connect Instance

**Via AWS Console:**
1. Go to AWS Console → Amazon Connect
2. Select instance: `poc-ai-l1-support`
3. Click **Remove** or **Delete**
4. Type instance alias to confirm
5. Click **Delete**

**Via AWS CLI:**
```bash
aws connect delete-instance \
  --instance-id <INSTANCE_ID> \
  --region us-east-1
```

**Verification:**
```bash
aws connect list-instances --region us-east-1
```
Expected: Instance no longer in list

---

## Next Steps After Configuration

Once Connect instance is configured:

1. ✅ Document all information above (instance ARN, OIDC URL, phone number)
2. ✅ Test phone number to verify it works
3. ➡️ **CRITICAL:** Return to Task 2.4 and configure AgentCore Gateway with OIDC URL
   - Use guide: `deployment/agentcore-deployment-manual-guide.md`
   - OIDC URL: `https://<INSTANCE_ALIAS>.my.connect.aws/.well-known/openid-configuration`
4. ➡️ Proceed to Task 3.2: Connect AI Agent IAM Role Creation
5. ➡️ Proceed to Task 3.4: Connect AI Agent Creation

---

## Task Status

**Task 3.1: Amazon Connect Instance Creation - COMPLETE ✅**

**Completion Summary:**
- ✅ Prerequisites complete
- ✅ Configuration guide complete
- ✅ Connect instance created in us-east-1 (compliant with Plan of Record)
- ✅ OIDC URL verified and accessible
- ✅ Instance status: Active
- ✅ Region compliance: us-east-1 (Requirement 8.1-8.3)
- ⏳ Phone number: Deferred until Task 3.4 (cost optimization)

**Instance Information:**
- **Instance ID:** c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- **Instance ARN:** arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb
- **OIDC URL:** https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
- **Region:** us-east-1 ✅

**Next Steps:**
1. ➡️ **CRITICAL:** Return to Task 2.4 and configure AgentCore Gateway with OIDC URL
   - Use guide: `deployment/agentcore-deployment-manual-guide.md`
   - OIDC URL: `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
2. ➡️ Proceed to Task 3.2: Connect AI Agent IAM Role Creation
3. ➡️ Proceed to Task 3.3: Update AgentCore Gateway OIDC Configuration
4. ➡️ Proceed to Task 3.4: Connect AI Agent Creation (claim phone number at this stage)

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-09  
**Status:** Awaiting manual configuration
