Assumptions and Limitations
This document outlines the key assumptions made during the development of the HR Policy Assistant's core logic and the known limitations of the current version.

Assumptions
It is assumed that:

Document Format: All policy documents stored in the Google Drive folder are in the .docx (Microsoft Word) format. The current script is not configured to parse other file types like .pdf, .txt, or Google Docs.

Internet Connectivity: The application requires a stable internet connection to perform its primary functions: authenticating with Google, syncing files from Google Drive, and communicating with the OpenAI API.

Folder Structure: There is a single, specific folder in the user's Google Drive named "HR Policies" that contains all relevant documents. The script does not search for files outside of this designated folder.

API Key and Credentials: The user running the script has valid API keys for OpenAI and has correctly set up the credentials.json file for the Google Drive API as per the instructions in the README.md.

Limitations
The current implementation has the following limitations:

User Interface: This version is a command-line tool designed to demonstrate the core backend functionality. It does not have a graphical user interface (GUI) and is not yet integrated into a front-end chat platform like Microsoft Teams.

Document Syncing: The synchronisation with Google Drive occurs only once when the script is started. Any changes made to the documents in the Google Drive folder while the script is running will not be reflected until the script is restarted.

No Conversational Memory: In its current command-line form, each question is treated as a standalone query. The assistant does not remember the context of previous questions, so it cannot answer follow-up questions like "Can you explain that in simpler terms?". This functionality would be handled by the front-end chat application.

Error Handling for Document Content: The script assumes the .docx files are well-formed. It may not handle corrupted files or complex document structures (like deeply nested tables or extensive formatting) gracefully.
