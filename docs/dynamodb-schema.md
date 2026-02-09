# DynamoDB Schema Design - Task 0.3

## Overview

This document defines the DynamoDB table schema for storing mock ITSM tickets in the DAS Holding AI L1 Voice Service Desk PoC. The schema is designed to support all four API operations: create ticket, get ticket status, add comment, and list recent tickets.

**IMPORTANT:** This is a non-production table clearly labeled with a "poc-" prefix to prevent any confusion with production ITSM systems.

---

## Table Configuration

### Table Name
```
poc-itsm-tickets
```

**Naming Convention:**
- Prefix: `poc-` (clearly identifies as non-production)
- Purpose: `itsm-tickets` (describes content)

### Region
```
us-east-1
```

### Billing Mode
```
PAY_PER_REQUEST (On-Demand)
```

**Rationale:**
- No need to provision capacity for PoC
- Pay only for actual read/write requests
- Automatically scales with usage
- Cost-effective for low-volume PoC workload
- No risk of throttling due to under-provisioning

---

## Primary Key Schema

### Partition Key (Hash Key)

**Attribute Name:** `ticket_id`  
**Type:** String (S)  
**Description:** Unique identifier for each ticket (UUID format)  
**Example:** `33567ee8-f182-4f8a-b03e-2f1515915471`

**Rationale:**
- Provides unique identification for each ticket
- Enables fast O(1) lookups by ticket ID
- UUID format ensures global uniqueness
- No sort key needed for primary access pattern

---

## Attributes

### Required Attributes

| Attribute Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ticket_id` | String (S) | Unique ticket identifier (UUID) | `33567ee8-f182-4f8a-b03e-2f1515915471` |
| `caller_id` | String (S) | Caller identifier (session ID or hashed phone) | `poc-user-001` |
| `issue_description` | String (S) | Description of the IT issue | `My laptop won't turn on` |
| `status` | String (S) | Current ticket status | `open` |
| `created_at` | String (S) | ISO 8601 timestamp of creation | `2026-02-09T12:20:25.343883Z` |
| `updated_at` | String (S) | ISO 8601 timestamp of last update | `2026-02-09T12:20:25.343883Z` |
| `comments` | List (L) | Array of comment objects | `[]` or `[{comment_text: "...", added_at: "..."}]` |

### Comment Object Structure

Each comment in the `comments` list is a Map (M) with:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `comment_text` | String (S) | The comment content | `Tried restarting but still not working` |
| `added_at` | String (S) | ISO 8601 timestamp | `2026-02-09T12:30:00.123456Z` |

---

## Global Secondary Index (GSI)

### Index Name
```
CallerIdIndex
```

### Index Keys

**Partition Key:** `caller_id` (String)  
**Sort Key:** `created_at` (String)

### Projection Type
```
ALL
```

**Rationale:**
- Projects all attributes to avoid additional read costs
- Enables full ticket retrieval without base table access

### Purpose

Supports the `list_recent_tickets` operation:
- Query tickets by `caller_id`
- Sort by `created_at` in descending order (most recent first)
- Limit to 10 most recent tickets

### Query Pattern

```python
response = table.query(
    IndexName='CallerIdIndex',
    KeyConditionExpression='caller_id = :caller_id',
    ExpressionAttributeValues={':caller_id': 'poc-user-001'},
    ScanIndexForward=False,  # Descending order (newest first)
    Limit=10
)
```

---

## Access Patterns

### 1. Create Ticket (POST /tickets)

**Operation:** PutItem  
**Key:** `ticket_id` (generated UUID)  
**Attributes:** All required attributes

```python
table.put_item(Item={
    'ticket_id': '33567ee8-f182-4f8a-b03e-2f1515915471',
    'caller_id': 'poc-user-001',
    'issue_description': 'My laptop won\'t turn on',
    'status': 'open',
    'created_at': '2026-02-09T12:20:25.343883Z',
    'updated_at': '2026-02-09T12:20:25.343883Z',
    'comments': []
})
```

### 2. Get Ticket Status (GET /tickets/{id})

**Operation:** GetItem  
**Key:** `ticket_id`

```python
response = table.get_item(Key={'ticket_id': '33567ee8-f182-4f8a-b03e-2f1515915471'})
ticket = response.get('Item')
```

### 3. Add Comment (POST /tickets/{id}/comments)

**Operation:** UpdateItem  
**Key:** `ticket_id`  
**Update Expression:** Append to `comments` list, update `updated_at`

```python
table.update_item(
    Key={'ticket_id': '33567ee8-f182-4f8a-b03e-2f1515915471'},
    UpdateExpression='SET comments = list_append(if_not_exists(comments, :empty_list), :comment), updated_at = :timestamp',
    ExpressionAttributeValues={
        ':comment': [{'comment_text': 'Tried restarting', 'added_at': '2026-02-09T12:30:00Z'}],
        ':timestamp': '2026-02-09T12:30:00Z',
        ':empty_list': []
    }
)
```

### 4. List Recent Tickets (GET /tickets?caller={caller_id})

**Operation:** Query on GSI  
**Index:** CallerIdIndex  
**Key Condition:** `caller_id = :caller_id`  
**Sort:** Descending by `created_at`  
**Limit:** 10

```python
response = table.query(
    IndexName='CallerIdIndex',
    KeyConditionExpression='caller_id = :caller_id',
    ExpressionAttributeValues={':caller_id': 'poc-user-001'},
    ScanIndexForward=False,
    Limit=10
)
tickets = response.get('Items', [])
```

---

## Sample Data

### Example Ticket (No Comments)

```json
{
  "ticket_id": "33567ee8-f182-4f8a-b03e-2f1515915471",
  "caller_id": "poc-user-001",
  "issue_description": "My laptop won't turn on after pressing the power button",
  "status": "open",
  "created_at": "2026-02-09T12:20:25.343883Z",
  "updated_at": "2026-02-09T12:20:25.343883Z",
  "comments": []
}
```

### Example Ticket (With Comments)

```json
{
  "ticket_id": "1d8d2fe2-4543-4e6d-aad0-9deed9d57070",
  "caller_id": "poc-user-001",
  "issue_description": "Email not working in Outlook",
  "status": "open",
  "created_at": "2026-02-09T12:32:57.917604Z",
  "updated_at": "2026-02-09T12:35:00.123456Z",
  "comments": [
    {
      "comment_text": "Tried restarting Outlook but still not working",
      "added_at": "2026-02-09T12:35:00.123456Z"
    },
    {
      "comment_text": "Checked internet connection - it's working fine",
      "added_at": "2026-02-09T12:36:30.789012Z"
    }
  ]
}
```

---

## DynamoDB Item Structure (AWS Format)

### Example in DynamoDB JSON Format

```json
{
  "ticket_id": {"S": "33567ee8-f182-4f8a-b03e-2f1515915471"},
  "caller_id": {"S": "poc-user-001"},
  "issue_description": {"S": "My laptop won't turn on"},
  "status": {"S": "open"},
  "created_at": {"S": "2026-02-09T12:20:25.343883Z"},
  "updated_at": {"S": "2026-02-09T12:20:25.343883Z"},
  "comments": {
    "L": [
      {
        "M": {
          "comment_text": {"S": "Tried restarting"},
          "added_at": {"S": "2026-02-09T12:30:00.123456Z"}
        }
      }
    ]
  }
}
```

---

## Cost Considerations

### On-Demand Pricing (us-east-1)

**Write Requests:** $1.25 per million write request units  
**Read Requests:** $0.25 per million read request units  
**Storage:** $0.25 per GB-month

### Estimated PoC Costs

Assuming:
- 10 tickets created (10 writes)
- 50 ticket status queries (50 reads)
- 20 comments added (20 writes)
- 10 list operations (10 reads)
- Total storage: < 1 MB

**Estimated Cost:** < $0.01 for entire PoC

---

## Performance Characteristics

### Latency

- **GetItem (by ticket_id):** Single-digit milliseconds
- **PutItem (create ticket):** Single-digit milliseconds
- **UpdateItem (add comment):** Single-digit milliseconds
- **Query (GSI - list tickets):** Single-digit milliseconds

### Scalability

- On-demand mode automatically scales
- No throttling concerns for PoC workload
- Can handle thousands of requests per second if needed

---

## Security Considerations

### IAM Permissions

Lambda function requires:
- `dynamodb:PutItem` on table
- `dynamodb:GetItem` on table
- `dynamodb:UpdateItem` on table
- `dynamodb:Query` on table and GSI

**No wildcard permissions** - scoped to specific table ARN.

### Data Privacy

- No real employee IDs or HR identifiers stored
- Caller identification uses session IDs or hashed phone numbers
- No sensitive information (passwords, MFA codes, device serials)

---

## Acceptance Criteria Validation

### Requirement 13.1-13.6: DynamoDB Schema

- ✅ Table name: `poc-itsm-tickets` (clear non-production prefix)
- ✅ Partition key: `ticket_id` (String)
- ✅ Attributes: ticket_id, caller_id, issue_description, status, created_at, updated_at, comments (List)
- ✅ Billing mode: ON_DEMAND (PAY_PER_REQUEST)
- ✅ GSI: `CallerIdIndex` with caller_id (partition key) and created_at (sort key)
- ✅ Region: us-east-1

### Query Pattern Support

- ✅ Supports create ticket (PutItem)
- ✅ Supports get ticket status (GetItem)
- ✅ Supports add comment (UpdateItem with list_append)
- ✅ Supports list recent tickets (Query on GSI with descending sort)

---

## AWS CLI Creation Command

```bash
aws dynamodb create-table \
  --table-name poc-itsm-tickets \
  --attribute-definitions \
    AttributeName=ticket_id,AttributeType=S \
    AttributeName=caller_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
  --key-schema \
    AttributeName=ticket_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[{
      \"IndexName\": \"CallerIdIndex\",
      \"KeySchema\": [
        {\"AttributeName\": \"caller_id\", \"KeyType\": \"HASH\"},
        {\"AttributeName\": \"created_at\", \"KeyType\": \"RANGE\"}
      ],
      \"Projection\": {\"ProjectionType\": \"ALL\"}
    }]" \
  --tags \
    "[{\"Key\": \"Environment\", \"Value\": \"PoC\"}, {\"Key\": \"Project\", \"Value\": \"AI-L1-Support\"}]" \
  --region us-east-1
```

---

## Task Status

**Task 0.3: DynamoDB Schema Design - COMPLETE ✅**

Schema design complete and documented:
- Table structure defined
- Primary key and GSI specified
- All access patterns documented
- Sample data provided
- Cost estimates included
- Security considerations addressed

**Note:** This schema was implemented in Task 1.1 (DynamoDB Table Creation). This document provides the design rationale and documentation that should have existed before deployment.
