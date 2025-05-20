#!/usr/bin/env python
import cmd
import typer
from rich.console import Console
from rich.markdown import Markdown
from ollama_client.core.client import OllamaClient

console = Console()
app = typer.Typer()

class OllamaShell(cmd.Cmd):
    intro = "Welcome to Ollama Shell. Type help or ? to list commands."
    prompt = "ollama> "

    def __init__(self, client: OllamaClient):
        super().__init__()
        self.client = client
        self.model = "llama3"

    def do_query(self, arg):
        """Query the model: query [text]"""
        if not arg:
            console.print("[yellow]Please provide a query text[/yellow]")
            return

        try:
            response = self.client.generate(arg, model=self.model)
            console.print(Markdown(response.text))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_model(self, arg):
        """Change the model: model [model_name]"""
        if not arg:
            console.print(f"Current model: {self.model}")
            return

        try:
            models = self.client.list_models()
            if arg in [m.name for m in models]:
                self.model = arg
                console.print(f"[green]Model changed to {self.model}[/green]")
            else:
                console.print(f"[yellow]Model '{arg}' not found. Available models:[/yellow]")
                for model in models:
                    console.print(f"- {model.name}")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_models(self, arg):
        """List available models"""
        try:
            models = self.client.list_models()
            console.print("[bold]Available models:[/bold]")
            for model in models:
                console.print(f"- {model.name} ({model.size})")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_exit(self, arg):
        """Exit the shell"""
        return True

    # Aliases
    do_quit = do_exit
    do_q = do_query

@app.command()
def main(host: str = "http://localhost:11434"):
    """Interactive Ollama Shell"""
    client = OllamaClient(host=host)
    shell = OllamaShell(client)
    shell.cmdloop()

if __name__ == "__main__":
    app()