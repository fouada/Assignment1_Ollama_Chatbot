"""
🤖 Ollama Chatbot - Luxurious Local ChatGPT Interface
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Built with: Python 3.13 + Streamlit + Ollama API
Features: 100% Private | Cost-Free | No Internet Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import html
import logging
from datetime import datetime
from pathlib import Path

import ollama
import streamlit as st
import streamlit.components.v1 as components

# Import custom CSS styles from separate module
from streamlit_styles import get_custom_css

# ============================================
# LOGGING CONFIGURATION
# ============================================

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "streamlit_app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Log application startup
logger.info("=" * 50)
logger.info("🤖 Ollama Chatbot - Streamlit Interface Starting")
logger.info("=" * 50)

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Ollama Chat - Your Private AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "🤖 Ollama Chatbot - 100% Private, Cost-Free AI Chat"},
)

# ============================================
# CUSTOM CSS - LUXURIOUS PREMIUM DESIGN
# ============================================
# CSS is now imported from separate module for better maintainability
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================


def check_ollama_connection():
    """Check if Ollama server is running"""
    try:
        ollama.list()
        logger.info("✓ Ollama connection successful")
        return True
    except ConnectionError as e:
        logger.error(f"✗ Ollama connection failed - ConnectionError: {str(e)}")
        return False
    except TimeoutError as e:
        logger.error(f"✗ Ollama connection timeout: {str(e)}")
        return False
    except Exception as e:
        logger.error(
            f"✗ Ollama connection failed - Unexpected error: {str(e)}", exc_info=True
        )
        return False


def get_available_models():
    """Fetch available Ollama models"""
    try:
        logger.debug("Fetching available models from Ollama")
        models = ollama.list()
        # models is a ListResponse object with a .models attribute
        # Each model has a .model attribute (not .name)
        model_list = [model.model for model in models.models]
        logger.info(f"✓ Successfully retrieved {len(model_list)} models: {model_list}")
        return model_list
    except ConnectionError as e:
        error_msg = f"Cannot connect to Ollama server: {str(e)}"
        logger.error(f"✗ {error_msg}")
        st.error(f"❌ {error_msg}")
        return []
    except Exception as e:
        error_msg = f"Error fetching models: {str(e)}"
        logger.error(f"✗ {error_msg}", exc_info=True)
        st.error(f"❌ {error_msg}")
        return []


def generate_response(prompt, model, temperature=0.7):
    """Generate response using Ollama with streaming"""
    logger.info(
        f"🤖 Generating response - Model: {model}, Temperature: {temperature}, Prompt length: {len(prompt)}"
    )

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            options={"temperature": temperature},
        )

        token_count = 0
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                token_count += 1
                yield chunk["message"]["content"]

        logger.info(
            f"✓ Response generation completed - Tokens generated: {token_count}"
        )

    except ConnectionError as e:
        error_msg = f"Cannot connect to Ollama server: {str(e)}"
        logger.error(f"✗ {error_msg}")
        yield f"❌ Error: {error_msg}"
    except ValueError as e:
        error_msg = f"Invalid model or parameters: {str(e)}"
        logger.error(f"✗ {error_msg}")
        yield f"❌ Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error during response generation: {str(e)}"
        logger.error(f"✗ {error_msg}", exc_info=True)
        yield f"❌ Error: {error_msg}"


# ============================================
# SESSION STATE INITIALIZATION
# ============================================

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False


# ============================================
# CACHE-BASED PERSISTENCE FUNCTIONS
# ============================================


def load_messages_from_localstorage():
    """Load messages from local cache file and restore to session state"""
    if not st.session_state.history_loaded:
        import json
        from pathlib import Path

        cache_file = Path.home() / ".ollama_streamlit_cache.json"

        try:
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    st.session_state.messages = data.get("messages", [])
                    st.session_state.total_messages = data.get("totalMessages", 0)
                    logger.info(
                        f"💾 Loaded {len(st.session_state.messages)} messages from cache"
                    )
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            # Clear corrupted cache file
            try:
                cache_file.unlink(missing_ok=True)
            except Exception:
                pass

        st.session_state.history_loaded = True


def save_messages_to_localstorage():
    """Save messages to browser's localStorage using Streamlit components"""
    import json
    
    # Return early if no messages to save
    if not hasattr(st.session_state, 'messages') or not st.session_state.messages:
        return
    
    try:
        # Prepare data to save
        data = {
            "messages": st.session_state.messages,
            "totalMessages": getattr(st.session_state, 'total_messages', len(st.session_state.messages)),
            "timestamp": datetime.now().isoformat()
        }
        
        # Convert to JSON string and escape for JavaScript
        json_data = json.dumps(data).replace("'", "\\'")
        
        # Use components.html to execute JavaScript that saves to localStorage
        js_code = f"""
        <script>
        try {{
            localStorage.setItem('ollama_chat_history', '{json_data}');
            console.log('Saved chat history to localStorage');
        }} catch (e) {{
            console.error('Error saving to localStorage:', e);
        }}
        </script>
        """
        
        components.html(js_code, height=0)
        logger.debug("💾 Saved messages to localStorage via components.html")
        
    except Exception as e:
        logger.error(f"Error saving to localStorage: {e}")


def save_messages_to_cache():
    """Save messages to a local cache file with size limits"""
    import json
    from pathlib import Path

    cache_file = Path.home() / ".ollama_streamlit_cache.json"
    max_messages = 100  # Limit to last 100 messages

    try:
        # Trim messages if too many
        messages_to_save = st.session_state.messages[-max_messages:]
        
        data = {
            "messages": messages_to_save,
            "totalMessages": st.session_state.total_messages,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Write atomically by writing to temp file first
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        # Atomic rename
        temp_file.replace(cache_file)
        
        logger.info(f"💾 Saved {len(messages_to_save)} messages to cache")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")


def clear_cache():
    """Clear the local cache file"""
    from pathlib import Path

    cache_file = Path.home() / ".ollama_streamlit_cache.json"

    try:
        if cache_file.exists():
            cache_file.unlink()
            logger.info("🗑️ Cache file cleared")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")


# Load messages on first run
load_messages_from_localstorage()

# ============================================
# SIDEBAR - SETTINGS & CONTROLS
# ============================================
# pragma: no cover - UI rendering code difficult to unit test

with st.sidebar:  # pragma: no cover
    st.markdown("# ⚙️ Settings")
    st.markdown("---")

    # Connection Status
    st.markdown("### 🔌 Connection Status")
    ollama_connected = check_ollama_connection()

    if ollama_connected:
        st.markdown(
            '<span class="status-online"></span> **Ollama Connected**',
            unsafe_allow_html=True,
        )
        st.success("✅ Ready to chat!")
    else:
        st.error("❌ Ollama Not Running")
        st.markdown(
            """
        **Start Ollama:**
        ```bash
        brew services start ollama
        ```
        or
        ```bash
        ollama serve
        ```
        """
        )
        st.stop()

    st.markdown("---")

    # Model Selection
    st.markdown("### 🤖 AI Model")
    available_models = get_available_models()

    if not available_models:
        st.warning("⚠️ No models found!")
        st.code("ollama pull llama3.2", language="bash")
        st.stop()

    selected_model = st.selectbox(
        "Choose your AI model:",
        available_models,
        index=0,
        help="Select which AI model to use for conversations",
    )
    st.session_state.selected_model = selected_model

    # Model Info
    model_info = {
        "llama3.2": {
            "icon": "🦙",
            "desc": "General purpose, balanced",
            "params": "3.2B",
        },
        "mistral": {"icon": "⚡", "desc": "Powerful & fast", "params": "7B"},
        "codellama": {"icon": "💻", "desc": "Code specialist", "params": "7B"},
        "phi3": {"icon": "🧠", "desc": "Compact & efficient", "params": "3.8B"},
    }

    for key, info in model_info.items():
        if selected_model and key in selected_model.lower():
            st.info(f"{info['icon']} {info['desc']} ({info['params']})")
            break

    st.markdown("---")

    # Temperature Control
    st.markdown("### 🌡️ Creativity Level")
    temperature = st.slider(
        "Temperature:",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Lower = More focused and deterministic\nHigher = More creative and random",
    )

    temp_label = (
        "🎯 Focused"
        if temperature < 0.5
        else "⚖️ Balanced" if temperature < 1.0 else "🎨 Creative"
    )
    st.caption(temp_label)

    st.markdown("---")

    # Statistics
    st.markdown("### 📊 Session Stats")
    st.metric("Messages", st.session_state.total_messages)
    st.metric("Model", selected_model.split(":")[0] if selected_model else "N/A")

    # Storage info
    from pathlib import Path

    cache_file = Path.home() / ".ollama_streamlit_cache.json"
    if cache_file.exists():
        st.caption("💾 Conversation saved locally")
    else:
        st.caption("📝 Start chatting to save")

    st.markdown("---")

    # Chat History Panel
    st.markdown("### 💬 Conversation History")

    if len(st.session_state.messages) > 0:
        # Create scrollable container with all messages
        history_items = []

        for idx, message in enumerate(st.session_state.messages):
            role = message["role"]
            content = message["content"]

            # Truncate long messages for preview (show first 150 chars)
            preview = content[:150] + "..." if len(content) > 150 else content

            # Escape HTML to prevent tags from showing or breaking layout
            preview_escaped = html.escape(preview)

            # Create clickable history item with data-target attribute
            message_id = f"msg-{idx}"
            history_items.append(
                f'<div class="chat-history-item {role}" data-target="{message_id}" style="cursor: pointer;">'
                f'<div class="chat-history-role {role}">{"👤 You" if role == "user" else "🤖 Assistant"}</div>'
                f'<div class="chat-history-content">{preview_escaped}</div>'
                f"</div>"
            )

        # Build complete HTML (single line, no extra whitespace)
        history_html = (
            '<div class="chat-history-container">' + "".join(history_items) + "</div>"
        )

        # Use st.write with unsafe_allow_html instead of st.markdown
        st.write(history_html, unsafe_allow_html=True)

        # Add JavaScript for clickable history items (using components.html for proper execution)
        components.html(
            """
            <script>
            (function() {
                // Function to handle message clicks
                function handleMessageClick(event) {
                    const targetId = event.currentTarget.getAttribute('data-target');
                    if (!targetId) return;
                    
                    event.preventDefault();
                    
                    // Access parent document (Streamlit's main frame)
                    const parentDoc = window.parent.document;
                    
                    // Find the target element in parent document
                    const targetElement = parentDoc.getElementById(targetId);
                    if (targetElement) {
                        // Smooth scroll to element
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                        
                        // Find the chat message container to highlight
                        const chatMessage = targetElement.closest('[data-testid="stChatMessage"]');
                        if (chatMessage) {
                            // Add highlight class
                            chatMessage.classList.add('highlight');
                            
                            // Remove highlight after animation
                            setTimeout(function() {
                                chatMessage.classList.remove('highlight');
                            }, 2000);
                        }
                    }
                }
                
                // Function to attach event listeners
                function attachListeners() {
                    const parentDoc = window.parent.document;
                    const historyItems = parentDoc.querySelectorAll('.chat-history-item[data-target]');
                    
                    historyItems.forEach(function(item) {
                        // Remove old listener if exists
                        item.removeEventListener('click', handleMessageClick);
                        // Add new listener
                        item.addEventListener('click', handleMessageClick);
                    });
                }
                
                // Initial setup
                attachListeners();
                
                // Observe DOM changes in parent document
                const observer = new MutationObserver(function(mutations) {
                    attachListeners();
                });
                
                // Start observing the sidebar in parent document
                const parentDoc = window.parent.document;
                const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    observer.observe(sidebar, {
                        childList: true,
                        subtree: true
                    });
                }
            })();
            </script>
            """,
            height=0,
        )
    else:
        st.write(
            '<div class="chat-history-empty">No messages yet.<br>Start a conversation!</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Clear Chat Button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.total_messages = 0
        clear_cache()  # Clear saved cache
        st.rerun()

    st.markdown("---")

    # Privacy Features
    st.markdown("### 🔒 Privacy Features")
    st.markdown(
        """
    <div class="feature-badge">✅ 100% Local</div>
    <div class="feature-badge">✅ No API Keys</div>
    <div class="feature-badge">✅ Cost-Free</div>
    <div class="feature-badge">✅ Private Data</div>
    <div class="feature-badge">✅ Fast Response</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Built with Python + Streamlit + Ollama")
    st.caption(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================
# MAIN CHAT INTERFACE
# ============================================

# Title
st.markdown("# 💬 Ollama Chat")
st.markdown("### Your Personal AI Assistant - Private, Fast & Free")
st.markdown("---")

# Welcome Message (First Time)
if len(st.session_state.messages) == 0:
    st.markdown(
        """
    <div class="welcome-card">
        <h2>👋 Welcome to Your Private AI Chat!</h2>
        <p style="font-size: 1.1em; margin: 15px 0;">
            This chatbot runs entirely on your machine using Ollama.
            Experience the power of AI without compromising your privacy.
        </p>
        <h3>🌟 Key Features:</h3>
        <ul style="font-size: 1em; line-height: 1.8;">
            <li>🔒 <strong>Complete Privacy</strong> - All data stays on your machine</li>
            <li>💰 <strong>Zero Cost</strong> - No API fees or subscriptions</li>
            <li>⚡ <strong>Lightning Fast</strong> - Direct local processing</li>
            <li>🛡️ <strong>Secure</strong> - No internet connection required</li>
            <li>🎨 <strong>Multiple Models</strong> - Choose the best AI for your task</li>
        </ul>
        <p style="margin-top: 20px; font-size: 1.1em;">
            💡 <strong>Tip:</strong> Select a model from the sidebar and start chatting below!
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:  # pragma: no cover
    # Display Chat History
    for idx, message in enumerate(st.session_state.messages):
        # Add anchor ID for this message
        st.markdown(
            f'<span id="msg-{idx}" class="message-anchor"></span>',
            unsafe_allow_html=True,
        )

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input(
    "💭 Type your message here...", key="chat_input"
):  # pragma: no cover
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.total_messages += 1

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Stream response
        model_to_use = selected_model if selected_model else "llama3.2"
        for chunk in generate_response(prompt, model_to_use, temperature):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.total_messages += 1

    # Save to cache for persistence
    save_messages_to_cache()

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; padding: 20px;">
    <p style="color: #7dd3fc !important; margin: 10px 0;">
        🔒 Your conversations are completely private and saved locally on your machine
    </p>
    <p style="color: #7dd3fc !important; margin: 10px 0;">💡 Powered by Ollama | Built with ❤️ using Streamlit</p>
</div>
""",
    unsafe_allow_html=True,
)