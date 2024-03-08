import os
from twilio.rest import Client
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.utils.load_keys import load_twilio_credentials
import httpx
import urllib

class TwilioWhatsAppAdapter(MessagingInterface):
    def __init__(self):
        load_twilio_credentials()
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.twilio_webhook_url = os.getenv("TWILIO_WEBHOOK_URL")
        # Print out environment variables for verification
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            print(f"Failed to initialize Twilio client: {e}")
            raise

    def send_message(self, recipient: str, message_body: str) -> bool:
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=recipient
            )
            print(message.sid)

            return message.sid is not None
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False

    def send_media(self, recipient: str, media_url: str) -> bool:
        try:
            message = self.client.messages.create(
                body=None,  # No text body required for media messages
                from_=self.twilio_phone_number,
                to=recipient,
                media_url=[media_url]  # The MediaUrl parameter expects a list
            )
            print(f"Media message SID: {message.sid}")
            return True
        except Exception as e:
            print(f"Failed to send media message: {e}")
            return False

    def receive_message(self, request_body: dict) -> dict:
        # Example implementation
        sender = request_body.get("From")
        text_body = request_body.get("Body")
        print(f"Message received from {sender}: {text_body}")
        # Process the message as needed
        return {"sender": sender, "text_body": text_body}

    def receive_media(self, request_body: dict) -> dict:
        # Example implementation for receiving media
        sender = request_body.get("From")
        media_url = request_body.get("MediaUrl0")  # Assuming one media item for simplicity
        print(f"Media received from {sender}: {media_url}")
        # Process the media as needed
        return {"sender": sender, "media_url": media_url}
    
    def download_media(self, media_url):
        """Download media from the given URL and return its content.

        Args:
            media_url (str): URL of the media to download.

        Returns:
            bytes: The content of the downloaded media if successful, None otherwise.
        """
        try:
            print(f"Downloading media from {media_url}")
            with httpx.stream("GET", media_url) as response:
                if response.status_code == 200:
                    content = b''.join(response.iter_bytes())
                    print(f"Media downloaded successfully.")
                    return content
                else:
                    print(f"Failed to download media. Status code: {response.status_code}")
                    return None
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None
