import os
import pytest
from berlayar.utils.load_keys import load_environment_variables
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter
from berlayar.dataops.storage.gcs import make_blob_public
import httpx
import tempfile

@pytest.fixture
def twilio_adapter():
    load_environment_variables()
    return TwilioWhatsAppAdapter()

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

def test_send_receive_download_media_functional(twilio_adapter, setup_media_files):
    # Get the audio URL from setup_media_files fixture
    audio_url = setup_media_files["audio_url"]

    # Send media
    test_recipient = os.getenv("TEST_RECIPIENT")
    result = twilio_adapter.send_media(test_recipient, audio_url)
    assert result is True, "Failed to send media via Twilio"

    # Simulate receiving media from Twilio
    test_data = {
        "From": "whatsapp:+1234567890",
        "MediaUrl0": audio_url,
        "MessageSid": "SM12345"
    }
    response = httpx.post(twilio_adapter.twilio_webhook_url, data=test_data)
    assert response.status_code == 200, "Failed to receive media from Twilio"

    # Download media
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path, _ = twilio_adapter.download_media(audio_url, temp_dir)

        # Check that the downloaded file is not empty
        assert os.path.isfile(file_path), "Downloaded file does not exist"
        assert os.path.getsize(file_path) > 0, "Downloaded file is empty"

        # Print file size and type
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(audio_url)[1][1:]  # Get file extension
        print(f"Downloaded file size: {file_size} bytes")
        print(f"Downloaded file type: {file_type}")
