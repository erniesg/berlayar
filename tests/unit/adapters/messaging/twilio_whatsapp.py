import os
import pytest
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter
from unittest.mock import patch, MagicMock
import httpx

@pytest.fixture
def twilio_adapter():
    return TwilioWhatsAppAdapter()

import pytest
from unittest.mock import patch, MagicMock
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter

@pytest.fixture
def twilio_adapter():
    return TwilioWhatsAppAdapter()

def test_download_media(twilio_adapter):
    media_url = "http://example.com/media.jpg"
    expected_content = b'Mocked media content'

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = iter([expected_content])
    mock_response.status_code = 200

    with patch('httpx.Client.stream') as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response
        content = twilio_adapter.download_media(media_url)

        assert content == expected_content, "Media content did not match expected content"
