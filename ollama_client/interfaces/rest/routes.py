from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ollama_client.core.client import OllamaClient
from ollama_client.interfaces.rest.schemas import (
    GenerateRequest,
    GenerateResponse,
    ModelListResponse,
    ChatRequest,
    ChatResponse,
    ChatMessage
)

router = APIRouter()

def get_ollama_client():
    """Dependency to get OllamaClient instance"""
    from ollama_client.interfaces.rest.app import get_client
    return get_client()

@router.get("/health", summary="Health check endpoint")
async def health_check(client: OllamaClient = Depends(get_ollama_client)):
    """Check if the API and Ollama are running"""
    ollama_health = client.health()
    return {"api_status": "ok", "ollama_status": "ok" if ollama_health else "down"}

@router.get("/models", response_model=ModelListResponse, summary="List available models")
async def list_models(client: OllamaClient = Depends(get_ollama_client)):
    """List all available models in Ollama"""
    try:
        models = client.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=GenerateResponse, summary="Generate text from prompt")
async def generate(
    request: GenerateRequest,
    client: OllamaClient = Depends(get_ollama_client)
):
    """Generate text based on the provided prompt"""
    try:
        response = client.generate(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {"text": response.text, "model": request.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse, summary="Chat with the model")
async def chat(
    request: ChatRequest,
    client: OllamaClient = Depends(get_ollama_client)
):
    """Chat with the model using a list of messages"""
    try:
        # Convert ChatMessage objects to dictionaries
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = client.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return {
            "message": ChatMessage(role="assistant", content=response.text),
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))