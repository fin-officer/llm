# Quick Start

This guide will help you get up and running with the Ollama Client quickly.

## Starting the Interactive Shell

```bash
# Using Poetry
poetry run ollama-shell

# Or directly
python -m ollama_client.interfaces.shell.interactive
```

## Starting the REST API Server

```bash
# Using Poetry
poetry run ollama-api

# Or directly
python -m ollama_client.interfaces.rest.app
```

## Starting the MCP Adapter

```bash
# Using Poetry
poetry run ollama-mcp

# Or directly
python -m ollama_client.interfaces.mcp.adapter
```

## Using Docker Compose

You can start all services using Docker Compose:

```bash
docker-compose up -d
```

Or start specific services:

```bash
docker-compose up rest-api
```

## Next Steps

- [Core Client API](../features/core-client.md)
- [REST API](../features/rest-api.md)
- [MCP Adapter](../features/mcp-adapter.md)
