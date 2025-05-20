# Ollama Client

A comprehensive Python client library for [Ollama](https://ollama.ai/) with multiple interfaces:

- **Shell Interface**: Interactive command-line interface for Ollama
- **REST API**: HTTP API for integration with web applications
- **MCP Adapter**: Model Context Protocol adapter for seamless integration with MCP-compatible applications

## Features

- Complete Ollama API support (generation, chat, model management)
- Synchronous and asynchronous API methods
- Multiple interface options (CLI, REST, MCP)
- Docker support for easy deployment
- Comprehensive test suite

## Installation

### Using Poetry

```bash
poetry install

Using pip
# Start the interactive shell
python -m ollama_client.interfaces.shell.interactive

# Or use the script installed by Poetry
ollama-shell


# Start the REST API server
python -m ollama_client.interfaces.rest.app

# Or use the script installed by Poetry
ollama-api

# Start the MCP adapter
python -m ollama_client.interfaces.mcp.adapter

# Or use the script installed by Poetry
ollama-mcp


# Start all services
docker-compose up -d

# Start specific service
docker-compose up rest-api

```

API Reference
Core Client API

```bash
from ollama_client.core.client import OllamaClient

# Initialize client
client = OllamaClient(host="http://localhost:11434")

# Generate text
response = client.generate(
    prompt="Hello, how are you?",
    model="llama3",
    temperature=0.7,
    max_tokens=512
)
print(response.text)

# Chat with the model
messages = [
    {"role": "user", "content": "Hello, how are you?"}
]
response = client.chat(messages, model="llama3")
print(response.text)

# List available models
models = client.list_models()
for model in models:
    print(f"{model.name} ({model.size} bytes)")
```


REST API Endpoints
```
GET /health: Health check endpoint
GET /models: List available models
POST /generate: Generate text from prompt
POST /chat: Chat with the model
```
MCP Protocol Actions
```
generate: Generate text from prompt
chat: Chat with the model
list_models: List available models
```

Development
```bash
pytest
black ollama_client
isort ollama_client

ruff ollama_client
mypy ollama_client
```


Kontynuuję plik Makefile dla projektu ollama-client:

```makefile
.PHONY: install dev test lint format clean build docker docker-compose docs

# Default Python executable
PYTHON ?= python3

# Poetry command
POETRY ?= poetry

# Docker compose command
DOCKER_COMPOSE ?= docker-compose

# Default image name for Docker
IMAGE_NAME ?= ollama-client

# Default tag for Docker image
IMAGE_TAG ?= latest

# Install dependencies
install:
	$(POETRY) install

# Install development dependencies
dev:
	$(POETRY) install --with dev

# Run tests
test:
	$(POETRY) run pytest

# Run tests with coverage
coverage:
	$(POETRY) run pytest --cov=ollama_client tests/ --cov-report=term --cov-report=html

# Run linters
lint:
	$(POETRY) run ruff ollama_client
	$(POETRY) run mypy ollama_client

# Format code
format:
	$(POETRY) run black ollama_client
	$(POETRY) run isort ollama_client

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build:
	$(POETRY) build

# Build Docker image
docker:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Run with Docker Compose
docker-compose:
	$(DOCKER_COMPOSE) up -d

# Stop Docker Compose services
docker-compose-down:
	$(DOCKER_COMPOSE) down

# Generate OpenAPI documentation
docs:
	mkdir -p docs
	$(POETRY) run python -m ollama_client.interfaces.rest.openapi docs/openapi.json

# Run shell interface
shell:
	$(POETRY) run python -m ollama_client.interfaces.shell.interactive

# Run REST API server
api:
	$(POETRY) run python -m ollama_client.interfaces.rest.app

# Run MCP adapter
mcp:
	$(POETRY) run python -m ollama_client.interfaces.mcp.adapter

# Run all services locally (not in Docker)
run-all:
	$(POETRY) run python -m ollama_client.interfaces.rest.app & \
	$(POETRY) run python -m ollama_client.interfaces.mcp.adapter & \
	wait

# Generate requirements.txt from poetry
requirements:
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

# Install pre-commit hooks
pre-commit:
	$(POETRY) run pre-commit install

# Help target
help:
	@echo "Available targets:"
	@echo "  install             Install dependencies"
	@echo "  dev                 Install development dependencies"
	@echo "  test                Run tests"
	@echo "  coverage            Run tests with coverage"
	@echo "  lint                Run linters"
	@echo "  format              Format code"
	@echo "  clean               Clean build artifacts"
	@echo "  build               Build package"
	@echo "  docker              Build Docker image"
	@echo "  docker-compose      Run with Docker Compose"
	@echo "  docker-compose-down Stop Docker Compose services"
	@echo "  docs                Generate OpenAPI documentation"
	@echo "  shell               Run shell interface"
	@echo "  api                 Run REST API server"
	@echo "  mcp                 Run MCP adapter"
	@echo "  run-all             Run all services locally"
	@echo "  requirements        Generate requirements.txt from poetry"
	@echo "  pre-commit          Install pre-commit hooks"
```

## 27. Ansible Deploy Role (ansible/roles/ollama-deploy/tasks/main.yml)

```yaml
---
- name: Create ollama-client directory
  file:
    path: "{{ ollama_client_dir }}"
    state: directory
    mode: 0755
  become: true

- name: Copy ollama-client files
  copy:
    src: "{{ item }}"
    dest: "{{ ollama_client_dir }}"
    mode: 0644
  with_items:
    - Dockerfile
    - docker-compose.yml
    - pyproject.toml
    - poetry.lock
    - README.md
  become: true

- name: Copy ollama-client source code
  copy:
    src: "{{ playbook_dir }}/../../ollama_client"
    dest: "{{ ollama_client_dir }}"
    mode: 0644
  become: true

- name: Create .env file
  template:
    src: env.j2
    dest: "{{ ollama_client_dir }}/.env"
    mode: 0644
  become: true

- name: Ensure Docker is installed
  package:
    name: docker.io
    state: present
  become: true

- name: Ensure Docker Compose is installed
  apt:
    name: docker-compose
    state: present
  become: true

- name: Start Docker service
  service:
    name: docker
    state: started
    enabled: yes
  become: true

- name: Pull Ollama image
  docker_image:
    name: ollama/ollama
    source: pull
  become: true

- name: Build and run with Docker Compose
  shell: cd {{ ollama_client_dir }} && docker-compose up -d --build
  become: true

- name: Wait for Ollama to be ready
  uri:
    url: "http://localhost:11434/api/health"
    status_code: 200
  register: result
  until: result.status == 200
  retries: 30
  delay: 10
  become: true

- name: Wait for REST API to be ready
  uri:
    url: "http://localhost:8000/health"
    status_code: 200
  register: result
  until: result.status == 200
  retries: 30
  delay: 5
  become: true

- name: Create systemd service for ollama-client
  template:
    src: ollama-client.service.j2
    dest: /etc/systemd/system/ollama-client.service
    mode: 0644
  become: true

- name: Enable and start ollama-client service
  systemd:
    name: ollama-client
    state: started
    enabled: yes
    daemon_reload: yes
  become: true
```

## 28. Ansible Deploy Template (ansible/roles/ollama-deploy/templates/ollama-client.service.j2)

```
[Unit]
Description=Ollama Client Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory={{ ollama_client_dir }}
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

## 29. Ansible Deploy Environment Template (ansible/roles/ollama-deploy/templates/env.j2)

```
# Ollama configuration
OLLAMA_HOST=http://ollama:11434

# REST API configuration
HOST=0.0.0.0
PORT=8000

# MCP configuration
MCP_HOST=0.0.0.0
MCP_PORT=8080
```

## 30. Integration Guide for MCP (docs/mcp-integration.md)

```markdown
# MCP Integration Guide

This guide explains how to integrate the Ollama client with applications using the Model Context Protocol (MCP).

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. It provides a standardized way to connect LLMs with the context they need.

## Connection

The Ollama MCP adapter runs a WebSocket server that you can connect to:

```javascript
// Connect to MCP adapter
const socket = new WebSocket('ws://localhost:8080');

// Handle connection open
socket.addEventListener('open', (event) => {
  console.log('Connected to Ollama MCP adapter');
});

// Handle messages
socket.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
});

// Handle errors
socket.addEventListener('error', (event) => {
  console.error('WebSocket error:', event);
});

// Handle connection close
socket.addEventListener('close', (event) => {
  console.log('Connection closed:', event.code, event.reason);
});
```

## Available Tools

When you connect to the MCP adapter, it will send a list of available tools:

```json
{
  "type": "tools",
  "tools": {
    "generate": {
      "description": "Generate text based on a prompt using Ollama",
      "parameters": [
        {
          "name": "prompt",
          "description": "The prompt text to generate from",
          "type": "string",
          "required": true
        },
        {
          "name": "model",
          "description": "The model to use for generation",
          "type": "string",
          "required": false,
          "default": "llama3"
        },
        {
          "name": "temperature",
          "description": "The sampling temperature (0-1)",
          "type": "number",
          "required": false,
          "default": 0.7
        },
        {
          "name": "max_tokens",
          "description": "Maximum number of tokens to generate",
          "type": "integer",
          "required": false,
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
          "required": true
        },
        {
          "name": "model",
          "description": "The model to use for chat",
          "type": "string",
          "required": false,
          "default": "llama3"
        },
        {
          "name": "temperature",
          "description": "The sampling temperature (0-1)",
          "type": "number",
          "required": false,
          "default": 0.7
        },
        {
          "name": "max_tokens",
          "description": "Maximum number of tokens to generate",
          "type": "integer",
          "required": false,
          "default": 512
        }
      ]
    },
    "list_models": {
      "description": "List available models in Ollama",
      "parameters": []
    }
  }
}
```

## Using Tools

You can use the available tools by sending a message with the action name and parameters:

### List Models

```javascript
socket.send(JSON.stringify({
  id: "1",  // Unique ID for tracking the request
  action: "list_models"
}));
```

Response:

```json
{
  "id": "1",
  "result": {
    "models": [
      {
        "name": "llama3",
        "size": 4200000000,
        "modified_at": "2023-11-09T12:34:56Z"
      },
      {
        "name": "mistral",
        "size": 8600000000,
        "modified_at": "2023-11-08T10:11:12Z"
      }
    ],
    "status": "success"
  }
}
```

### Generate Text

```javascript
socket.send(JSON.stringify({
  id: "2",  // Unique ID for tracking the request
  action: "generate",
  prompt: "Hello, how are you?",
  model: "llama3",
  temperature: 0.7,
  max_tokens: 512
}));
```

Response:

```json
{
  "id": "2",
  "result": {
    "text": "I'm doing well, thank you for asking! How can I assist you today?",
    "model": "llama3",
    "status": "success"
  }
}
```

### Chat

```javascript
socket.send(JSON.stringify({
  id: "3",  // Unique ID for tracking the request
  action: "chat",
  messages: [
    { "role": "user", "content": "Hello, how are you?" }
  ],
  model: "llama3",
  temperature: 0.7,
  max_tokens: 512
}));
```

Response:

```json
{
  "id": "3",
  "result": {
    "message": {
      "role": "assistant",
      "content": "I'm doing well, thank you for asking! How can I assist you today?"
    },
    "model": "llama3",
    "status": "success"
  }
}
```

## Error Handling

If an error occurs, the response will include an error message:

```json
{
  "id": "4",
  "error": "Model 'nonexistent-model' not found"
}
```

## Practical Example: Chat Application

Here's a complete example of a simple chat application using the MCP adapter:

```javascript
// Connect to MCP adapter
const socket = new WebSocket('ws://localhost:8080');
const chatMessages = [];

// Handle connection open
socket.addEventListener('open', (event) => {
  console.log('Connected to Ollama MCP adapter');
});

// Handle messages
socket.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  
  // Skip tools message
  if (data.type === 'tools') {
    return;
  }
  
  if (data.result && data.result.message) {
    // Add assistant message to chat history
    chatMessages.push(data.result.message);
    
    // Display message in UI
    displayMessage(data.result.message.role, data.result.message.content);
  } else if (data.error) {
    console.error('Error:', data.error);
  }
});

// Function to send user message
function sendMessage(content) {
  // Add user message to chat history
  const userMessage = { role: 'user', content };
  chatMessages.push(userMessage);
  
  // Display message in UI
  displayMessage('user', content);
  
  // Send chat request with full history
  socket.send(JSON.stringify({
    id: Date.now().toString(),
    action: 'chat',
    messages: chatMessages,
    model: 'llama3'
  }));
}

// Function to display message in UI
function displayMessage(role, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  messageDiv.textContent = content;
  document.getElementById('chat-messages').appendChild(messageDiv);
}

// Handle form submission
document.getElementById('chat-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const input = document.getElementById('message-input');
  const content = input.value.trim();
  
  if (content) {
    sendMessage(content);
    input.value = '';
  }
});
```

This example shows how to build a chat application that maintains conversation history and displays messages in the UI.
```

Powyższe pliki dostarczają kompleksową implementację projektu ollama-client z trzema interfejsami (shell, REST API i MCP) oraz wszystkimi wymaganymi narzędziami i konfiguracjami. Projekt jest dobrze ustrukturyzowany, z jasno zdefiniowanymi modułami, testami, dokumentacją i narzędziami deployment.

Główne zalety tej implementacji:

1. **Modularność** - każdy komponent jest oddzielny i może być używany niezależnie
2. **Pełne pokrycie testami** - testy jednostkowe oraz integracyjne dla każdego komponentu
3. **Wsparcie dla CI/CD** - konfiguracja GitHub Actions do automatycznego testowania i buildowania
4. **Dokumentacja** - szczegółowa dokumentacja API i instrukcje integracji
5. **Narzędzia deployment** - konfiguracja Ansible i Docker do łatwego wdrażania
6. **Minimalizacja kodu** - używanie bibliotek zewnętrznych i wzorców projektowych do ograniczenia ilości kodu

Projekt został zaprojektowany z myślą o elastyczności i łatwości rozszerzania, dzięki czemu można go łatwo dostosować do różnych przypadków użycia i zintegrować z innymi systemami.