import os
import re
import json
import logging
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient
from bson.objectid import ObjectId, InvalidId
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

# Flask secret key from environment only
secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("FLASK_SECRET_KEY environment variable not set. Refusing to start.")
app.secret_key = secret_key

CORS(app)
oauth = OAuth(app)

# Google Cloud setup
GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_REGION = os.environ.get('GCP_REGION', 'us-central1')

gemini_model = None
if GCP_PROJECT_ID:
    try:
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        gemini_model = GenerativeModel("gemini-1.5-flash-001")
        logging.info(f"Initialized Vertex AI for project {GCP_PROJECT_ID} in {GCP_REGION}")
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI: {e}", exc_info=True)
        gemini_model = None
else:
    logging.warning("GCP_PROJECT_ID not set. Gemini LLM disabled.")

# Speech-to-Text Config
SPEECH_AUDIO_ENCODING = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
SPEECH_SAMPLE_RATE_HERTZ = 48000
SPEECH_LANGUAGE_CODE = "en-US"
speech_client = speech.SpeechClient()

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI')
mongo_client = None
mongo_db = None
if MONGO_URI:
    try:
        mongo_client = MongoClient(MONGO_URI)
        mongo_db = mongo_client.get_database("voice_ai_debug_assistant")
        logging.info("Connected to MongoDB Atlas successfully.")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
else:
    logging.warning("MONGO_URI not set. MongoDB disabled.")

# GitLab API setup
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
        gitlab_client = None
else:
    logging.warning("GITLAB_PRIVATE_TOKEN not set. GitLab integration disabled.")

# OAuth Configs
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GITLAB_CLIENT_ID = os.environ.get('GITLAB_CLIENT_ID')
GITLAB_CLIENT_SECRET = os.environ.get('GITLAB_CLIENT_SECRET')

# Register Google OAuth client
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'}
)

# Register GitLab OAuth client
oauth.register(
    name='gitlab',
    client_id=GITLAB_CLIENT_ID,
    client_secret=GITLAB_CLIENT_SECRET,
    access_token_url='https://gitlab.com/oauth/token',
    authorize_url='https://gitlab.com/oauth/authorize',
    api_base_url='https://gitlab.com/api/v4/',
    client_kwargs={'scope': 'read_user'}
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

def save_message(message_data):
    if not mongo_client:
        logging.error("MongoDB not initialized. Cannot save message.")
        return None
    try:
        result = mongo_db.messages.insert_one(message_data)
        logging.info(f"Message saved: {message_data['sender']}: {message_data['text'][:50]}...")
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"Error saving message to MongoDB: {e}", exc_info=True)
        return None

def get_or_create_conversation(conversation_id_str=None):
    if not mongo_client:
        logging.error("MongoDB not initialized. Cannot get/create conversation.")
        return None
    if conversation_id_str:
        try:
            conversation = mongo_db.conversations.find_one({"_id": ObjectId(conversation_id_str)})
            if conversation:
                return conversation
        except Exception as e:
            logging.warning(f"Invalid conversation ID or error: {e}. Creating new one.")
    new_conversation = {
        "start_time": datetime.utcnow(),
        "title": "New Conversation"
    }
    result = mongo_db.conversations.insert_one(new_conversation)
    new_conversation['_id'] = result.inserted_id
    logging.info(f"New conversation created with ID: {result.inserted_id}")
    return new_conversation

def fetch_conversation_messages_from_db(conversation_id, limit=10):
    if not mongo_client:
        logging.error("MongoDB client not initialized. Cannot fetch messages.")
        return []
    try:
        messages = list(
            mongo_db.messages.find(
                {'conversation_id': ObjectId(conversation_id)}
            ).sort('timestamp', 1).limit(limit)
        )
        return [{"sender": msg['sender'], "text": msg['text']} for msg in messages]
    except Exception as e:
        logging.error(f"Error fetching messages from MongoDB: {e}", exc_info=True)
        return []

# ... (Other AI, GitLab, and app logic routes here) ...

@app.route('/feedback', methods=['POST'])
def save_feedback():
    if not mongo_client:
        return jsonify({"error": "MongoDB not connected."}), 500
    data = request.get_json()
    if not data:
        logging.error("No JSON body in feedback request.")
        return jsonify({"error": "No data provided"}), 400
    if 'message_id' not in data or 'feedback_type' not in data:
        logging.error(f"Missing required fields in feedback: {data}")
        return jsonify({"error": "Missing required fields"}), 400
    try:
        # Safely convert to ObjectId and handle invalid input
        try:
            message_object_id = ObjectId(data['message_id'])
        except (InvalidId, TypeError):
            logging.error(f"Invalid message_id for feedback: {data['message_id']}")
            return jsonify({"error": "Invalid message_id"}), 400
        feedback_data = {
            'message_id': message_object_id,
            'feedback_type': data['feedback_type'], # 'like' or 'dislike'
            'timestamp': datetime.utcnow(),
            'comment': data.get('comment')
        }
        mongo_db.feedback.insert_one(feedback_data)
        logging.info(f"Feedback received for message {data['message_id']}: {data['feedback_type']}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error saving feedback: {e}", exc_info=True)
        return jsonify({"error": "Failed to save feedback"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
