import unittest
import pandas as pd
from src.dataops.artwork import ArtworkDataManager
from pathlib import Path
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

FIXTURES_PATH = Path(os.environ.get("FIXTURES_PATH"))

class TestArtworkDataManager(unittest.TestCase):

    def setUp(self):
        self.image_directory = FIXTURES_PATH / "ngs"
        self.spreadsheet_path = FIXTURES_PATH / "artworks.xlsx"
        self.artwork_manager = ArtworkDataManager(self.image_directory, self.spreadsheet_path)
        self.artwork_manager.ingest_data()

    def test_directory_of_images(self):
        images = list(self.image_directory.glob("*.jpg"))
        print(f"\nNumber of images in directory: {len(images)}")

    def test_image_only(self):
        images = self.artwork_manager.get_image_data()
        for image_path in images:
            with Image.open(image_path) as img:
                width, height = img.size
                print(f"\nImage {image_path.name} dimensions: {width}x{height}")

    def test_image_with_specific_column(self):
        images, metadata_dict = self.artwork_manager.get_artwork_data(Path("1991-00226.jpg"), columns=["Artist/Maker"])
        print(f"\nMetadata Type: {type(metadata_dict)}")
        print(f"Metadata Content: {metadata_dict}")
        self.assertIn("Artist/Maker", metadata_dict)

    def test_image_with_multiple_columns(self):
        columns_to_fetch = ["Artist/Maker", "Dating"]
        images, metadata_dict = self.artwork_manager.get_artwork_data(Path("1991-00226.jpg"), columns=columns_to_fetch)
        print(f"\nMetadata Type: {type(metadata_dict)}")
        print(f"Metadata Content: {metadata_dict}")
        for col in columns_to_fetch:
            self.assertIn(col, metadata_dict)

    def test_image_with_entire_row(self):
        images, metadata_dict = self.artwork_manager.get_artwork_data(Path("1991-00226.jpg"))
        spreadsheet_data = pd.read_excel(self.spreadsheet_path)
        identifier = "1991-00226"
        matched_row = spreadsheet_data[spreadsheet_data["Accession No."] == identifier].iloc[0]
        print(f"\nMetadata Type: {type(metadata_dict)}")
        print(f"Metadata Content: {metadata_dict}")
        for column in spreadsheet_data.columns:
            if pd.notna(matched_row[column]):  # Ignore NaN values
                self.assertIn(column, metadata_dict)
                self.assertEqual(matched_row[column], metadata_dict[column])

    def test_image_with_key_value_pairs(self):
        images, metadata_dict = self.artwork_manager.get_artwork_data(Path("1991-00226.jpg"), return_as_dict=True)
        spreadsheet_data = pd.read_excel(self.spreadsheet_path)
        identifier = "1991-00226"
        matched_row = spreadsheet_data[spreadsheet_data["Accession No."] == identifier].iloc[0]
        print(f"\nMetadata Type: {type(metadata_dict)}")
        print(f"Metadata Content: {metadata_dict}")
        for column, value in metadata_dict.items():
            if pd.notna(matched_row[column]):  # Ignore NaN values
                self.assertEqual(matched_row[column], value)

if __name__ == '__main__':
    unittest.main()
