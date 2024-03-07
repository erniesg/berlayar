import os
import pytest
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter

@pytest.fixture
def twilio_adapter():
    return TwilioWhatsAppAdapter()

def test_send_message(twilio_adapter):
    print("Environment Variables for Twilio Configuration in Test:")
    print(f"TWILIO_ACCOUNT_SID: {twilio_adapter.account_sid[-3:]}")
    print(f"TWILIO_AUTH_TOKEN: {twilio_adapter.auth_token[-3:]}")
    print(f"TWILIO_PHONE_NUMBER: {twilio_adapter.twilio_phone_number[-3:]}")
    test_recipient = os.getenv("TEST_RECIPIENT")
    print("Test recipient:", test_recipient)
    message_body = "This is a test message from the Twilio WhatsApp adapter."

    # Send message
    result = twilio_adapter.send_message(test_recipient, message_body)
    print("Message sent:", result)

    # Check if message was sent successfully
    assert result is True, "Failed to send message"
