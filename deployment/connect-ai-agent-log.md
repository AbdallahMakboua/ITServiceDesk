# Amazon Connect AI Agent Deployment Log - Task 3.4

## Status: PENDING MANUAL CONFIGURATION ⏳

**Date:** 2026-02-18  
**Task:** Task 3.4 - Connect AI Agent Creation  
**Region:** us-east-1

---

## Configuration Guide

**See:** `deployment/connect-ai-agent-manual-guide.md` for detailed step-by-step instructions.

---

## Prerequisites (Complete)

- ✅ **Task 3.1:** Amazon Connect instance created
  - Instance: `poc-ai-l1-support`
  - Instance ID: `c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
  - Instance ARN: `arn:aws:connect:us-east-1:714059461907:instance/c1d8f6f7-3e9c-4d11-9ac0-04d7965d6ceb`
  - Access URL: `https://poc-ai-l1-support.my.connect.aws`
  - Phone Number: +16782709241

- ✅ **Task 3.2:** Connect AI Agent IAM role created
  - Role: `poc-connect-ai-agent-role`
  - Role ARN: `arn:aws:iam::714059461907:role/poc-connect-ai-agent-role`

- ✅ **Task 2.4:** AgentCore Gateway deployed
  - Gateway: `poc-itsm-agentcore-gateway`
  - Gateway ARN: `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`

- ✅ **Task 3.3:** OIDC configuration verified

---

## Configuration Information (To Be Completed)

### AI Agent Details
- **Name:** `poc-l1-support-agent`
- **Description:** PoC AI Agent for L1 IT support - handles ticket creation and management via AgentCore Gateway
- **Language:** English (US)
- **Voice:** (To be selected - recommend Neural voice)
- **Region:** us-east-1

### IAM Role
- **Role Name:** `poc-connect-ai-agent-role`
- **Role ARN:** `arn:aws:iam::714059461907:role/poc-connect-ai-agent-role`
- **Permissions:** bedrock:InvokeAgent on AgentCore Gateway

### AgentCore Gateway Integration
- **Gateway Name:** `poc-itsm-agentcore-gateway`
- **Gateway ARN:** `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`

### Available Tools (4 total)
1. `create_ticket` - Create a new support ticket
2. `get_ticket_status` - Retrieve ticket status by ID
3. `add_ticket_comment` - Add a comment to an existing ticket
4. `list_recent_tickets` - List recent tickets for a caller

### AI Agent Instructions

The AI Agent will use the following instructions:

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

## Manual Configuration Steps

**See:** `deployment/connect-ai-agent-manual-guide.md`

**Summary:**
1. Access Amazon Connect admin console
2. Navigate to AI Agents
3. Create new AI Agent: `poc-l1-support-agent`
4. Configure IAM role: `poc-connect-ai-agent-role`
5. Link AgentCore Gateway: `poc-itsm-agentcore-gateway`
6. Configure AI Agent instructions (see above)
7. Enable CloudWatch logging
8. Add tags (Environment=PoC, Project=AI-L1-Support)
9. Review and create
10. Verify agent is active

---

## Acceptance Criteria (To Be Verified After Configuration)

### Requirement 6.2-6.6: Voice-first Interaction with Confirmation

- [ ] Agent name: `poc-l1-support-agent`
- [ ] Greeting: "Hello, I'm your AI IT support assistant. How can I help you today?"
- [ ] Collects issue description and caller identification
- [ ] Does NOT ask for passwords, MFA codes, or device serials
- [ ] Summarizes issue and asks for confirmation before creating ticket
- [ ] Provides ticket ID after creation
- [ ] Offers escalation option for complex issues
- [ ] Responses are short and spoken-friendly

### Requirement 7.1-7.8: Ticket Operations via Tools

- [ ] AgentCore Gateway integration: `poc-itsm-agentcore-gateway`
- [ ] IAM role: `poc-connect-ai-agent-role`
- [ ] Tools available: create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets
- [ ] Caller identification uses session ID or hashed phone (NOT real employee IDs)

### Task 3.4 Specific Criteria

- [ ] Agent status: Active/Ready
- [ ] AgentCore Gateway linked
- [ ] IAM role attached
- [ ] Instructions comply with requirements
- [ ] NO sensitive data collection in instructions
- [ ] CloudWatch logging enabled
- [ ] Tags applied

---

## Verification Steps (To Be Completed After Configuration)

### Step 1: Verify AI Agent Creation

**Via Console:**
1. Navigate to Amazon Connect admin console
2. Go to AI Agents
3. Verify `poc-l1-support-agent` appears in list
4. Status should be Active/Ready
5. Click on agent to view details

**Via AWS CLI (if available):**
```bash
# List Connect instances
aws connect list-instances --region us-east-1

# Note: AI Agent CLI commands may vary
# Check AWS documentation for latest commands
```

### Step 2: Verify AgentCore Gateway Link

**Via Console:**
1. Open AI Agent details
2. Verify AgentCore Gateway section shows: `poc-itsm-agentcore-gateway`
3. Verify Gateway ARN matches: `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`
4. Verify 4 tools are available

### Step 3: Verify IAM Role

**Via Console:**
1. Open AI Agent details
2. Verify IAM role section shows: `poc-connect-ai-agent-role`
3. Verify Role ARN matches: `arn:aws:iam::714059461907:role/poc-connect-ai-agent-role`

### Step 4: Verify Instructions

**Via Console:**
1. Open AI Agent details
2. Review instructions field
3. Verify greeting message is present
4. Verify NO requests for passwords or sensitive data
5. Verify confirmation step before ticket creation
6. Verify escalation path is mentioned

### Step 5: Test AI Agent (Optional)

**If test interface is available:**
1. Use Connect test interface to simulate a call
2. Test greeting: "Hello, I'm your AI IT support assistant..."
3. Test ticket creation flow
4. Test escalation path

---

## Cost Tracking

### Task 3.4 Estimated Costs
- **AI Agent creation:** $0.00 (no charge for agent itself)
- **AI Agent usage:** Charged per conversation turn during testing
  - Estimate: ~$0.01-0.05 per test call
  - Plan: 2-3 short test calls
- **Total Task 3.4:** ~$0.05 (during testing phase)

### Cumulative PoC Costs
- **Phase 1:** < $0.03
- **Phase 2:** ~$0.40
- **Phase 3 (Task 3.1):** ~$0.03 (phone number)
- **Phase 3 (Task 3.2):** $0.00
- **Phase 3 (Task 3.3):** $0.00
- **Phase 3 (Task 3.4):** ~$0.05 (estimated, during testing)
- **Total:** ~$0.51 (estimated)
- **Remaining Budget:** ~$9.49 (of $10.00)
- **Status:** WELL WITHIN BUDGET ✅

---

## Rollback Commands

If rollback is needed after configuration:

### Via Console:
1. Navigate to Amazon Connect admin console
2. Go to AI Agents
3. Select `poc-l1-support-agent`
4. Click Delete or Remove
5. Confirm deletion

### Verify Deletion:
- Check that agent no longer appears in AI Agents list
- Verify CloudWatch logs are deleted (or delete manually)

**Note:** Deleting the AI Agent does NOT delete the IAM role, AgentCore Gateway, or Connect instance. These must be deleted separately if needed.

---

## Next Steps After Configuration

Once the AI Agent is created:

1. ✅ Document the AI Agent ARN or ID in this file
2. ✅ Verify all acceptance criteria
3. ✅ Test the AI Agent (if test interface is available)
4. ➡️ Proceed to Task 3.5: Create Connect Contact Flow
   - Link the contact flow to this AI Agent
   - Configure phone number to use the contact flow
5. ➡️ Proceed to Phase 4: End-to-End Testing
   - Call the phone number: +16782709241
   - Test ticket creation, status queries, and escalation

---

## Task Status

**Task 3.4: Connect AI Agent Creation - PENDING MANUAL CONFIGURATION ⏳**

**Configuration Guide:** `deployment/connect-ai-agent-manual-guide.md`

**Prerequisites Complete:**
- ✅ Connect instance created (Task 3.1)
- ✅ IAM role created (Task 3.2)
- ✅ AgentCore Gateway deployed (Task 2.4)
- ✅ OIDC configuration verified (Task 3.3)

**Required Information:**
- **Agent Name:** `poc-l1-support-agent`
- **IAM Role ARN:** `arn:aws:iam::714059461907:role/poc-connect-ai-agent-role`
- **Gateway ARN:** `arn:aws:bedrock-agentcore:us-east-1:714059461907:gateway/poc-itsm-agentcore-gateway-9ygtgj9qzu`
- **Connect Instance:** `poc-ai-l1-support`
- **Phone Number:** +16782709241

**Next Action:** Follow the manual configuration guide to create the AI Agent through the AWS Console.

---

**Prepared by:** Kiro AI Assistant  
**Date:** 2026-02-18  
**Status:** PENDING MANUAL CONFIGURATION ⏳
