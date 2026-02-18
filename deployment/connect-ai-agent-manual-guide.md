# Amazon Connect AI Agent Manual Configuration Guide - Task 3.4

## Overview

This guide provides step-by-step instructions for creating the Amazon Connect AI Agent through the AWS Console. The AI Agent will handle voice interactions and invoke the AgentCore Gateway to perform ITSM operations.

**Task:** Task 3.4 - Connect AI Agent Creation  
**Agent Name:** `poc-l1-support-agent`  
**Region:** us-east-1

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Task 3.1 Complete:** Amazon Connect instance created
  - Instance: `poc-ai-l1-support`
  - Instance ID: `c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
  - Access URL: `https://poc-ai-l1-support.my.connect.aws`

- ✅ **Task 3.2 Complete:** Connect AI Agent IAM role created
  - Role: `poc-connect-ai-agent-role`
  - Role ARN: `arn:aws:iam::714059461907:role/poc-connect-ai-agent-role`

- ✅ **Task 2.4 Complete:** AgentCore Gateway deployed
  - Gateway: `poc-itsm-agentcore-gateway`
  - Gateway ARN: `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`

- ✅ **Task 3.3 Complete:** OIDC configuration verified

---

## AI Agent Instructions

The AI Agent will use the following instructions to guide its behavior:

```
You are an AI IT support assistant for DAS Holding. Your role is to help callers with Level 1 IT support issues by creating and managing support tickets.

GREETING:
- Greet callers warmly: "Hello, I'm your AI IT support assistant. How can I help you today?"

INFORMATION COLLECTION:
- Ask the caller to describe their IT issue
- Keep your questions short and conversational
- DO NOT ask for passwords, MFA codes, or complete device serial numbers
- Use the caller's phone number or session ID as their identifier

TICKET CREATION:
- Once you understand the issue, summarize it back to the caller
- Ask for confirmation: "I'll create a ticket for [issue summary]. Is that correct?"
- If confirmed, use the create_ticket tool with the caller_id and issue_description
- After creating the ticket, provide the ticket ID: "Your ticket number is [ticket_id]. We'll work on this issue."

TICKET STATUS:
- If a caller asks about a ticket, use the get_ticket_status tool with the ticket_id
- Provide the current status in simple terms

ADDING COMMENTS:
- If a caller provides additional information, use the add_ticket_comment tool
- Confirm the comment was added: "I've added that information to your ticket."

LISTING TICKETS:
- If a caller asks about their recent tickets, use the list_recent_tickets tool
- Summarize the tickets briefly

ESCALATION:
- If the issue is complex or the caller requests human assistance, say: "I'll transfer you to a human agent who can help with this."
- Offer escalation if you cannot resolve the issue

VOICE OPTIMIZATION:
- Keep all responses short and spoken-friendly
- Avoid technical jargon
- Use natural, conversational language
- Speak clearly and at a moderate pace

SECURITY:
- NEVER ask for passwords, MFA codes, or sensitive credentials
- NEVER store or process real employee IDs or HR identifiers
- Use session IDs or hashed phone numbers for caller identification
```

---

## Step-by-Step Configuration

### Step 1: Access Amazon Connect Console

1. Open AWS Console
2. Navigate to **Amazon Connect**
3. Click on your instance: **poc-ai-l1-support**
4. Click **Open admin console** (or access directly: `https://poc-ai-l1-support.my.connect.aws`)

### Step 2: Navigate to AI Agents

1. In the Connect admin console, look for the left navigation menu
2. Click on **Agent applications** or **AI Agents** (menu location may vary)
3. Click **Create AI Agent** or **Add AI Agent**

**Note:** If you don't see AI Agents in the menu, you may need to:
- Check that your instance has AI Agent features enabled
- Look under **Flows** → **AI Agents** or **Routing** → **AI Agents**
- Contact AWS Support if the feature is not available

### Step 3: Configure Basic Settings ✅ COMPLETE

**Agent Name:** `poc-l1-support-agent` ✅
**Agent Type:** Orchestration (SelfServiceOrchestrator template) ✅
**Status:** Created ✅

### Step 4: Configure Security Profiles

**Current Screen:** Security Profiles section

**What to do:**
1. Click on the **"Select Security Profiles"** dropdown
2. Look for a security profile that includes:
   - Basic Connect permissions
   - Agent permissions
   - Or create a new security profile if needed
3. **Recommendation:** Select the default or admin security profile for the PoC
4. This allows the AI Agent to access necessary Connect features

**Note:** For a PoC, you can use a permissive security profile. In production, you'd restrict this.

### Step 5: Configure Tools - ADD AGENTCORE GATEWAY TOOLS ⚠️ CRITICAL

**Current Status:** You have 3 default tools (Complete, Escalate, Retrieve)

**What you need to do:**
1. Click **"Add tool"** button (top right of Tools section)
2. You need to add 4 custom tools from your AgentCore Gateway:
   - `create_ticket`
   - `get_ticket_status`
   - `add_ticket_comment`
   - `list_recent_tickets`

**How to add AgentCore Gateway tools:**
- Look for an option to add **"External tools"** or **"MCP tools"** or **"Bedrock AgentCore tools"**
- Select your AgentCore Gateway: `poc-itsm-agentcore-gateway`
- The 4 tools should appear automatically from the gateway

**Keep the default tools:**
- ✅ **Complete** - Mark conversation as complete
- ✅ **Escalate** - Escalate to human agent
- ⚠️ **Retrieve** - Shows "Insufficient" permissions (you can ignore this or remove it)

### Step 6: Configure Prompts - UPDATE INSTRUCTIONS

**Current Screen:** Prompts section

**What you see:**
- Prompt: **SelfServiceOrchestration** (Status: Published, Version: 1)
- This is the default prompt from the template

**What to do:**
1. Click **"Edit"** button next to the SelfServiceOrchestration prompt
2. You'll see the prompt editor
3. **Replace the entire prompt** with our custom IT support instructions (see below)

**Custom IT Support Instructions to paste:**

**Instructions Field:**

Copy and paste the AI Agent instructions from the section above into the instructions field.

**Key Points to Verify:**
- ✅ Greeting message is friendly and clear
- ✅ NO requests for passwords, MFA codes, or device serials
- ✅ Confirmation step before ticket creation
- ✅ Ticket ID provided after creation
- ✅ Escalation path mentioned
- ✅ Responses are short and voice-optimized

### Step 7: Add AgentCore Gateway Tools ⚠️ CRITICAL STEP

**Current Status:** You have 3 default tools, but you need to add 4 custom tools from AgentCore Gateway

**Steps:**
1. Scroll to the **Tools** section
2. Click **"Add tool"** button (top right)
3. Look for options to add:
   - **External tools**
   - **MCP tools** 
   - **Bedrock AgentCore tools**
   - **Custom tools**
4. Select your AgentCore Gateway: `poc-itsm-agentcore-gateway`
5. The following 4 tools should appear:
   - `create_ticket`
   - `get_ticket_status`
   - `add_ticket_comment`
   - `list_recent_tickets`
6. Select all 4 tools and add them

**If you don't see an option to add AgentCore Gateway tools:**
- The integration might need to be configured differently
- You may need to add tools manually with API specifications
- Let me know and I'll provide alternative instructions

### Step 8: Configure Guardrails (Optional)

**Session Timeout:**
- Default: 5 minutes (adjust if needed)

**Maximum Conversation Turns:**
- Default: 20 turns (adjust if needed)

**Logging:**
- Enable CloudWatch Logs: **Yes** (for debugging)
- Log Group: `/aws/connect/poc-ai-l1-support` (default)

**Tags:**
- Key: `Environment`, Value: `PoC`
- Key: `Project`, Value: `AI-L1-Support`

### Step 8: Review and Create

1. Review all settings:
   - Agent name: `poc-l1-support-agent`
   - IAM role: `poc-connect-ai-agent-role`
   - AgentCore Gateway: `poc-itsm-agentcore-gateway`
   - Instructions: Verified
   - Tools: 4 tools available

2. Click **Create AI Agent** or **Save**

3. Wait for the agent to be created (may take 1-2 minutes)

### Step 9: Verify AI Agent Creation

**Via Console:**
1. Verify the agent appears in the AI Agents list
2. Status should be **Active** or **Ready**
3. Click on the agent to view details
4. Verify AgentCore Gateway is linked
5. Verify IAM role is attached

**Via AWS CLI (Optional):**
```bash
# List Connect instances
aws connect list-instances --region us-east-1

# Note: AI Agent CLI commands may vary depending on AWS CLI version
# Check AWS documentation for the latest commands
```

---

## Verification Checklist

After creating the AI Agent, verify:

- [ ] Agent name is `poc-l1-support-agent`
- [ ] Agent status is Active/Ready
- [ ] IAM role `poc-connect-ai-agent-role` is attached
- [ ] AgentCore Gateway `poc-itsm-agentcore-gateway` is linked
- [ ] Instructions include greeting, confirmation, and escalation
- [ ] Instructions do NOT request passwords or sensitive data
- [ ] 4 tools are available (create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets)
- [ ] CloudWatch logging is enabled
- [ ] Tags are applied (Environment=PoC, Project=AI-L1-Support)

---

## Troubleshooting

### Issue: AI Agents menu not visible

**Solution:**
- Verify your Connect instance has AI Agent features enabled
- Check AWS region (must be us-east-1)
- Contact AWS Support to enable AI Agents for your instance

### Issue: Cannot link AgentCore Gateway

**Solution:**
- Verify AgentCore Gateway exists and is active
- Check IAM role has `bedrock:InvokeAgent` permission
- Verify OIDC configuration is correct (Task 3.3)
- Check that Gateway ARN is correct

### Issue: IAM role not found

**Solution:**
- Verify Task 3.2 was completed successfully
- Check role ARN: `arn:aws:iam::714059461907:role/poc-connect-ai-agent-role`
- Verify role exists in IAM console

### Issue: Tools not appearing

**Solution:**
- Verify AgentCore Gateway has 4 operations configured
- Check that Gateway is active
- Refresh the AI Agent configuration page
- Verify Task 2.4 was completed successfully

---

## Next Steps After Configuration

Once the AI Agent is created:

1. ✅ Document the AI Agent ARN or ID
2. ✅ Test the AI Agent (if test interface is available in Console)
3. ➡️ Proceed to Task 3.5: Create Connect Contact Flow
   - Link the contact flow to this AI Agent
   - Configure phone number to use the contact flow
4. ➡️ Proceed to Phase 4: End-to-End Testing
   - Call the phone number: +16782709241
   - Test ticket creation, status queries, and escalation

---

## Cost Tracking

**Task 3.4 Estimated Costs:**
- AI Agent creation: $0.00 (no charge for agent itself)
- AI Agent usage: Charged per conversation turn during testing
  - Estimate: ~$0.01-0.05 per test call (2-3 short calls)
- Total Task 3.4: ~$0.05 (during testing phase)

**Note:** Keep test calls minimal (2-3 short calls) to stay within budget.

---

## Rollback Commands

If rollback is needed:

### Via Console:
1. Navigate to Amazon Connect admin console
2. Go to **AI Agents**
3. Select `poc-l1-support-agent`
4. Click **Delete** or **Remove**
5. Confirm deletion

### Verify Deletion:
- Check that agent no longer appears in AI Agents list
- Verify CloudWatch logs are deleted (or delete manually if needed)

**Note:** Deleting the AI Agent does NOT delete the IAM role, AgentCore Gateway, or Connect instance. These must be deleted separately if needed.

---

## Important Notes

1. **Voice Optimization:** The AI Agent instructions are optimized for voice interactions. Keep responses short and conversational.

2. **Security:** The instructions explicitly prohibit asking for passwords, MFA codes, or sensitive credentials.

3. **Caller Identification:** Use session IDs or hashed phone numbers, NOT real employee IDs.

4. **Escalation:** The AI Agent should offer escalation for complex issues or when requested by the caller.

5. **Testing:** Test the AI Agent thoroughly before proceeding to Phase 4. Verify that:
   - Greeting is clear and friendly
   - Ticket creation works correctly
   - Ticket ID is provided after creation
   - Escalation path is available

6. **Budget:** Keep test calls minimal (2-3 short calls) to stay within the $10 budget.

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-18  
**Status:** Configuration Guide Ready


### Step 8: Configure Guardrails (Optional)

**Current Status:** Guardrails (0)

**What to do:**
- For this PoC, you can skip adding guardrails
- Guardrails are used to implement content filtering and safety policies
- Our instructions already include security guidelines (no passwords, etc.)

**If you want to add guardrails (optional):**
- Click "Add guardrail"
- Configure content filters for:
  - Sensitive information (PII, passwords)
  - Inappropriate content
  - Topic restrictions

### Step 9: Save and Publish

**After completing all configurations:**
1. Look for **"Save"** or **"Publish"** button (usually top right or bottom)
2. Click to save your changes
3. The AI Agent will be published and ready to use
4. You may need to publish a new version if you edited the prompt

---

## Current Status Summary

Based on your screenshot, here's what you need to do:

### ✅ Completed:
1. Agent created: `poc-l1-support-agent`
2. Agent type: Orchestration (SelfServiceOrchestrator)
3. Default tools added: Complete, Escalate, Retrieve

### ⏳ Next Steps (In Order):

1. **Configure Security Profiles** (Step 4)
   - Select a security profile from the dropdown
   - Use default/admin profile for PoC

2. **Edit the Prompt** (Step 6)
   - Click "Edit" on SelfServiceOrchestration prompt
   - Replace with our custom IT support instructions (see AI Agent Instructions section above)

3. **Add AgentCore Gateway Tools** (Step 7) ⚠️ CRITICAL
   - Click "Add tool"
   - Add the 4 ITSM tools from AgentCore Gateway
   - This is essential for ticket operations

4. **Save/Publish** (Step 9)
   - Save all changes
   - Publish the agent

---

## Important Notes for Current Configuration

### Security Profiles
The "Retrieve" tool shows "Insufficient" permissions. This is okay - it's for knowledge base search which we're not using. You can:
- Leave it as is (it won't be used)
- Or remove it if you want a cleaner configuration

### Tools Priority
The most critical step is **adding the 4 AgentCore Gateway tools**. Without these, the AI Agent cannot:
- Create tickets
- Check ticket status
- Add comments
- List tickets

### Prompt Customization
Make sure to edit the SelfServiceOrchestration prompt with our custom instructions that include:
- IT support greeting
- Ticket creation workflow
- Security guidelines (no passwords)
- Escalation path

---
