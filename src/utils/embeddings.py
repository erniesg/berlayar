from src.base_classes import AbstractEmbeddingModel, AbstractEmbeddingStrategy
from src.models.imagebind_model_wrapper import ImageBindModelWrapper as IBModelWrapper
import torch
from typing import List, Optional, Type
from imagebind.models.imagebind_model import ModalityType

class EmbeddingModelFactory:
    _models = {}  # To store single instances of models

    @classmethod
    def get_model(cls, model_class: Type[AbstractEmbeddingModel]) -> AbstractEmbeddingModel:
        if model_class not in cls._models:
            cls._models[model_class] = model_class()
        return cls._models[model_class]

class ImageEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, image_path: str) -> torch.Tensor:
        embedding = self.embedding_model.get_embeddings('image', [image_path])[0]
        # Ensure the output is a 2D tensor
        if len(embedding.shape) == 1:
            embedding = embedding.unsqueeze(0)
        return embedding

class TextualMetadataEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, text: str) -> torch.Tensor:
        embedding = self.embedding_model.get_embeddings('text', [text])[0]
        # Ensure the output is a 2D tensor
        if len(embedding.shape) == 1:
            embedding = embedding.unsqueeze(0)
        return embedding

def generate_image_embeddings(model_class: Type[AbstractEmbeddingModel], image_paths: List[str]) -> List[torch.Tensor]:
    model = EmbeddingModelFactory.get_model(model_class)
    embeddings = model.get_embeddings(image_paths, ModalityType.VISION)
    # Ensure all embeddings have a 2D shape
    return [emb.unsqueeze(0) if len(emb.shape) == 1 else emb for emb in embeddings]

def generate_textual_embeddings(model_class: Type[AbstractEmbeddingModel], text_list: List[str]) -> List[torch.Tensor]:
    model = EmbeddingModelFactory.get_model(model_class)
    embeddings = model.get_embeddings(text_list, ModalityType.TEXT)
    # Ensure all embeddings have a 2D shape
    return [emb.unsqueeze(0) if len(emb.shape) == 1 else emb for emb in embeddings]
