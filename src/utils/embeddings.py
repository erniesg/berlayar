from src.base_classes import AbstractEmbeddingModel, AbstractEmbeddingStrategy
import torch
from typing import List, Optional

class ImageBindModelWrapper(AbstractEmbeddingModel):

    # ... other methods ...

    def get_embeddings(self, modality: str, data: List[str]) -> torch.Tensor:
        if modality == 'image':
            return self.get_image_embeddings(data)
        elif modality == 'text':
            return self.get_text_embeddings(data)
        else:
            raise ValueError(f"Unsupported modality {modality}")

class ImageEmbeddings(AbstractEmbeddingStrategy):

    def embed(self, image_path: str) -> torch.Tensor:
        return self.embedding_model.get_embeddings('image', [image_path])[0]

class TextualMetadataEmbeddings(AbstractEmbeddingStrategy):

    def embed(self, text: str) -> torch.Tensor:
        return self.embedding_model.get_embeddings('text', [text])[0]

def generate_image_embeddings(model: ImageBindModelWrapper, image_paths: List[str]) -> List[torch.Tensor]:
    return model.get_image_embeddings(image_paths)

def generate_textual_embeddings(model: ImageBindModelWrapper, text_list: List[str]) -> List[torch.Tensor]:
    return model.get_text_embeddings(text_list)
