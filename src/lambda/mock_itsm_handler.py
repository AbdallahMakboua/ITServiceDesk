import json
import uuid
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import time
import os

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
table_name = os.environ.get('TABLE_NAME', 'poc-itsm-tickets')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Main Lambda handler for Mock ITSM API operations.
    Handles: POST /tickets, GET /tickets/{id}, POST /tickets/{id}/comments, GET /tickets
    """
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        # Parse body if present
        if body:
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                return error_response(400, "Invalid JSON in request body")
        else:
            body_data = {}
        
        # Route to appropriate handler
        if http_method == 'POST' and path == '/tickets':
            return create_ticket(body_data)
        elif http_method == 'GET' and path.startswith('/tickets/'):
            ticket_id = path_parameters.get('id')
            if not ticket_id:
                return error_response(400, "Missing ticket ID")
            return get_ticket_status(ticket_id)
        elif http_method == 'POST' and path.startswith('/tickets/') and path.endswith('/comments'):
            ticket_id = path_parameters.get('id')
            if not ticket_id:
                return error_response(400, "Missing ticket ID")
            return add_ticket_comment(ticket_id, body_data)
        elif http_method == 'GET' and path == '/tickets':
            caller_id = query_parameters.get('caller')
            if not caller_id:
                return error_response(400, "Missing caller query parameter")
            return list_recent_tickets(caller_id)
        else:
            return error_response(404, "Endpoint not found")
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return error_response(500, "Internal server error")


def create_ticket(body_data):
    """
    Create a new ticket in DynamoDB.
    Expected input: {"caller_id": "string", "issue_description": "string"}
    """
    # Validate input
    caller_id = body_data.get('caller_id')
    issue_description = body_data.get('issue_description')
    
    if not caller_id or not issue_description:
        return error_response(400, "Missing required fields: caller_id and issue_description")
    
    # Generate ticket ID and timestamps
    ticket_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create ticket item
    ticket_item = {
        'ticket_id': ticket_id,
        'caller_id': caller_id,
        'issue_description': issue_description,
        'status': 'open',
        'created_at': timestamp,
        'updated_at': timestamp,
        'comments': []
    }
    
    # Put item in DynamoDB with retry
    try:
        retry_dynamodb_operation(lambda: table.put_item(Item=ticket_item))
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'ticket_id': ticket_id,
                'status': 'open',
                'created_at': timestamp
            })
        }
    except Exception as e:
        print(f"Error creating ticket: {str(e)}")
        return error_response(500, "Failed to create ticket")


def get_ticket_status(ticket_id):
    """
    Retrieve ticket by ID from DynamoDB.
    """
    try:
        response = retry_dynamodb_operation(lambda: table.get_item(Key={'ticket_id': ticket_id}))
        
        if 'Item' not in response:
            return error_response(404, f"Ticket {ticket_id} not found")
        
        ticket = response['Item']
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(ticket, default=str)
        }
    except Exception as e:
        print(f"Error retrieving ticket: {str(e)}")
        return error_response(500, "Failed to retrieve ticket")


def add_ticket_comment(ticket_id, body_data):
    """
    Add a comment to an existing ticket.
    Expected input: {"comment": "string"}
    """
    comment_text = body_data.get('comment')
    
    if not comment_text:
        return error_response(400, "Missing required field: comment")
    
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create comment object
    comment = {
        'comment_text': comment_text,
        'added_at': timestamp
    }
    
    try:
        # Update ticket with new comment
        response = retry_dynamodb_operation(lambda: table.update_item(
            Key={'ticket_id': ticket_id},
            UpdateExpression='SET comments = list_append(if_not_exists(comments, :empty_list), :comment), updated_at = :timestamp',
            ExpressionAttributeValues={
                ':comment': [comment],
                ':timestamp': timestamp,
                ':empty_list': []
            },
            ReturnValues='UPDATED_NEW'
        ))
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'updated_at': timestamp
            })
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return error_response(404, f"Ticket {ticket_id} not found")
        print(f"Error adding comment: {str(e)}")
        return error_response(500, "Failed to add comment")
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        return error_response(500, "Failed to add comment")


def list_recent_tickets(caller_id):
    """
    List recent tickets for a caller using GSI.
    """
    try:
        response = retry_dynamodb_operation(lambda: table.query(
            IndexName='CallerIdIndex',
            KeyConditionExpression='caller_id = :caller_id',
            ExpressionAttributeValues={
                ':caller_id': caller_id
            },
            ScanIndexForward=False,  # Sort by created_at descending
            Limit=10  # Limit to 10 most recent tickets
        ))
        
        tickets = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'tickets': tickets}, default=str)
        }
    except Exception as e:
        print(f"Error listing tickets: {str(e)}")
        return error_response(500, "Failed to list tickets")


def retry_dynamodb_operation(operation, max_attempts=3):
    """
    Retry DynamoDB operation with exponential backoff.
    """
    for attempt in range(max_attempts):
        try:
            return operation()
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['ProvisionedThroughputExceededException', 'ThrottlingException']:
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) * 0.1  # Exponential backoff: 0.1s, 0.2s, 0.4s
                    print(f"Throttled, retrying in {wait_time}s (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise
    raise Exception("Max retry attempts reached")


def error_response(status_code, message):
    """
    Generate standardized error response.
    """
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message})
    }
