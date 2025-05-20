#!/usr/bin/env python
"""
Main entry point for Ollama client
"""
import typer
import sys
import os
from typing import Optional
from rich.console import Console

from ollama_client.core.client import OllamaClient
from ollama_client.utils.config import load_config
from ollama_client.utils.logging import setup_logging

app = typer.Typer(help="Ollama client")
console = Console()


@app.command()
def shell(
        host: Optional[str] = typer.Option(None, help="Ollama API host"),
        model: Optional[str] = typer.Option(None, help="Default model to use"),
        interactive: bool = typer.Option(True, help="Start interactive shell")
):
    """Start shell interface"""
    config = load_config()

    if interactive:
        # Run interactive shell
        from ollama_client.interfaces.shell.interactive import main as run_interactive

        run_interactive(
            host=host or config["ollama_host"],
            model=model or config["default_model"]
        )
    else:
        # Import CLI application
        from ollama_client.interfaces.shell.cli import app as cli_app

        # Set default host if provided
        if host:
            os.environ["OLLAMA_HOST"] = host

        # Run CLI app
        cli_app()


@app.command()
def api(
        host: Optional[str] = typer.Option(None, help="API host to bind"),
        port: Optional[int] = typer.Option(None, help="API port to bind"),
        ollama_host: Optional[str] = typer.Option(None, help="Ollama API host")
):
    """Start REST API server"""
    config = load_config()

    # Set environment variables for API app
    if ollama_host:
        os.environ["OLLAMA_HOST"] = ollama_host
    else:
        os.environ["OLLAMA_HOST"] = config["ollama_host"]

    if host:
        os.environ["HOST"] = host
    else:
        os.environ["HOST"] = config["api"]["host"]

    if port:
        os.environ["PORT"] = str(port)
    else:
        os.environ["PORT"] = str(config["api"]["port"])

    # Import and run API app
    from ollama_client.interfaces.rest.app import start as run_api
    run_api()


@app.command()
def mcp(
        host: Optional[str] = typer.Option(None, help="MCP host to bind"),
        port: Optional[int] = typer.Option(None, help="MCP port to bind"),
        ollama_host: Optional[str] = typer.Option(None, help="Ollama API host")
):
    """Start MCP adapter"""
    config = load_config()

    # Set environment variables for MCP adapter
    if ollama_host:
        os.environ["OLLAMA_HOST"] = ollama_host
    else:
        os.environ["OLLAMA_HOST"] = config["ollama_host"]

    if host:
        os.environ["HOST"] = host
    else:
        os.environ["HOST"] = config["mcp"]["host"]

    if port:
        os.environ["MCP_PORT"] = str(port)
    else:
        os.environ["MCP_PORT"] = str(config["mcp"]["port"])

    # Import and run MCP adapter
    from ollama_client.interfaces.mcp.adapter import start as run_mcp
    run_mcp()


@app.command()
def health(
        host: Optional[str] = typer.Option(None, help="Ollama API host")
):
    """Check if Ollama is running"""
    config = load_config()

    client = OllamaClient(host=host or config["ollama_host"])
    status = client.health()

    if status:
        console.print("[green]Ollama is running[/green]")
    else:
        console.print("[red]Ollama is not running[/red]")
        sys.exit(1)


if __name__ == "__main__":
    # Setup logging
    setup_logging()

    # Run app
    app()