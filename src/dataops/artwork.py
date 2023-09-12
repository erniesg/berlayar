from pathlib import Path
from typing import Optional, Union, Dict, List
from src.sources.img import ImageDataSource
from src.sources.spreadsheet import SpreadsheetDataSource
from src.utils.embeddings import generate_embeddings, EmbeddingModelFactory
from src.models.imagebind_model_wrapper import ImageBindModelWrapper
from src.utils.cloud import AzureBlobStorage
import deeplake
import torch
import pandas as pd
import os
from db.ops.deeplake import DeepLake

class ArtworkDataManager:

    def __init__(self, image_directory: Path, spreadsheet_path: Optional[str] = None, embedding_model: Optional[ImageBindModelWrapper] = None):
        self.image_source = ImageDataSource(image_directory)
        self.spreadsheet_source = SpreadsheetDataSource(spreadsheet_path) if spreadsheet_path else None
        self.embedding_model = embedding_model if embedding_model else EmbeddingModelFactory.get_model(ImageBindModelWrapper)
        self.vector_store = None
        self.blob_storage = None

    def ingest_data(self):
        self.image_source.ingest()
        if self.spreadsheet_source:
            self.spreadsheet_source.ingest()

    def get_image_data(self):
        return self.image_source.images

    def get_artwork_data(self, image_file: str, columns: Optional[List[str]] = None, identifier_column: Optional[str] = None, return_as_dict: bool = False):
        images = self.get_image_data()

        if not self.spreadsheet_source:
            return image_file, None

        identifier_value = image_file.stem

        if not columns:
            # If no columns are specified, fetch all columns
            columns = self.spreadsheet_source.df.columns

        metadata = {}
        for col in columns:
            value = self.spreadsheet_source.get_column(col, identifier_value, identifier_column)
            if pd.notna(value):  # only populate non-empty values
                metadata[col] = value

        return image_file, metadata

    def upload_to_blob(self, file_path: str, blob_name: str):
        if not self.blob_storage:
            self.blob_storage = AzureBlobStorage()
        self.blob_storage.upload(file_path, blob_name)

    def generate_and_store_embeddings(self, model_class, data: Union[str, Dict[str, str]], modality: str):
        if not self.vector_store:
            self.vector_store = DeepLake()

        if modality == 'image':
            embeddings_data = {'image_paths': [data]}
        elif modality == 'text':
            embeddings_data = {'text_list': [data]}
        else:
            raise ValueError(f"Unsupported modality {modality}")

        embeddings = generate_embeddings(model_class, **embeddings_data)

        # Store in Deep Lake
        for _, embedding in embeddings.items():
            add_torch_embeddings(self.vector_store, embedding)

    def store_artwork_in_deeplake(self, original_image_path: Path, weighted_embedding, metadata):
        """Store the artwork (image, embedding, and full metadata) in DeepLake."""
        if not self.vector_store:
            self.vector_store = DeepLake()

        # Convert the torch tensor to numpy for storage
        embedding_np = weighted_embedding.cpu().numpy()

        # Prepare data for appending
        data_entry = {
            "images": deeplake.read(str(original_image_path)),
            "embeddings": embedding_np,
            "metadata": metadata
        }

        # Append data to DeepLake
        self.vector_store.append(data_entry)

# Helper function to store embeddings in Deep Lake
def add_torch_embeddings(ds: deeplake.Dataset, embedding: torch.Tensor):
    # Convert torch tensor to numpy for storage in Deep Lake
    embedding_np = embedding.cpu().numpy()
    ds.append({"embeddings": embedding_np})
