import os
import base64
import uuid
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from pathlib import Path
import httpx
from berlayar.utils.load_keys import load_environment_variables
from berlayar.utils.path import construct_path_from_root
from berlayar.dataops.storage.gcs import upload_to_gcs
from fastapi import APIRouter, HTTPException, Depends
from berlayar.schemas.user import UserModel
from berlayar.services.user import User
from berlayar.services.session import Session
from berlayar.server.api import router  # Import the router from api.py
from berlayar.services.user import User
from berlayar.services.session import Session

# Load environment variables
load_environment_variables()

app = FastAPI()

# Load the Audio Transform Service URL from environment variables
AUDIO_TRANSFORM_SERVICE_URL = os.getenv("AUDIO_TRANSFORM_SERVICE_URL")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Initialize User and Session services
user_service = User()
session_service = Session(user_service)

router = APIRouter()

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
        return None, None

async def process_audio_message(media_url):
    file_path, unique_filename = await download_media(media_url)
    if file_path:
        transformed_file_path = os.path.join(os.path.dirname(file_path), f"{unique_filename}_neural.mp3")
        async with httpx.AsyncClient() as client:
            payload = {
                "input_audio_path": file_path,
                "output_audio_path": transformed_file_path,
                "params": {"Chaos": 0.5, "Z edit index": 0.2, "Z scale": 1.0, "Z offset": 0.0}  # Example parameters
            }
            await client.post(AUDIO_TRANSFORM_SERVICE_URL, json=payload)
        return transformed_file_path
    else:
        return None

async def transform_audio_message(media_url):
    """
    Function to transform audio message using the Audio Transform Service.
    """
    transformed_file_path = await process_audio_message(media_url)
    if transformed_file_path:
        return transformed_file_path
    else:
        return None

@app.post("/webhook")
async def webhook(request: Request):
    response = MessagingResponse()

    # Check if user is new
    form_data = await request.form()
    user_id = form_data.get("From")
    existing_user = user_service.get_user_info(user_id)

    if not existing_user:
        # If user is new, initiate welcome message, create user, and session
        welcome_message = "Welcome to our service! Please provide your name, age, and location to get started."
        response.message(welcome_message)

        user_data = {
            "user_id": user_id,
            "language": "en",
            "preferred_name": "Test User",
            "age": 30,
            "email": "test@example.com",
            "location": "Test City",
            "mobile_number": "+1234567890",
            "preferences": {
                "image_gen_model": "model_name",
                "language": "en"
            }
        }

        create_user_response = await user_service.create_user(user_data)
        if "user_id" in create_user_response:
            create_session_response = await session_service.create_session(user_data)
            if "message" in create_session_response:
                # Additional onboarding messages can be sent here
                pass
            else:
                response.message("Failed to create session.")
        else:
            response.message("Failed to create user.")

    else:
        # For existing users, proceed with audio message processing
        response.message("Audio message received, applying neural audio synthesis magic...")

        media_url = form_data.get("MediaUrl0")

        if media_url:
            # Process the audio message
            transformed_file_path = transform_audio_message(media_url)

            if transformed_file_path:
                # Upload the transformed audio file to GCS
                output_blob_name = f"berlayar/raw_data/sessions/{os.path.basename(transformed_file_path)}"
                public_url = upload_to_gcs(GCS_BUCKET_NAME, transformed_file_path, output_blob_name)

                if public_url:
                    # Send the transformed audio file as an audio message
                    response.message().media(public_url)
                else:
                    response.message("Failed to upload the transformed audio file.")
            else:
                response.message("Failed to process the audio message.")
        else:
            response.message("No media received.")

    return Response(content=str(response), media_type="application/xml")

# Register the webhook endpoint with the FastAPI app
app.post("/webhook")(webhook)
