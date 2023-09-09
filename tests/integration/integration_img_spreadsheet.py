import unittest
from src.sources.img import ImageDataSource
from src.sources.spreadsheet import SpreadsheetDataSource
from src.processors.img import ImageFileProcessor
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
FIXTURES_PATH = Path(os.environ.get("FIXTURES_PATH"))
IMAGE_PATH = FIXTURES_PATH / 'ngs'
SPREADSHEET_PATH = FIXTURES_PATH / 'artworks.xlsx'
PROCESSED_DIR = Path(os.environ.get("PROCESSED_IMAGE_DIR"))

class TestImgSpreadsheetIntegration(unittest.TestCase):

    def setUp(self):
        print("Setting up the test...")
        self.img_data_source = ImageDataSource(IMAGE_PATH)
        self.spreadsheet_data_source = SpreadsheetDataSource(SPREADSHEET_PATH)
        self.image_processor = ImageFileProcessor()
        self.original_files = set(PROCESSED_DIR.glob("*"))

        # Explicitly ingest the data
        self.img_data_source.ingest()
        self.spreadsheet_data_source.ingest()

    def tearDown(self):
        print("Tearing down the test...")
        # Remove any new files that were added during the test
        for f in PROCESSED_DIR.glob("*"):
            if f not in self.original_files:
                f.unlink()

    def test_image_resize_and_metadata_integration(self):
        try:
            print("Setting up the test...")
            print("Resizing images...")
            resized_image_paths = [self.image_processor.resize_image(img_path) for img_path in self.img_data_source.images]
            resized_image_filenames = [img.stem for img in resized_image_paths]

            print("Getting ID columns from the spreadsheet...")
            id_columns = self.spreadsheet_data_source.get_id_column()

            print("Checking accession numbers match...")
            matched_ids = [id_col for id_col in id_columns if id_col in resized_image_filenames]
            unmatched_ids = [id_col for id_col in id_columns if id_col not in resized_image_filenames]

            print(f"Total matched IDs: {len(matched_ids)}")
            print(f"Total unmatched IDs: {len(unmatched_ids)}")

            # Ensure at least one image is matched to an ID
            self.assertGreater(len(matched_ids), 0, "No IDs matched!")

        except ValueError as e:
            self.fail(f"Failed due to error: {e}")

if __name__ == '__main__':
    unittest.main()
