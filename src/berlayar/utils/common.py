# berlayar/utils/common.py

from berlayar.config.config_loader import ConfigLoader, EnvConfigLoader
from berlayar.config.google_secrets import GoogleSecretsConfigLoader
import os
import asyncio

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

def sync_wrapper(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_func(*args, **kwargs))
    loop.close()
    return result
