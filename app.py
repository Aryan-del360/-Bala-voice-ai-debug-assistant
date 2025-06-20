import streamlit as st
import os

# --- Securely load Gemini API Key ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please set it in Streamlit secrets.")
    st.stop()

import google.generativeai as genai

# --- Configure Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --- Streamlit Page Config ---
st.set_page_config(page_title="Gemini Canvas AI - Code & Chat", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(120deg, #EAF0FF 0%, #F7F8FA 100%);
            color: #222;
        }
        .glass-card {
            background: rgba(255,255,255,0.78);
            border-radius: 24px;
            box-shadow: 0 4px 32px 0 #6b7cff11;
            padding: 2.5em 2em 1.8em 2em;
            margin-bottom: 2.2em;
            margin-top: 1.5em;
            border: 1.5px solid #f5f7fa;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }
        .main-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -1.1px;
            color: #222C7B;
            text-align: left;
            margin-bottom: 0.09em;
        }
        .subtitle {
            font-size: 1.14rem;
            color: #5A5A89;
            text-align: left;
            margin-bottom: 2.1em;
        }
        .stTextArea textarea {
            min-height: 96px;
        }
        .mistake-title {
            color: #d7263d;
            font-weight: bold;
            font-size: 1.05em;
            margin-bottom: 0.1em;
        }
        .mistake-list ul {
            color: #d7263d;
            font-size: 1.01em;
        }
        .gchat-container {
            background: rgba(255,255,255,0.93);
            border-radius: 20px;
            box-shadow: 0 4px 32px 0 #6b7cff22;
            padding: 1.2em 1.2em 1em 1.2em;
            margin-top: 1.2em;
            margin-bottom: 1.2em;
            font-size: 1.08em;
            min-height: 380px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🪄 Gemini Canvas AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A Gemini-powered code & chat playground inspired by Google Canvas and Stitch.</div>', unsafe_allow_html=True)

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "code_area" not in st.session_state:
    st.session_state.code_area = ""

if "mistakes" not in st.session_state:
    st.session_state.mistakes = ""

# --- Layout: Two columns ---
col1, col2 = st.columns([1.25, 0.75], gap="large")

# ----------- MAIN AREA: Code & Mistakes -----------
with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📝 Your Code")
    code = st.text_area(
        "Paste your code here (any language):", 
        value=st.session_state.code_area,
        key="code_input",
        height=220,
        placeholder="Paste or write your code here for AI analysis..."
    )

    st.session_state.code_area = code

    # Button to Analyze Code
    if st.button("🔍 Analyze Code for Mistakes", use_container_width=True):
        if code.strip():
            with st.spinner("Gemini is analyzing your code..."):
                prompt = (
                    "Analyze the following code and list all mistakes, errors, or bad practices. "
                    "Explain each mistake clearly. Provide the list in markdown bullet points and make it concise for developers:\n\n"
                    f"{code}"
                )
                try:
                    response = model.generate_content(prompt)
                    mistakes_md = response.text
                    st.session_state.mistakes = mistakes_md
                except Exception as e:
                    st.session_state.mistakes = f"Error analyzing code: {e}"

    # Show code and mistakes
    if st.session_state.code_area.strip():
        lang = "python"  # Default; could improve by auto-detecting
        st.code(st.session_state.code_area, language=lang)

    if st.session_state.mistakes and st.session_state.code_area.strip():
        st.markdown('<div class="mistake-title">Mistakes & Suggestions:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mistake-list">{st.session_state.mistakes}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------- RIGHT: Chat Sidebar -----------
with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💬 Gemini Chat")
    chat_input = st.text_area(
        "Ask Gemini anything (code, dev, AI, etc.):", 
        key="chat_input", 
        height=90,
        placeholder="Type your question here..."
    )

    send_chat = st.button("👉 Send to Gemini", use_container_width=True)

    if send_chat and chat_input.strip():
        with st.spinner("Gemini is thinking..."):
            # Add user message to chat history
            st.session_state.chat_history.append(("user", chat_input))
            try:
                resp = model.generate_content(chat_input)
                reply = resp.text
            except Exception as e:
                reply = f"Error: {e}"
            # Add Gemini reply to chat history
            st.session_state.chat_history.append(("gemini", reply))

    # Render Chat History
    st.markdown('<div class="gchat-container">', unsafe_allow_html=True)
    for sender, msg in st.session_state.chat_history[-10:]:
        if sender == "user":
            st.markdown(f"<b style='color:#222C7B'>You:</b> {msg}", unsafe_allow_html=True)
        else:
            st.markdown(f"<b style='color:#6B7CFF'>Gemini:</b> {msg}", unsafe_allow_html=True)
        st.markdown("<hr style='margin:0.5em 0 0.5em 0; border:0.5px solid #EAF0FF;'>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown(
    """
    <div style="text-align:center; color:#5A5A89; font-size:0.99em; margin-top:1.1em;">
    Inspired by <b>Google Gemini Canvas</b> & <b>Stitch</b> | <a href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank" style="color:#6B7CFF;">GitHub Repo</a>
    </div>
    """,
    unsafe_allow_html=True
)
