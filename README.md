# HR Policy Assistant Bot

This project is an HR Policy Assistant chatbot that answers employee questions based on HR policy documents. It uses Google Drive to sync policy documents, reads their content, and leverages OpenAI's GPT-3.5-turbo to generate answers.

## Features
- Syncs HR policy documents from a specified Google Drive folder.
- Reads and combines the content of all `.docx` policy files.
- Answers questions using OpenAI's GPT-3.5-turbo, referencing only the provided policy documents.
- Exposes a REST API endpoint for integration with other tools (e.g., Power Automate).

## Prerequisites
- Python 3.7+
- Google Cloud project with Drive API enabled
- `credentials.json` file for Google Drive API (OAuth 2.0 client credentials)
- OpenAI API key

## Installation
1. **Clone the repository** and navigate to the project folder:
   ```bash
   git clone <repo-url>
   cd hr_chatbot
   ```
2. **Install dependencies:**
   ```bash
   pip install flask openai google-auth google-auth-oauthlib google-api-python-client python-docx
   ```
3. **Add your Google API credentials:**
   - Place your `credentials.json` file in the project root.
4. **Set your OpenAI API key:**
   - The key is currently hardcoded in `run_assistant3.py`. For production, use environment variables or a config file.

## Usage
1. **Run the Flask app:**
   ```bash
   flask run
   ```
   The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

2. **Ask a question:**
   Send a POST request to `/ask` with a JSON body containing your question. Example using `curl`:
   ```bash
   curl -X POST http://127.0.0.1:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the leave policy for India?"}'
   ```

## Folder Structure
- `run_assistant3.py` - Main application script
- `policies/` - Local folder where policy documents are stored
- `token.json` - Stores Google API authentication tokens

## Notes
- The bot syncs policy documents from Google Drive every time a question is asked. For better performance, consider scheduling this sync separately.
- If the answer is not found in the policy documents, the bot will respond accordingly.

## License
Specify your license here. 