import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

DEFAULT_CONFIG_DIR = os.path.expanduser("~/.config/ollama-client")
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "config.json")


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file"""
    config_file = config_file or DEFAULT_CONFIG_FILE

    # Default configuration
    config = {
        "ollama_host": "http://localhost:11434",
        "default_model": "llama3",
        "temperature": 0.7,
        "max_tokens": 512,
        "api": {
            "host": "0.0.0.0",
            "port": 8000
        },
        "mcp": {
            "host": "0.0.0.0",
            "port": 8080
        }
    }

    # Load from file if it exists
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Error loading config file: {e}")

    # Override with environment variables
    if "OLLAMA_HOST" in os.environ:
        config["ollama_host"] = os.environ["OLLAMA_HOST"]

    if "OLLAMA_MODEL" in os.environ:
        config["default_model"] = os.environ["OLLAMA_MODEL"]

    if "API_HOST" in os.environ:
        config["api"]["host"] = os.environ["API_HOST"]

    if "API_PORT" in os.environ:
        try:
            config["api"]["port"] = int(os.environ["API_PORT"])
        except ValueError:
            pass

    if "MCP_HOST" in os.environ:
        config["mcp"]["host"] = os.environ["MCP_HOST"]

    if "MCP_PORT" in os.environ:
        try:
            config["mcp"]["port"] = int(os.environ["MCP_PORT"])
        except ValueError:
            pass

    return config


def save_config(config: Dict[str, Any], config_file: Optional[str] = None) -> None:
    """Save configuration to file"""
    config_file = config_file or DEFAULT_CONFIG_FILE

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    # Save config
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)