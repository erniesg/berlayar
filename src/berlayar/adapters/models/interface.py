from abc import ABC, abstractmethod
from typing import Dict, Any

class GenerationInterface(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, params: Dict[str, Any] = None) -> str:
        pass

    @abstractmethod
    def generate_image(self, prompt: str, params: Dict[str, Any] = None) -> str:
        pass

    @abstractmethod
    def generate_audio(self, prompt: str, params: Dict[str, Any] = None) -> str:
        pass
