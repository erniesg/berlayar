from src.base_classes import AbstractEmbeddingModel, AbstractEmbeddingStrategy
from src.models.imagebind_model_wrapper import ImageBindModelWrapper as IBModelWrapper
import torch
from typing import List, Optional, Type, Dict, Union
from imagebind.models.imagebind_model import ModalityType
from pathlib import Path

class EmbeddingModelFactory:
    _models = {}  # To store single instances of models

    @classmethod
    def get_model(cls, model_class_or_instance: Union[Type[AbstractEmbeddingModel], AbstractEmbeddingModel]) -> AbstractEmbeddingModel:
        if isinstance(model_class_or_instance, AbstractEmbeddingModel):
            # If it's already an instance, return it directly
            return model_class_or_instance

        if model_class_or_instance not in cls._models:
            cls._models[model_class_or_instance] = model_class_or_instance()

        return cls._models[model_class_or_instance]

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

class AudioEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, audio_path: str) -> torch.Tensor:
        embedding = self.embedding_model.get_embeddings('audio', [audio_path])[0]
        # Ensure the output is a 2D tensor
        if len(embedding.shape) == 1:
            embedding = embedding.unsqueeze(0)
        return embedding

def generate_embeddings(model_class: Type[AbstractEmbeddingModel],
                        image_paths: Optional[List[str]] = None,
                        text_list: Optional[List[str]] = None,
                        audio_paths: Optional[List[str]] = None) -> Dict[str, torch.Tensor]:

    model = EmbeddingModelFactory.get_model(model_class)

    inputs = {}
    if image_paths:
        inputs[ModalityType.VISION] = image_paths
    if text_list:
        inputs[ModalityType.TEXT] = text_list
    if audio_paths:
        inputs[ModalityType.AUDIO] = audio_paths

    embeddings = {}
    for modality, data_items in inputs.items():
        embeddings[modality] = model.get_embeddings(data_items, modality)

    # Print the shape of the embeddings if they exist
    if ModalityType.VISION in embeddings:
        print(f"Image Embeddings Shape in generate_embeddings: {embeddings[ModalityType.VISION].shape}")
    if ModalityType.TEXT in embeddings:
        print(f"Text Embeddings Shape in generate_embeddings: {embeddings[ModalityType.TEXT].shape}")
    if ModalityType.AUDIO in embeddings:
        print(f"Audio Embeddings Shape in generate_embeddings: {embeddings[ModalityType.AUDIO].shape}")

    print(f"Returning from generate_embeddings: {embeddings}")

    return embeddings

def get_embeddings(model: AbstractEmbeddingModel,
                   texts: Optional[List[str]] = None,
                   images: Optional[List[Path]] = None,
                   audio: Optional[List[str]] = None) -> Dict[str, torch.Tensor]:

    embeddings = {}
    if texts:
        embeddings[ModalityType.TEXT] = model.get_embeddings(texts, ModalityType.TEXT)
    if images:
        embeddings[ModalityType.VISION] = model.get_embeddings(images, ModalityType.VISION)
    if audio:
        embeddings[ModalityType.AUDIO] = model.get_embeddings(audio, ModalityType.AUDIO)

    return embeddings
