const ws = new WebSocket(`ws://${location.host}/ws`);
const chat = document.getElementById('chat');
const input = document.getElementById('message');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'message') addMessage('Agent', data.content);
    else if (data.type === 'tool') addMessage(`Tool: ${data.name}`, data.result, 'tool');
    else if (data.type === 'error') addMessage('Error', data.content, 'error');
};

function addMessage(sender, text, cls = '') {
    const div = document.createElement('div');
    div.className = `message ${cls}`;
    div.innerHTML = `<strong>${sender}:</strong> <pre>${text}</pre>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
    if (!input.value.trim()) return;
    addMessage('You', input.value);
    ws.send(JSON.stringify({ type: 'chat', content: input.value }));
    input.value = '';
}

function clearChat() {
    ws.send(JSON.stringify({ type: 'clear' }));
    chat.innerHTML = '';
}

input.addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});
