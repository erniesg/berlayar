import os
from twilio.rest import Client
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.utils.load_keys import load_twilio_credentials

class TwilioWhatsAppAdapter(MessagingInterface):
    def __init__(self):
        load_twilio_credentials()
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")  # Add this line
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
        # Implement logic to send media message
        pass

    def receive_message(self, request_body: dict) -> dict:
        # Implement logic to receive message
        pass

    def receive_media(self, request_body: dict) -> dict:
        # Implement logic to receive media message
        pass

def main():
    # Instantiate Twilio adapter
    twilio_adapter = TwilioWhatsAppAdapter()

    # Define test recipient and message body
    test_recipient = os.getenv("TEST_RECIPIENT")
    test_message = "This is a test message from the Twilio WhatsApp adapter."

    # Send test message
    result = twilio_adapter.send_message(test_recipient, test_message)

    # Check if message was sent successfully
    if result:
        print("Test message sent successfully!")
    else:
        print("Failed to send test message.")

if __name__ == "__main__":
    main()
