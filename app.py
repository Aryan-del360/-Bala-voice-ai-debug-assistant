import streamlit as st
import os
from google.generativeai import GenerativeModel, configure as gemini_configure
from github import Github
import gitlab
import requests

# --- Load API keys/secrets securely ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
GITLAB_TOKEN = st.secrets.get("GITLAB_TOKEN", os.environ.get("GITLAB_TOKEN", ""))

if not GEMINI_API_KEY:
    st.error("Set your Gemini API key in Streamlit secrets.")
    st.stop()

gemini_configure(api_key=GEMINI_API_KEY)
gemini_model = GenerativeModel("gemini-pro")

# --- Custom CSS for modern look ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(120deg, #181e25 0%, #232b38 100%);
        color: #e7eaf2;
    }
    .glass {
        background: rgba(30,40,60,0.92);
        border-radius: 24px;
        box-shadow: 0 4px 24px #0f1a2d60;
        padding: 2em 2em 1.3em 2em;
        margin-bottom: 2.2em;
        margin-top: 1.5em;
        border: 1.5px solid #2c3850;
        max-width: 740px;
        margin-left: auto;
        margin-right: auto;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -1.1px;
        background: linear-gradient(90deg, #6b7cff, #b7c0ff 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: left;
        margin-bottom: 0.09em;
    }
    .subtitle {
        font-size: 1.16rem;
        color: #89a1f8;
        margin-bottom: 2.1em;
    }
    .stTextArea textarea {
        min-height: 110px;
        background: #21283a !important;
        color: #e7eaf2 !important;
        border-radius: 10px;
        border: 1.5px solid #303a5d;
    }
    .stFileUploader label {
        font-size: 1.13em;
        color: #6B7CFF;
        font-weight: 700;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6b7cff, #232b38 90%);
        color: #fff;
        border-radius: 13px;
        font-weight: 700;
        font-size: 1.13em;
        padding: 0.54em 2.4em;
        box-shadow: 0 2px 18px #6b7cff33;
        transition: 0.16s all;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ffb86b, #6b7cff 60%);
        color: #181e25;
        transform: scale(1.03);
    }
    .stCodeBlock, .stMarkdown {
        font-size: 1.07em;
        background: #222a36 !important;
        color: #e7eaf2 !important;
        border-radius: 8px;
    }
    .ai-mistake {
        margin: 1em 0 1em 0;
        padding: 1.1em 1.3em;
        background: #351e2e77;
        color: #ff6b80;
        border-left: 5px solid #ff6b80;
        border-radius: 13px;
        font-weight: 600;
    }
    .chat-bubble {
        margin: 1.1em 0 1.1em 0;
        padding: 1.1em 1.4em;
        background: #222a36;
        border-radius: 16px;
        font-size: 1.09em;
        border-bottom: 2.5px solid #6b7cff44;
        box-shadow: 0 3px 20px #6b7cff24;
    }
    .user-bubble { background: #2b3a5e; color: #b7c0ff; border-bottom-color: #b7c0ff44;}
    .ai-bubble { background: #1f254d; color: #fff;}
    .stSidebar { background: #1a1e30; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 Gemini Dev AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload, debug, connect to GitHub/GitLab, auto-fix CI/CD, review code – all powered by Gemini & modern dev tools.</div>', unsafe_allow_html=True)

# --- Sidebar: Connect external services ---
st.sidebar.header("🔗 Integrations")
st.sidebar.markdown("Connect your developer tools:")

github_connected = False
gitlab_connected = False

if GITHUB_TOKEN:
    try:
        gh = Github(GITHUB_TOKEN)
        user = gh.get_user()
        st.sidebar.success(f"GitHub: {user.login} connected!")
        github_connected = True
    except Exception:
        st.sidebar.error("Invalid GitHub token.")
else:
    st.sidebar.info("Set GITHUB_TOKEN in Streamlit secrets for GitHub features.")

if GITLAB_TOKEN:
    try:
        gl = gitlab.Gitlab('https://gitlab.com', private_token=GITLAB_TOKEN)
        gl.auth()
        st.sidebar.success("GitLab connected!")
        gitlab_connected = True
    except Exception:
        st.sidebar.error("Invalid GitLab token.")
else:
    st.sidebar.info("Set GITLAB_TOKEN in Streamlit secrets for GitLab features.")

st.sidebar.markdown("---")
st.sidebar.markdown("✨ <b>Pro tips</b>: You can also add Gmail integration for AI notifications (coming soon).", unsafe_allow_html=True)

# --- Session state for chat & files ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_code" not in st.session_state:
    st.session_state.last_code = ""

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = ""

# --- Main app: Two columns: Code+AI (left), Chat (right) ---
col1, col2 = st.columns([1.25, 0.7], gap="large")

### LEFT: Code upload, AI debug, auto-fix, CI/CD
with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🗂️ Upload & Debug Code")
    code_file = st.file_uploader(
        "Upload a code file (.py, .js, .html, .json, .yaml, .yml, .sh, .c, .cpp, .java, .ts, .rb, etc.):",
        type=["py", "js", "html", "json", "yaml", "yml", "sh", "c", "cpp", "java", "ts", "rb", "php", "cs", "go", "ipynb"]
    )
    code_text = ""
    if code_file:
        ext = code_file.name.split('.')[-1].lower()
        try:
            content = code_file.read().decode("utf-8")
            code_text = content
        except Exception:
            st.error("Could not read file as text.")
    else:
        code_text = st.text_area("Or paste your code here", height=170, placeholder="Paste or write code for debugging/review...")

    st.session_state.last_code = code_text

    # --- Debug & auto-fix code button ---
    debug_btn, fix_btn = st.columns(2)
    with debug_btn:
        analyze_code = st.button("🔍 Debug/Review Code")
    with fix_btn:
        fix_code = st.button("🪄 Auto-Correct Code")

    # --- CI/CD Review & Correction ---
    st.markdown("#### 🛠️ CI/CD Pipeline Review")
    ci_code = st.text_area("Paste your GitHub Actions, GitLab CI, or other pipeline YAML for analysis/correction", height=110, placeholder="Paste pipeline YAML here...")
    ci_analyze = st.button("🤖 Analyze & Fix CI/CD Pipeline")

    # --- Output for code analysis/fix ---
    if analyze_code and code_text.strip():
        with st.spinner("Gemini is analyzing your code..."):
            prompt = (
                "Analyze the following code for errors, vulnerabilites, and bad practices. "
                "List all mistakes with explanations and suggest corrections. "
                "Output markdown bullet points and short summaries:\n\n"
                f"{code_text}"
            )
            try:
                resp = gemini_model.generate_content(prompt)
                st.session_state.last_analysis = resp.text
            except Exception as e:
                st.session_state.last_analysis = f"Error: {e}"
    if fix_code and code_text.strip():
        with st.spinner("Gemini is auto-correcting your code..."):
            prompt = (
                "Fix all mistakes and bad practices in this code. "
                "Return ONLY the corrected code, no explanations:\n\n"
                f"{code_text}"
            )
            try:
                resp = gemini_model.generate_content(prompt)
                st.session_state.last_code = resp.text
                st.success("Corrected code below:")
            except Exception as e:
                st.session_state.last_code = f"Error: {e}"

    if ci_analyze and ci_code.strip():
        with st.spinner("Gemini is reviewing your CI/CD pipeline..."):
            prompt = (
                "Analyze this CI/CD pipeline configuration (YAML). "
                "List mistakes, anti-patterns, and offer corrections. "
                "If possible, return the corrected YAML with brief explanations:\n\n"
                f"{ci_code}"
            )
            try:
                resp = gemini_model.generate_content(prompt)
                st.markdown(f'<div class="ai-mistake">{resp.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="ai-mistake">Error: {e}</div>', unsafe_allow_html=True)

    if st.session_state.last_analysis:
        st.markdown(f'<div class="ai-mistake">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
    if st.session_state.last_code and not code_file:
        st.code(st.session_state.last_code, language="python")

    st.markdown('</div>', unsafe_allow_html=True)

### RIGHT: Gemini Chat
with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("💬 Gemini Chat & Copilot")
    chat_input = st.text_area("Ask Gemini anything (dev, code, CI/CD, GitHub, etc.):",
                              key="chat_input", height=90, placeholder="Type your question here...")
    send_chat = st.button("👉 Send to Gemini", use_container_width=True)
    if send_chat and chat_input.strip():
        st.session_state.chat_history.append(("user", chat_input))
        with st.spinner("Gemini is thinking..."):
            try:
                resp = gemini_model.generate_content(chat_input)
                reply = resp.text
            except Exception as e:
                reply = f"Error: {e}"
            st.session_state.chat_history.append(("gemini", reply))

    # Render chat history
    for sender, msg in st.session_state.chat_history[-10:]:
        if sender == "user":
            st.markdown(f'<div class="chat-bubble user-bubble"><b>You:</b> {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble ai-bubble"><b>Gemini:</b> {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown(
    """
    <div style="text-align:center; color:#b7c0ff; font-size:0.99em; margin-top:1.1em;">
    Inspired by <b>Gemini Canvas</b> & <b>Stitch</b> | <a href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank" style="color:#b7c0ff;">GitHub Repo</a>
    </div>
    """,
    unsafe_allow_html=True
)
