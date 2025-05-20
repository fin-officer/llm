import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    name: str
    size: int
    modified_at: str
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class GenerationResponse(BaseModel):
    text: str
    model: str
    created_at: Optional[str] = None
    done: bool = True
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
    
    def generate(
        self, 
        prompt: str, 
        model: str = "llama3", 
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> GenerationResponse:
        """Generate text based on the provided prompt"""
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        with httpx.Client() as client:
            response = client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                text=data.get("response", ""),
                model=model,
                created_at=data.get("created_at"),
                done=data.get("done", True),
                total_duration=data.get("total_duration"),
                load_duration=data.get("load_duration"),
                prompt_eval_duration=data.get("prompt_eval_duration"),
                eval_count=data.get("eval_count"),
                eval_duration=data.get("eval_duration")
            )
    
    async def generate_async(
        self, 
        prompt: str, 
        model: str = "llama3", 
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> GenerationResponse:
        """Generate text asynchronously based on the provided prompt"""
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                text=data.get("response", ""),
                model=model,
                created_at=data.get("created_at"),
                done=data.get("done", True),
                total_duration=data.get("total_duration"),
                load_duration=data.get("load_duration"),
                prompt_eval_duration=data.get("prompt_eval_duration"),
                eval_count=data.get("eval_count"),
                eval_duration=data.get("eval_duration")
            )
    
    def list_models(self) -> List[ModelInfo]:
        """List all available models in Ollama"""
        url = f"{self.host}/api/tags"
        
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model_data in data.get("models", []):
                models.append(ModelInfo(
                    name=model_data.get("name"),
                    size=model_data.get("size", 0),
                    modified_at=model_data.get("modified_at", ""),
                    digest=model_data.get("digest"),
                    details=model_data.get("details")
                ))
            
            return models
    
    async def list_models_async(self) -> List[ModelInfo]:
        """List all available models in Ollama asynchronously"""
        url = f"{self.host}/api/tags"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model_data in data.get("models", []):
                models.append(ModelInfo(
                    name=model_data.get("name"),
                    size=model_data.get("size", 0),
                    modified_at=model_data.get("modified_at", ""),
                    digest=model_data.get("digest"),
                    details=model_data.get("details")
                ))
            
            return models
    
    def create_model(
        self,
        name: str,
        model_file: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new model from a Modelfile"""
        url = f"{self.host}/api/create"
        
        with open(model_file, "r") as f:
            modelfile = f.read()
        
        payload = {
            "name": name,
            "modelfile": modelfile
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        with httpx.Client() as client:
            response = client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
    
    def delete_model(self, name: str) -> Dict[str, Any]:
        """Delete a model from Ollama"""
        url = f"{self.host}/api/delete"
        
        payload = {
            "name": name
        }
        
        with httpx.Client() as client:
            response = client.delete(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama3",
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> GenerationResponse:
        """Chat with the model using a list of messages"""
        url = f"{self.host}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        with httpx.Client() as client:
            response = client.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                text=data.get("message", {}).get("content", ""),
                model=model,
                created_at=data.get("created_at"),
                done=True
            )
    
    def health(self) -> bool:
        """Check if Ollama is running"""
        url = f"{self.host}/api/health"
        
        try:
            with httpx.Client() as client:
                response = client.get(url)
                return response.status_code == 200
        except Exception:
            return False