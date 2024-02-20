# Inside src/berlayar/utils/common.py
from berlayar.config.config_loader import ConfigLoader, EnvConfigLoader
from berlayar.config.google_secrets import GoogleSecretsConfigLoader
import os
# Import other secret managers as needed

def get_config_loader() -> ConfigLoader:
    # Example: Determine source from an environment variable
    source = os.getenv("CONFIG_SOURCE", "env").lower()
    if source == "google_secrets":
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        return GoogleSecretsConfigLoader(project_id=project_id)
    # Add more elif blocks for other sources like Azure, AWS, etc.
    else:
        return EnvConfigLoader()

