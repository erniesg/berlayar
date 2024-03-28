import importlib
import logging
from berlayar.config.config_loader import ModelConfigLoader
from berlayar.utils.load_keys import get_api_key

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ContentStrategyRegistry:
    def __init__(self):
        self.model_config_loader = ModelConfigLoader()
        logger.debug("ContentStrategyRegistry initialized")

    def get_adapter(self, content_type: str, language: str = 'en'):
        logger.debug(f"Getting adapter for content_type: {content_type}, language: {language}")
        model_config = self.model_config_loader.get(content_type, language)
        if not model_config:
            logger.error(f"No configuration found for content_type: {content_type}, language: {language}")
            raise ValueError(f"No configuration found for content_type: {content_type}, language: {language}")

        adapter_path = model_config.pop('adapter')
        api_key_env = model_config.pop('api_key_env', None)
        api_key = get_api_key(api_key_env) if api_key_env else None

        # Remove the api_key_env from the model_config as it's already used to get the api_key
        model_config.pop('api_key_env', None)  # Ensure it's removed if present

        logger.debug(f"Adapter path: {adapter_path}, API key env: {api_key_env}")
        AdapterClass = self._dynamic_import(adapter_path)
        # Pass the entire model_config as **kwargs to the adapter constructor.
        return AdapterClass(api_key=api_key, **model_config)

    def _dynamic_import(self, path):
        logger.debug(f"Dynamically importing {path}")
        module_path, class_name = path.rsplit('.', 1)
        try:
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except ImportError as e:
            logger.error(f"Error importing module {module_path}: {e}")
            raise
        except AttributeError as e:
            logger.error(f"Error accessing class {class_name} in module {module_path}: {e}")
            raise

    def generate_text(self, prompt: str, language: str = 'en', params: dict = None):
        if not prompt:
            logger.error("Prompt cannot be empty")
            raise ValueError("Prompt cannot be empty")

        logger.debug(f"Generating text for prompt: {prompt}, language: {language}, params: {params}")
        adapter = self.get_adapter('text_generation', language)

        # Fetch the default parameters from the configuration directly
        model_config = self.model_config_loader.get('text_generation', language)
        # Ensure api_key_env and adapter are not passed as parameters
        model_config.pop('api_key_env', None)
        model_config.pop('adapter', None)

        # Merge the configuration defaults with the provided params
        final_params = {**model_config, **(params or {})}
        return adapter.generate_text(prompt, **final_params)
