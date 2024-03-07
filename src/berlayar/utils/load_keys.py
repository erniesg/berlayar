# berlayar/utils/load_keys.py

import os
from dotenv import load_dotenv
from berlayar.config.google_secrets import GoogleSecretsConfigLoader
from berlayar.utils.path import construct_path_from_root
import firebase_admin
from firebase_admin import credentials

# Load .env from the project root
dotenv_path = construct_path_from_root('.env')
print(f"Constructed path for env: {dotenv_path}")
load_dotenv(dotenv_path)


def load_twilio_credentials():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    twilio_webhook_url = os.getenv("TWILIO_WEBHOOK_URL")
    test_recipient = os.getenv("TEST_RECIPIENT")

    if account_sid and auth_token:
        os.environ['TWILIO_ACCOUNT_SID'] = account_sid
        os.environ['TWILIO_AUTH_TOKEN'] = auth_token
    else:
        print("Twilio Account SID and/or Auth Token not found in environment variables.")

    if twilio_phone_number:
        os.environ['TWILIO_PHONE_NUMBER'] = twilio_phone_number
    else:
        print("Twilio Phone Number not found in environment variables.")

    if twilio_webhook_url:
        os.environ['TWILIO_WEBHOOK_URL'] = twilio_webhook_url
    else:
        print("Twilio Webhook URL not found in environment variables.")

    if test_recipient:
        os.environ['TEST_RECIPIENT'] = test_recipient
    else:
        print("Test Recipient not found in environment variables.")

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

    firebase_key = os.getenv('FIREBASE_KEY')
    if not firebase_key:
        try:
            config_loader = GoogleSecretsConfigLoader(project_id)
            firebase_key = config_loader.get('FIREBASE_KEY')
            if firebase_key:
                os.environ['FIREBASE_KEY'] = firebase_key
        except Exception as e:
            print("Failed to load Firebase Key from Google Secrets:", e)

    user_collection_name = os.getenv('USER_COLLECTION_NAME')
    if not user_collection_name:
        try:
            config_loader = GoogleSecretsConfigLoader(project_id)
            user_collection_name = config_loader.get('USER_COLLECTION_NAME')
            if user_collection_name:
                os.environ['USER_COLLECTION_NAME'] = user_collection_name
        except Exception as e:
            print("Failed to load User Collection Name from Google Secrets:", e)
