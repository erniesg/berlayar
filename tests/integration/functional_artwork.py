import unittest
import os
from pathlib import Path
from dotenv import load_dotenv
from src.dataops.artwork import ArtworkDataManager
from src.models.imagebind_model_wrapper import ImageBindModelWrapper
from src.utils.embeddings import generate_image_embeddings, generate_textual_embeddings
import torch

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

FIXTURES_PATH = Path(os.environ.get("FIXTURES_PATH"))

class ArtworkEmbeddingTest(unittest.TestCase):

    def setUp(self):
        self.image_directory = FIXTURES_PATH / "ngs"
        self.spreadsheet_path = FIXTURES_PATH / "artworks.xlsx"
        self.artwork_manager = ArtworkDataManager(self.image_directory, self.spreadsheet_path)

    def test_generate_image_and_text_embeddings(self):
        # Ingest data
        self.artwork_manager.ingest_data()

        # Get image and text data for the test
        test_image_file = "1991-00226.jpg"
        print(f"\nImage File: {test_image_file}")

        # Using ArtworkDataManager methods to fetch required data based on the identifier "Accession No."
        metadata = self.artwork_manager.get_spreadsheet_data("Artist/Maker", as_dict=True, identifier_column="Accession No.")
        print(metadata)
        print(type(metadata))
        artist_maker_value = metadata[test_image_file[:-4]]
        print(f"Artist/Maker Value: {artist_maker_value}")

        # Generate embeddings
        image_embeddings = generate_image_embeddings(ImageBindModelWrapper, [test_image_file])
        text_embeddings = generate_textual_embeddings(ImageBindModelWrapper, [artist_maker_value])

        # Validate embeddings
        self._print_and_validate_embeddings(image_embeddings, "Image Embeddings")
        self._print_and_validate_embeddings(text_embeddings, "Text Embeddings")

    def _print_and_validate_embeddings(self, embeddings: torch.Tensor, label: str):
        print(f"\n{label}")
        print("Type:", type(embeddings[0]))
        print("Shape:", embeddings[0].shape)
        print("Truncated Data:", embeddings[0][:5])  # Assuming the embeddings might be very long, just displaying the first 5 elements

        self.assertIsInstance(embeddings[0], torch.Tensor)
        self.assertTrue(len(embeddings[0].shape) == 2)  # Ensure it's a 2D tensor
        self.assertTrue(embeddings[0].shape[1] > 0)     # Ensure there's a dimension for embeddings

if __name__ == "__main__":
    unittest.main()
