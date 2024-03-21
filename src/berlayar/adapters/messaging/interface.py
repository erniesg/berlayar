#berlayar/adapters/messaging/interface.py
from abc import ABC, abstractmethod

class MessagingInterface(ABC):
    @abstractmethod
    async def send_message(self, recipient: str, message_body: str) -> bool:
        pass

    @abstractmethod
    async def send_media(self, recipient: str, media_url: str) -> bool:
        pass

    @abstractmethod
    async def receive_message(self, request_body: dict) -> dict:
        pass

    @abstractmethod
    async def receive_media(self, request_body: dict) -> dict:
        pass

    @abstractmethod
    async def download_media(self, media_url: str, destination_path: str) -> bool:
        pass
