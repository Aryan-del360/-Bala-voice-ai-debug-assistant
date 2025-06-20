import streamlit as st
import os

st.set_page_config(page_title="Bala Voice AI Debug Assistant", layout="wide")

st.title("Bala Voice AI Debug Assistant")
st.write("Ask development, DevOps, or GitLab related questions. This Streamlit app is a frontend. If you want backend features (AI, MongoDB, GitLab), ensure your API endpoints are available and set below.")

# --- Collect API URLs or Env Vars (Optional) ---
st.sidebar.header("Configuration")
backend_url = st.sidebar.text_input("Backend API URL (Flask/FastAPI)", os.getenv("BACKEND_URL", ""))
api_key = st.sidebar.text_input("API Key (Optional)", type="password")

# --- Main UX ---
query = st.text_area("Enter your question or request:", "")

upload_audio = st.file_uploader("Or upload audio for transcription (wav, mp3, ogg):", type=["wav", "mp3", "ogg"])

if st.button("Submit"):
    if backend_url:
        import requests

        # Send query (and optionally audio) to backend
        files = {}
        data = {}
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if query.strip():
            data["query_text"] = query.strip()
        if upload_audio:
            files["audio"] = upload_audio

        # Choose endpoint
        if upload_audio:
            endpoint = backend_url.rstrip("/") + "/transcribe-audio"
        else:
            endpoint = backend_url.rstrip("/") + "/transcribe-query"

        try:
            if files:
                response = requests.post(endpoint, data=data, files=files, headers=headers)
            else:
                response = requests.post(endpoint, data=data, headers=headers)
            if response.ok:
                st.success("Response from backend:")
                st.write(response.json())
            else:
                st.error(f"Backend error: {response.text}")
        except Exception as e:
            st.error(f"Error contacting backend: {e}")
    else:
        st.warning("No backend URL set. This is a demo UI only.")

st.markdown("""
---
**How Streamlit Deployment Works:**  
- This code gives you a frontend for queries and audio uploads.
- If you want full AI/GitLab/MongoDB features, run your Flask backend somewhere (e.g., Google Cloud Run, Render, Heroku) and set its URL in the sidebar.
- Streamlit Cloud can only run this frontend, not a backend API server.
""")
