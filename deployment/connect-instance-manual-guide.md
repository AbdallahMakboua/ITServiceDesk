# Amazon Connect Instance Manual Configuration Guide - Task 3.1

## Overview

This guide provides step-by-step instructions for creating an Amazon Connect instance for the DAS Holding AI IT L1 Voice Service Desk PoC.

**Instance Name:** `poc-ai-l1-support`  
**Region:** us-east-1  
**Purpose:** Voice-first AI support with Bedrock AgentCore Gateway integration

---

## Prerequisites

Before starting, ensure:
- ✅ AWS Console access with appropriate permissions
- ✅ Budget alert configured ($10 total, $8 threshold)
- ✅ Phase 1 and Phase 2 Tasks 2.1-2.3 complete
- ✅ Ready to claim a phone number (will incur charges)

---

## Cost Considerations

**Amazon Connect Pricing (us-east-1):**
- **Usage:** $0.018 per minute (voice)
- **Phone Number:** ~$0.03 per day (~$1/month for DID)
- **Estimated PoC Cost:** $1.50-$2.00 for 2-3 short test calls

**Cost Optimization Tips:**
1. Claim the **cheapest available DID** (Direct Inward Dialing number)
2. Keep test calls **short** (2-3 minutes maximum)
3. Limit to **2-3 test calls** total
4. **Release phone number immediately** after testing
5. **Delete Connect instance** after PoC completion

---

## Step-by-Step Configuration

### Step 1: Access Amazon Connect Console

1. Log in to AWS Console
2. Ensure region is set to **us-east-1** (top-right corner)
3. Navigate to **Amazon Connect** service
   - Search for "Connect" in the services search bar
   - Click **Amazon Connect**

---

### Step 2: Create Connect Instance

1. Click **Create instance** button

2. **Step 1: Identity management**
   
   **Choose identity management:**
   - Select: **Store users in Amazon Connect** (recommended for PoC)
   - Reason: Simplest setup, no external directory needed
   
   **Access URL (Instance Alias):**
   - Enter: `poc-ai-l1-support`
   - This creates the URL: `https://poc-ai-l1-support.my.connect.aws`
   - ⚠️ **IMPORTANT:** Note this alias - it's used in the OIDC URL
   - ⚠️ Must be globally unique across all AWS accounts
   - If taken, try: `poc-ai-l1-support-<your-initials>` or `poc-ai-l1-support-<random-number>`
   
   Click **Next**

3. **Step 2: Add administrator**
   
   **Administrator:**
   - **Username:** `poc-admin` (or your preferred username)
   - **First name:** PoC
   - **Last name:** Administrator
   - **Email:** Your email address (for password reset)
   - **Password:** (will be set via email)
   
   Click **Next**

4. **Step 3: Telephony options**
   
   **Select telephony options:**
   - ✅ **I want to handle incoming calls with Amazon Connect**
   - ✅ **I want to make outbound calls with Amazon Connect**
   
   **Early media:**
   - ☐ Leave unchecked (not needed for PoC)
   
   Click **Next**

5. **Step 4: Data storage**
   
   **Call recordings:**
   - ☐ **Disable call recordings** (to save costs)
   - Reason: Not needed for PoC, reduces S3 storage costs
   
   **Chat transcripts:**
   - ☐ **Disable chat transcripts** (not using chat)
   
   **Exported reports:**
   - ☐ **Disable exported reports** (not needed for PoC)
   
   **Live media streaming:**
   - ☐ **Disable live media streaming** (not needed)
   
   Click **Next**

6. **Step 5: Review and create**
   
   Review all settings:
   - ✅ Instance alias: `poc-ai-l1-support` (or your chosen alias)
   - ✅ Identity management: Store users in Amazon Connect
   - ✅ Administrator: poc-admin
   - ✅ Telephony: Incoming and outgoing calls enabled
   - ✅ Data storage: All disabled (cost optimization)
   
   Click **Create instance**

7. **Wait for instance creation**
   - Status will show "Creating..."
   - Takes 2-5 minutes
   - Wait until status shows "Active"

---

### Step 3: Note Instance Information

Once instance is created:

1. Click on the instance name (`poc-ai-l1-support`)

2. **Note the following information:**

   **Instance ARN:**
   ```
   arn:aws:connect:us-east-1:<ACCOUNT_ID>:instance/<INSTANCE_ID>
   ```
   
   **Instance Alias:**
   ```
   poc-ai-l1-support (or your chosen alias)
   ```
   
   **Access URL:**
   ```
   https://poc-ai-l1-support.my.connect.aws
   ```
   
   **OIDC Discovery URL (CRITICAL for Task 2.4):**
   ```
   https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
   ```
   
   ⚠️ **Save this OIDC URL - you'll need it for Task 2.4 (AgentCore Gateway configuration)**

---

### Step 4: Claim Phone Number

1. In the Connect instance details page, click **View contact flows** or **Open admin console**
   - This opens the Connect admin interface

2. In the left navigation, go to **Channels** → **Phone numbers**

3. Click **Claim a number**

4. **Select country/region:**
   - Choose: **United States** (+1)
   - Reason: Typically has cheapest DID numbers

5. **Select phone type:**
   - Choose: **DID (Direct Inward Dialing)**
   - Reason: Cheapest option (~$0.03/day vs. toll-free ~$0.06/day)

6. **Select a phone number:**
   - Browse available numbers
   - Choose the **first available number** (all are same price)
   - Click **Select** next to the number

7. **Configure phone number:**
   - **Description:** PoC AI L1 Support Test Number
   - **Contact flow/IVR:** Select **Default contact flow** (for now)
   - Click **Save**

8. **Note the phone number:**
   ```
   +1-XXX-XXX-XXXX
   ```
   
   ⚠️ **Save this number - you'll use it for testing**

---

### Step 5: Configure Contact Flow (Basic Setup)

For now, the default contact flow is sufficient. We'll configure the AI Agent contact flow in Task 3.4.

**Current setup:**
- Default contact flow plays a message and disconnects
- This is fine for verifying the phone number works

**To test the phone number:**
1. Call the number from your phone
2. You should hear: "Thank you for calling. Goodbye."
3. Call disconnects
4. ✅ This confirms the phone number is working

---

### Step 6: Enable Contact Lens (Optional)

Contact Lens provides analytics and insights. For PoC, this is optional.

**To enable (optional):**
1. In Connect admin console, go to **Analytics and optimization** → **Contact Lens**
2. Click **Enable Contact Lens**
3. Accept terms
4. **Note:** This may add minimal costs (~$0.015 per minute analyzed)

**Recommendation:** Skip this for PoC to minimize costs.

---

### Step 7: Configure Security Settings

1. In Connect admin console, go to **Users** → **Security profiles**

2. Review default security profiles:
   - **Admin:** Full access
   - **Agent:** Limited access
   - **CallCenterManager:** Supervisor access

3. For PoC, default profiles are sufficient

---

### Step 8: Verify Instance Configuration

**Via AWS Console:**

1. Go to AWS Console → Amazon Connect
2. Verify instance status: **Active**
3. Verify instance alias: `poc-ai-l1-support`
4. Verify region: us-east-1

**Via AWS CLI:**

```bash
# List Connect instances
aws connect list-instances --region us-east-1

# Describe specific instance (if you have instance ID)
aws connect describe-instance --instance-id <INSTANCE_ID> --region us-east-1
```

---

## Configuration Summary

After completing the setup, you should have:

### Instance Information
- **Instance Alias:** `poc-ai-l1-support` (or your chosen alias)
- **Instance ARN:** `arn:aws:connect:us-east-1:<ACCOUNT_ID>:instance/<INSTANCE_ID>`
- **Access URL:** `https://poc-ai-l1-support.my.connect.aws`
- **OIDC Discovery URL:** `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
- **Region:** us-east-1
- **Status:** Active

### Phone Number
- **Number:** `+1-XXX-XXX-XXXX`
- **Type:** DID (Direct Inward Dialing)
- **Country:** United States (+1)
- **Cost:** ~$0.03 per day (~$1/month)

### Configuration
- **Identity Management:** Store users in Amazon Connect
- **Administrator:** poc-admin
- **Telephony:** Incoming and outgoing calls enabled
- **Data Storage:** All disabled (cost optimization)
- **Call Recordings:** Disabled
- **Contact Flow:** Default (to be updated in Task 3.4)

---

## Post-Configuration Actions

### Immediate Actions

1. **Document OIDC URL:**
   - Save the OIDC discovery URL: `https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration`
   - You'll need this for Task 2.4 (AgentCore Gateway configuration)

2. **Test phone number:**
   - Call the number to verify it works
   - Should hear default message and disconnect
   - ✅ Confirms phone number is operational

3. **Complete deployment log:**
   - Fill in `deployment/connect-instance-log.md` with actual values
   - Document instance ARN, alias, phone number, OIDC URL

### Next Steps

1. ✅ **Task 3.1 Complete:** Amazon Connect instance created
2. ➡️ **Return to Task 2.4:** Configure AgentCore Gateway with OIDC URL
3. ➡️ **Proceed to Task 3.2:** Create Connect AI Agent IAM role
4. ➡️ **Proceed to Task 3.4:** Create Connect AI Agent and configure contact flow

---

## Troubleshooting

### Issue: Instance Alias Already Taken

**Error:** "The access URL you entered is already in use"

**Solution:**
- Try a different alias: `poc-ai-l1-support-<your-initials>`
- Or add a random number: `poc-ai-l1-support-001`
- The alias must be globally unique across all AWS accounts

### Issue: No Phone Numbers Available

**Error:** "No phone numbers available in this region"

**Solution:**
1. Try a different country/region
2. Try toll-free numbers (more expensive but more available)
3. Contact AWS Support to request phone numbers
4. Alternative: Use Amazon Connect Test Phone Number (if available)

### Issue: Cannot Access Admin Console

**Error:** "Access denied" when clicking "Open admin console"

**Solution:**
1. Verify you have Connect permissions in IAM
2. Try accessing directly: `https://poc-ai-l1-support.my.connect.aws`
3. Check if you need to set up administrator password via email

### Issue: Phone Number Not Working

**Problem:** Calling the number doesn't connect

**Solution:**
1. Verify phone number is claimed and saved
2. Check contact flow is assigned to the number
3. Verify telephony options are enabled (incoming calls)
4. Wait 2-3 minutes for number provisioning to complete
5. Try calling again

---

## Cost Monitoring

### Expected Costs for Task 3.1

- **Phone Number:** ~$0.03 per day (~$1 for PoC duration)
- **Test Calls:** ~$0.018 per minute × 5 minutes = ~$0.09
- **Total Task 3.1:** ~$1.10

### Cost Optimization Reminders

1. ✅ Disabled call recordings (saves S3 costs)
2. ✅ Disabled chat transcripts (not needed)
3. ✅ Disabled exported reports (not needed)
4. ✅ Chose DID over toll-free (cheaper)
5. ⚠️ **Remember to release phone number after testing**
6. ⚠️ **Remember to delete Connect instance after PoC**

---

## Rollback Instructions

### Release Phone Number

1. Go to Connect admin console
2. Navigate to **Channels** → **Phone numbers**
3. Find your phone number
4. Click **Release** or **Remove**
5. Confirm release

**Note:** You'll stop being charged for the number immediately.

### Delete Connect Instance

⚠️ **WARNING:** This deletes all configuration, contact flows, and data.

**Via AWS Console:**
1. Go to AWS Console → Amazon Connect
2. Select the instance (`poc-ai-l1-support`)
3. Click **Remove** or **Delete**
4. Type the instance alias to confirm
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
Expected: Instance no longer appears in list

---

## Acceptance Criteria Validation

### Requirement 6.1: Voice-first interaction using Connect AI Agents
- ✅ Connect instance created
- ✅ Telephony enabled (incoming and outgoing calls)
- ✅ Phone number claimed and working

### Requirement 8.1-8.3: All resources in us-east-1
- ✅ Instance created in us-east-1
- ✅ Phone number in us-east-1 region

### Instance Configuration
- ✅ Instance name: poc-ai-l1-support (or chosen alias)
- ✅ Region: us-east-1
- ✅ Identity management: Store users in Amazon Connect
- ✅ Data storage: Call recordings disabled (cost optimization)
- ✅ Phone number: Claimed (cheapest DID)

### OIDC Discovery URL
- ✅ OIDC URL format: `https://<ALIAS>.my.connect.aws/.well-known/openid-configuration`
- ✅ OIDC URL documented for Task 2.4

---

## Task Status

**Task 3.1: Amazon Connect Instance Creation - MANUAL CONFIGURATION REQUIRED ⚠️**

**Status:** Awaiting manual configuration

**Prerequisites Complete:**
- ✅ Phase 1 complete (Mock ITSM backend)
- ✅ Phase 2 Tasks 2.1-2.3 complete (AgentCore Gateway prerequisites)

**Action Required:**
1. Follow this guide to create Connect instance manually
2. Note the instance alias and OIDC discovery URL
3. Test the phone number
4. Document configuration in `deployment/connect-instance-log.md`
5. **THEN:** Return to Task 2.4 to configure AgentCore Gateway with OIDC URL
6. Proceed to Task 3.2 (Connect AI Agent IAM role)

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-09  
**Configuration Guide Version:** 1.0
