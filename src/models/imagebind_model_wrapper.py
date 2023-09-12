from imagebind import data
from imagebind.models import imagebind_model
from imagebind.models.imagebind_model import ModalityType
import torch
from typing import List, Union
from src.base_classes import AbstractEmbeddingModel
import os
import dotenv

dotenv.load_dotenv()

# Load BPE_PATH from environment variables
BPE_PATH = os.environ.get("BPE_PATH")

# Override BPE_PATH in ImageBind's data module
data.BPE_PATH = BPE_PATH

class ImageBindModelWrapper(AbstractEmbeddingModel):

    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = imagebind_model.imagebind_huge(pretrained=True).to(self.device).eval()

    def get_embeddings(self, data: Union[List[str], List[torch.Tensor]], modality: ModalityType) -> torch.Tensor:
        print(f"Invoking get_embeddings with modality: {modality}")

        if modality == ModalityType.VISION:
            return self.get_image_embeddings(data)
        elif modality == ModalityType.TEXT:
            return self.get_text_embeddings(data)
        elif modality == ModalityType.AUDIO:
            return self.get_audio_embeddings(data)
        else:
            raise ValueError(f"Unsupported modality: {modality}")

    def get_image_embeddings(self, image_paths: List[str]) -> torch.Tensor:
        print("Invoking get_image_embeddings")

        inputs = {ModalityType.VISION: data.load_and_transform_vision_data(image_paths, self.device)}
        with torch.no_grad():
            embeddings = self.model(inputs)[ModalityType.VISION]

        print(f"Image Embeddings Shape Before: {embeddings.shape}")
        if len(embeddings.shape) == 1:
            embeddings = embeddings.unsqueeze(0)
        print(f"Image Embeddings Shape After: {embeddings.shape}")

        return embeddings

    def get_text_embeddings(self, texts: List[str]) -> torch.Tensor:
        print("Invoking get_text_embeddings")

        inputs = {ModalityType.TEXT: data.load_and_transform_text(texts, self.device)}
        with torch.no_grad():
            embeddings = self.model(inputs)[ModalityType.TEXT]

        print(f"Text Embeddings Shape Before: {embeddings.shape}")
        if len(embeddings.shape) == 1:
            embeddings = embeddings.unsqueeze(0)
        print(f"Text Embeddings Shape After: {embeddings.shape}")

        return embeddings

    def get_audio_embeddings(self, audio_paths: List[str]) -> torch.Tensor:
        print("Invoking get_audio_embeddings")

        inputs = {ModalityType.AUDIO: data.load_and_transform_audio_data(audio_paths, self.device)}
        with torch.no_grad():
            embeddings = self.model(inputs)[ModalityType.AUDIO]

        print(f"Audio Embeddings Shape Before: {embeddings.shape}")
        if len(embeddings.shape) == 1:
            embeddings = embeddings.unsqueeze(0)
        print(f"Audio Embeddings Shape After: {embeddings.shape}")

        return embeddings

    def compare_embeddings(self, embeddings1: torch.Tensor, embeddings2: torch.Tensor) -> torch.Tensor:
        return torch.softmax(embeddings1 @ embeddings2.T, dim=-1)
