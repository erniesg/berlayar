from pathlib import Path
import os
from PIL import Image
import numpy as np
from dotenv import load_dotenv
from src.base_classes import DataSource
from typing import List

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
IMAGE_DIR = Path(os.environ.get("IMAGE_DIR"))

def load_images_from_directory(directory: Path) -> List[np.array]:
    """
    Load images from a directory into a list of numpy arrays.

    Args:
        directory (Path): Directory containing the images.

    Returns:
        List[np.array]: List of images as numpy arrays.
    """
    images = []
    for image_path in directory.glob("*"):
        if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:  # Only process common image file types
            with Image.open(image_path) as img:
                images.append(np.array(img))
        else:
            raise ValueError(f"Unexpected file type {image_path.suffix} encountered in the image directory.")
    return images

class ImageDataSource(DataSource):
    def __init__(self, directory=IMAGE_DIR):
        self.directory = directory
        self.images = None
        self.metadata = {}

    def ingest(self) -> List[Path]:
        """
        Ingests images and store their paths and filenames.
        """
        self.images = [img_path for img_path in self.directory.glob("*") if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        return self.images

    def get_metadata(self):
        """
        Extract metadata specific to images.
        """
        # For the sake of simplicity, we will only extract image dimensions and formats.
        # This can be expanded upon.
        for image_path in self.directory.glob("*"):
            with Image.open(image_path) as img:
                self.metadata[image_path.name] = {"dimensions": img.size, "format": img.format}
        return self.metadata
