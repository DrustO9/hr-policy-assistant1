# -----------------------------------------------------------------------------
# HR Policy Assistant - Core Logic (The Brain)
#
# This script is a command-line tool that performs the core functions
# of the HR chatbot. It connects to Google Drive, reads policy documents,
# and uses the OpenAI API to answer user questions based on the documents.
#
# --- IMPORTANT: HOW TO SET UP AND RUN ---
#
# 1. Install necessary Python libraries:
#    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib openai python-docx
#
# 2. Set up Google Drive API Credentials:
#    - Go to the Google Cloud Console and enable the "Google Drive API".
#    - Create credentials for a "Desktop app".
#    - Download the credentials file and rename it to 'credentials.json'.
#    - Place 'credentials.json' in the same folder as this script.
#
# 3. Add your OpenAI API Key:
#    - Find the line `openai.api_key = "YOUR_OPENAI_API_KEY_HERE"` below
#      and replace the placeholder with your actual secret key.
#
# 4. Run the script from your terminal:
#    python your_script_name.py
#
# 5. First-time Run:
#    - The script will open your web browser to ask you to log in to Google
#      and grant permission. This creates a 'token.json' file so you
#      don't have to log in every time.
# -----------------------------------------------------------------------------

import os
import io
import docx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import openai

# --- Configuration ---
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"

# 2. Set the name of your Google Drive folder.
GDRIVE_FOLDER_NAME = "HR Policies"

# --- Constants ---
LOCAL_POLICY_FOLDER = "policies_cache"  # Local folder to store downloaded files
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"] # Permissions for Google Drive


def sync_google_drive_files():
    """
    Connects to Google Drive, finds the specified folder, and downloads
    all .docx files to a local cache folder.
    """
    print("Attempting to connect to Google Drive...")
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except HttpError as e:
                print(f"Error refreshing token, re-authentication is needed: {e}")
                creds = None # Force re-authentication
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("\nERROR: 'credentials.json' not found.")
                print("Please follow Step 2 in the setup instructions at the top of this file.")
                return False

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        
        # Find the folder by name
        query = f"name='{GDRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        folders = response.get('files', [])

        if not folders:
            print(f"\nERROR: The folder '{GDRIVE_FOLDER_NAME}' was not found in your Google Drive.")
            return False

        folder_id = folders[0]['id']
        print(f"Successfully found folder '{GDRIVE_FOLDER_NAME}'.")

        # Create local cache folder if it doesn't exist
        if not os.path.exists(LOCAL_POLICY_FOLDER):
            os.makedirs(LOCAL_POLICY_FOLDER)

        # Download all .docx files from the folder
        print("Syncing policy documents...")
        query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' and trashed=false"
        response = service.files().list(q=query, fields='files(id, name)').execute()
        files = response.get('files', [])

        if not files:
            print("No .docx policy files found in the folder.")
            return True # It's not an error, just an empty folder

        for file in files:
            file_path = os.path.join(LOCAL_POLICY_FOLDER, file.get('name'))
            request = service.files().get_media(fileId=file.get('id'))
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
            with open(file_path, 'wb') as f:
                f.write(fh.getvalue())
            print(f" - Synced '{file.get('name')}'")
        
        print("Document sync complete.")
        return True

    except HttpError as error:
        print(f"\nAn HTTP error occurred with the Google API: {error}")
        return False
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return False


def read_all_policies():
    """
    Reads all .docx files from the local cache folder and combines their
    text content into a single string for the AI.
    """
    print("Reading policy documents from cache...")
    combined_text = ""
    if not os.path.exists(LOCAL_POLICY_FOLDER):
        return ""
        
    for filename in os.listdir(LOCAL_POLICY_FOLDER):
        if filename.endswith(".docx"):
            try:
                doc = docx.Document(os.path.join(LOCAL_POLICY_FOLDER, filename))
                full_text = [para.text for para in doc.paragraphs]
                
                # Add document titles for better context for the AI
                combined_text += f"--- Start of Document: {filename} ---\n"
                combined_text += '\n'.join(full_text)
                combined_text += f"\n--- End of Document: {filename} ---\n\n"
            except Exception as e:
                print(f"Could not read file {filename}: {e}")
    
    if not combined_text:
        print("Could not find any text in the policy documents.")
    else:
        print("Successfully loaded all policy text.")
    return combined_text


def get_answer_from_ai(question, policy_context):
    """
    Sends the user's question and the policy text to OpenAI to get an answer.
    This version uses an improved, more flexible prompt.
    """
    if not openai.api_key or openai.api_key == "YOUR_OPENAI_API_KEY_HERE":
        return "ERROR: Please add your OpenAI API key to the script to get an answer."

    # --- NEW, IMPROVED PROMPT ---
    # This prompt gives the AI a better strategy for answering questions,
    # including summarizing policies for general questions.
    system_prompt = """
    You are an intelligent HR Policy Assistant. Your primary goal is to answer employee questions using *only* the content from the provided HR documents.

    Your tasks are:
    1.  **Analyze the User's Question:** Understand the user's intent. Are they asking for a specific detail (e.g., 'how many sick days?') or a general policy summary (e.g., 'tell me about travel')?

    2.  **Search the Documents:** Carefully search all the provided document text to find relevant information. The user's phrasing might not be an exact match, so look for related topics and keywords. For example, if they ask about 'posh', look for 'Prevention of Sexual Harassment'.

    3.  **Formulate the Answer:**
        * If you find a **direct answer** to a specific question, provide it clearly and cite the source document name (e.g., "According to 'Leave Policy.docx', you are entitled to...").
        * If the user asks a **general question** (like 'tell me about travel policy'), and you find the relevant document, provide a brief summary of that policy's main points. You must still cite the source document.
        * If after a thorough search you genuinely **cannot find any relevant information** in the documents, you MUST respond with the exact phrase: 'I could not find an answer to your question in the provided policy documents.'

    4.  **Adhere to Boundaries:** Do not make up information or use any knowledge outside of the provided text. Be formal and professional.
    """

    print("Sending question to AI with new prompt...")
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here are the HR policies:\n{policy_context}"},
                {"role": "user", "content": f"Please answer this question: {question}"}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return "An error occurred while trying to contact the AI."



# --- Main Program Execution ---
if __name__ == "__main__":
    print("--- HR Policy Assistant Brain ---")
    
    # Step 1: Sync files from Google Drive.
    if sync_google_drive_files():
        
        # Step 2: Read the downloaded files into memory.
        policy_knowledge_base = read_all_policies()
        
        # --- ADD THIS LINE TO DEBUG ---
        # This will print all the text that the script successfully read from your documents.
        print("\n--- DEBUG: TEXT BEING SENT TO AI ---\n", policy_knowledge_base, "\n--- END OF DEBUG ---\n")
        
        if not policy_knowledge_base:
            print("\nCould not load any policy information. Please check your Google Drive folder and files.")
        else:
            print("\nHR Assistant is ready. Type 'exit' to quit.")
            print("-" * 40)
            
            # Step 3: Start a loop to ask for questions.
            while True:
                user_question = input("\nYour question: ")
                
                if user_question.lower() == 'exit':
                    break
                
                # Step 4: Get the answer from the AI.
                answer = get_answer_from_ai(user_question, policy_knowledge_base)
                
                # Step 5: Print the answer.
                print(f"\nAssistant: {answer}")
    else:
        print("\nCould not initialize the HR Assistant due to an error during Google Drive sync.")



