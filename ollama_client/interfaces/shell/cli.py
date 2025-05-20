#!/usr/bin/env python
import typer
import os
import sys
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

from ollama_client.core.client import OllamaClient

app = typer.Typer(help="Command-line interface for Ollama")
console = Console()

def get_client(host: str) -> OllamaClient:
    """Get Ollama client"""
    client = OllamaClient(host=host)
    if not client.health():
        console.print("[red]Error: Ollama is not running![/red]")
        console.print("[yellow]Please make sure Ollama is running and try again.[/yellow]")
        sys.exit(1)
    return client

@app.command()
def models(
    host: str = typer.Option("http://localhost:11434", help="Ollama API host")
):
    """List available models"""
    client = get_client(host)
    
    try:
        models = client.list_models()
        
        if not models:
            console.print("[yellow]No models available.[/yellow]")
            return
        
        console.print("[bold]Available Models:[/bold]")
        for model in models:
            # Convert size to human-readable format
            size_str = f"{model.size / (1024**3):.2f} GB" if model.size > 1024**3 else f"{model.size / (1024**2):.2f} MB"
            console.print(f"- [cyan]{model.name}[/cyan] ({size_str}, modified: {model.modified_at})")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Prompt text to generate from"),
    model: str = typer.Option("llama3", help="Model to use"),
    temperature: float = typer.Option(0.7, min=0.0, max=1.0, help="Sampling temperature"),
    max_tokens: int = typer.Option(512, help="Maximum tokens to generate"),
    host: str = typer.Option("http://localhost:11434", help="Ollama API host")
):
    """Generate text from a prompt"""
    client = get_client(host)
    
    try:
        with console.status("[bold green]Generating...[/bold green]"):
            response = client.generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        console.print(Markdown(response.text))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send"),
    model: str = typer.Option("llama3", help="Model to use"),
    temperature: float = typer.Option(0.7, min=0.0, max=1.0, help="Sampling temperature"),
    max_tokens: int = typer.Option(512, help="Maximum tokens to generate"),
    host: str = typer.Option("http://localhost:11434", help="Ollama API host")
):
    """Chat with the model (single message)"""
    client = get_client(host)
    
    try:
        messages = [{"role": "user", "content": message}]
        
        with console.status("[bold green]Thinking...[/bold green]"):
            response = client.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        console.print(Markdown(response.text))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@app.command()
def health(
    host: str = typer.Option("http://localhost:11434", help="Ollama API host")
):
    """Check if Ollama is running"""
    client = OllamaClient(host=host)
    
    status = client.health()
    
    if status:
        console.print("[green]Ollama is running[/green]")
    else:
        console.print("[red]Ollama is not running[/red]")
        sys.exit(1)

if __name__ == "__main__":
    app()