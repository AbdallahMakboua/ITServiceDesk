# Amazon Connect Contact Flow Manual Configuration Guide - Task 3.5

## Overview

This guide provides step-by-step instructions for creating the Amazon Connect Contact Flow that integrates with the AI Agent and handles voice interactions.

**Task:** Task 3.5 - Connect Contact Flow Creation  
**Flow Name:** `poc-l1-support-flow`  
**Region:** us-east-1

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Task 3.1 Complete:** Amazon Connect instance created
  - Instance: `poc-ai-l1-support`
  - Phone Number: +16782709241

- ✅ **Task 3.4 Complete:** AI Agent created and published
  - Agent: `poc-l1-support-agent`
  - Prompt: `POC-prompt`
  - Status: Published

---

## Step-by-Step Configuration

### Step 1: Access Contact Flows

1. Open the **Amazon Connect admin console**
   - URL: `https://poc-ai-l1-support.my.connect.aws`
   - Or from AWS Console → Amazon Connect → Open admin console

2. In the left navigation menu, look for:
   - **Routing** → **Contact flows**
   - Or **Flows** → **Contact flows**

3. Click **Create contact flow**

### Step 2: Configure Flow Details

**Flow Name:**
```
poc-l1-support-flow
```

**Description:**
```
PoC contact flow for L1 IT support - integrates with AI Agent for voice interactions
```

**Flow Type:** Contact flow (default)

### Step 3: Build the Contact Flow

You'll see a visual flow builder with blocks on the left side. Here's the flow structure:

#### Flow Structure:

```
Entry Point
    ↓
Set logging behavior (optional)
    ↓
Play prompt (Greeting)
    ↓
Invoke AI Agent
    ↓
Check AI Agent response
    ↓
Transfer to queue (if escalation) OR Disconnect
```

### Step 4: Add Flow Blocks

#### Block 1: Entry Point
- This is automatically added
- No configuration needed

#### Block 2: Set Logging Behavior (Optional)
- **Block Type:** Set logging behavior
- **Purpose:** Enable CloudWatch logging for debugging
- **Configuration:**
  - Enable CloudWatch Logs: Yes
  - Log Group: Default (`/aws/connect/poc-ai-l1-support`)
- **Connect to:** Next block

#### Block 3: Play Prompt (Greeting)
- **Block Type:** Play prompt
- **Purpose:** Play initial greeting
- **Configuration:**
  - Select: **Text-to-speech**
  - Text: `Thank you for calling DAS Holding IT Support. Please wait while I connect you to our AI assistant.`
  - Voice: Select a natural voice (e.g., Joanna, Matthew)
- **Connect "Success" to:** Invoke AI Agent block

#### Block 4: Invoke AI Agent
- **Block Type:** Invoke AI Agent
- **Purpose:** Start conversation with the AI Agent
- **Configuration:**
  - Select AI Agent: `poc-l1-support-agent`
  - Timeout: 300 seconds (5 minutes)
  - Enable streaming: Yes (if available)
- **Connect "Success" to:** Check AI Agent response
- **Connect "Error" to:** Play error message → Disconnect

#### Block 5: Check AI Agent Response (Optional)
- **Block Type:** Check contact attributes
- **Purpose:** Check if escalation was requested
- **Configuration:**
  - Check if AI Agent used "Escalate" tool
  - If yes → Transfer to queue
  - If no → Disconnect
- **Alternative:** Skip this and go directly to Disconnect if you don't have a queue set up

#### Block 6: Transfer to Queue (Optional - for escalation)
- **Block Type:** Transfer to queue
- **Purpose:** Transfer to human agent if escalation requested
- **Configuration:**
  - Select queue: BasicQueue (or create a simple queue)
  - Timeout: 60 seconds
- **Connect "Success" to:** Disconnect
- **Connect "Error" to:** Play message → Disconnect

#### Block 7: Disconnect
- **Block Type:** Disconnect / hang up
- **Purpose:** End the call
- **Configuration:** No configuration needed

### Step 5: Simplified Flow (Recommended for PoC)

If the above is too complex, use this minimal flow:

```
Entry Point
    ↓
Play prompt: "Thank you for calling DAS Holding IT Support."
    ↓
Invoke AI Agent (poc-l1-support-agent)
    ↓
Disconnect
```

This minimal flow:
- Answers the call
- Plays a greeting
- Starts the AI Agent conversation
- Ends the call when done

### Step 6: Save and Publish the Flow

1. **Click "Save"** (top right)
2. **Click "Publish"** (top right)
3. Confirm publication

### Step 7: Assign Flow to Phone Number

1. In the Connect admin console, go to:
   - **Channels** → **Phone numbers**
   - Or **Routing** → **Phone numbers**

2. Find your phone number: **+16782709241**

3. Click on the phone number to edit

4. **Contact flow / IVR:**
   - Select: `poc-l1-support-flow`

5. **Save** the changes

---

## Verification Steps

### Step 1: Verify Flow is Published

1. Go to **Routing** → **Contact flows**
2. Find `poc-l1-support-flow`
3. Status should be: **Published**

### Step 2: Verify Phone Number Assignment

1. Go to **Channels** → **Phone numbers**
2. Find: +16782709241
3. Contact flow should show: `poc-l1-support-flow`

### Step 3: Test the Flow

**Call the phone number: +16782709241**

Expected behavior:
1. Call connects
2. Greeting plays: "Thank you for calling DAS Holding IT Support..."
3. AI Agent responds: "Hello, I'm your AI IT support assistant. How can I help you today?"
4. You can describe an IT issue
5. AI Agent responds appropriately
6. Call ends when conversation is complete

---

## Troubleshooting

### Issue: Flow doesn't save

**Solution:**
- Make sure all blocks are connected properly
- Check that there are no orphaned blocks
- Ensure Entry Point is connected to the first block

### Issue: AI Agent doesn't respond

**Solution:**
- Verify AI Agent is published (not draft)
- Check that POC-prompt is linked to the agent
- Verify Security Profile is configured
- Check CloudWatch logs for errors

### Issue: Call doesn't connect

**Solution:**
- Verify phone number is assigned to the flow
- Check that flow is published (not draft)
- Verify Connect instance is active
- Check phone number status (should be claimed)

### Issue: "Escalate" doesn't work

**Solution:**
- For PoC, escalation can simply end the call
- Or create a basic queue and transfer block
- Or play a message: "I'll transfer you to a human agent" then disconnect

---

## Alternative Approach: Lambda Integration

If the AI Agent integration doesn't work as expected, you can create a simpler flow that:

1. Plays greeting
2. Collects input using "Get customer input" block
3. Invokes Lambda function (that calls AgentCore Gateway)
4. Plays response
5. Loops or disconnects

This approach bypasses the AI Agent and uses Lambda directly.

---

## Cost Tracking

### Task 3.5 Estimated Costs
- **Contact Flow creation:** $0.00 (no charge)
- **Test calls:** ~$0.01-0.02 per minute
  - Plan: 2-3 short test calls (1-2 minutes each)
  - Estimated: ~$0.05
- **AI Agent usage:** ~$0.01-0.02 per conversation turn
  - Estimated: ~$0.05 per test call
- **Total Task 3.5:** ~$0.15 (for testing)

### Cumulative PoC Costs
- **Phase 1:** < $0.03
- **Phase 2:** ~$0.40
- **Phase 3 (Tasks 3.1-3.4):** ~$0.05
- **Phase 3 (Task 3.5 testing):** ~$0.15
- **Total:** ~$0.63
- **Remaining Budget:** ~$9.37 (of $10.00)
- **Status:** WELL WITHIN BUDGET ✅

---

## Next Steps After Configuration

Once the contact flow is created and assigned:

1. ✅ Test the flow by calling +16782709241
2. ✅ Verify AI Agent responds correctly
3. ✅ Test ticket creation workflow (if integrated)
4. ✅ Test escalation path
5. ➡️ Proceed to Phase 4: End-to-End Testing
6. ➡️ Document test results
7. ➡️ Proceed to Phase 5: Cleanup

---

## Important Notes

1. **Keep test calls short** (1-2 minutes) to minimize costs

2. **Limit test calls** to 2-3 calls maximum for the PoC

3. **AI Agent limitations:** Since we couldn't add AgentCore Gateway tools directly, the AI Agent will:
   - Greet callers
   - Collect information
   - Provide conversational responses
   - Use Escalate tool if needed
   - But won't actually create tickets in DynamoDB (would need Lambda integration)

4. **For full ticket creation:** Would need to add Lambda functions that the Contact Flow calls directly

5. **PoC Success Criteria:** Demonstrating voice interaction with AI Agent is sufficient for the PoC, even without full ticket creation

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-18  
**Status:** Configuration Guide Ready
