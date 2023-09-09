from typing import Dict, Optional
from pathlib import Path

class Artwork:
    def __init__(self, image: Path, metadata: Optional[Dict] = None):
        self.image = image
        self.metadata = metadata if metadata else {}

    def set_metadata(self, key: str, value: any):
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Optional[any]:
        return self.metadata.get(key)

    # ... other methods specific to an artwork can be added here
