# HR Policy Assistant - Core Logic

This project is the core logic for an HR Policy Assistant chatbot. It answers employee questions based on HR policy documents by using Google Drive to sync the files and OpenAI's GPT-3.5-turbo to generate context-aware answers. This command-line tool serves as the foundation for a future user-facing application.

## Features

* **Google Drive Sync**: Automatically syncs `.docx` policy documents from a specified Google Drive folder.
* **AI-Powered Q&A**: Reads and combines the content of all policy files to answer questions using OpenAI's GPT-3.5-turbo.
* **Source Citing**: The AI is instructed to reference only the provided policy documents and cite the source document when answering.
* **Command-Line Interface**: Includes a simple CLI for direct interaction and testing of the core logic.

## Prerequisites

* Python 3.8+
* A Google Cloud project with the Drive API enabled.
* An OpenAI API key.

## Installation

1.  **Clone the repository** and navigate to the project folder:
    ```bash
    git clone [https://github.com/your-username/hr-policy-assistant.git](https://github.com/your-username/hr-policy-assistant.git)
    cd hr-policy-assistant
    ```
2.  **Install dependencies** from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Add Google API credentials**:
    * Follow the setup guide to create OAuth 2.0 client credentials for a **Desktop app**.
    * Download the `credentials.json` file and place it in the project root.
4.  **Set your OpenAI API key**:
    * Open the `assistant.py` script.
    * Find the line `openai.api_key = "YOUR_OPENAI_API_KEY_HERE"` and insert your key.

## Usage

1.  **Run the script** from your terminal:
    ```bash
    python assistant.py
    ```
2.  **First-Time Authentication**: On the first run, your browser will open to ask for Google account login and permission. This creates a `token.json` file for future sessions.

3.  **Ask a question**: Once the assistant is ready, type your question and press Enter.
    ```
    Your question: What is the company policy on sick leave?
    ```

## Folder Structure


hr-policy-assistant/
├── assistant.py            # Main application script
├── credentials.json        # (You provide) Google API credentials
├── token.json              # (Auto-generated) Google API auth tokens
├── requirements.txt        # Project dependencies
└── policies_cache/         # (Auto-generated) Local folder for synced documents


## Notes

* The bot syncs all policy documents from Google Drive every time it starts.
* If the answer is not found in the policy documents, the bot is instructed to respond accordingly.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
