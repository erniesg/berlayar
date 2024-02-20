import pytest
from berlayar.config.google_secrets import GoogleSecretsConfigLoader

# This test requires valid Google Cloud credentials and a test secret in Secret Manager
@pytest.mark.skip(reason="Requires Google Cloud credentials and setup")
def test_google_secrets_config_loader_integration():
    project_id = "your_test_project_id"
    secret_id = "your_test_secret_id"
    expected_value = "secret_value"  # Ensure this is the value of your_test_secret_id in Secret Manager
    loader = GoogleSecretsConfigLoader(project_id=project_id)
    assert loader.get(secret_id) == expected_value, "Failed to retrieve the correct value from Google Secrets Manager"

