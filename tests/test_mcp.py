import pytest
import asyncio
import websockets
import json
from unittest.mock import patch, MagicMock

from ollama_client.interfaces.mcp.adapter import MCPAdapter
from ollama_client.core.client import OllamaClient

@pytest.fixture
def client():
    return MagicMock(spec=OllamaClient)

@pytest.fixture
def adapter(client):
    return MCPAdapter(client=client, host="localhost", port=8080)

@pytest.mark.asyncio
async def test_handle_list_models(adapter, client):
    """Test the handle_list_models method"""
    # Setup mock
    client.list_models.return_value = [
        MagicMock(name="llama3", size=4200000000, modified_at="2023-11-09T12:34:56Z"),
        MagicMock(name="mistral", size=8600000000, modified_at="2023-11-08T10:11:12Z")
    ]
    
    # Call method
    result = await adapter.handle_list_models({})
    
    # Assertions
    assert result["status"] == "success"
    assert "models" in result
    assert len(result["models"]) == 2
    assert result["models"][0]["name"] == "llama3"
    assert result["models"][1]["name"] == "mistral"
    
    # Verify mock was called
    client.list_models.assert_called_once()

@pytest.mark.asyncio
async def test_handle_generate(adapter, client):
    """Test the handle_generate method"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.text = "I'm doing well, thank you for asking!"
    client.generate.return_value = mock_response
    
    # Call method
    result = await adapter.handle_generate({
        "prompt": "Hello, how are you?",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 512
    })
    
    # Assertions
    assert result["status"] == "success"
    assert result["text"] == "I'm doing well, thank you for asking!"
    assert result["model"] == "llama3"
    
    # Verify mock was called with correct arguments
    client.generate.assert_called_once_with(
        prompt="Hello, how are you?",
        model="llama3",
        temperature=0.7,
        max_tokens=512
    )

@pytest.mark.asyncio
async def test_handle_generate_missing_prompt(adapter, client):
    """Test the handle_generate method with missing prompt"""
    # Call method
    result = await adapter.handle_generate({
        "model": "llama3"
    })
    
    # Assertions
    assert result["status"] == "error"
    assert "error" in result
    assert "Prompt is required" in result["error"]
    
    # Verify mock was not called
    client.generate.assert_not_called()

@pytest.mark.asyncio
async def test_handle_chat(adapter, client):
    """Test the handle_chat method"""
    # Setup mock
    mock_response = MagicMock()
    mock_response.text = "I'm doing well, thank you for asking!"
    client.chat.return_value = mock_response
    
    # Call method
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    result = await adapter.handle_chat({
        "messages": messages,
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 512
    })
    
    # Assertions
    assert result["status"] == "success"
    assert result["message"]["role"] == "assistant"
    assert result["message"]["content"] == "I'm doing well, thank you for asking!"
    assert result["model"] == "llama3"
    
    # Verify mock was called with correct arguments
    client.chat.assert_called_once_with(
        messages=messages,
        model="llama3",
        temperature=0.7,
        max_tokens=512
    )

@pytest.mark.asyncio
async def test_handle_chat_missing_messages(adapter, client):
    """Test the handle_chat method with missing messages"""
    # Call method
    result = await adapter.handle_chat({
        "model": "llama3"
    })
    
    # Assertions
    assert result["status"] == "error"
    assert "error" in result
    assert "Messages are required" in result["error"]
    
    # Verify mock was not called
    client.chat.assert_not_called()