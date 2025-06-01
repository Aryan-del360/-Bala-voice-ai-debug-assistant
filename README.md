# Bala Voice AI Debug Assistant

This project is my take on building a smart, voice-activated assistant for developers, especially for those working with GitLab. My goal was to create a tool that uses AI to help analyze common development and DevOps challenges, making the debugging process quicker and more intuitive.

# Bala Voice AI Debug Assistant

This project is my take on building a smart, voice-activated assistant for developers...

**🚀 Live Demo:** [https://bala-ai-app-222119246190.us-central1.run.app/](https://bala-ai-app-222119246190.us-central1.run.app/)

## What It Does

This assistant is designed to:

* **Transcribe Voice Queries:** You can speak your questions, and the assistant will convert them into text.
* **Connect to GitLab:** It hooks into GitLab to pull information about your projects, pipelines, job logs, and even issues.
* **AI-Powered Insights:** Using Google's Gemini AI, it can:
    * **Summarize Issues:** Quickly give you the gist of complex GitLab issues.
    * **Analyze CI/CD Logs:** Help pinpoint problems in your pipeline failures.
    * **Suggest Fixes:** Offer ideas for code improvements or optimize your GitLab CI/CD YAML files.
    * **Refactor Code:** Even suggest better ways to write your code.
* **Remember Conversations:** It stores your chat history and lets you provide feedback on AI responses.

## Technologies I Used

* **Python:** The core language for the application.
* **Flask:** To build the web service that powers the assistant.
* **Google Cloud:**
    * **Speech-to-Text:** For voice recognition.
    * **Vertex AI (Gemini LLM):** For the AI intelligence and generating responses.
* **MongoDB:** To store conversation history and feedback.
* **python-gitlab:** To interact with the GitLab API.
* **GitLab CI/CD:** I've set up a basic pipeline that includes Static Application Security Testing (SAST) to check for security vulnerabilities.

## How to Get It Running (Local Setup)

Want to see it in action on your machine?

1.  **Clone the project:**
    ```bash
    git clone [https://gitlab.com/aryan-del360-group/bala-voice-ai-debug-assistant.git](https://gitlab.com/aryan-del360-group/bala-voice-ai-debug-assistant.git)
    cd bala-voice-ai-debug-assistant
    ```
    *(Note: This uses the GitLab URL from your provided README. If you're pushing to GitHub, adjust the clone URL.)*

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install all dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Google Cloud Setup:**
    * Make sure you have a Google Cloud project with the necessary APIs enabled (Speech-to-Text, Vertex AI).
    * Set up authentication (e.g., using `gcloud auth application-default login` or by providing service account credentials via the `GOOGLE_APPLICATION_CREDENTIALS` environment variable).
    * Set environment variables for your GCP Project ID and Region (e.g., `GCP_PROJECT_ID`, `GCP_REGION`).

5.  **MongoDB Setup:**
    * Ensure you have a MongoDB instance running (local or cloud-based).
    * Set your MongoDB connection string as an environment variable (e.g., `MONGO_URI`).

6.  **GitLab Setup:**
    * Generate a GitLab Personal Access Token with appropriate scopes (e.g., `api`, `read_repository`).
    * Set it as an environment variable (e.g., `GITLAB_PRIVATE_TOKEN`).
    * Set your GitLab API URL (e.g., `https://gitlab.com` or your self-hosted instance) as `GITLAB_URL`.

7.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The app will typically run on `http://127.0.0.1:5000`.

## Future Ideas

I'm keen to keep improving this. Some ideas include:

* **Frontend Interface:** Build a dedicated web UI to interact with the assistant more smoothly.
* **More Integrations:** Connect to other developer tools like Jira, Jenkins, or GitHub itself.
* **Advanced AI Capabilities:** Explore more complex use cases for debugging and code analysis.
* **User Management:** Add proper user authentication and management for team use.

## Let's Connect!

Got questions or want to discuss this project? Feel free to reach out!

**Shubham Sharma**
* **Email:** shubhamdatascientist76@gmail.com
* **LinkedIn:** [My LinkedIn Profile](https://www.linkedin.com/in/shubham-sharma-224954367/)
* **GitHub:** [My GitHub Profile](https://github.com/Aryan-del360)
