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
    print(f"Calling sync_wrapper for function: {async_func.__name__}")  # Print the name of the async function

    if not asyncio.iscoroutinefunction(async_func):
        raise TypeError("Expected an async function")

    print("sync_wrapper: async function verified.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(async_func(*args, **kwargs))
        print("sync_wrapper: Successfully executed the async function.")
    except Exception as e:
        print("sync_wrapper: Exception occurred during execution:", e)
        raise  # Re-raise the exception for proper error handling
    finally:
        loop.close()

    return result
