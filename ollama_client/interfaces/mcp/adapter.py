import asyncio
import json
import websockets
from typing import Dict, Any, List, Optional
import os
import logging

from ollama_client.core.client import OllamaClient

logger = logging.getLogger(__name__)


class MCPAdapter:
    def __init__(
            self,
            client: OllamaClient,
            host: str = "0.0.0.0",
            port: int = 8080
    ):
        self.client = client
        self.host = host
        self.port = port
        self.connections = set()
        self.handlers = {
            "generate": self.handle_generate,
            "list_models": self.handle_list_models,
            "chat": self.handle_chat,
        }

        # MCP Tool definitions
        self.tools = {
            "generate": {
                "description": "Generate text based on a prompt using Ollama",
                "parameters": [
                    {
                        "name": "prompt",
                        "description": "The prompt text to generate from",
                        "type": "string",
                        "required": True
                    },
                    {
                        "name": "model",
                        "description": "The model to use for generation",
                        "type": "string",
                        "required": False,
                        "default": "llama3"
                    },
                    {
                        "name": "temperature",
                        "description": "The sampling temperature (0-1)",
                        "type": "number",
                        "required": False,
                        "default": 0.7
                    },
                    {
                        "name": "max_tokens",
                        "description": "Maximum number of tokens to generate",
                        "type": "integer",
                        "required": False,
                        "default": 512
                    }
                ]
            },
            "chat": {
                "description": "Chat with an Ollama model using a conversation history",
                "parameters": [
                    {
                        "name": "messages",
                        "description": "List of chat messages",
                        "type": "array",
                        "required": True
                    },
                    {
                        "name": "model",
                        "description": "The model to use for chat",
                        "type": "string",
                        "required": False,
                        "default": "llama3"
                    },
                    {
                        "name": "temperature",
                        "description": "The sampling temperature (0-1)",
                        "type": "number",
                        "required": False,
                        "default": 0.7
                    },
                    {
                        "name": "max_tokens",
                        "description": "Maximum number of tokens to generate",
                        "type": "integer",
                        "required": False,
                        "default": 512
                    }
                ]
            },
            "list_models": {
                "description": "List available models in Ollama",
                "parameters": []
            },
        }

    async def handle_generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate request from MCP"""
        prompt = data.get("prompt")
        model = data.get("model", "llama3")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 512)

        if not prompt:
            return {"error": "Prompt is required", "status": "error"}

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
            return {"error": str(e), "status": "error"}

    async def handle_list_models(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_models request from MCP"""
        try:
            models = self.client.list_models()
            return {
                "models": [
                    {
                        "name": model.name,
                        "size": model.size,
                        "modified_at": model.modified_at
                    }
                    for model in models
                ],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return {"error": str(e), "status": "error"}

    async def handle_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat request from MCP"""
        messages = data.get("messages", [])
        model = data.get("model", "llama3")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 512)

        if not messages:
            return {"error": "Messages are required", "status": "error"}

        try:
            response = self.client.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "message": {
                    "role": "assistant",
                    "content": response.text
                },
                "model": model,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {"error": str(e), "status": "error"}

    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection"""
        self.connections.add(websocket)

        try:
            # Send tools on connection
            await websocket.send(json.dumps({
                "type": "tools",
                "tools": self.tools
            }))

            async for message in websocket:
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
                except json.JSONDecodeError as e:
                    await websocket.send(json.dumps({
                        "error": f"Invalid JSON: {e}"
                    }))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await websocket.send(json.dumps({
                        "error": str(e)
                    }))
        finally:
            self.connections.remove(websocket)

    async def run(self):
        """Run the MCP adapter server"""
        server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        )

        logger.info(f"MCP adapter running at ws://{self.host}:{self.port}")

        try:
            await asyncio.Future()  # Run forever
        finally:
            server.close()
            await server.wait_closed()


def start():
    """Start the MCP adapter"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", 8080))
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Create client and adapter
    client = OllamaClient(host=ollama_host)
    adapter = MCPAdapter(client, host=host, port=port)

    # Run the adapter
    asyncio.run(adapter.run())


if __name__ == "__main__":
    start()