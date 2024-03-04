import os
import base64
import uuid
from fastapi import FastAPI, Request, Response
from pydantic import ValidationError
from twilio.twiml.messaging_response import MessagingResponse
from pathlib import Path
import httpx
import logging
from berlayar.utils.load_keys import load_environment_variables
from berlayar.utils.path import construct_path_from_root
from berlayar.schemas.user import UserModel
from berlayar.services.user import User
from berlayar.services.session import Session
from berlayar.dataops.storage.local import LocalStorage
# Setup logging
logging.basicConfig(level=logging.DEBUG, filename="app.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_environment_variables()

# App initialization
app = FastAPI()

# Environment variables
AUDIO_TRANSFORM_SERVICE_URL = os.getenv("AUDIO_TRANSFORM_SERVICE_URL")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Services initialization
local_storage = LocalStorage()
user_service = User(storages=[local_storage])
session_service = Session(user_service)

async def download_media(media_url):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    auth_header = base64.b64encode(f'{account_sid}:{auth_token}'.encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.get(media_url, headers={"Authorization": f"Basic {auth_header}"}, follow_redirects=True)

    if response.status_code == 200:
        unique_filename = str(uuid.uuid4())
        sessions_dir = construct_path_from_root('raw_data/sessions/whatsapp')
        Path(sessions_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(sessions_dir, f"{unique_filename}.mp3")

        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path, unique_filename
    else:
        logger.error(f"Failed to download media from {media_url}, status code {response.status_code}")
        return None, None

async def process_audio_message(media_url):
    file_path, unique_filename = await download_media(media_url)
    if file_path:
        transformed_file_path = os.path.join(os.path.dirname(file_path), f"{unique_filename}_neural.mp3")
        async with httpx.AsyncClient() as client:
            payload = {
                "input_audio_path": file_path,
                "output_audio_path": transformed_file_path,
                "params": {"Chaos": 0.5, "Z edit index": 0.2, "Z scale": 1.0, "Z offset": 0.0}
            }
            response = await client.post(AUDIO_TRANSFORM_SERVICE_URL, json=payload)
            if response.status_code == 200:
                return transformed_file_path
            else:
                logger.error(f"Failed to process audio message, status code {response.status_code}")
                return None
    else:
        return None

async def transform_audio_message(media_url):
    transformed_file_path = await process_audio_message(media_url)
    if transformed_file_path:
        return transformed_file_path
    else:
        return None

@app.post("/webhook")
async def webhook(request: Request):
    response = MessagingResponse()

    try:
        form_data = await request.form()
        # Extract the mobile number, removing 'whatsapp:' prefix
        mobile_number = form_data.get("From").replace("whatsapp:", "")
        logger.debug(f"Webhook received with form data: {form_data}")

        # Use the extracted mobile number to check for or create a new user
        existing_user = await user_service.get_user_info(mobile_number)
        if existing_user:
            logger.info(f"Existing user found: Mobile {mobile_number}")
            # Existing user logic...
        else:
            logger.debug("New user detected, attempting to create user and session.")
            user_data = {
                "preferred_name": "Placeholder Name",  # Placeholder, adjust as needed
                "age": 30,  # Placeholder
                "email": "placeholder@example.com",  # Placeholder
                "location": "Placeholder Location",  # Placeholder
                "mobile_number": mobile_number,
                "preferences": {
                    "image_gen_model": "Placeholder Model",  # Placeholder
                    "language": "en"  # Placeholder
                }
            }

            validated_user_data = UserModel.parse_obj(user_data)
            # Convert UserModel instance to a dictionary before passing
            create_user_response = await user_service.create_user(validated_user_data.dict())

            if create_user_response:
                logger.info(f"User created successfully with Mobile: {mobile_number}")
                # Assuming `response.message("Your welcome message")` sends the message
                welcome_message = "Welcome to our service! Please follow the instructions..."
                response.message(welcome_message)
            else:
                logger.error("User creation failed, create_user_response is None.")
                response.message("Failed to create user.")

    except Exception as e:
        logger.error(f"Unhandled exception in /webhook endpoint: {e}", exc_info=True)
        response.message("An error occurred while processing your request.")

    return Response(content=str(response), media_type="application/xml")
