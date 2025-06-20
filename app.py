# Final Flask backend code adjusted for Streamlit hosting
import os
import re
import json
import logging
import io
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Google Cloud Imports
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import aiplatform
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

# GitLab API
import gitlab
import gitlab.exceptions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "bala_secret_key")
CORS(app)
oauth = OAuth(app)

# Google Cloud
GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_REGION = os.environ.get('GCP_REGION', 'us-central1')

# Gemini Model Init
gemini_model = None
if GCP_PROJECT_ID:
    try:
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        gemini_model = GenerativeModel("gemini-1.5-flash-001")
        logging.info(f"Initialized Vertex AI for project {GCP_PROJECT_ID} in {GCP_REGION}")
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI: {e}", exc_info=True)
else:
    logging.warning("GCP_PROJECT_ID not set. Gemini LLM disabled.")

# Speech-to-Text
SPEECH_AUDIO_ENCODING = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
SPEECH_SAMPLE_RATE_HERTZ = 48000
SPEECH_LANGUAGE_CODE = "en-US"
speech_client = speech.SpeechClient()

# MongoDB Setup
MONGO_URI = os.environ.get('MONGO_URI')
mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None
mongo_db = mongo_client.get_database("voice_ai_debug_assistant") if mongo_client else None

# GitLab
GITLAB_URL = os.environ.get('GITLAB_URL', 'https://gitlab.com')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN')
gitlab_client = None
if GITLAB_PRIVATE_TOKEN:
    try:
        gitlab_client = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_PRIVATE_TOKEN)
        gitlab_client.auth()
        logging.info(f"Connected to GitLab at {GITLAB_URL}")
    except Exception as e:
        logging.error(f"Could not connect to GitLab: {e}", exc_info=True)

# OAuth Configs
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GITLAB_CLIENT_ID = os.environ.get('GITLAB_CLIENT_ID')
GITLAB_CLIENT_SECRET = os.environ.get('GITLAB_CLIENT_SECRET')

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={ 'scope': 'openid email profile' }
)

oauth.register(
    name='gitlab',
    client_id=GITLAB_CLIENT_ID,
    client_secret=GITLAB_CLIENT_SECRET,
    access_token_url='https://gitlab.com/oauth/token',
    authorize_url='https://gitlab.com/oauth/authorize',
    api_base_url='https://gitlab.com/api/v4/',
    client_kwargs={ 'scope': 'read_user' }
)

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def authorize_google():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    session['user'] = user_info
    return jsonify(user_info)

@app.route('/login/gitlab')
def login_gitlab():
    redirect_uri = url_for('authorize_gitlab', _external=True)
    return oauth.gitlab.authorize_redirect(redirect_uri)

@app.route('/authorize/gitlab')
def authorize_gitlab():
    token = oauth.gitlab.authorize_access_token()
    user_info = oauth.gitlab.get('user').json()
    session['user'] = user_info
    return jsonify(user_info)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login/google')
    return jsonify(session['user'])

# DO NOT include app.run() when deploying to Streamlit
# For local testing only:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
