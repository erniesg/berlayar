from pathlib import Path
from typing import Optional
from src.sources.img import ImageDataSource
from src.sources.spreadsheet import SpreadsheetDataSource

class ArtworkDataManager:
    def __init__(self, image_directory: Path, spreadsheet_path: str):
        self.image_source = ImageDataSource(image_directory)
        self.spreadsheet_source = SpreadsheetDataSource(spreadsheet_path)

    def ingest_data(self):
        self.image_source.ingest()
        self.spreadsheet_source.ingest()

    def get_image_data(self):
        return self.image_source.images

    def get_spreadsheet_data(self, column_name: Optional[str] = None):
        if column_name:
            return self.spreadsheet_source.get_column(column_name)
        else:
            return self.spreadsheet_source.get_metadata()

    def get_artwork_data(self, column_name: Optional[str] = None):
        images = self.get_image_data()
        metadata = self.get_spreadsheet_data(column_name)
        return images, metadata

    # Additional methods to process and generate embeddings can be added here
