from src.base_classes import AbstractEmbeddingModel, AbstractEmbeddingStrategy
from src.models.imagebind_model_wrapper import ImageBindModelWrapper as IBModelWrapper
import torch
from typing import List, Optional, Type

class EmbeddingModelFactory:
    _models = {}  # To store single instances of models

    @classmethod
    def get_model(cls, model_class: Type[AbstractEmbeddingModel]) -> AbstractEmbeddingModel:
        if model_class not in cls._models:
            cls._models[model_class] = model_class()
        return cls._models[model_class]

class ImageEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, image_path: str) -> torch.Tensor:
        return self.embedding_model.get_embeddings('image', [image_path])[0]

class TextualMetadataEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, text: str) -> torch.Tensor:
        return self.embedding_model.get_embeddings('text', [text])[0]

def generate_image_embeddings(model_class: Type[AbstractEmbeddingModel], image_paths: List[str]) -> List[torch.Tensor]:
    model = EmbeddingModelFactory.get_model(model_class)
    return model.get_embeddings('image', image_paths)

def generate_textual_embeddings(model_class: Type[AbstractEmbeddingModel], text_list: List[str]) -> List[torch.Tensor]:
    model = EmbeddingModelFactory.get_model(model_class)
    return model.get_embeddings('text', text_list)
