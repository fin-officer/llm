"""
Exception classes for Ollama client
"""

class OllamaError(Exception):
    """Base exception for Ollama client errors"""
    pass

class OllamaConnectionError(OllamaError):
    """Error connecting to Ollama server"""
    pass

class OllamaAPIError(OllamaError):
    """Error in Ollama API response"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)

class ModelNotFoundError(OllamaError):
    """Model not found"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__(f"Model '{model_name}' not found")

class InvalidModelError(OllamaError):
    """Invalid model definition"""
    pass