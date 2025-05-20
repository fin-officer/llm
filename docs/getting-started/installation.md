# Installation

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) (recommended) or pip
- [Ollama](https://ollama.ai/) server running (default: http://localhost:11434)

## Using Poetry (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ollama-client.git
   cd ollama-client
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

## Using pip

```bash
pip install ollama-client
```

## Verifying the Installation

To verify that the installation was successful, you can run:

```bash
python -m ollama_client.interfaces.shell.interactive --version
```

## Next Steps

- [Quick Start](./quickstart.md)
