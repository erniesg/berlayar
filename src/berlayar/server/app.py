# app.py

import os
import requests
import base64
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pathlib import Path
import uuid
from berlayar.utils.load_keys import load_environment_variables
from berlayar.utils.path import construct_path_from_root

# Load environment variables
load_environment_variables()

app = Flask(__name__)

def download_media(media_url):
    # Twilio Account SID and Auth Token
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    # Make a GET request to the media URL with authentication headers
    print("Downloading media from:", media_url)
    headers = {"Authorization": f"Basic {base64.b64encode(f'{account_sid}:{auth_token}'.encode()).decode()}"}
    response = requests.get(media_url, headers=headers, allow_redirects=True)

    # Check if the request was successful
    if response.status_code == 200:
        print("Media download successful.")
        # Generate a unique filename for the media file
        unique_filename = str(uuid.uuid4()) + ".mp3"

        # Construct the path for saving the media file
        sessions_dir = construct_path_from_root('raw_data/sessions/whatsapp')
        Path(sessions_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(sessions_dir, unique_filename)

        # Save the media content to a file
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print("Media saved to:", file_path)

        # Return the file path
        return file_path
    else:
        # If the request fails, return None
        print("Media download failed. Status code:", response.status_code)
        return None

@app.route("/webhook", methods=['POST'])
def webhook():
    # Get the media URL from the request
    media_url = request.values.get("MediaUrl0")

    if media_url:
        # Download the media file
        file_path = download_media(media_url)

        if file_path:
            # If the file was downloaded successfully, respond with a success message
            response = MessagingResponse()
            response.message("Your audio message has been received and saved.")
        else:
            # If the file download failed, respond with an error message
            response = MessagingResponse()
            response.message("Failed to download and save the audio message.")

        return str(response)
    else:
        # If no media URL was provided, respond with a message indicating the same
        response = MessagingResponse()
        response.message("No media received.")

        return str(response)

if __name__ == "__main__":
    app.run(debug=True)
