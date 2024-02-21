# berlayar/utils/load_keys.py

import os
from dotenv import load_dotenv
from berlayar.config.google_secrets import GoogleSecretsConfigLoader
from berlayar.utils.path import construct_path_from_root

# Load .env from the project root
dotenv_path = construct_path_from_root('.env')
print(f"Constructed path for env: {dotenv_path}")
load_dotenv(dotenv_path)

# Function to load environment variables from Google Secrets or .env file
def load_environment_variables():
    project_id = os.getenv('GOOGLE_PROJECT_ID')

    # Load Google Application Credentials
    google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not google_credentials_path:
        project_id = os.getenv('GOOGLE_PROJECT_ID')
        if project_id:
            try:
                config_loader = GoogleSecretsConfigLoader(project_id)
                google_credentials = config_loader.get('GOOGLE_APPLICATION_CREDENTIALS')
                if google_credentials:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials
            except Exception as e:
                print("Failed to load configuration from Google Secrets:", e)

    # Load OpenAI API Key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        try:
            config_loader = GoogleSecretsConfigLoader(project_id)
            openai_api_key = config_loader.get('OPENAI_API_KEY')
            if openai_api_key:
                os.environ['OPENAI_API_KEY'] = openai_api_key
        except Exception as e:
            print("Failed to load OpenAI API Key from Google Secrets:", e)

    # Load ElevenLabs API Key
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    if not elevenlabs_api_key:
        try:
            config_loader = GoogleSecretsConfigLoader(project_id)
            elevenlabs_api_key = config_loader.get('ELEVENLABS_API_KEY')
            if elevenlabs_api_key:
                os.environ['ELEVENLABS_API_KEY'] = elevenlabs_api_key
        except Exception as e:
            print("Failed to load ElevenLabs API Key from Google Secrets:", e)
