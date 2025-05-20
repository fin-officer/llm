import pytest
import httpx
from unittest.mock import patch, MagicMock

from ollama_client.core.client import OllamaClient, ModelInfo, GenerationResponse

@pytest.fixture
def client():
    return OllamaClient(host="http://localhost:11434")

def test_client_initialization():
    """Test client initialization with default and custom host"""
    client1 = OllamaClient()
    assert client1.host == "http://localhost:11434"

    client2 = OllamaClient(host="http://custom-host:11434")
    assert client2.host == "http://custom-host:11434"

    # Test trailing slash is removed
    client3 = OllamaClient(host="http://localhost:11434/")
    assert client3.host == "http://localhost:11434"

@patch("httpx.Client")
def test_generate(mock_client, client):
    """Test the generate method"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "I'm doing well, thank you for asking!",
        "created_at": "2023-11-09T12:34:56Z",
        "done": True,
        "total_duration": 1234567890,
        "load_duration": 123456,
        "prompt_eval_duration": 234567,
        "eval_count": 100,
        "eval_duration": 345678
    }

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Call generate method
    response = client.generate(
        prompt="Hello, how are you?",
        model="llama3",
        temperature=0.7,
        max_tokens=512
    )

    # Assertions
    assert isinstance(response, GenerationResponse)
    assert response.text == "I'm doing well, thank you for asking!"
    assert response.model == "llama3"
    assert response.created_at == "2023-11-09T12:34:56Z"
    assert response.done is True
    assert response.total_duration == 1234567890
    assert response.load_duration == 123456
    assert response.prompt_eval_duration == 234567
    assert response.eval_count == 100
    assert response.eval_duration == 345678

    # Check if post was called with correct arguments
    mock_client_instance.post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": "Hello, how are you?",
            "temperature": 0.7,
            "max_tokens": 512
        },
        headers={"Content-Type": "application/json"}
    )

@patch("httpx.Client")
def test_list_models(mock_client, client):
    """Test the list_models method"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {
                "name": "llama3",
                "size": 4200000000,
                "modified_at": "2023-11-09T12:34:56Z",
                "digest": "sha256:abc123",
                "details": {"some": "details"}
            },
            {
                "name": "mistral",
                "size": 8600000000,
                "modified_at": "2023-11-08T10:11:12Z"
            }
        ]
    }

    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Call list_models method
    models = client.list_models()

    # Assertions
    assert len(models) == 2
    assert isinstance(models[0], ModelInfo)
    assert models[0].name == "llama3"
    assert models[0].size == 4200000000
    assert models[0].modified_at == "2023-11-09T12:34:56Z"
    assert models[0].digest == "sha256:abc123"
    assert models[0].details == {"some": "details"}

    assert models[1].name == "mistral"
    assert models[1].size == 8600000000
    assert models[1].modified_at == "2023-11-08T10:11:12Z"
    assert models[1].digest is None
    assert models[1].details is None

    # Check if get was called with correct arguments
    mock_client_instance.get.assert_called_once_with(
        "http://localhost:11434/api/tags",
        headers={"Content-Type": "application/json"}
    )

@patch("httpx.Client")
def test_chat(mock_client, client):
    """Test the chat method"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "role": "assistant",
            "content": "I'm doing well, thank you for asking!"
        },
        "created_at": "2023-11-09T12:34:56Z"
    }

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Call chat method
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]

    response = client.chat(
        messages=messages,
        model="llama3",
        temperature=0.7,
        max_tokens=512
    )

    # Assertions
    assert isinstance(response, GenerationResponse)
    assert response.text == "I'm doing well, thank you for asking!"
    assert response.model == "llama3"
    assert response.created_at == "2023-11-09T12:34:56Z"

    # Check if post was called with correct arguments
    mock_client_instance.post.assert_called_once_with(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512
        },
        headers={"Content-Type": "application/json"}
    )

@patch("httpx.Client")
def test_health(mock_client, client):
    """Test the health method"""
    # Setup mock for successful health check
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200

    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response_success
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Call health method - success case
    health_status = client.health()

    # Assertions
    assert health_status is True

    # Setup mock for failed health check
    mock_client.reset_mock()
    mock_client_instance.get.side_effect = httpx.HTTPError("Connection error")

    # Call health method - failure case
    health_status = client.health()

    # Assertions
    assert health_status is False