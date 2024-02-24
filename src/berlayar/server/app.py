import os
import base64
import uuid
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from pathlib import Path
import httpx
from berlayar.utils.load_keys import load_environment_variables
from berlayar.utils.path import construct_path_from_root

# Load environment variables
load_environment_variables()

app = FastAPI()

# Load the Audio Transform Service URL from environment variables
AUDIO_TRANSFORM_SERVICE_URL = os.getenv("AUDIO_TRANSFORM_SERVICE_URL")

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

@app.post("/webhook")
async def webhook(request: Request):
    form_data = await request.form()
    media_url = form_data.get("MediaUrl0")
    response = MessagingResponse()

    if media_url:
        file_path, unique_filename = await download_media(media_url)
        if file_path:
            # Prepare to call the audio transformation microservice
            transformed_file_path = os.path.join(os.path.dirname(file_path), f"{unique_filename}_neural.mp3")
            async with httpx.AsyncClient() as client:
                # Define the payload for the microservice
                payload = {
                    "input_audio_path": file_path,
                    "output_audio_path": transformed_file_path,
                    "params": {"Chaos": 0.5, "Z edit index": 0.2, "Z scale": 1.0, "Z offset": 0.0}  # Example parameters
                }
                await client.post(AUDIO_TRANSFORM_SERVICE_URL, json=payload)

            response.message("Your audio message has been received, transformed, and saved.")
        else:
            response.message("Failed to download and save the audio message.")
    else:
        response.message("No media received.")

    return Response(content=str(response), media_type="application/xml")
