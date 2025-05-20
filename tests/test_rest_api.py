import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from ollama_client.core.client import OllamaClient
from ollama_client.interfaces.rest.app import app, get_client

# Mock the get_client function to return our mock client
@pytest.fixture
def client():
    return MagicMock(spec=OllamaClient)

@pytest.fixture
def test_client(client):
    # Patch the get_client function
    with patch("ollama_client.interfaces.rest.routes.get_client", return_value=client):
        # Create test client
        test_client = TestClient(app)
        yield test_client

def test_health_endpoint(test_client, client):
    """Test the health endpoint"""
    # Setup mock
    client.health.return_value = True
    
    # Make request
    response = test_client.get("/health")
    
    # Assertions
    assert response.status_code == 200
    assert response.json() == {"api_status": "ok", "ollama_status": "ok"}
    
    # Verify mock was called
    client.health.assert_called_once()

def test_health_endpoint_ollama_down(test_client, client):
    """Test the health endpoint when Ollama is down"""
    # Setup mock
    client.health.return_value = False
    
    # Make request
    response = test_client.get("/health")
    
    # Assertions
    assert response.status_code == 200
    assert response.json() == {"api_status": "ok", "ollama_status": "down"}
    
    # Verify mock was called
    client.health.assert_called_once()

def test_list_models_endpoint(test_client, client):
    """Test the list models endpoint"""
    # Setup mock
    model1 = MagicMock()
    model1.name = "llama3"
    model1.size = 4200000000
    model1.modified_at = "2023-11-09T12:34:56Z"
    model1.dict.return_value = {
        "name": "llama3",
        "size": 4200000000,
        "modified_at": "2023-11-09T12:34:56Z"
    }
    
    model2 = MagicMock()
    model2.name = "mistral"
    model2.size = 8600000000
    model2.modified_at = "2023-11-08T10:11:12Z"
    model2.dict.return_value = {
        "name": "mistral",
        "size": 8600000000,
        "modified_at": "2023-11-08T10:11:12Z"
    }
    
    client.list_models.return_value = [model1, model2]
    
    # Make request
    response = test_client.get("/models")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) == 2
    assert data["models"][0]["name"] == "llama3"
    assert data["models"][1]["name"] == "mistral"
    
    # Verify mock was called
    client.list_models.assert_called_once()

def test_generate_endpoint(test_client, client):
    """Test the generate endpoint"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.text = "I'm doing well, thank you for asking!"
    client.generate.return_value = mock_response
    
    # Make request
    response = test_client.post(
        "/generate",
        json={
            "prompt": "Hello, how are you?",
            "model": "llama3",
            "temperature": 0.7,
            "max_tokens": 512
        }
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "I'm doing well, thank you for asking!"
    assert data["model"] == "llama3"
    
    # Verify mock was called with correct arguments
    client.generate.assert_called_once_with(
        prompt="Hello, how are you?",
        model="llama3",
        temperature=0.7,
        max_tokens=512
    )

def test_chat_endpoint(test_client, client):
    """Test the chat endpoint"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.text = "I'm doing well, thank you for asking!"
    client.chat.return_value = mock_response
    
    # Make request
    response = test_client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "model": "llama3",
            "temperature": 0.7,
            "max_tokens": 512
        }
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["message"]["role"] == "assistant"
    assert data["message"]["content"] == "I'm doing well, thank you for asking!"
    assert data["model"] == "llama3"
    
    # Verify mock was called with correct arguments
    client.chat.assert_called_once()
    args, kwargs = client.chat.call_args
    assert kwargs["model"] == "llama3"
    assert kwargs["temperature"] == 0.7
    assert kwargs["max_tokens"] == 512
    assert len(kwargs["messages"]) == 1
    assert kwargs["messages"][0]["role"] == "user"
    assert kwargs["messages"][0]["content"] == "Hello, how are you?"