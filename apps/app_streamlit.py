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
import logging
import os
from pathlib import Path

# ============================================
# LOGGING CONFIGURATION
# ============================================

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'streamlit_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log application startup
logger.info("="*50)
logger.info("🤖 Ollama Chatbot - Streamlit Interface Starting")
logger.info("="*50)

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
# CUSTOM CSS - LUXURIOUS PREMIUM DESIGN
# ============================================
st.markdown("""
<style>
    /* Import Premium Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

    /* Force Dark Theme at Root Level */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #0f0f1e !important;
        color: #e4e4e7 !important;
    }

    /* Main App Background with Animated Gradient */
    .main {
        background: #0f0f1e !important;
        font-family: 'Inter', sans-serif;
        color: #e4e4e7 !important;
    }

    /* Force Dark Background for Main Content Area */
    .block-container {
        background: transparent !important;
    }

    /* Ensure ALL text elements are readable - Universal text color fix */
    * {
        color: #e4e4e7;
    }

    .main p, .main span, .main div, .main li, .main a {
        color: #e4e4e7 !important;
    }

    /* Text elements */
    p, span, div, label, li, a, td, th {
        color: #e4e4e7 !important;
    }

    /* Animated Background Effect */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background:
            radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(240, 147, 251, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(79, 172, 254, 0.1) 0%, transparent 50%);
        z-index: 0;
        pointer-events: none;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.1); }
    }

    /* Sidebar - Premium Glass Effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(19, 19, 36, 0.98) 0%, rgba(13, 13, 26, 0.98) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stSidebar"] > div {
        padding: 2rem 1rem;
    }

    /* Sidebar text colors */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #e4e4e7 !important;
    }

    /* Headers with Gradient Text */
    h1 {
        font-family: 'Playfair Display', serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        text-shadow: none;
        margin-bottom: 0.5rem;
    }

    h2 {
        color: #f093fb;
        font-weight: 600;
        margin-top: 1rem;
    }

    h3 {
        color: #a8a8b3;
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Chat Messages - Luxurious Style */
    .stChatMessage {
        background: rgba(30, 30, 46, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        transition: all 0.3s ease;
    }

    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
        border-color: rgba(102, 126, 234, 0.4);
    }

    /* User Messages - Pink Gradient */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, rgba(240, 147, 251, 0.15) 0%, rgba(245, 87, 108, 0.15) 100%) !important;
        border: 1px solid rgba(240, 147, 251, 0.4) !important;
    }

    /* Assistant Messages - Purple Gradient */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
    }

    /* Message Content */
    [data-testid="stChatMessageContent"] {
        color: #f4f4f5 !important;
        line-height: 1.6;
        font-size: 1rem;
    }

    [data-testid="stChatMessageContent"] p {
        color: #f4f4f5 !important;
    }

    [data-testid="stChatMessageContent"] * {
        color: #f4f4f5 !important;
    }

    /* Chat Input Box - Premium Style */
    .stChatInput > div {
        background: rgba(26, 26, 36, 0.8);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }

    .stChatInput input {
        color: #ffffff !important;
        font-size: 1rem;
    }

    .stChatInput input::placeholder {
        color: #a1a1aa;
    }

    /* All Streamlit labels */
    label {
        color: #e4e4e7 !important;
    }

    /* Markdown text */
    .stMarkdown {
        color: #e4e4e7;
    }

    /* Text Input & TextArea */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(26, 26, 36, 0.8);
        color: #ffffff;
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 12px;
        font-family: 'Inter', sans-serif;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
    }

    /* Buttons - Premium Gradient */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.6);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Selectbox - Premium Style - Fixed for visibility */
    .stSelectbox > div > div {
        background: rgba(26, 26, 36, 0.95) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
    }

    .stSelectbox [data-baseweb="select"] {
        background: rgba(26, 26, 36, 0.95) !important;
        color: #ffffff !important;
    }

    /* Selectbox text color */
    .stSelectbox [data-baseweb="select"] > div {
        color: #ffffff !important;
        background: rgba(26, 26, 36, 0.95) !important;
    }

    /* Selected option text */
    .stSelectbox [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* Dropdown menu background */
    [data-baseweb="popover"] {
        background: rgba(26, 26, 36, 0.98) !important;
    }

    /* Dropdown menu items */
    [role="listbox"] {
        background: rgba(26, 26, 36, 0.98) !important;
    }

    [role="option"] {
        background: rgba(26, 26, 36, 0.95) !important;
        color: #ffffff !important;
    }

    [role="option"]:hover {
        background: rgba(102, 126, 234, 0.3) !important;
        color: #ffffff !important;
    }

    /* Selectbox input field */
    .stSelectbox input {
        color: #ffffff !important;
        background: rgba(26, 26, 36, 0.95) !important;
    }

    /* Slider - Premium Gradient */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    .stSlider [role="slider"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 2px 8px rgba(240, 147, 251, 0.4);
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(26, 26, 36, 0.5);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    [data-testid="stMetricValue"] {
        color: #667eea;
        font-size: 1.8rem;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: #a8a8b3;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.75rem;
    }

    /* Alert Boxes */
    .stAlert {
        border-radius: 12px;
        border: 1px solid;
        backdrop-filter: blur(10px);
    }

    .stSuccess {
        background: rgba(34, 197, 94, 0.1);
        border-color: rgba(34, 197, 94, 0.3);
        color: #4ade80;
    }

    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.3);
        color: #f87171;
    }

    .stWarning {
        background: rgba(251, 146, 60, 0.1);
        border-color: rgba(251, 146, 60, 0.3);
        color: #fb923c;
    }

    .stInfo {
        background: rgba(79, 172, 254, 0.1);
        border-color: rgba(79, 172, 254, 0.3);
        color: #4facfe;
    }

    /* Welcome Card - Ultra Premium */
    .welcome-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 20px;
        color: #f4f4f5;
        margin: 2rem 0;
        border: 1px solid rgba(102, 126, 234, 0.4);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }

    .welcome-card h2 {
        font-family: 'Playfair Display', serif;
        background: linear-gradient(135deg, #8b9fef 0%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    .welcome-card h3 {
        color: #d4d4d8 !important;
    }

    .welcome-card p {
        color: #e4e4e7 !important;
    }

    .welcome-card ul {
        list-style: none;
        padding-left: 0;
    }

    .welcome-card li {
        padding: 0.5rem 0;
        font-size: 1.05rem;
        color: #e4e4e7;
    }

    .welcome-card strong {
        color: #f4f4f5;
    }

    /* Feature Badge */
    .feature-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        border: 1px solid rgba(102, 126, 234, 0.5);
        font-size: 0.85rem;
        font-weight: 500;
        color: #e4e4e7;
        transition: all 0.3s ease;
    }

    .feature-badge:hover {
        background: rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* Status Indicator - Enhanced */
    .status-online {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #4ade80;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 12px #4ade80;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            box-shadow: 0 0 12px #4ade80;
        }
        50% {
            opacity: 0.6;
            box-shadow: 0 0 20px #4ade80;
        }
    }

    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.3) 50%, transparent 100%);
        margin: 1.5rem 0;
    }

    /* Caption Text */
    .caption {
        color: #a1a1aa;
        font-size: 0.85rem;
    }

    /* Streamlit caption elements */
    .stCaption {
        color: #a1a1aa !important;
    }

    /* Code Blocks */
    code {
        background: rgba(26, 26, 36, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        padding: 0.25rem 0.5rem;
        color: #f093fb;
        font-family: 'Monaco', 'Courier New', monospace;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(26, 26, 36, 0.5);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
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
        logger.info("✓ Ollama connection successful")
        return True
    except ConnectionError as e:
        logger.error(f"✗ Ollama connection failed - ConnectionError: {str(e)}")
        return False
    except TimeoutError as e:
        logger.error(f"✗ Ollama connection timeout: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"✗ Ollama connection failed - Unexpected error: {str(e)}", exc_info=True)
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
    logger.info(f"🤖 Generating response - Model: {model}, Temperature: {temperature}, Prompt length: {len(prompt)}")

    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
            options={'temperature': temperature}
        )

        token_count = 0
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                token_count += 1
                yield chunk['message']['content']

        logger.info(f"✓ Response generation completed - Tokens generated: {token_count}")

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

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = None

if 'total_messages' not in st.session_state:
    st.session_state.total_messages = 0

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
        'phi3': {'icon': '🧠', 'desc': 'Compact & efficient', 'params': '3.8B'}
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
else:  # pragma: no cover
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("💭 Type your message here...", key="chat_input"):  # pragma: no cover
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
<div style="text-align: center; padding: 20px;">
    <p style="color: #7dd3fc !important; margin: 10px 0;">🔒 Your conversations are completely private and stored only in your browser session</p>
    <p style="color: #7dd3fc !important; margin: 10px 0;">💡 Powered by Ollama | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
