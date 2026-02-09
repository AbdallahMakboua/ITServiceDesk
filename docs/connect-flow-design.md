# Amazon Connect Flow Design - Task 0.7

## Overview

This document defines the Amazon Connect contact flow and AI Agent configuration for the DAS Holding AI L1 Voice Service Desk PoC. The design focuses on voice-first interaction with natural conversation flow, ticket management capabilities, and clear escalation paths.

---

## Architecture Overview

```
Caller (Phone)
    ↓
Amazon Connect (Phone Number)
    ↓
Contact Flow (poc-l1-support-flow)
    ↓
AI Agent (poc-l1-support-agent)
    ↓
AgentCore Gateway (poc-itsm-agentcore-gateway)
    ↓
Mock ITSM API
```

---

## Amazon Connect Instance

### Instance Name
```
poc-ai-l1-support
```

### Region
```
us-east-1
```

### Instance Alias
```
poc-ai-l1-support
```

**OIDC Discovery URL:**
```
https://poc-ai-l1-support.my.connect.aws/.well-known/openid-configuration
```

### Identity Management
```
Store users in Amazon Connect
```

**Rationale:** Minimal setup for PoC, no external identity provider needed

### Data Storage
```
Call recordings: DISABLED
Chat transcripts: DISABLED
```

**Rationale:** Reduce costs, not needed for PoC demonstration

### Telephony
```
Claim one DID (Direct Inward Dial) number
```

**Cost Optimization:**
- Claim cheapest available number
- Keep test calls minimal (2-3 short calls, < 5 minutes total)
- Release number immediately after PoC completion

---

## AI Agent Configuration

### Agent Name
```
poc-l1-support-agent
```

### Agent Type
```
Amazon Connect AI Agent (Bedrock-powered)
```

### AgentCore Gateway Integration
```
Gateway: poc-itsm-agentcore-gateway
```

### IAM Role
```
poc-connect-ai-agent-role
```

---

## AI Agent Instructions

### System Prompt

```
You are an AI IT support assistant for DAS Holding. Your role is to help callers with Level 1 IT support issues by creating and managing support tickets.

CAPABILITIES:
- Create new support tickets for IT issues
- Check the status of existing tickets
- Add updates or comments to tickets
- List recent tickets for the caller

CONVERSATION GUIDELINES:
1. Be friendly, professional, and helpful
2. Keep responses SHORT and spoken-friendly (2-3 sentences maximum)
3. Speak naturally as if having a phone conversation
4. Avoid technical jargon unless necessary
5. Confirm understanding before taking actions

TICKET CREATION PROCESS:
1. Greet the caller warmly
2. Ask how you can help
3. Listen to the issue description
4. Summarize what you understood
5. Ask for confirmation before creating the ticket
6. Provide the ticket number clearly after creation

CALLER IDENTIFICATION:
- Use the session ID or call identifier as the caller_id
- DO NOT ask for employee IDs, usernames, or HR identifiers
- DO NOT ask for sensitive information (passwords, MFA codes, device serial numbers)

SENSITIVE INFORMATION:
- NEVER ask for passwords
- NEVER ask for MFA codes or security tokens
- NEVER ask for complete device serial numbers
- NEVER ask for credit card or payment information

ESCALATION:
- If the issue is complex or beyond your capabilities, offer to escalate to a human agent
- If the caller explicitly requests a human agent, immediately offer escalation
- If you cannot help after 2-3 attempts, suggest escalation

RESPONSE STYLE:
- Keep responses concise (2-3 sentences)
- Use natural, conversational language
- Avoid long explanations
- Speak as if you're on the phone, not writing an email
```

### Example Interactions

**Scenario 1: Create Ticket**

```
Caller: "Hi, my laptop won't turn on."

AI Agent: "I'm sorry to hear that. Let me create a support ticket for you. Just to confirm, your laptop isn't responding when you press the power button, is that correct?"

Caller: "Yes, that's right."

AI Agent: "Got it. I've created ticket number 3-3-5-6-7-E-E-8 for your laptop issue. Our support team will look into this and reach out to you soon. Is there anything else I can help you with?"
```

**Scenario 2: Check Ticket Status**

```
Caller: "I want to check on my ticket."

AI Agent: "Sure, I can help with that. What's your ticket number?"

Caller: "It's 3-3-5-6-7-E-E-8."

AI Agent: "Let me check that for you. Your ticket about the laptop not turning on is currently open and was created today. Our team is working on it. Is there anything else you'd like to know?"
```

**Scenario 3: Add Comment**

```
Caller: "I have an update on my laptop ticket."

AI Agent: "Great, what's your ticket number?"

Caller: "3-3-5-6-7-E-E-8. I tried plugging it into a different outlet and it still doesn't work."

AI Agent: "Thanks for that information. I've added your update to the ticket. The support team will see this when they review your case. Anything else I can help with?"
```

**Scenario 4: Escalation**

```
Caller: "This is really urgent, I need to speak to someone now."

AI Agent: "I understand this is urgent. Let me connect you with a human agent who can assist you right away. Please hold for a moment."

[Transfer to human agent queue]
```

---

## Contact Flow Design

### Flow Name
```
poc-l1-support-flow
```

### Flow Structure

```
1. Entry Point
   ↓
2. Play Greeting (Optional)
   "Thank you for calling DAS Holding IT Support."
   ↓
3. Invoke AI Agent
   Agent: poc-l1-support-agent
   ↓
4. AI Agent Interaction
   (Natural conversation with caller)
   ↓
5. Check for Escalation Request
   ↓
6a. If Escalation Requested:
       → Transfer to Queue (or play escalation message)
   ↓
6b. If Conversation Complete:
       → Play Thank You Message
       → End Call
```

### Flow Blocks

#### Block 1: Entry Point
- **Type:** Entry point
- **Action:** Start flow

#### Block 2: Play Greeting (Optional)
- **Type:** Play prompt
- **Prompt:** "Thank you for calling DAS Holding IT Support. An AI assistant will help you shortly."
- **Duration:** 3-5 seconds

**Note:** This greeting is optional. The AI Agent can provide its own greeting.

#### Block 3: Invoke AI Agent
- **Type:** Invoke AI Agent
- **Agent:** poc-l1-support-agent
- **Timeout:** 30 seconds per interaction
- **Max Duration:** 5 minutes total

#### Block 4: AI Agent Interaction
- **Type:** AI Agent conversation
- **Behavior:** Natural language conversation
- **Tools Available:** create_ticket, get_ticket_status, add_ticket_comment, list_recent_tickets

#### Block 5: Check for Escalation
- **Type:** Check contact attributes
- **Condition:** Check if AI Agent set escalation flag OR caller said "speak to human"

#### Block 6a: Escalation Path
- **Type:** Transfer to queue OR Play message
- **Option 1 (Full Implementation):** Transfer to human agent queue
- **Option 2 (PoC Simulation):** Play message: "I'll transfer you to a human agent. Please hold."
- **Action:** End call (for PoC) or transfer to queue (for production)

#### Block 6b: Completion Path
- **Type:** Play prompt
- **Prompt:** "Thank you for calling DAS Holding IT Support. Have a great day!"
- **Action:** Disconnect call

---

## Caller Identification Strategy

### Privacy-Safe Approach

**DO NOT USE:**
- ❌ Real employee IDs
- ❌ Usernames
- ❌ HR identifiers
- ❌ Email addresses
- ❌ Social Security Numbers

**USE INSTEAD:**
- ✅ Session ID (Connect contact ID)
- ✅ Hashed phone number
- ✅ PoC-specific aliases (e.g., "poc-user-001")

### Implementation

**In AI Agent Instructions:**
```
When creating a ticket, use the session identifier as the caller_id.
Do not ask the caller for their employee ID or username.
```

**In Lambda Function:**
```python
# Extract caller_id from Connect session
caller_id = event.get('Details', {}).get('ContactData', {}).get('ContactId', 'unknown')

# Or use hashed phone number
phone_number = event.get('Details', {}).get('ContactData', {}).get('CustomerEndpoint', {}).get('Address', '')
caller_id = hashlib.sha256(phone_number.encode()).hexdigest()[:16]
```

---

## Escalation Triggers

### Automatic Escalation

**Trigger 1:** Caller explicitly says:
- "I want to speak to a human"
- "Transfer me to an agent"
- "I need a real person"
- "This isn't working"

**Trigger 2:** AI Agent determines issue is too complex:
- Issue requires physical hardware inspection
- Issue requires administrative privileges
- Issue is outside AI's knowledge base

**Trigger 3:** Conversation exceeds time limit:
- More than 5 minutes without resolution
- More than 3 back-and-forth exchanges without progress

### Escalation Flow

```
AI Agent detects escalation trigger
    ↓
AI Agent: "I understand you need additional help. Let me connect you with a human agent."
    ↓
Set escalation flag in contact attributes
    ↓
Contact flow checks escalation flag
    ↓
Transfer to human agent queue (or play escalation message for PoC)
```

---

## Voice Optimization

### Response Length

**Guideline:** 2-3 sentences maximum per response

**Good Example:**
```
"I've created ticket number 3-3-5-6-7-E-E-8 for your laptop issue. 
Our support team will reach out to you soon. 
Is there anything else I can help you with?"
```

**Bad Example (Too Long):**
```
"Thank you for providing that information. I have successfully created 
a support ticket in our system with the unique identifier 33567ee8-f182-4f8a-b03e-2f1515915471. 
This ticket has been assigned to our Level 1 support team who will review 
your issue regarding the laptop that is not powering on and will contact 
you via your registered contact information within the next 24 to 48 hours 
during normal business hours. In the meantime, you can check the status 
of your ticket by calling back and providing this ticket number. 
Is there anything else I can assist you with today?"
```

### Ticket Number Pronunciation

**Format:** Spell out UUID in groups for clarity

**Example:**
- UUID: `33567ee8-f182-4f8a-b03e-2f1515915471`
- Spoken: "3-3-5-6-7-E-E-8" (first 8 characters only for brevity)

**Alternative:** Use shorter ticket IDs if possible (e.g., "Ticket 1234")

### Natural Language

**Use:**
- "Let me help you with that"
- "I've created a ticket for you"
- "Can you tell me more about the issue?"

**Avoid:**
- "Initiating ticket creation process"
- "Executing query on database"
- "Validating input parameters"

---

## Testing Checklist

### Smoke Tests

**Test 1: Basic Call Flow**
- [ ] Call phone number
- [ ] Hear greeting (if configured)
- [ ] AI Agent responds
- [ ] Can have basic conversation

**Test 2: Create Ticket**
- [ ] Describe an IT issue
- [ ] AI Agent summarizes issue
- [ ] Confirm ticket creation
- [ ] Receive ticket number

**Test 3: Check Ticket Status**
- [ ] Ask to check ticket status
- [ ] Provide ticket number
- [ ] Receive status information

**Test 4: Add Comment**
- [ ] Ask to add information to ticket
- [ ] Provide ticket number and comment
- [ ] Receive confirmation

**Test 5: List Tickets**
- [ ] Ask to see recent tickets
- [ ] Receive list of tickets

**Test 6: Escalation**
- [ ] Say "I want to speak to a human"
- [ ] AI Agent acknowledges escalation
- [ ] Transfer occurs (or escalation message plays)

---

## Cost Optimization

### Minimize Call Duration

- Keep test calls short (< 2 minutes each)
- Limit to 2-3 test calls total
- Use concise test scenarios

### Minimize Phone Number Costs

- Claim number only when ready to test
- Release number immediately after testing
- Use cheapest available DID

### Estimated Costs

**Phone Number:**
- Claim fee: $0 (included in Connect)
- Daily rate: $0.03/day
- For 3 days: $0.09

**Call Minutes:**
- Inbound: $0.018/minute
- 3 calls × 2 minutes = 6 minutes
- Cost: 6 × $0.018 = $0.108

**AI Agent Usage:**
- Bedrock charges apply (see AgentCore Gateway costs)

**Total Connect Costs:** ~$0.20 for PoC

---

## Acceptance Criteria Validation

### Requirement 6.1-6.8: Voice-First Interaction with Escalation

- ✅ Voice-first interaction using Amazon Connect AI Agents
- ✅ AI Agent greets caller and asks how it can help
- ✅ Short, spoken-friendly responses optimized for voice
- ✅ NO requests for sensitive information (passwords, MFA codes, device serials)
- ✅ Confirmation step before ticket creation
- ✅ Ticket ID provided to caller after creation
- ✅ Explicit "Escalate to human" path defined

### Requirement 7.1-7.8: Ticket Operations via AgentCore Tools

- ✅ AI Agent collects issue description and caller identification
- ✅ AI Agent invokes create_ticket tool via AgentCore Gateway
- ✅ AI Agent provides ticket ID to caller
- ✅ AI Agent can query ticket status
- ✅ AI Agent can add comments
- ✅ AI Agent can list recent tickets
- ✅ Caller identification uses session ID or hashed phone number (NO real employee IDs)

---

## Task Status

**Task 0.7: Amazon Connect Flow Design - COMPLETE ✅**

Amazon Connect flow and AI Agent configuration documented:
- Contact flow structure defined
- AI Agent instructions written
- Caller identification strategy (privacy-safe)
- Escalation triggers and flow
- Voice optimization guidelines
- Testing checklist
- Cost optimization strategies

**Note:** This design will be implemented in Phase 3 (Tasks 3.1-3.6). This document provides the design that should exist before implementation.
