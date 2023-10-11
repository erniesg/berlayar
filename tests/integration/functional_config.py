import pytest
from berlayar import config

def test_config_values():
    assert config.OPENAI_API_KEY is not None, "OPENAI_API_KEY is not set!"
    assert config.ACTIVELOOP_TOKEN is not None, "ACTIVELOOP_TOKEN is not set!"
    assert config.HUGGINGFACE_TOKEN is not None, "HUGGINGFACE_TOKEN is not set!"
    assert config.EMAIL_PASSWORD is not None, "EMAIL_PASSWORD is not set!"
    assert config.GITHUB_TOKEN is not None, "GITHUB_TOKEN is not set!"
    assert config.GITHUB_TEST_TOKEN is not None, "GITHUB_TEST_TOKEN is not set!"
    assert config.AZURE_STORAGE_CONNECTION_STRING is not None, "AZURE_STORAGE_CONNECTION_STRING is not set!"
    assert config.AZURE_SUBSCRIPTION_ID is not None, "AZURE_SUBSCRIPTION_ID is not set!"
    # Add similar checks for other keys

    # Check paths or other non-secret values
    assert config.JSON_PATH is not None, "JSON_PATH is not set!"
    assert config.DEEPLAKE_PATH is not None, "DEEPLAKE_PATH is not set!"
    assert config.CLONE_PATH is not None, "CLONE_PATH is not set!"
    # Add more tests for the other configurations

    # You can also add more granular checks or even check if the values are valid (e.g., valid connection strings)
