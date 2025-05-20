from typing import List, Dict, Any, Optional, Union
import os
import tempfile
import contextlib
import logging

from ollama_client.core.client import OllamaClient, ModelInfo

logger = logging.getLogger(__name__)

class ModelManager:
    """Manager for Ollama models"""
    
    def __init__(self, client: OllamaClient):
        self.client = client
    
    def list_models(self) -> List[ModelInfo]:
        """List all available models"""
        return self.client.list_models()
    
    def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        models = self.list_models()
        for model in models:
            if model.name == name:
                return model
        return None
    
    def create_model_from_template(
        self,
        name: str,
        base_model: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new model from a template"""
        # Create model file content
        modelfile_content = [f"FROM {base_model}"]
        
        if system_prompt:
            modelfile_content.append(f"SYSTEM {system_prompt}")
        
        if parameters:
            for key, value in parameters.items():
                modelfile_content.append(f"PARAMETER {key} {value}")
        
        # Create temporary modelfile
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            for line in modelfile_content:
                f.write(f"{line}\n")
            modelfile_path = f.name
        
        try:
            # Create model
            return self.client.create_model(name, modelfile_path)
        finally:
            # Clean up temporary file
            os.unlink(modelfile_path)
    
    def delete_model(self, name: str) -> Dict[str, Any]:
        """Delete a model"""
        return self.client.delete_model(name)
    
    @contextlib.contextmanager
    def temporary_model(
        self,
        base_model: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Create a temporary model that will be deleted after use"""
        import uuid
        
        # Generate unique name
        name = f"temp-{uuid.uuid4().hex[:8]}"
        
        # Create model
        self.create_model_from_template(
            name=name,
            base_model=base_model,
            system_prompt=system_prompt,
            parameters=parameters
        )
        
        try:
            # Yield the model name
            yield name
        finally:
            # Clean up
            try:
                self.delete_model(name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary model {name}: {e}")