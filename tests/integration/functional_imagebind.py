import unittest
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

from src.models.imagebind_model_wrapper import ImageBindModelWrapper, ModalityType
from src.sources.img import ImageDataSource
from src.sources.spreadsheet import SpreadsheetDataSource

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

FIXTURES_PATH = Path(os.environ.get("FIXTURES_PATH"))
IMAGE_PATH = FIXTURES_PATH / 'ngs'
SPREADSHEET_PATH = FIXTURES_PATH / 'artworks.xlsx'

class TestImageBindIntegration(unittest.TestCase):

    def setUp(self):
        self.img_data_source = ImageDataSource(IMAGE_PATH)
        self.spreadsheet_data_source = SpreadsheetDataSource(SPREADSHEET_PATH)

        # Explicitly ingest the data
        self.img_data_source.ingest()
        self.spreadsheet_data_source.ingest()

        # Initialize the ImageBindModelWrapper
        self.wrapper = ImageBindModelWrapper()

    def test_generate_embeddings(self):
        # Generate embeddings for a single sampled image
        sampled_image = [self.img_data_source.images[0]]
        image_embeddings = self.wrapper.get_embeddings(sampled_image, ModalityType.VISION)

        self.assertTrue(image_embeddings.shape[0] == 1, "Incorrect number of image embeddings generated.")
        self.assertTrue(image_embeddings.shape[1] > 0, "Embedding dimensions not expected.")
        print(f"Generated image embeddings for 1 image.")

        # Load the ingested spreadsheet and sample 1 row
        df = pd.read_excel(self.spreadsheet_data_source.path)
        sampled_row = df.sample(n=1)

        # Generate text embeddings for the sampled row
        text_embeddings = []
        for _, row in sampled_row.iterrows():
            for col in df.columns:
                text = str(row[col])  # Convert to string in case of any non-string data
                if text and text != "nan":  # Check if cell is not empty
                    embedding = self.wrapper.get_embeddings([text], ModalityType.TEXT)
                    text_embeddings.append(embedding)

        self.assertTrue(len(text_embeddings) > 0, "No text embeddings generated.")
        print(f"Generated text embeddings for {len(text_embeddings)} text samples.")

if __name__ == '__main__':
    unittest.main()
