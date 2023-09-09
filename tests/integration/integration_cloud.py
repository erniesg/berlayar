import unittest
from src.sources.img import ImageDataSource
from src.sources.spreadsheet import SpreadsheetDataSource
from src.processors.img import ImageFileProcessor
from src.utils.cloud import AzureBlobStorage
from src.utils.helpers import validate_azure_connection  # Import the validation function
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

class TestIntegration(unittest.TestCase):

    def setUp(self):
        print("\nSetting up for the test...")
        # Validate Azure connection and subscription
        if not validate_azure_connection():
            # Handle the case where Azure login fails
            raise RuntimeError("Azure login and subscription validation failed.")

        # Setting up DataSource and Processor
        self.img_data_source = ImageDataSource(IMAGE_PATH)
        self.spreadsheet_data_source = SpreadsheetDataSource(SPREADSHEET_PATH)
        self.img_processor = ImageFileProcessor()

        # Setting up Azure Blob Storage
        self.storage = AzureBlobStorage()

    def test_integration(self):
        # 1. Ingest data
        print("Ingesting data from sources...")
        images = self.img_data_source.ingest()  # Changed .read() to .ingest()
        data = self.spreadsheet_data_source.ingest()

        # 2. Process data
        print("Processing images...")
        processed_images = self.img_processor.process(images)

        # 3. Upload processed images to Azure Blob Storage
        print("Uploading images to Azure Blob Storage...")
        for img in processed_images:
            blob_name = os.path.basename(img)
            self.storage.upload(img, blob_name)

        # Assert: Ensure the files are in Azure Blob Storage
        print("Verifying uploaded images in Azure Blob Storage...")
        uploaded_files = self.storage.list_objects()
        self.assertCountEqual([os.path.basename(img) for img in processed_images], uploaded_files)

    def tearDown(self):
        # Cleanup: Delete the test files from Azure Blob Storage
        print("Cleaning up: Deleting test files from Azure Blob Storage...")
        uploaded_files = self.storage.list_objects()
        for file in uploaded_files:
            self.storage.delete(file)

if __name__ == '__main__':
    unittest.main()
