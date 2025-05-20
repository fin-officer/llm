import asyncio
import json
import websockets
from typing import Dict, Any, List, Optional, Callable
import os
import logging

from ollama_client.core.client import OllamaClient

logger = logging.getLogger(__name__)

class MCPAdapter:
    def __init__(self, client: OllamaClient, host: str = "0.0.0.0", port: int = 8080):
        self.client = client
        self.host = host
        self.port = port
        self.connections = set()
        self.handlers = {
            "generate": self.handle_generate,
            "list_models": self.handle_list_models,
        }
    
    async def handle_generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate request from MCP"""
        prompt = data.get("prompt", "")
        model = data.get("model", "llama3")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 512)
        
        try:
            response = self.client.generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return {
                "text": response.text,
                "model": model,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def handle_list_models(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_models request from MCP"""
        try:
            models = self.client.list_models()
            return {
                "models": [model.dict() for model in models],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming MCP message"""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action in self.handlers:
                result = await self.handlers[action](data)
                await websocket.send(json.dumps({
                    "id": data.get("id"),
                    "result": result
                }))
            else:
                await websocket.send(json.dumps({
                    "id": data.get("id"),
                    "error": f"Unknown action: {action}"
                }))
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "error": "Invalid JSON"
            }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                "error": str(e)
            }))
    
    async def handler(self, websocket, path):
        """WebSocket connection handler"""
        self.connections.add(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            self.connections.remove(websocket)
    
    async def run(self):
        """Run the MCP adapter server"""
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # Run forever

def start():
    """Start the MCP adapter"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", 8080))
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    client = OllamaClient(host=ollama_host)
    adapter = MCPAdapter(client, host=host, port=port)
    
    asyncio.run(adapter.run())

if __name__ == "__main__":
    start()