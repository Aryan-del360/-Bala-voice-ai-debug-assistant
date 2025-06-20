import streamlit as st
import os

# --- Custom CSS for GenZ/Modern look ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css?family=JetBrains+Mono:400,700|Inter:400,700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', 'JetBrains Mono', monospace;
        background: linear-gradient(120deg, #141e30 0%, #243b55 100%);
        color: #f3f3f3;
    }
    .main-title {
        font-size: 2.7rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        letter-spacing: -1.5px;
        background: linear-gradient(90deg, #4b6cb7, #182848 70%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3em;
    }
    .subtitle {
        font-size: 1.25rem;
        color: #cfcfcf;
        margin-bottom: 2em;
    }
    .stTextInput>div>div>input, .stTextArea textarea, .stFileUploader>div>div>input {
        background: #222a36;
        color: #f3f3f3;
        border-radius: 9px;
        font-size: 1.05em;
        border: 1.5px solid #5c6bc0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7, #182848 70%);
        color: #fff;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1em;
        transition: 0.2s;
        box-shadow: 0 2px 9px 0 #1114;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #f7971e, #ffd200 90%);
        color: #1a1a1a;
        transform: scale(1.04);
    }
    .stSidebar {
        background: #1a2332;
    }
    .stFileUploader label {
        font-size: 1.07em;
        font-weight: 600;
        color: #ffd200;
    }
    .stMarkdown {
        font-size: 1.03em;
    }
    .hint {
        color: #ffd200;
        font-size: 0.96em;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .card {
        background: rgba(22, 31, 49, 0.93);
        border-radius: 1.2rem;
        box-shadow: 0 8px 38px 0 #0003;
        padding: 2.5em 2em;
        margin-bottom: 2.5em;
        margin-top: 1.2em;
    }
    .stAlert {
        border-radius: 0.7em;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="main-title">🚀 Bala Voice AI Debug Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A Gen Z-ready, developer-first productivity tool.<br>Transcribe, analyze, and review – all in one place.</div>', unsafe_allow_html=True)

# --- Sidebar config ---
st.sidebar.header("🛠️ Configuration")
backend_url = st.sidebar.text_input("API URL", os.getenv("BACKEND_URL", ""), help="Your backend endpoint (Flask/FastAPI)")
api_key = st.sidebar.text_input("API Key", type="password", help="Optional: Secret or token for backend auth")

st.sidebar.markdown("---")
st.sidebar.markdown("🌈 **Pro Tip:** Use the light/dark mode toggle in Streamlit menu!")

# --- Main Card Layout ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📝 Query", "🎵 Transcribe Audio", "🐍 Python Code Review"])

    # --- Tab 1: Query ---
    with tab1:
        st.markdown("**Ask anything related to Dev, DevOps, or GitLab:**")
        query = st.text_area("Type your question...", placeholder="e.g. How do I fix a merge conflict in GitLab CI?", help="Ask technical queries here.")
        st.markdown('<div class="hint">💡 You can also ask about code, deployment, or debugging!</div>', unsafe_allow_html=True)
        if st.button("Send Query", key="query_btn"):
            if not backend_url:
                st.warning("Set the API URL in the sidebar.")
            elif not query.strip():
                st.error("Please enter a question.")
            else:
                import requests
                data = {"query_text": query.strip()}
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                try:
                    endpoint = backend_url.rstrip("/") + "/transcribe-query"
                    resp = requests.post(endpoint, data=data, headers=headers)
                    if resp.ok:
                        st.success("✅ Response from backend:")
                        st.write(resp.json())
                    else:
                        st.error(f"Backend error: {resp.text}")
                except Exception as e:
                    st.error(f"Error contacting backend: {e}")

    # --- Tab 2: Audio ---
    with tab2:
        st.markdown("**Transcribe Audio File (wav/mp3/ogg):**")
        audio_file = st.file_uploader(
            "Drop your audio file here",
            type=["wav", "mp3", "ogg"],
            help="Upload a voice note or meeting recording."
        )
        st.markdown('<div class="hint">🔊 Supports up to 200MB per file.</div>', unsafe_allow_html=True)
        if st.button("Transcribe Audio", key="audio_btn"):
            if not backend_url:
                st.warning("Please set the API URL in the sidebar.")
            elif not audio_file:
                st.error("Please upload an audio file.")
            else:
                import requests
                files = {"audio": (audio_file.name, audio_file, audio_file.type)}
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                try:
                    endpoint = backend_url.rstrip("/") + "/transcribe-audio"
                    resp = requests.post(endpoint, files=files, headers=headers)
                    if resp.ok:
                        st.success("📝 Transcription:")
                        st.write(resp.json())
                    else:
                        st.error(f"Backend error: {resp.text}")
                except Exception as e:
                    st.error(f"Error contacting backend: {e}")

    # --- Tab 3: Python Code Review ---
    with tab3:
        st.markdown("**Upload a Python file for instant code review:**")
        py_file = st.file_uploader(
            "Drop your .py file here",
            type=["py"],
            help="Upload a Python script for review and display."
        )
        st.markdown('<div class="hint">🐍 Only .py files supported.</div>', unsafe_allow_html=True)
        if py_file:
            try:
                code_string = py_file.read().decode("utf-8")
                st.code(code_string, language="python")
                st.success("Python file uploaded and displayed! 🚀")
            except Exception as e:
                st.error(f"Could not read the Python file. Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
---
<div style="text-align:center; color:#bbb; font-size:0.92em;">
Made with ❤️ by <b>Bala Voice AI Debug Assistant</b> | <a style="color:#ffd200;" href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
