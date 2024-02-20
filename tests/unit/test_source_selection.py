import pytest
from unittest.mock import Mock, patch
from berlayar.utils.common import get_config_loader
from berlayar.config.config_loader import EnvConfigLoader
from berlayar.config.google_secrets import GoogleSecretsConfigLoader
import os

# Mock implementations for testing
class MockEnvConfigLoader(EnvConfigLoader):
    pass

class MockGoogleSecretsConfigLoader(GoogleSecretsConfigLoader):
    pass

@patch('berlayar.utils.common.EnvConfigLoader', MockEnvConfigLoader)
@patch('berlayar.utils.common.GoogleSecretsConfigLoader', MockGoogleSecretsConfigLoader)
def test_correct_loader_selected_based_on_env_variable():
    with patch.dict("os.environ", {"CONFIG_SOURCE": "google_secrets", "GOOGLE_CLOUD_PROJECT": "test_project"}):
        loader = get_config_loader()
        assert isinstance(loader, MockGoogleSecretsConfigLoader), "GoogleSecretsConfigLoader should be selected for CONFIG_SOURCE=google_secrets"

    with patch.dict("os.environ", {"CONFIG_SOURCE": "env"}):
        loader = get_config_loader()
        assert isinstance(loader, MockEnvConfigLoader), "EnvConfigLoader should be selected for CONFIG_SOURCE=env"
