"""
Tests for demo_agent.py SSE functionality.

This test file validates that the /ask endpoint correctly handles both
JSON and Server-Sent Events (SSE) responses based on the Accept header.

Note: These tests use mocking to avoid dependencies on AWS services and MCP servers.
For full integration testing, use the manual testing scripts.
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# Mock the dependencies before importing the module
sys.modules['strands'] = MagicMock()
sys.modules['strands.models'] = MagicMock()
sys.modules['strands.tools'] = MagicMock()
sys.modules['strands.tools.mcp'] = MagicMock()
sys.modules['strands.session'] = MagicMock()
sys.modules['strands.session.file_session_manager'] = MagicMock()
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.client'] = MagicMock()
sys.modules['mcp.client.sse'] = MagicMock()

# Now import the app
from demo_agent import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_agent_response():
    """Mock the agent response."""
    mock_response = MagicMock()
    mock_response.message = {
        'content': [
            {'text': 'This is a test response from the agent'}
        ]
    }
    return mock_response

def test_ask_endpoint_with_json_accept(client, mock_agent_response):
    """Test /ask endpoint returns JSON when Accept header is not text/event-stream."""
    with patch('demo_agent.MCPClient') as mock_mcp, \
         patch('demo_agent.Agent') as mock_agent_class:
        
        # Setup mocks
        mock_agent_instance = MagicMock()
        mock_agent_instance.return_value = mock_agent_response
        mock_agent_class.return_value = mock_agent_instance
        
        mock_client_instance = MagicMock()
        mock_client_instance.list_tools_sync.return_value = []
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=None)
        mock_mcp.return_value = mock_client_instance
        
        # Make request with JSON accept header
        response = client.post('/ask',
                               json={'query': 'test query', 'session_id': 'test_session'},
                               headers={'Accept': 'application/json'})
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'response' in data
        assert data['response'] == 'This is a test response from the agent'

def test_ask_endpoint_with_sse_accept(client, mock_agent_response):
    """Test /ask endpoint returns SSE when Accept header is text/event-stream."""
    with patch('demo_agent.MCPClient') as mock_mcp, \
         patch('demo_agent.Agent') as mock_agent_class:
        
        # Setup mocks
        mock_agent_instance = MagicMock()
        mock_agent_instance.return_value = mock_agent_response
        mock_agent_class.return_value = mock_agent_instance
        
        mock_client_instance = MagicMock()
        mock_client_instance.list_tools_sync.return_value = []
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=None)
        mock_mcp.return_value = mock_client_instance
        
        # Make request with SSE accept header
        response = client.post('/ask',
                               json={'query': 'test query', 'session_id': 'test_session'},
                               headers={'Accept': 'text/event-stream'})
        
        assert response.status_code == 200
        assert response.content_type == 'text/event-stream; charset=utf-8'
        
        # Verify SSE format
        response_data = response.data.decode('utf-8')
        assert response_data == 'data: This is a test response from the agent\n\n'

def test_ask_endpoint_without_query(client):
    """Test /ask endpoint returns 400 when query is not provided."""
    response = client.post('/ask',
                           json={'session_id': 'test_session'},
                           headers={'Accept': 'application/json'})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Query not provided'

def test_ask_endpoint_default_accept_header(client, mock_agent_response):
    """Test /ask endpoint returns JSON when Accept header is not specified."""
    with patch('demo_agent.MCPClient') as mock_mcp, \
         patch('demo_agent.Agent') as mock_agent_class:
        
        # Setup mocks
        mock_agent_instance = MagicMock()
        mock_agent_instance.return_value = mock_agent_response
        mock_agent_class.return_value = mock_agent_instance
        
        mock_client_instance = MagicMock()
        mock_client_instance.list_tools_sync.return_value = []
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=None)
        mock_mcp.return_value = mock_client_instance
        
        # Make request without explicit Accept header
        response = client.post('/ask',
                               json={'query': 'test query', 'session_id': 'test_session'})
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'response' in data
        assert data['response'] == 'This is a test response from the agent'
