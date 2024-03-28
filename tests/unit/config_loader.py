import pytest
from unittest.mock import patch
from berlayar.config.config_loader import EnvConfigLoader
import os

# Test environment variable loader
def test_env_config_loader_reads_environment_variable():
    key = "TEST_KEY"
    expected_value = "test_value"
    with patch.dict("os.environ", {key: expected_value}):
        loader = EnvConfigLoader()
        assert loader.get(key) == expected_value, "EnvConfigLoader did not load the environment variable correctly"
