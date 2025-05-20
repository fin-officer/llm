from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import os

from ollama_client.core.client import OllamaClient
from ollama_client.core.models import ModelResponse, GenerationResponse
from ollama_client.interfaces.rest.schemas import (
    GenerateRequest,
    GenerateResponse,
    ModelListResponse
)

app = FastAPI(
    title="Ollama API",
    description="REST API for Ollama LLM",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_ollama_client():
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    return OllamaClient(host=host)

@app.get("/health", summary="Health check endpoint")
async def health_check():
    """Check if the API is running"""
    return {"status": "ok"}

@app.get("/models", response_model=ModelListResponse, summary="List available models")
async def list_models(client: OllamaClient = Depends(get_ollama_client)):
    """List all available models in Ollama"""
    try:
        models = client.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize the OllamaClient on startup"""
    global ollama_client

    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    ollama_client = OllamaClient(host=host)


# Include routes

@app.post("/generate", response_model=GenerateResponse, summary="Generate text from prompt")
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

def start():
    """Start the FastAPI server"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("ollama_client.interfaces.rest.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start()