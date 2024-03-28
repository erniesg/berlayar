import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from berlayar.utils.path import construct_path_from_root
import yaml

class ConfigLoader(ABC):
    @abstractmethod
    def get(self, key: str) -> str:
        pass

class EnvConfigLoader(ConfigLoader):
    def __init__(self):
        load_dotenv()

    def get(self, key: str) -> str:
        return os.getenv(key)

class ModelConfigLoader:
    def __init__(self):
        self.model_configs = self._load_model_configs()

    def _load_model_configs(self):
        model_config_path = construct_path_from_root('src/berlayar/config/models.yaml')
        with open(model_config_path, 'r') as file:
            model_configs = yaml.safe_load(file)
        return model_configs

    def get(self, content_type: str, language: str = 'en') -> dict:
        # Attempt to load the configuration for the specified language
        config = self.model_configs.get(content_type, {}).get(language)
        if config is None and language != 'en':
            # If not found and the language is not English, fall back to English
            config = self.model_configs.get(content_type, {}).get('en')
        if config is None:
            # If no configuration is found, raise an error or handle it accordingly
            raise ValueError(f"No configuration found for content_type: {content_type}, language: {language}")
        return config
