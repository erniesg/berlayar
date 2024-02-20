import os
import pytest
from berlayar.config.config_loader import EnvConfigLoader

def test_env_config_loader_integration():
    key = "INTEGRATION_TEST_KEY"
    expected_value = "integration_test_value"
    os.environ[key] = expected_value  # Set environment variable
    loader = EnvConfigLoader()
    assert loader.get(key) == expected_value, "Failed to retrieve the correct value from the environment"
    del os.environ[key]  # Clean up

