# backend/app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from google.cloud import speech
import logging # Import the logging module

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Set your Google Cloud Project ID (Optional if using gcloud auth application-default login locally)
# Uncomment and replace "your-gcp-project-id" if you want to explicitly set it here,
# otherwise, ensure your local gcloud CLI is authenticated to the correct project.
# os.environ["GOOGLE_CLOUD_PROJECT"] = "your-gcp-project-id"

# Important: Audio configuration for Speech-to-Text
# This should match what your frontend's MediaRecorder captures.
# audio/webm;codecs=opus typically results in OGG_OPUS encoding.
AUDIO_ENCODING = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
SAMPLE_RATE_HERTZ = 48000 # Common sample rate for webm/opus, adjust if your frontend captures differently
LANGUAGE_CODE = "en-US" # Or your desired language, e.g., "en-IN" for Indian English

app = Flask(__name__)
CORS(app) # Enable CORS for all routes - crucial for frontend running on different port

# Initialize Google Cloud Speech-to-Text client
client = speech.SpeechClient() # <--- THIS LINE WAS MISSING! Make sure it's included!

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    audio_file = request.files['audio']
    audio_content = audio_file.read() # Read the audio bytes

    logging.info("Received audio content. Size: %s bytes", len(audio_content))

    # --- Prepare audio for Speech-to-Text API ---
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=AUDIO_ENCODING,
        sample_rate_hertz=SAMPLE_RATE_HERTZ,
        language_code=LANGUAGE_CODE,
        # If you expect common phrases or domain-specific terms, you can add speech_contexts
        # speech_contexts=[{"phrases": ["pipeline status", "log errors", "Cloud Run", "GitLab CI"]}]
    )

    try:
        # Perform transcription
        # For short audio (< 1 minute), use recognize. For longer, use long_running_recognize.
        # For real-time streaming, use streaming_recognize (more complex for this step).
        response = client.recognize(config=config, audio=audio)
        logging.info("Speech-to-Text API call successful.")

        transcript = ""
        if response.results:
            # Get the first alternative of the first result
            transcript = response.results[0].alternatives[0].transcript
            logging.info(f"Transcript: {transcript}")
        else:
            logging.warning("No transcription results found.")
            transcript = "Could not transcribe audio."

        return jsonify({"transcript": transcript}), 200

    except Exception as e:
        logging.error(f"Error during transcription: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    # Simple health check endpoint for Cloud Run/monitoring
    return "VoiceAI Backend is running!", 200

if __name__ == '__main__':
    # When running locally, Flask defaults to 127.0.0.1:5000
    # In Cloud Run, it will listen on 0.0.0.0:8080 (or port defined by PORT env var)
    app.run(debug=True, host='0.0.0.0', port=5000)