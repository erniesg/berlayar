import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod

class ConfigLoader(ABC):
    @abstractmethod
    def get(self, key: str) -> str:
        pass

class EnvConfigLoader(ConfigLoader):
    def __init__(self):
        load_dotenv()

    def get(self, key: str) -> str:
        return os.getenv(key)

