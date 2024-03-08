import os
import pytest
from berlayar.utils.load_keys import load_environment_variables
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter
from berlayar.dataops.storage.gcs import make_blob_public
import httpx
import tempfile
import mimetypes

@pytest.fixture
def twilio_adapter():
    load_environment_variables()
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

@pytest.fixture(scope="module")
def setup_media_files():
    load_environment_variables()
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    # Assuming these blobs are already uploaded and you just need to make them public
    image_blob_name = "berlayar/raw_data/fixtures/2008-06923.jpg"
    audio_blob_name = "berlayar/raw_data/fixtures/5c77998c-87cf-477b-a232-e3ada4168cc3_neural.mp3"
    make_blob_public(bucket_name, image_blob_name)
    make_blob_public(bucket_name, audio_blob_name)
    # Return the public URLs for use in tests
    return {
        "image_url": f"https://storage.googleapis.com/{bucket_name}/{image_blob_name}",
        "audio_url": f"https://storage.googleapis.com/{bucket_name}/{audio_blob_name}"
    }

def test_send_media(twilio_adapter, setup_media_files):
    test_recipient = os.getenv("TEST_RECIPIENT")
    image_url = setup_media_files["image_url"]
    audio_url = setup_media_files["audio_url"]

    # Test sending the image
    image_send_result = twilio_adapter.send_media(test_recipient, image_url)
    assert image_send_result is True, "Failed to send image via media"

    # Test sending the audio
    audio_send_result = twilio_adapter.send_media(test_recipient, audio_url)
    assert audio_send_result is True, "Failed to send audio via media"

def test_receive_message(twilio_adapter):
    test_data = {
        "From": "whatsapp:+1234567890",
        "Body": "Test message",
        "MessageSid": "SM12345"
    }
    # Use the twilio_webhook_url from the twilio_adapter instance
    response = httpx.post(twilio_adapter.twilio_webhook_url, data=test_data)
    assert response.status_code == 200
    # Update this assertion to match the actual response structure
    expected_response = {
        "received": True,
        "data": {
            "sender": "whatsapp:+1234567890",
            "text_body": "Test message"
        }
    }
    assert response.json() == expected_response

def test_receive_media_valid_response(twilio_adapter):
    # Mock a valid request body containing a media URL
    test_data = {
        "From": "whatsapp:+1234567890",
        "MediaUrl0": "http://example.com/media.jpg",
        "MessageSid": "SM12345"
    }

    # Call the receive_media function
    response = twilio_adapter.receive_media(test_data)

    # Check that the response is valid
    assert response is not None, "No response received"
    assert isinstance(response, dict), "Response is not a dictionary"
    assert "sender" in response, "Sender information missing in response"
    assert "media_url" in response, "Media URL missing in response"
    assert response["sender"] == "whatsapp:+1234567890", "Incorrect sender in response"
    assert response["media_url"] == "http://example.com/media.jpg", "Incorrect media URL in response"

def get_file_size(url):
    """Fetches the size of the file at the given URL using a HEAD request."""
    with httpx.Client() as client:
        response = client.head(url)
        if response.status_code == 200 and 'Content-Length' in response.headers:
            return int(response.headers['Content-Length'])
        else:
            return None

def test_download_media(twilio_adapter):
    test_media_url = "https://storage.googleapis.com/thesoundofstories/berlayar/raw_data/fixtures/5c77998c-87cf-477b-a232-e3ada4168cc3_neural.mp3"
    expected_mime_type = 'audio/mpeg'

    # Dynamically obtain the expected file size
    expected_file_size = get_file_size(test_media_url)
    assert expected_file_size is not None, "Failed to fetch expected file size"

    # Size tolerance might still be necessary due to the way data is streamed or encoded
    size_tolerance = 1000  # Adjust based on your requirements

    # Perform the actual download
    content = twilio_adapter.download_media(test_media_url)
    assert content is not None, "Failed to download media"

    # Write the downloaded content to a temporary file for validation
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        tmp_file.write(content)
        tmp_file.seek(0)  # Rewind to start of file for reading
        actual_file_size = os.path.getsize(tmp_file.name)

        # Validate file size within the specified tolerance
        assert abs(actual_file_size - expected_file_size) <= size_tolerance, f"Downloaded file size {actual_file_size} bytes is outside the allowed tolerance from expected {expected_file_size} bytes"
