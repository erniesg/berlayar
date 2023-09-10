from typing import Dict, Optional, Union
from pathlib import Path
import uuid

class Item:
    def __init__(self, content: Union[Path, str], metadata: Optional[Dict[str, Union[str, int, float]]] = None, embeddings: Optional[Dict[str, Union[Dict[str, float], float]]] = None, item_id: Optional[str] = None):
        self.item_id = item_id if item_id else str(uuid.uuid4())  # Use provided ID or generate a new UUID.
        self.content = content   # This can be a path to an image/video/audio, or raw text.
        self.metadata = metadata if metadata else {}
        self.embeddings = embeddings if embeddings else {}

    def set_metadata(self, key: str, value: any):
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Optional[any]:
        return self.metadata.get(key)

    def set_embedding(self, model_name: str, embedding: Union[Dict[str, float], float]):
        self.embeddings[model_name] = embedding

    def get_embedding(self, model_name: str) -> Optional[Union[Dict[str, float], float]]:
        return self.embeddings.get(model_name)

    # ... other methods specific to an item can be added here
