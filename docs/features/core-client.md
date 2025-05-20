# Core Client API

The Core Client provides a Python interface to interact with the Ollama server.

## Basic Usage

```python
from ollama_client.core.client import OllamaClient

# Initialize the client
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

## Available Methods

### `generate(prompt, model, **kwargs)`
Generate text from a prompt.

**Parameters:**
- `prompt` (str): The input prompt
- `model` (str): The model to use
- `temperature` (float, optional): Controls randomness (0.0 to 1.0)
- `max_tokens` (int, optional): Maximum number of tokens to generate
- `top_p` (float, optional): Nucleus sampling parameter
- `top_k` (int, optional): Top-k sampling parameter

**Returns:**
`GenerationResponse` object containing the generated text and metadata.

### `chat(messages, model, **kwargs)`
Have a conversation with the model.

**Parameters:**
- `messages` (List[Dict]): List of message dictionaries with 'role' and 'content'
- `model` (str): The model to use
- `temperature` (float, optional): Controls randomness (0.0 to 1.0)
- `max_tokens` (int, optional): Maximum number of tokens to generate

**Returns:**
`ChatResponse` object containing the model's response and metadata.

### `list_models()`
List all available models.

**Returns:**
List of `Model` objects with name and size attributes.

## Error Handling

The client raises specific exceptions for different error conditions:

- `OllamaConnectionError`: Failed to connect to the Ollama server
- `OllamaAPIError`: The API returned an error
- `OllamaValidationError`: Invalid parameters were provided
