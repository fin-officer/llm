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