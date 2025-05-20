#!/usr/bin/env python
import cmd
import typer
import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from typing import List, Dict, Any, Optional

from ollama_client.core.client import OllamaClient

console = Console()
app = typer.Typer()


class OllamaShell(cmd.Cmd):
    intro = "Welcome to Ollama Shell. Type help or ? to list commands."
    prompt = "ollama> "

    def __init__(self, client: OllamaClient, model: str = "llama3"):
        super().__init__()
        self.client = client
        self.model = model
        self.conversation = []

        # Check if Ollama is running
        if not self.client.health():
            console.print("[red]Error: Ollama is not running![/red]")
            console.print("[yellow]Please make sure Ollama is running and try again.[/yellow]")
            sys.exit(1)

        # Check if the model exists
        try:
            models = self.client.list_models()
            if not any(m.name == self.model for m in models):
                console.print(f"[yellow]Warning: Model '{self.model}' not found.[/yellow]")

                if models:
                    self.model = models[0].name
                    console.print(f"[green]Using '{self.model}' instead.[/green]")
                else:
                    console.print("[red]No models available. Please download a model first.[/red]")
                    sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error checking models: {e}[/red]")

    def do_query(self, arg):
        """Generate response for a single query: query [text]"""
        if not arg:
            console.print("[yellow]Please provide a query text[/yellow]")
            return

        try:
            console.print(f"[bold blue]Query:[/bold blue] {arg}")
            with console.status("[bold green]Generating response...[/bold green]"):
                response = self.client.generate(arg, model=self.model)

            console.print("[bold green]Response:[/bold green]")
            console.print(Markdown(response.text))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_chat(self, arg):
        """Chat with the model (maintains conversation history): chat [text]"""
        if not arg:
            console.print("[yellow]Please provide a message[/yellow]")
            return

        try:
            # Add user message to conversation
            self.conversation.append({"role": "user", "content": arg})

            console.print(f"[bold blue]You:[/bold blue] {arg}")
            with console.status("[bold green]Thinking...[/bold green]"):
                response = self.client.chat(self.conversation, model=self.model)

            # Add assistant response to conversation
            self.conversation.append({"role": "assistant", "content": response.text})

            console.print(f"[bold green]{self.model}:[/bold green]")
            console.print(Markdown(response.text))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_reset(self, arg):
        """Reset the conversation history"""
        self.conversation = []
        console.print("[green]Conversation history has been reset.[/green]")

    def do_model(self, arg):
        """Change the model: model [model_name]"""
        if not arg:
            console.print(f"Current model: {self.model}")
            return

        try:
            models = self.client.list_models()
            model_names = [m.name for m in models]

            if arg in model_names:
                self.model = arg
                console.print(f"[green]Model changed to {self.model}[/green]")
            else:
                console.print(f"[yellow]Model '{arg}' not found. Available models:[/yellow]")
                for model in model_names:
                    console.print(f"- {model}")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_models(self, arg):
        """List available models"""
        try:
            models = self.client.list_models()

            if not models:
                console.print("[yellow]No models available.[/yellow]")
                return

            table = Table(title="Available Models")
            table.add_column("Name", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Modified", style="blue")

            for model in models:
                # Convert size to human-readable format
                size_str = f"{model.size / (1024 ** 3):.2f} GB" if model.size > 1024 ** 3 else f"{model.size / (1024 ** 2):.2f} MB"
                table.add_row(model.name, size_str, model.modified_at)

            console.print(table)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_info(self, arg):
        """Show information about the current session"""
        console.print(Panel(f"[bold]Ollama Session Info[/bold]"))
        console.print(f"Ollama Host: [cyan]{self.client.host}[/cyan]")
        console.print(f"Current Model: [cyan]{self.model}[/cyan]")
        console.print(f"Conversation Length: [cyan]{len(self.conversation)}[/cyan] messages")

        # Check Ollama status
        health = self.client.health()
        status = "[green]Running[/green]" if health else "[red]Not Running[/red]"
        console.print(f"Ollama Status: {status}")

    def do_exit(self, arg):
        """Exit the shell"""
        console.print("[green]Goodbye![/green]")
        return True

    # Aliases
    do_quit = do_exit
    do_q = do_query
    do_c = do_chat


@app.command()
def main(
        host: str = typer.Option("http://localhost:11434", help="Ollama API host"),
        model: str = typer.Option("llama3", help="Default model to use")
):
    """Interactive Ollama Shell"""
    client = OllamaClient(host=host)
    shell = OllamaShell(client, model=model)
    shell.cmdloop()


if __name__ == "__main__":
    app()