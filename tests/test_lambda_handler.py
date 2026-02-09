import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src/lambda to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

import mock_itsm_handler


@pytest.fixture
def mock_table():
    """Mock DynamoDB table"""
    with patch('mock_itsm_handler.table') as mock:
        yield mock


@pytest.fixture
def sample_ticket():
    """Sample ticket data"""
    return {
        'ticket_id': 'test-ticket-123',
        'caller_id': 'user-001',
        'issue_description': 'Laptop not turning on',
        'status': 'open',
        'created_at': '2026-02-09T12:00:00Z',
        'updated_at': '2026-02-09T12:00:00Z',
        'comments': []
    }


class TestCreateTicket:
    """Test create_ticket operation"""
    
    def test_create_ticket_success(self, mock_table):
        """Test successful ticket creation"""
        mock_table.put_item.return_value = {}
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'caller_id': 'user-001',
                'issue_description': 'Laptop not turning on'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'ticket_id' in body
        assert body['status'] == 'open'
        assert 'created_at' in body
        mock_table.put_item.assert_called_once()
    
    def test_create_ticket_missing_caller_id(self, mock_table):
        """Test ticket creation with missing caller_id"""
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'issue_description': 'Laptop not turning on'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        mock_table.put_item.assert_not_called()
    
    def test_create_ticket_missing_issue_description(self, mock_table):
        """Test ticket creation with missing issue_description"""
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'caller_id': 'user-001'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        mock_table.put_item.assert_not_called()
    
    def test_create_ticket_invalid_json(self, mock_table):
        """Test ticket creation with invalid JSON"""
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': 'invalid json'
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        mock_table.put_item.assert_not_called()
    
    def test_create_ticket_dynamodb_error(self, mock_table):
        """Test ticket creation with DynamoDB error"""
        from botocore.exceptions import ClientError
        
        mock_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}},
            'PutItem'
        )
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'caller_id': 'user-001',
                'issue_description': 'Laptop not turning on'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body


class TestGetTicketStatus:
    """Test get_ticket_status operation"""
    
    def test_get_ticket_success(self, mock_table, sample_ticket):
        """Test successful ticket retrieval"""
        mock_table.get_item.return_value = {'Item': sample_ticket}
        
        event = {
            'httpMethod': 'GET',
            'path': '/tickets/test-ticket-123',
            'pathParameters': {'id': 'test-ticket-123'}
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['ticket_id'] == 'test-ticket-123'
        assert body['caller_id'] == 'user-001'
        mock_table.get_item.assert_called_once()
    
    def test_get_ticket_not_found(self, mock_table):
        """Test ticket retrieval when ticket doesn't exist"""
        mock_table.get_item.return_value = {}
        
        event = {
            'httpMethod': 'GET',
            'path': '/tickets/nonexistent',
            'pathParameters': {'id': 'nonexistent'}
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body
    
    def test_get_ticket_missing_id(self, mock_table):
        """Test ticket retrieval with missing ID"""
        event = {
            'httpMethod': 'GET',
            'path': '/tickets/',
            'pathParameters': {}
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        mock_table.get_item.assert_not_called()


class TestAddTicketComment:
    """Test add_ticket_comment operation"""
    
    def test_add_comment_success(self, mock_table):
        """Test successful comment addition"""
        mock_table.update_item.return_value = {
            'Attributes': {
                'updated_at': '2026-02-09T12:30:00Z'
            }
        }
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets/test-ticket-123/comments',
            'pathParameters': {'id': 'test-ticket-123'},
            'body': json.dumps({
                'comment': 'Tried restarting, still not working'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'updated_at' in body
        mock_table.update_item.assert_called_once()
    
    def test_add_comment_missing_comment(self, mock_table):
        """Test comment addition with missing comment text"""
        event = {
            'httpMethod': 'POST',
            'path': '/tickets/test-ticket-123/comments',
            'pathParameters': {'id': 'test-ticket-123'},
            'body': json.dumps({})
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        mock_table.update_item.assert_not_called()
    
    def test_add_comment_ticket_not_found(self, mock_table):
        """Test comment addition when ticket doesn't exist"""
        from botocore.exceptions import ClientError
        
        mock_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Item not found'}},
            'UpdateItem'
        )
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets/nonexistent/comments',
            'pathParameters': {'id': 'nonexistent'},
            'body': json.dumps({
                'comment': 'Test comment'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body


class TestListRecentTickets:
    """Test list_recent_tickets operation"""
    
    def test_list_tickets_success(self, mock_table, sample_ticket):
        """Test successful ticket listing"""
        mock_table.query.return_value = {
            'Items': [sample_ticket]
        }
        
        event = {
            'httpMethod': 'GET',
            'path': '/tickets',
            'queryStringParameters': {'caller': 'user-001'}
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'tickets' in body
        assert len(body['tickets']) == 1
        assert body['tickets'][0]['ticket_id'] == 'test-ticket-123'
        mock_table.query.assert_called_once()
    
    def test_list_tickets_empty(self, mock_table):
        """Test ticket listing with no results"""
        mock_table.query.return_value = {'Items': []}
        
        event = {
            'httpMethod': 'GET',
            'path': '/tickets',
            'queryStringParameters': {'caller': 'user-999'}
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'tickets' in body
        assert len(body['tickets']) == 0
    
    def test_list_tickets_missing_caller(self, mock_table):
        """Test ticket listing with missing caller parameter"""
        event = {
            'httpMethod': 'GET',
            'path': '/tickets',
            'queryStringParameters': {}
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        mock_table.query.assert_not_called()


class TestRetryLogic:
    """Test DynamoDB retry logic"""
    
    def test_retry_on_throttling(self, mock_table):
        """Test retry logic on throttling exception"""
        from botocore.exceptions import ClientError
        
        # First two calls fail with throttling, third succeeds
        mock_table.put_item.side_effect = [
            ClientError(
                {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
                'PutItem'
            ),
            ClientError(
                {'Error': {'Code': 'ThrottlingException', 'Message': 'Throttled'}},
                'PutItem'
            ),
            {}
        ]
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'caller_id': 'user-001',
                'issue_description': 'Test issue'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 201
        assert mock_table.put_item.call_count == 3
    
    def test_retry_max_attempts_exceeded(self, mock_table):
        """Test retry logic when max attempts exceeded"""
        from botocore.exceptions import ClientError
        
        # All attempts fail with throttling
        mock_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
            'PutItem'
        )
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'caller_id': 'user-001',
                'issue_description': 'Test issue'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 500
        assert mock_table.put_item.call_count == 3


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self, mock_table):
        """Test request to invalid endpoint"""
        event = {
            'httpMethod': 'DELETE',
            'path': '/tickets/test-ticket-123'
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body
    
    def test_unexpected_exception(self, mock_table):
        """Test handling of unexpected exceptions"""
        mock_table.put_item.side_effect = Exception("Unexpected error")
        
        event = {
            'httpMethod': 'POST',
            'path': '/tickets',
            'body': json.dumps({
                'caller_id': 'user-001',
                'issue_description': 'Test issue'
            })
        }
        
        response = mock_itsm_handler.lambda_handler(event, {})
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
