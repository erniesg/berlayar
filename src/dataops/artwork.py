from pathlib import Path
from typing import Optional, Union, Dict, List
from src.sources.img import ImageDataSource
from src.sources.spreadsheet import SpreadsheetDataSource
from src.utils.embeddings import generate_image_embeddings, generate_textual_embeddings, EmbeddingModelFactory
from src.utils.cloud import AzureBlobStorage
import deeplake
import torch

class ArtworkDataManager:
    def __init__(self, image_directory: Path, spreadsheet_path: Optional[str] = None):
        self.image_source = ImageDataSource(image_directory)
        if spreadsheet_path:
            self.spreadsheet_source = SpreadsheetDataSource(spreadsheet_path)
        else:
            self.spreadsheet_source = None
        self.blob_storage = AzureBlobStorage()

    def ingest_data(self):
        self.image_source.ingest()
        if self.spreadsheet_source:
            self.spreadsheet_source.ingest()

    def get_image_data(self):
        return self.image_source.images

    def get_artwork_data(self, image_file: str, columns: Optional[List[str]] = None, identifier_column: Optional[str] = None, return_as_dict: bool = False):
        images = self.get_image_data()

        if not self.spreadsheet_source:
            return images, None

        if columns:
            if return_as_dict:
                metadata = {col: {col: self.spreadsheet_source.get_column(col, image_file[:-4], identifier_column)} for col in columns}
            else:
                metadata = {col: self.spreadsheet_source.get_column(col, image_file[:-4], identifier_column) for col in columns}
        else:
            metadata = self.spreadsheet_source.get_row(image_file[:-4], identifier_column, return_as_dict)
        return images, metadata

    def upload_to_blob(self, file_path: str, blob_name: str):
        self.blob_storage.upload(file_path, blob_name)

    def generate_and_store_embeddings(self, model_class, data: Union[str, Dict[str, str]], modality: str, ds: deeplake.Dataset):
        if modality == 'image':
            embeddings = generate_image_embeddings(model_class, [data])
        elif modality == 'text':
            embeddings = generate_textual_embeddings(model_class, [data])
        else:
            raise ValueError(f"Unsupported modality {modality}")

        # Store in Deep Lake
        for embedding in embeddings:
            add_torch_embeddings(ds, embedding)

# Helper function to store embeddings in Deep Lake
def add_torch_embeddings(ds: deeplake.Dataset, embedding: torch.Tensor):
    # Convert torch tensor to numpy for storage in Deep Lake
    embedding_np = embedding.cpu().numpy()
    ds.append({"embeddings": embedding_np})
