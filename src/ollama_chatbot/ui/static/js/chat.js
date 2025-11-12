/**
 * ============================================
 * LUXURIOUS OLLAMA CHATBOT - CLIENT SCRIPT
 * ============================================
 */

class LuxuryChatbot {
    constructor() {
        this.chatHistory = []; // Store chat messages for sidebar
        this.messageCounter = 0; // Unique ID counter for messages
        this.storageKey = 'ollama_chat_history'; // localStorage key
        this.initElements();
        this.initEventListeners();
        this.loadModels();
        this.checkHealth();
        this.configureMarked();
        this.loadChatHistory(); // Load saved chat history
    }

    configureMarked() {
        // Configure marked.js for better rendering
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.error('Highlight error:', err);
                        }
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }
    }

    saveChatHistory() {
        // Save chat history to localStorage
        try {
            const historyData = {
                messages: this.chatHistory,
                messageCounter: this.messageCounter,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem(this.storageKey, JSON.stringify(historyData));
            console.log('💾 Chat history saved to localStorage');
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    loadChatHistory() {
        // Load chat history from localStorage
        try {
            const savedData = localStorage.getItem(this.storageKey);
            if (savedData) {
                const historyData = JSON.parse(savedData);
                this.chatHistory = historyData.messages || [];
                this.messageCounter = historyData.messageCounter || 0;
                
                // Restore messages to the UI
                this.chatHistory.forEach(message => {
                    this.restoreMessage(message);
                });
                
                this.updateChatHistory();
                console.log(`💾 Loaded ${this.chatHistory.length} messages from localStorage`);
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            // Clear corrupted data
            localStorage.removeItem(this.storageKey);
        }
    }

    restoreMessage(message) {
        // Restore a message to the UI (similar to addMessage but from saved data)
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}-message`;
        messageDiv.id = message.id;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = message.role === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        this.renderContent(textDiv, message.content);

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = message.timestamp;

        bubbleDiv.appendChild(textDiv);
        bubbleDiv.appendChild(timeDiv);
        contentDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
    }

    clearStoredHistory() {
        // Clear saved history from localStorage
        try {
            localStorage.removeItem(this.storageKey);
            console.log('🗑️ Chat history cleared from localStorage');
        } catch (error) {
            console.error('Error clearing chat history:', error);
        }
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
                            if (fullResponse && botMessageElement) {
                                this.chatHistory.push({
                                    id: botMessageElement.id,
                                    role: 'bot',
                                    content: fullResponse,
                                    timestamp: this.getCurrentTime()
                                });
                                this.updateChatHistory();
                                // Save to localStorage
                                this.saveChatHistory();
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
        const messageId = `message-${this.messageCounter++}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.id = messageId;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = role === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        this.renderContent(textDiv, content);

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

    renderContent(element, content) {
        // Render content as markdown with syntax highlighting
        if (typeof marked !== 'undefined') {
            element.innerHTML = marked.parse(content);
            // Apply syntax highlighting to code blocks
            if (typeof hljs !== 'undefined') {
                element.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        } else {
            element.textContent = content;
        }
    }

    addMessage(role, content) {
        const messageId = `message-${this.messageCounter++}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.id = messageId;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = role === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        this.renderContent(textDiv, content);

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
            id: messageId,
            role: role,
            content: content,
            timestamp: this.getCurrentTime()
        });
        this.updateChatHistory();
        
        // Save to localStorage
        this.saveChatHistory();

        return messageDiv;
    }

    updateMessage(messageElement, content) {
        const textDiv = messageElement.querySelector('.message-text');
        if (textDiv) {
            this.renderContent(textDiv, content);
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
        const confirmClear = confirm('Are you sure you want to clear the conversation? This will also delete saved history.');
        if (confirmClear) {
            // Remove all messages except welcome card
            const messages = this.chatMessages.querySelectorAll('.message');
            messages.forEach(message => message.remove());

            // Clear chat history
            this.chatHistory = [];
            this.messageCounter = 0;
            this.updateChatHistory();

            // Clear from localStorage
            this.clearStoredHistory();

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
        
        this.chatHistory.forEach((message, index) => {
            const role = message.role === 'user' ? 'user' : 'assistant';
            const roleLabel = message.role === 'user' ? '👤 You' : '🤖 Assistant';
            
            // Truncate long messages (escape HTML to prevent XSS)
            const preview = this.escapeHtml(message.content).length > 150 
                ? this.escapeHtml(message.content).substring(0, 150) + '...'
                : this.escapeHtml(message.content);

            historyHTML += `
                <div class="chat-history-item ${role}" data-message-id="${message.id}" data-index="${index}">
                    <div class="chat-history-role ${role}">
                        ${roleLabel}
                    </div>
                    <div class="chat-history-content">${preview}</div>
                </div>
            `;
        });

        // Use innerHTML to render the HTML properly
        this.chatHistoryContainer.innerHTML = historyHTML;

        // Add click event listeners to history items
        this.chatHistoryContainer.querySelectorAll('.chat-history-item').forEach(item => {
            item.addEventListener('click', () => {
                const messageId = item.getAttribute('data-message-id');
                this.scrollToMessage(messageId);
            });
        });
    }

    scrollToMessage(messageId) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            // Close sidebar
            if (this.sidebar.classList.contains('open')) {
                this.toggleSidebar();
            }

            // Scroll to message with smooth behavior
            messageElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });

            // Add highlight animation
            messageElement.classList.add('highlight');
            setTimeout(() => {
                messageElement.classList.remove('highlight');
            }, 2000);
        }
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
