"""
🤖 Ollama Chatbot - Luxurious Local ChatGPT Interface
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Built with: Python 3.13 + Streamlit + Ollama API
Features: 100% Private | Cost-Free | No Internet Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import ollama
from datetime import datetime
import json

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Ollama Chat - Your Private AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "🤖 Ollama Chatbot - 100% Private, Cost-Free AI Chat"
    }
)

# ============================================
# CUSTOM CSS - LUXURIOUS CHATGPT-LIKE DESIGN
# ============================================
st.markdown("""
<style>
    /* Main App Background */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
        border-right: 2px solid #533483;
    }

    /* Headers */
    h1 {
        color: #00d4ff;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }

    h2, h3 {
        color: #7dd3fc;
    }

    /* Chat Messages */
    .stChatMessage {
        background: rgba(30, 30, 50, 0.8);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(83, 52, 131, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* User message */
    [data-testid="stChatMessageContent"] {
        color: #e0e0e0;
    }

    /* Input Box */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(22, 33, 62, 0.9);
        color: #ffffff;
        border: 2px solid #533483;
        border-radius: 10px;
        padding: 12px;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    /* Info/Success/Warning Boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #00d4ff;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(22, 33, 62, 0.9);
        border: 2px solid #533483;
        border-radius: 10px;
    }

    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    /* Welcome Card */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* Feature Badge */
    .feature-badge {
        display: inline-block;
        background: rgba(0, 212, 255, 0.2);
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        border: 1px solid #00d4ff;
    }

    /* Status Indicator */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff00;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def check_ollama_connection():
    """Check if Ollama server is running"""
    try:
        ollama.list()
        return True
    except Exception:
        return False

def get_available_models():
    """Fetch available Ollama models"""
    try:
        models = ollama.list()
        return [model['name'] for model in models.get('models', [])]
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        return []

def generate_response(prompt, model, temperature=0.7):
    """Generate response using Ollama with streaming"""
    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
            options={'temperature': temperature}
        )

        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']

    except Exception as e:
        yield f"Error: {str(e)}"

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = None

if 'total_messages' not in st.session_state:
    st.session_state.total_messages = 0

# ============================================
# SIDEBAR - SETTINGS & CONTROLS
# ============================================

with st.sidebar:
    st.markdown("# ⚙️ Settings")
    st.markdown("---")

    # Connection Status
    st.markdown("### 🔌 Connection Status")
    ollama_connected = check_ollama_connection()

    if ollama_connected:
        st.markdown('<span class="status-online"></span> **Ollama Connected**', unsafe_allow_html=True)
        st.success("✅ Ready to chat!")
    else:
        st.error("❌ Ollama Not Running")
        st.markdown("""
        **Start Ollama:**
        ```bash
        brew services start ollama
        ```
        or
        ```bash
        ollama serve
        ```
        """)
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
        help="Select which AI model to use for conversations"
    )
    st.session_state.selected_model = selected_model

    # Model Info
    model_info = {
        'llama3.2': {'icon': '🦙', 'desc': 'General purpose, balanced', 'params': '3.2B'},
        'mistral': {'icon': '⚡', 'desc': 'Powerful & fast', 'params': '7B'},
        'codellama': {'icon': '💻', 'desc': 'Code specialist', 'params': '7B'},
        'phi': {'icon': '🧠', 'desc': 'Compact & efficient', 'params': '2.7B'}
    }

    for key, info in model_info.items():
        if key in selected_model.lower():
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
        help="Lower = More focused and deterministic\nHigher = More creative and random"
    )

    temp_label = "🎯 Focused" if temperature < 0.5 else "⚖️ Balanced" if temperature < 1.0 else "🎨 Creative"
    st.caption(temp_label)

    st.markdown("---")

    # Statistics
    st.markdown("### 📊 Session Stats")
    st.metric("Messages", st.session_state.total_messages)
    st.metric("Model", selected_model.split(':')[0])

    st.markdown("---")

    # Clear Chat Button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.total_messages = 0
        st.rerun()

    st.markdown("---")

    # Privacy Features
    st.markdown("### 🔒 Privacy Features")
    st.markdown("""
    <div class="feature-badge">✅ 100% Local</div>
    <div class="feature-badge">✅ No API Keys</div>
    <div class="feature-badge">✅ Cost-Free</div>
    <div class="feature-badge">✅ Private Data</div>
    <div class="feature-badge">✅ Fast Response</div>
    """, unsafe_allow_html=True)

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
    st.markdown("""
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
    """, unsafe_allow_html=True)
else:
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("💭 Type your message here...", key="chat_input"):
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
        for chunk in generate_response(prompt, selected_model, temperature):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.total_messages += 1

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7dd3fc; padding: 20px;">
    <p>🔒 Your conversations are completely private and stored only in your browser session</p>
    <p>💡 Powered by Ollama | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
