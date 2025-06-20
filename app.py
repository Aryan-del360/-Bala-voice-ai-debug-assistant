import streamlit as st
import requests
import os

# --- Custom CSS for "Stitch by Google" look & feel ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(120deg, #EAF0FF 0%, #F7F8FA 100%);
        color: #222;
    }
    .stApp {
        background: linear-gradient(120deg, #EAF0FF 0%, #F7F8FA 100%);
    }
    .stButton>button {
        background: #6B7CFF;
        color: white;
        border: none;
        border-radius: 16px;
        font-weight: 600;
        font-size: 1.08em;
        padding: 0.6em 2.2em;
        box-shadow: 0 2px 12px #6b7cff22;
        transition: 0.2s all;
    }
    .stButton>button:hover {
        background: #222C7B;
        color: #fff;
        transform: translateY(-2px) scale(1.045);
    }
    .glass-card {
        background: rgba(255,255,255,0.78);
        border-radius: 24px;
        box-shadow: 0 4px 32px 0 #6b7cff11;
        padding: 2.5em 2em 1.8em 2em;
        margin-bottom: 2.2em;
        margin-top: 1.5em;
        border: 1.5px solid #f5f7fa;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -1.1px;
        color: #222C7B;
        text-align: center;
        margin-bottom: 0.09em;
    }
    .subtitle {
        font-size: 1.14rem;
        color: #5A5A89;
        text-align: center;
        margin-bottom: 2.1em;
    }
    .stTextInput>div>div>input, .stTextArea textarea, .stFileUploader>div>div>input {
        background: #f5f7fa;
        border-radius: 12px;
        border: 1.5px solid #dde2ef;
        color: #222;
        font-size: 1.02em;
        padding: 0.7em 1em;
    }
    .stTextArea textarea {
        min-height: 100px;
    }
    .stFileUploader label {
        font-size: 1.06em;
        color: #6B7CFF;
        font-weight: 600;
    }
    .stMarkdown {
        font-size: 1.03em;
    }
    .stAlert {
        border-radius: 12px;
    }
    .stSidebar {
        background: #f5f7fa;
    }
    .tab-head {
        background: #f5f7fa;
        border-radius: 1.5em 1.5em 0 0;
        padding: 1.2em 0 0.4em 0;
        margin-bottom: 2em;
        text-align: center;
    }
    .tab-icon {
        font-size: 1.6em;
        margin-right: 0.4em;
        color: #6B7CFF;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar for config ---
st.sidebar.header("⚙️ Configuration")
backend_url = st.sidebar.text_input(
    "Backend API URL",
    os.getenv("BACKEND_URL", ""),
    help="Your deployed Flask/FastAPI endpoint (for processing queries, audio, etc)."
)
api_key = st.sidebar.text_input("API Key (optional)", type="password", help="If your backend requires authentication.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "👾 <b>Tip:</b> You can leave Backend URL blank for demo mode (no processing).",
    unsafe_allow_html=True
)

# --- Main UI ---
st.markdown('<div class="main-title">🪡 Bala Voice AI Debug Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Minimal, playful, and smooth — inspired by <b>Stitch by Google</b>.</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(
        [
            "💬 Query",
            "🎙️ Audio Transcription",
            "📁 Code File Review"
        ]
    )

    # --- Tab 1: Query ---
    with tab1:
        st.markdown('<div class="tab-head"><span class="tab-icon">💬</span><b>Ask a Developer Question</b></div>', unsafe_allow_html=True)
        query = st.text_area("Question", placeholder="e.g. How do I resolve merge conflicts in Git?", help="Ask any Dev/DevOps/AI question.")
        if st.button("Send Query", key="query_btn"):
            if not backend_url:
                st.info("Demo mode: No backend URL set. This would contact your backend.")
            elif not query.strip():
                st.warning("Please enter your question.")
            else:
                headers = {}
                if api_key: headers["Authorization"] = f"Bearer {api_key}"
                try:
                    r = requests.post(
                        backend_url.rstrip("/") + "/transcribe-query",
                        data={"query_text": query.strip()},
                        headers=headers,
                        timeout=20
                    )
                    if r.ok:
                        st.success("Backend Response:")
                        st.write(r.json())
                    else:
                        st.error(f"Backend error: {r.text}")
                except Exception as ex:
                    st.error(f"Backend error: {ex}")

    # --- Tab 2: Audio Transcription ---
    with tab2:
        st.markdown('<div class="tab-head"><span class="tab-icon">🎙️</span><b>Audio File to Text</b></div>', unsafe_allow_html=True)
        audio_file = st.file_uploader(
            "Upload audio (wav, mp3, ogg):",
            type=["wav", "mp3", "ogg"],
            help="Recordings, notes, meetings — up to 200MB"
        )
        if st.button("Transcribe Audio", key="audio_btn"):
            if not backend_url:
                st.info("Demo mode: No backend URL set. This would contact your backend.")
            elif not audio_file:
                st.warning("Please upload an audio file.")
            else:
                headers = {}
                if api_key: headers["Authorization"] = f"Bearer {api_key}"
                files = {"audio": (audio_file.name, audio_file, audio_file.type)}
                try:
                    r = requests.post(
                        backend_url.rstrip("/") + "/transcribe-audio",
                        files=files,
                        headers=headers,
                        timeout=60
                    )
                    if r.ok:
                        st.success("Transcription Result:")
                        st.write(r.json())
                    else:
                        st.error(f"Backend error: {r.text}")
                except Exception as ex:
                    st.error(f"Backend error: {ex}")

    # --- Tab 3: Multi-extension Code File Review ---
    with tab3:
        st.markdown('<div class="tab-head"><span class="tab-icon">📁</span><b>Upload & Preview Code Files</b></div>', unsafe_allow_html=True)
        code_file = st.file_uploader(
            "Upload code file (.py, .js, .html, .css, .json, .cpp, .java, .ts, .c, .cs, .go, .rb, .php, .ipynb):",
            type=["py", "js", "html", "css", "json", "cpp", "java", "ts", "c", "cs", "go", "rb", "php", "ipynb"],
            help="Paste or drop your code file for preview."
        )
        if code_file:
            file_ext = code_file.name.split('.')[-1].lower()
            try:
                # For Jupyter Notebooks, pretty print as JSON
                if file_ext == "ipynb":
                    import json
                    content = code_file.read().decode("utf-8")
                    st.json(json.loads(content))
                else:
                    content = code_file.read().decode("utf-8")
                    st.code(content, language=file_ext)
                st.success(f"{code_file.name} uploaded and displayed.")
            except Exception as ex:
                st.error(f"Could not display file: {ex}")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown(
    """
    <div style="text-align:center; color:#5A5A89; font-size:0.99em; margin-top:1.1em;">
    Inspired by <b>Stitch by Google</b> &nbsp;|&nbsp; <a href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank" style="color:#6B7CFF;">GitHub Repo</a>
    </div>
    """,
    unsafe_allow_html=True
)
