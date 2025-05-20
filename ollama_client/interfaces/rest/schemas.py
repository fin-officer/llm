from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "llama3"
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(512, gt=0)

class GenerateResponse(BaseModel):
    text: str
    model: str

class ModelInfo(BaseModel):
    name: str
    size: int
    modified_at: str
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "llama3"
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(512, gt=0)

class ChatResponse(BaseModel):
    message: ChatMessage
    model: str