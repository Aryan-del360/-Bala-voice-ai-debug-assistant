import os
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import logging
import io # For handling audio byte streams if needed

# Google Cloud Imports
# Ensure you have the correct versions installed:
# google-cloud-speech for speech-to-text
# google-cloud-aiplatform and vertexai for Gemini
from google.cloud import speech_v1p1beta1 as speech 
speech.RecognitionConfig.AudioEncoding.LINEAR16
from google.cloud import aiplatform
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

# GitLab Import
import gitlab
import gitlab.exceptions

# --- Configuration & Initialization ---
# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app) # Enable CORS for all routes - crucial for frontend running on different port

# Google Cloud Project & Region (from environment variables)
GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_REGION = os.environ.get('GCP_REGION', 'us-central1') # Default region

# Initialize Vertex AI / Gemini LLM
gemini_model = None
if GCP_PROJECT_ID:
    try:
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        # Using gemini-1.5-flash-001 for speed and cost-efficiency
        gemini_model = GenerativeModel("gemini-1.5-flash-001")
        logging.info(f"Initialized Vertex AI for project {GCP_PROJECT_ID} in {GCP_REGION}")
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI: {e}", exc_info=True)
        gemini_model = None
else:
    logging.warning("GCP_PROJECT_ID environment variable not set. Gemini LLM will not be available.")

# Google Cloud Speech-to-Text Client
SPEECH_AUDIO_ENCODING = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
SPEECH_SAMPLE_RATE_HERTZ = 48000
SPEECH_LANGUAGE_CODE = "en-US"
speech_client = speech.SpeechClient()


# MongoDB Client
MONGO_URI = os.environ.get('MONGO_URI')
mongo_client = None
if MONGO_URI:
    try:
        mongo_client = MongoClient(MONGO_URI)
        # Define your database name here, e.g., 'voice_ai_debug_assistant'
        mongo_db = mongo_client.get_database("voice_ai_debug_assistant")
        logging.info("Connected to MongoDB Atlas successfully.")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB Atlas: {e}", exc_info=True)
else:
    logging.warning("MONGO_URI environment variable not set. MongoDB integration will be disabled.")


# GitLab Client
GITLAB_URL = os.environ.get('GITLAB_URL', 'https://gitlab.com')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN')
gitlab_client = None
if GITLAB_PRIVATE_TOKEN:
    try:
        gitlab_client = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_PRIVATE_TOKEN)
        gitlab_client.auth() # Test authentication
        logging.info(f"Connected to GitLab at {GITLAB_URL}")
    except Exception as e:
        logging.error(f"Could not connect to GitLab: {e}", exc_info=True)
        gitlab_client = None
else:
    logging.warning("GITLAB_PRIVATE_TOKEN not set. GitLab integration will be disabled.")


# --- MongoDB Helper Functions ---
def save_message(message_data):
    if not mongo_client:
        logging.error("MongoDB client not initialized. Cannot save message.")
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
        logging.error("MongoDB client not initialized. Cannot get/create conversation.")
        return None

    if conversation_id_str:
        try:
            conversation = mongo_db.conversations.find_one({"_id": ObjectId(conversation_id_str)})
            if conversation:
                return conversation
        except Exception as e:
            logging.warning(f"Invalid conversation ID '{conversation_id_str}' or error finding conversation: {e}. Creating new one.")

    new_conversation = {
        "start_time": datetime.utcnow(),
        "title": "New Conversation" # Will be updated by AI or first query
    }
    result = mongo_db.conversations.insert_one(new_conversation)
    logging.info(f"New conversation created with ID: {result.inserted_id}")
    return new_conversation

def fetch_conversation_messages_from_db(conversation_id, limit=10):
    if not mongo_client:
        logging.error("MongoDB client not initialized. Cannot fetch messages.")
        return []
    try:
        # Fetch the last 'limit' messages for context
        messages = mongo_db.messages.find(
            {'conversation_id': ObjectId(conversation_id)}
        ).sort('timestamp', 1).limit(limit).to_list(length=limit)
        
        return [{"sender": msg['sender'], "text": msg['text']} for msg in messages]
    except Exception as e:
        logging.error(f"Error fetching messages from MongoDB: {e}", exc_info=True)
        return []

# --- Gemini LLM Helper Function ---
def get_gemini_response(prompt_text, conversation_history_for_llm=None, system_instruction=""):
    if not gemini_model:
        return "AI model not initialized. Please check backend configuration and logs."

    contents = []
    if conversation_history_for_llm:
        for msg in conversation_history_for_llm:
            contents.append(Part.from_text(f"{msg['sender']}: {msg['text']}"))
    
    # Add the current user prompt
    contents.append(Part.from_text(f"user: {prompt_text}"))

    # Default system instruction if not provided
    if not system_instruction:
        system_instruction = (
            "You are VoiceAI Debug Assistant, an expert in GitLab DevSecOps and Google Cloud. "
            "Your goal is to help developers 'build software faster' by providing immediate insights, "
            "root cause analysis, and actionable suggestions from GitLab data and general development knowledge. "
            "When providing code or YAML examples, always wrap them in markdown code blocks (```). "
            "When asked about GitLab, provide relevant project IDs or other necessary parameters. "
            "Prioritize helpfulness, accuracy, and brevity. "
            "Always align your responses with the theme of 'building software faster'. "
            "You have access to real-time GitLab data that will be provided by functions, so analyze it effectively. "
            "If asked to summarize logs, identify key errors and suggest solutions. "
            "For complex queries, briefly explain your reasoning (Thought Process) after your main answer."
        )

    try:
        response = gemini_model.generate_content(
            contents,
            generation_config={"temperature": 0.2, "max_output_tokens": 1024},
            system_instruction=system_instruction
        )
        return response.text
    except Exception as e:
        logging.error(f"Error generating Gemini response: {e}", exc_info=True)
        return f"An AI error occurred: {str(e)}"


# --- GitLab API Helper Functions (Internal, called by query processing) ---
def _fetch_gitlab_projects_internal():
    if not gitlab_client:
        return {"error": "GitLab integration not enabled."}
    try:
        # Fetch projects the private token has access to and is at least a reporter
        projects = gitlab_client.projects.list(owned=True, all=True, min_access_level=gitlab.const.AccessLevel.REPORTER)
        project_list = [{
            'id': p.id,
            'name': p.name_with_namespace,
            'web_url': p.web_url,
            'default_branch': p.default_branch,
            'last_activity_at': p.last_activity_at
        } for p in projects]
        return {"data": project_list}
    except gitlab.exceptions.GitlabError as e:
        logging.error(f"GitLab API error fetching projects: {e}", exc_info=True)
        return {"error": f"GitLab API error: {e.error_message}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}

def _fetch_gitlab_pipeline_status_internal(project_id):
    if not gitlab_client:
        return {"error": "GitLab integration not enabled."}
    try:
        project = gitlab_client.projects.get(project_id)
        # Fetch the latest pipeline for the default branch
        pipelines = project.pipelines.list(ref=project.default_branch, order_by='id', sort='desc', per_page=1)
        
        if not pipelines:
            return {"data": {"status": "No pipelines found for default branch", "project_name": project.name_with_namespace}}
        
        latest_pipeline = pipelines[0]
        pipeline_info = {
            'id': latest_pipeline.id,
            'status': latest_pipeline.status,
            'web_url': latest_pipeline.web_url,
            'ref': latest_pipeline.ref,
            'sha': latest_pipeline.sha,
            'created_at': latest_pipeline.created_at,
            'updated_at': latest_pipeline.updated_at,
            'detailed_status': latest_pipeline.detailed_status
        }
        return {"data": pipeline_info}
    except gitlab.exceptions.GitlabError as e:
        logging.error(f"GitLab API error fetching pipeline status for project {project_id}: {e}", exc_info=True)
        return {"error": f"GitLab API error: {e.error_message}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}

def _fetch_gitlab_job_logs_internal(project_id, job_id):
    if not gitlab_client:
        return {"error": "GitLab integration not enabled."}
    try:
        project = gitlab_client.projects.get(project_id)
        job = project.jobs.get(job_id)
        logs = job.trace().decode('utf-8')
        return {"data": {"logs": logs, "job_name": job.name, "job_id": job.id}}
    except gitlab.exceptions.GitlabError as e:
        logging.error(f"GitLab API error fetching job logs for project {project_id}, job {job_id}: {e}", exc_info=True)
        return {"error": f"GitLab API error: {e.error_message}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}

def _fetch_gitlab_issue_details_internal(project_id, issue_iid):
    """Fetches details of a specific GitLab issue."""
    if not gitlab_client:
        return {"error": "GitLab integration not enabled."}
    try:
        project = gitlab_client.projects.get(project_id)
        issue = project.issues.get(issue_iid)
        notes = issue.notes.list(all=True) # Fetch all comments/notes

        issue_data = {
            "title": issue.title,
            "description": issue.description,
            "state": issue.state,
            "labels": issue.labels,
            "assignees": [a['name'] for a in issue.assignees] if hasattr(issue, 'assignees') and issue.assignees else [],
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "web_url": issue.web_url,
            "comments": [{"author": n.author['name'], "body": n.body, "created_at": n.created_at} for n in notes]
        }
        return {"data": issue_data}
    except gitlab.exceptions.GitlabError as e:
        logging.error(f"Error fetching GitLab issue {issue_iid} from project {project_id}: {e}", exc_info=True)
        return {"error": f"GitLab API error: {e.error_message}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching issue {issue_iid}: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}

def _fetch_last_n_job_logs_for_analysis_internal(project_id, num_logs=1):
    """Fetches details and logs of the last N jobs for AI analysis."""
    if not gitlab_client:
        return {"error": "GitLab integration not enabled."}
    try:
        project = gitlab_client.projects.get(project_id)
        jobs = project.jobs.list(order_by='id', sort='desc', per_page=num_logs * 2) # Fetch more to ensure we get 'n' valid jobs
        
        recent_job_logs = []
        for job in jobs:
            if job.status in ['failed', 'success', 'running']: # Filter to relevant statuses
                try:
                    logs = job.trace().decode('utf-8')
                    recent_job_logs.append({
                        "job_id": job.id,
                        "job_name": job.name,
                        "status": job.status,
                        "logs": logs[:5000] # Truncate logs for LLM input, max 5000 chars
                    })
                    if len(recent_job_logs) >= num_logs:
                        break # Stop once we have enough valid logs
                except Exception as e:
                    logging.warning(f"Could not retrieve logs for job {job.id}: {e}")
        
        return {"data": recent_job_logs}
    except gitlab.exceptions.GitlabError as e:
        logging.error(f"GitLab API error fetching recent job logs for project {project_id}: {e}", exc_info=True)
        return {"error": f"GitLab API error: {e.error_message}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching recent logs: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}


# --- AI-Specific Helper Functions (for advanced features) ---

def triage_issue_with_gemini(issue_data):
    """Uses Gemini to triage and summarize a GitLab issue."""
    issue_text = f"Title: {issue_data['title']}\n"
    issue_text += f"Description: {issue_data['description'] or 'No description provided.'}\n"
    issue_text += f"Current State: {issue_data['state']}\n"
    issue_text += f"Labels: {', '.join(issue_data['labels']) if issue_data['labels'] else 'None'}\n"
    issue_text += f"Assignees: {', '.join(issue_data['assignees']) if issue_data['assignees'] else 'Unassigned'}\n"
    issue_text += f"Web URL: {issue_data['web_url']}\n"
    issue_text += "\nComments:\n"
    if issue_data['comments']:
        for comment in issue_data['comments']:
            issue_text += f"- {comment['author']} ({comment['created_at'].split('T')[0]}): {comment['body']}\n" # Just date
    else:
        issue_text += "No comments.\n"

    # Prompt for issue triage and summarization
    prompt = f"""
    You are an AI assistant specialized in triaging and summarizing GitLab issues.
    Analyze the following GitLab issue details and provide:
    1. A concise summary of the issue.
    2. Suggested labels (e.g., bug, feature, documentation, priority::high, severity::critical).
    3. Suggested next steps or actions to resolve it faster.
    4. An explanation of your reasoning (Thought Process).

    Issue details:
    {issue_text}

    Provide your response in a clear, structured markdown format.
    """
    return get_gemini_response(prompt, system_instruction="AI for GitLab Issue Triage")

def get_code_suggestion_with_gemini(prompt_text, context_code=""):
    """Uses Gemini to generate code or configuration suggestions."""
    full_prompt = f"""
    You are an expert software engineer and DevOps specialist.
    Based on the following request and optional code/log context, provide a relevant code snippet or configuration (e.g., .gitlab-ci.yml, Python, JavaScript).
    Always wrap your code in markdown code blocks (```).
    If you are generating a CI/CD configuration, assume it's for GitLab CI/CD.
    Explain your reasoning (Thought Process) briefly after the suggestion.

    Request: {prompt_text}
    """
    if context_code:
        full_prompt += f"\n\nAdditional Context (e.g., logs, existing code):```\n{context_code}\n```"

    prompt_for_code = f"""
    {full_prompt}

    Example:
    Request: "Fix the syntax error in this Python list comprehension: [x for x in range(10) if x % 2 = 0]"
    Suggestion:
    ```python
    [x for x in range(10) if x % 2 == 0]
    ```
    Thought Process: The original code used a single equals sign (`=`) for comparison, which is an assignment operator. Python uses `==` for equality comparison.

    Example 2:
    Request: "How do I add a deploy stage to my GitLab CI for a simple static site?"
    Suggestion:
    ```yaml
    deploy_staging:
      stage: deploy
      script:
        - echo "Deploying to staging..."
        - rsync -av --delete public/ user@your-staging-server:/var/www/your-app/staging/
      environment:
        name: staging
        url: [https://your-staging-url.com](https://your-staging-url.com)
      only:
        - main
    ```
    Thought Process: This stage defines a 'deploy' stage, uses `rsync` for deployment (a common method for static sites), and sets up a 'staging' environment with a specific URL. It runs only on the 'main' branch.

    Your Turn:
    """
    return get_gemini_response(prompt_for_code, system_instruction="AI for Code/Config Generation")

def analyze_logs_with_gemini(log_data_list):
    """Uses Gemini to analyze a list of job logs for anomalies and root causes."""
    if not log_data_list:
        return "No logs provided for analysis."

    logs_context = ""
    for i, log_data in enumerate(log_data_list):
        logs_context += f"\n--- Job {i+1} (ID: {log_data['job_id']}, Name: {log_data['job_name']}, Status: {log_data['status']}) ---\n"
        logs_context += f"{log_data['logs']}\n"
    
    prompt = f"""
    You are an AI assistant specialized in CI/CD log analysis and debugging.
    Analyze the following GitLab CI/CD job logs.
    Identify any errors, warnings, or anomalies.
    Provide a concise summary of the findings, the likely root cause of any failures, and concrete steps to fix them to 'build software faster'.
    If the logs indicate success, suggest areas for optimization or best practices.
    Always explain your reasoning (Thought Process).

    Logs to analyze:
    ```
    {logs_context}
    ```

    Provide your response in a clear, structured markdown format.
    """
    return get_gemini_response(prompt, system_instruction="AI for CI/CD Log Analysis")

def optimize_pipeline_with_gemini(pipeline_yaml_content):
    """Uses Gemini to suggest optimizations for GitLab CI/CD pipeline YAML."""
    if not pipeline_yaml_content:
        return "Please provide the GitLab CI/CD YAML content to optimize."

    prompt = f"""
    You are an expert in GitLab CI/CD pipeline optimization.
    Analyze the following `.gitlab-ci.yml` content and suggest improvements for:
    - **Speed:** How to make the pipeline run faster (e.g., caching, parallel jobs, optimizing stages).
    - **Cost Efficiency:** How to reduce resource usage (e.g., using smaller runners, optimizing image pull).
    - **Best Practices:** Adherence to GitLab CI/CD best practices, common pitfalls.
    - **Security:** Identify potential security improvements.
    
    Provide specific code (YAML) examples for any suggestions, wrapped in markdown code blocks.
    Always explain your reasoning (Thought Process) for each suggestion.

    GitLab CI/CD YAML to optimize:
    ```yaml
    {pipeline_yaml_content}
    ```

    Provide your response in a clear, structured markdown format.
    """
    return get_gemini_response(prompt, system_instruction="AI for CI/CD Pipeline Optimization")

def refactor_code_with_gemini(code_snippet, language="python"):
    """Uses Gemini to suggest refactoring or best practices for a code snippet."""
    if not code_snippet:
        return "Please provide the code snippet you want to refactor or get suggestions for."

    prompt = f"""
    You are an expert software engineer.
    Analyze the following code snippet in {language} and suggest improvements based on:
    - **Code quality:** Readability, maintainability, clarity.
    - **Best practices:** Adherence to common conventions for {language}.
    - **Potential bugs or edge cases.**
    - **Performance optimizations** (if applicable).
    - **Security vulnerabilities** (if applicable).

    Provide the refactored code (if any) wrapped in markdown code blocks.
    Always explain your reasoning (Thought Process) for each suggestion.

    Code to analyze:
    ```{language}
    {code_snippet}
    ```

    Provide your response in a clear, structured markdown format.
    """
    return get_gemini_response(prompt, system_instruction="AI for Code Refactoring and Best Practices")


# --- Flask Routes ---

@app.route('/health-check')
def health_check():
    """Simple health check endpoint for Cloud Run/monitoring."""
    return "VoiceAI Backend is running!", 200

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    """Transcribes audio to text using Google Cloud Speech-to-Text."""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    audio_file = request.files['audio']
    audio_content = audio_file.read()

    logging.info("Received audio content. Size: %s bytes", len(audio_content))

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=SPEECH_AUDIO_ENCODING,
        sample_rate_hertz=SPEECH_SAMPLE_RATE_HERTZ,
        language_code=SPEECH_LANGUAGE_CODE,
    )

    try:
        response = speech_client.recognize(config=config, audio=audio)
        logging.info("Speech-to-Text API call successful.")

        transcript = ""
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            logging.info(f"Transcript: {transcript}")
        else:
            logging.warning("No transcription results found.")
            transcript = "Could not transcribe audio."

        # This endpoint now *only* transcribes. The main AI processing happens in /transcribe-query
        return jsonify({"transcript": transcript}), 200

    except Exception as e:
        logging.error(f"Error during transcription: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe-query', methods=['POST'])
def transcribe_query():
    """
    Main endpoint for processing user queries (text or transcribed audio).
    Orchestrates AI interaction, GitLab API calls, and MongoDB operations.
    """
    data = request.form # Use request.form for multipart/form-data
    query = data.get('query_text', '').strip() # Assuming text comes from 'query_text' field
    conversation_id_str = data.get('conversationId')
    context_code = data.get('context_code', '').strip() # For code/YAML/logs input

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    logging.info(f"Received query: '{query}' for conversation ID: {conversation_id_str}")
    if context_code:
        logging.info(f"Received context code (first 100 chars): {context_code[:100]}...")

    # Get or create conversation for history tracking
    conversation = get_or_create_conversation(conversation_id_str)
    if not conversation:
        return jsonify({"error": "Failed to get or create conversation."}), 500
    conversation_id = conversation['_id']

    # Save user message
    user_message_data = {
        'text': query,
        'sender': 'user',
        'timestamp': datetime.utcnow(),
        'conversation_id': conversation_id,
        'original_transcription': query # For text queries, original and processed are same
    }
    user_message_id = save_message(user_message_data)
    if not user_message_id:
        logging.warning("Failed to save user message to DB, proceeding without history.")

    # Prepare conversation history for LLM context (excluding current query for now, it's the prompt)
    conversation_history_for_llm = []
    if mongo_client: # Only fetch if MongoDB is initialized
        # Fetch up to last 10 messages for context, excluding the current user message if it just saved
        conversation_history_for_llm = fetch_conversation_messages_from_db(conversation_id, limit=10) 
        # Optionally remove the last message if it's the current user query to avoid duplication in LLM prompt
        # if conversation_history_for_llm and conversation_history_for_llm[-1]['text'] == query:
        #     conversation_history_for_llm.pop()

    ai_response_text = "Processing your request with AI..."
    thought_process_explained = ""
    
    # --- Intelligent Orchestration (GitLab API calls + LLM) ---
    lower_query = query.lower()
    
    try:
        # Ordered from most specific to least specific GitLab/Tooling queries
        
        # 1. Handle GitLab Issue Triage/Summarization
        issue_match = re.search(r'(triage|summarize|analyze) issue #(\d+)( for project (\d+))?', lower_query)
        if issue_match and gitlab_client:
            action = issue_match.group(1)
            issue_iid = int(issue_match.group(2))
            project_id_from_query = issue_match.group(4) # Optional project ID from query

            # If no project ID is specified in query, you might default to a configured one
            # For hackathon, best to require it or have a strong default.
            # For now, let's assume we expect a project ID either explicitly or a well-known one.
            # Example: Default to an environment variable GITLAB_PROJECT_ID if no project ID in query
            project_id = int(project_id_from_query) if project_id_from_query else os.environ.get('GITLAB_DEFAULT_PROJECT_ID')
            
            if not project_id:
                 ai_response_text = "Please specify a GitLab project ID for issue triage. E.g., 'Triage issue #123 for project 456'."
            else:
                logging.info(f"Detected request to {action} GitLab issue {issue_iid} for project {project_id}")
                issue_data_result = _fetch_gitlab_issue_details_internal(project_id, issue_iid)
                
                if "error" in issue_data_result:
                    ai_response_text = f"Error fetching GitLab issue {issue_iid}: {issue_data_result['error']}"
                elif issue_data_result['data']:
                    ai_response_text = triage_issue_with_gemini(issue_data_result['data'])
                else:
                    ai_response_text = f"Could not retrieve issue {issue_iid} details from project {project_id}."

        # 2. Handle Proactive CI/CD Log Anomaly Detection & Root Cause Analysis
        elif re.search(r'(analyze logs for project|diagnose pipeline failure in project) (\d+)( for last (\d+) logs)?', lower_query):
            project_id_match = re.search(r'project (\d+)', lower_query)
            num_logs_match = re.search(r'last (\d+) logs', lower_query)
            
            if project_id_match and gitlab_client:
                project_id = int(project_id_match.group(1))
                num_logs = int(num_logs_match.group(1)) if num_logs_match else 1 # Default to 1 log if not specified

                logging.info(f"Detected request to analyze last {num_logs} logs for project {project_id}")
                
                gitlab_result = _fetch_last_n_job_logs_for_analysis_internal(project_id, num_logs)
                if "error" in gitlab_result:
                    ai_response_text = f"Could not fetch logs for analysis: {gitlab_result['error']}"
                elif gitlab_result['data']:
                    ai_response_text = analyze_logs_with_gemini(gitlab_result['data'])
                else:
                    ai_response_text = f"No recent logs found for project {project_id} to analyze."
            else:
                ai_response_text = "Please specify a GitLab project ID for log analysis. E.g., 'Analyze last 3 logs for project 123'."

        # 3. Handle CI/CD Pipeline Optimization Suggestions
        elif re.search(r'(optimize pipeline|improve ci/cd|review gitlab ci)', lower_query) and context_code:
            logging.info("Detected request for CI/CD pipeline optimization with provided YAML.")
            ai_response_text = optimize_pipeline_with_gemini(context_code)
        elif re.search(r'(optimize pipeline|improve ci/cd|review gitlab ci)', lower_query) and not context_code:
            ai_response_text = "Please provide the GitLab CI/CD YAML content you want me to optimize in the context code field."

        # 4. Handle AI-Driven Code Refactoring and Best Practice Suggestions
        elif re.search(r'(refactor|improve|optimize|best practices|fix) (code|function|script)', lower_query) and context_code:
            # Try to guess language, or ask user to specify in prompt
            language_match = re.search(r'in (python|javascript|java|yaml|json|go|ruby|c\+\+)', lower_query, re.IGNORECASE)
            language = language_match.group(1).lower() if language_match else "generic"
            
            logging.info(f"Detected request for code refactoring/improvement in {language}.")
            ai_response_text = refactor_code_with_gemini(context_code, language)
        elif re.search(r'(refactor|improve|optimize|best practices|fix) (code|function|script)', lower_query) and not context_code:
            ai_response_text = "Please provide the code snippet you want to refactor or get suggestions for in the context code field."


        # 5. Handle GitLab Project Listing
        elif "gitlab projects" in lower_query or ("list" in lower_query and "projects" in lower_query and "gitlab" in lower_query):
            gitlab_result = _fetch_gitlab_projects_internal()
            if "error" in gitlab_result:
                ai_response_text = f"GitLab projects could not be fetched: {gitlab_result['error']}"
            else:
                projects_data = gitlab_result['data']
                if projects_data:
                    context_for_llm = f"User asked for GitLab projects. Here is the raw data: {json.dumps(projects_data)}. Summarize these projects, highlighting their names, IDs, and default branches, and note how this helps in 'building software faster'."
                    ai_response_text = get_gemini_response(context_for_llm, conversation_history_for_llm)
                else:
                    ai_response_text = "No GitLab projects found for your account."
        
        # 6. Handle GitLab Pipeline Status
        elif "pipeline status" in lower_query and "project" in lower_query:
            project_id_match = re.search(r'project (\d+)', lower_query)
            if project_id_match and gitlab_client:
                project_id = int(project_id_match.group(1))
                gitlab_result = _fetch_gitlab_pipeline_status_internal(project_id)
                if "error" in gitlab_result:
                    ai_response_text = f"Could not get pipeline status for project {project_id}: {gitlab_result['error']}"
                else:
                    pipeline_data = gitlab_result['data']
                    context_for_llm = f"User asked for pipeline status for GitLab project ID {project_id}. Here is the raw data: {json.dumps(pipeline_data)}. Analyze this status and provide actionable insights or next steps related to 'building software faster'. If the status is 'failed', suggest how to investigate."
                    ai_response_text = get_gemini_response(context_for_llm, conversation_history_for_llm)
            else:
                ai_response_text = "Please specify a GitLab project ID. E.g., 'What's the pipeline status for project 123?'"

        # 7. Handle GitLab Job Logs
        elif "logs for job" in lower_query and "project" in lower_query and "job" in lower_query:
            project_id_match = re.search(r'project (\d+)', lower_query)
            job_id_match = re.search(r'job (\d+)', lower_query)
            if project_id_match and job_id_match and gitlab_client:
                project_id = int(project_id_match.group(1))
                job_id = int(job_id_match.group(1))
                gitlab_result = _fetch_gitlab_job_logs_internal(project_id, job_id)
                if "error" in gitlab_result:
                    ai_response_text = f"Could not get job logs for project {project_id}, job {job_id}: {gitlab_result['error']}"
                else:
                    logs_data = gitlab_result['data']
                    full_logs = logs_data.get('logs', 'No logs found.')
                    truncated_logs = full_logs[:5000] + ("..." if len(full_logs) > 5000 else "") # Truncate for LLM input
                    context_for_llm = f"User asked for job logs for GitLab project ID {project_id}, job ID {job_id}. The job name is '{logs_data.get('job_name', 'N/A')}'. Here are the logs (possibly truncated): ```{truncated_logs}```. Analyze these logs to identify the root cause of any failure, suggest a fix, or provide a concise summary that helps 'build software faster'."
                    ai_response_text = get_gemini_response(context_for_llm, conversation_history_for_llm)
            else:
                ai_response_text = "Please specify both a project ID and job ID for logs. E.g., 'Show me logs for job 456 in project 123.'"
        
        # 8. General AI Query (if no specific command is detected)
        else:
            logging.info(f"Defaulting to general AI query for: {query}")
            ai_response_text = get_gemini_response(query, conversation_history_for_llm)

    except Exception as e:
        logging.error(f"Error during AI processing or GitLab API call: {e}", exc_info=True)
        ai_response_text = f"An unexpected error occurred during AI processing: {str(e)}. Please try again."

    # Extract thought process if present (this assumes Gemini puts it at the end after a specific marker)
    # This logic assumes "Thought Process:" or "Explanation of reasoning:" appears as a clear separator.
    if "Thought Process:" in ai_response_text:
        parts = ai_response_text.split("Thought Process:", 1)
        ai_response_text = parts[0].strip()
        thought_process_explained = "Thought Process: " + parts[1].strip()
    elif "Explanation of reasoning:" in ai_response_text: # For issue triage
        parts = ai_response_text.split("Explanation of reasoning:", 1)
        ai_response_text = parts[0].strip()
        thought_process_explained = "Explanation of reasoning: " + parts[1].strip()

    # Save AI response
    ai_message_data = {
        'text': ai_response_text,
        'sender': 'ai',
        'timestamp': datetime.utcnow(),
        'conversation_id': conversation_id,
        'thought_process': thought_process_explained # Save thought process as well
    }
    ai_message_id = save_message(ai_message_data)
    if not ai_message_id:
        logging.warning("Failed to save AI message to DB.")

    return jsonify({
        'response': ai_response_text,
        'userMessageId': str(user_message_id),
        'aiMessageId': str(ai_message_id),
        'conversationId': str(conversation_id),
        'thought_process': thought_process_explained # Send to frontend
    })

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Fetches all past conversations."""
    if not mongo_client:
        return jsonify({"error": "MongoDB not connected."}), 500
    try:
        conversations = list(mongo_db.conversations.find().sort('start_time', -1))
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
        return jsonify(conversations), 200
    except Exception as e:
        logging.error(f"Error fetching conversations: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch conversations"}), 500

@app.route('/conversations/<conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Fetches all messages for a specific conversation."""
    if not mongo_client:
        return jsonify({"error": "MongoDB not connected."}), 500
    try:
        messages = list(mongo_db.messages.find({"conversation_id": ObjectId(conversation_id)}).sort('timestamp', 1))
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            msg['conversation_id'] = str(msg['conversation_id'])
            msg['timestamp'] = msg['timestamp'].isoformat() # Convert datetime to string
        return jsonify(messages), 200
    except Exception as e:
        logging.error(f"Error fetching messages for conversation {conversation_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch conversation messages"}), 500

@app.route('/feedback', methods=['POST'])
def save_feedback():
    """Saves user feedback for AI responses."""
    if not mongo_client:
        return jsonify({"error": "MongoDB not connected."}), 500
    data = request.json
    try:
        feedback_data = {
            'message_id': ObjectId(data['message_id']),
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

# --- Main App Runner ---
if __name__ == '__main__':
    # When running locally, Flask defaults to 127.0.0.1:5000
    # In Cloud Run, Gunicorn will manage the server, listening on 0.0.0.0:8080
    app.run(debug=True, host='0.0.0.0', port=5000)
