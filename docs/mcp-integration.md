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