import unittest
import os
from pathlib import Path
from dotenv import load_dotenv
from src.dataops.artwork import ArtworkDataManager
from src.models.imagebind_model_wrapper import ImageBindModelWrapper
from src.utils.embeddings import generate_image_embeddings, generate_textual_embeddings
from src.utils.embeddings_weighting import compute_weighted_embeddings
import random
import torch

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

FIXTURES_PATH = Path(os.environ.get("FIXTURES_PATH"))

class ArtworkEmbeddingTest(unittest.TestCase):

    def setUp(self):
        # Initialize and ingest data
        self.artwork_manager = ArtworkDataManager(FIXTURES_PATH / "ngs", FIXTURES_PATH / "artworks.xlsx")
        self.artwork_manager.ingest_data()

        # Sample 10 random images
        all_images = list((FIXTURES_PATH / "ngs").iterdir())
        self.sampled_images = random.sample(all_images, 3)

    def test_weighted_embeddings(self):
        for image in self.sampled_images:
            _, metadata = self.artwork_manager.get_artwork_data(image, return_as_dict=True)
            image_embedding = generate_image_embeddings(ImageBindModelWrapper, [image])[0]
            metadata_embedding = None
            if "Artist/Maker" in metadata:
                metadata_embedding = generate_textual_embeddings(ImageBindModelWrapper, [metadata["Artist/Maker"]])[0]

            weighted_embedding, weights = compute_weighted_embeddings(image_embedding, metadata_embedding, metadata)

            # Displaying the weights
            print(f"\nArtwork: {image.stem}")
            print(f"Value of image_weight: {weights['image_weight']:.2f}")
            print(f"Value of metadata_weight: {weights['metadata_weight']:.2f}")
            print(f"Shape of weighted_embedding tensor: {weighted_embedding.shape}")

            # You can add further assertions based on what you expect the weights to be, for a more robust test

if __name__ == "__main__":
    unittest.main()
