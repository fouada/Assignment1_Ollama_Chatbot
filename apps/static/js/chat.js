/**
 * ============================================
 * LUXURIOUS OLLAMA CHATBOT - CLIENT SCRIPT
 * ============================================
 */

class LuxuryChatbot {
    constructor() {
        this.chatHistory = []; // Store chat messages for sidebar
        this.initElements();
        this.initEventListeners();
        this.loadModels();
        this.checkHealth();
    }

    initElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatForm = document.getElementById('chat-form');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.clearButton = document.getElementById('clear-button');
        this.modelSelect = document.getElementById('model-select');
        this.temperatureSlider = document.getElementById('temperature');
        this.tempValue = document.getElementById('temp-value');
        this.statusBadge = document.getElementById('status-badge');
        this.charCount = document.getElementById('char-count');
        
        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.sidebarClose = document.getElementById('sidebar-close');
        this.chatHistoryContainer = document.getElementById('chat-history-container');
    }

    initEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));

        // Enter key handling
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.chatForm.dispatchEvent(new Event('submit'));
            }
        });

        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.updateCharCount();
        });

        // Clear chat
        this.clearButton.addEventListener('click', () => this.clearChat());

        // Temperature slider
        this.temperatureSlider.addEventListener('input', (e) => {
            this.tempValue.textContent = e.target.value;
        });

        // Sidebar toggle
        this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        this.sidebarClose.addEventListener('click', () => this.toggleSidebar());
        
        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (this.sidebar.classList.contains('open') && 
                !this.sidebar.contains(e.target) && 
                !this.sidebarToggle.contains(e.target)) {
                this.toggleSidebar();
            }
        });
    }

    autoResizeTextarea() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = this.userInput.scrollHeight + 'px';
    }

    updateCharCount() {
        const count = this.userInput.value.length;
        this.charCount.textContent = count;

        if (count > 4500) {
            this.charCount.style.color = '#f5576c';
        } else {
            this.charCount.style.color = 'var(--text-muted)';
        }
    }

    async loadModels() {
        try {
            const response = await fetch('/models');
            const data = await response.json();

            if (data.models && data.models.length > 0) {
                this.modelSelect.innerHTML = '';
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    this.modelSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();

            if (data.status === 'healthy') {
                this.updateStatus('connected', 'Connected');
            } else {
                this.updateStatus('disconnected', 'Disconnected');
            }
        } catch (error) {
            this.updateStatus('error', 'Error');
            console.error('Health check failed:', error);
        }
    }

    updateStatus(status, text) {
        const statusPulse = this.statusBadge.querySelector('.status-pulse');
        const statusText = this.statusBadge.querySelector('span:last-child');

        statusText.textContent = text;

        switch (status) {
            case 'connected':
                this.statusBadge.style.background = 'rgba(34, 197, 94, 0.1)';
                this.statusBadge.style.borderColor = 'rgba(34, 197, 94, 0.3)';
                this.statusBadge.style.color = '#4ade80';
                statusPulse.style.background = '#4ade80';
                break;
            case 'disconnected':
                this.statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
                this.statusBadge.style.borderColor = 'rgba(239, 68, 68, 0.3)';
                this.statusBadge.style.color = '#f87171';
                statusPulse.style.background = '#f87171';
                break;
            case 'error':
                this.statusBadge.style.background = 'rgba(251, 146, 60, 0.1)';
                this.statusBadge.style.borderColor = 'rgba(251, 146, 60, 0.3)';
                this.statusBadge.style.color = '#fb923c';
                statusPulse.style.background = '#fb923c';
                break;
        }
    }

    async handleSubmit(e) {
        e.preventDefault();

        const message = this.userInput.value.trim();
        if (!message) return;

        const model = this.modelSelect.value;
        const temperature = parseFloat(this.temperatureSlider.value);

        // Disable input
        this.setInputState(false);

        // Add user message
        this.addMessage('user', message);

        // Clear input
        this.userInput.value = '';
        this.autoResizeTextarea();
        this.updateCharCount();

        // Add typing indicator
        const typingId = this.addTypingIndicator();

        try {
            // Send request
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: model,
                    temperature: temperature,
                    stream: true
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Remove typing indicator
            this.removeTypingIndicator(typingId);

            // Handle streaming response
            await this.handleStreamingResponse(response);

        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator(typingId);
            this.addMessage('bot', '❌ Sorry, there was an error processing your request. Please make sure Ollama is running.');
        } finally {
            // Re-enable input
            this.setInputState(true);
            this.userInput.focus();
        }
    }

    async handleStreamingResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botMessageElement = null;
        let fullResponse = '';
        let isFirstChunk = true;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.content) {
                            fullResponse += data.content;

                            if (isFirstChunk) {
                                // First chunk: create message element but DON'T add to history yet
                                botMessageElement = this.addMessageWithoutHistory('bot', fullResponse);
                                isFirstChunk = false;
                            } else {
                                // Subsequent chunks: just update the displayed message
                                this.updateMessage(botMessageElement, fullResponse);
                            }
                        }

                        if (data.done) {
                            // Streaming complete: now add to history
                            if (fullResponse) {
                                this.chatHistory.push({
                                    role: 'bot',
                                    content: fullResponse,
                                    timestamp: this.getCurrentTime()
                                });
                                this.updateChatHistory();
                            }
                            break;
                        }

                        if (data.error) {
                            throw new Error(data.error);
                        }
                    } catch (error) {
                        console.error('Error parsing SSE:', error);
                    }
                }
            }
        }
    }

    addMessageWithoutHistory(role, content) {
        // Same as addMessage but without adding to history
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = role === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = content;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();

        bubbleDiv.appendChild(textDiv);
        bubbleDiv.appendChild(timeDiv);
        contentDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = role === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = content;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();

        bubbleDiv.appendChild(textDiv);
        bubbleDiv.appendChild(timeDiv);
        contentDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Add to chat history
        this.chatHistory.push({
            role: role,
            content: content,
            timestamp: this.getCurrentTime()
        });
        this.updateChatHistory();

        return messageDiv;
    }

    updateMessage(messageElement, content) {
        const textDiv = messageElement.querySelector('.message-text');
        if (textDiv) {
            textDiv.textContent = content;
            this.scrollToBottom();
        }
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'typing-indicator';
        indicatorDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

        bubbleDiv.appendChild(indicatorDiv);
        contentDiv.appendChild(bubbleDiv);
        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();

        return 'typing-indicator';
    }

    removeTypingIndicator(id) {
        const typingIndicator = document.getElementById(id);
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    clearChat() {
        const confirmClear = confirm('Are you sure you want to clear the conversation?');
        if (confirmClear) {
            // Remove all messages except welcome card
            const messages = this.chatMessages.querySelectorAll('.message');
            messages.forEach(message => message.remove());

            // Clear chat history
            this.chatHistory = [];
            this.updateChatHistory();

            // Scroll to top
            this.chatMessages.scrollTop = 0;
        }
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('open');
        document.body.classList.toggle('sidebar-open');
    }

    updateChatHistory() {
        // IMPORTANT: Use innerHTML (NOT textContent) to render HTML properly
        if (this.chatHistory.length === 0) {
            this.chatHistoryContainer.innerHTML = `
                <div class="chat-history-empty">
                    No messages yet.<br>Start a conversation!
                </div>
            `;
            return;
        }

        let historyHTML = '';
        
        this.chatHistory.forEach(message => {
            const role = message.role === 'user' ? 'user' : 'assistant';
            const roleLabel = message.role === 'user' ? '👤 You' : '🤖 Assistant';
            
            // Truncate long messages (escape HTML to prevent XSS)
            const preview = this.escapeHtml(message.content).length > 150 
                ? this.escapeHtml(message.content).substring(0, 150) + '...'
                : this.escapeHtml(message.content);

            historyHTML += `
                <div class="chat-history-item ${role}">
                    <div class="chat-history-role ${role}">
                        ${roleLabel}
                    </div>
                    <div class="chat-history-content">${preview}</div>
                </div>
            `;
        });

        // Use innerHTML to render the HTML properly
        this.chatHistoryContainer.innerHTML = historyHTML;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setInputState(enabled) {
        this.userInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        this.modelSelect.disabled = !enabled;
    }

    scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new LuxuryChatbot();
});
