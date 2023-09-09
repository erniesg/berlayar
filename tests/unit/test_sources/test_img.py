import unittest
from pathlib import Path
from PIL import Image
import tempfile
from src.sources.img import ImageDataSource

class TestImageDataSource(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a sample image
        img = Image.new('RGB', (512, 512), color = (73, 109, 137))
        self.sample_image_path = self.temp_path / "sample.jpg"
        img.save(self.sample_image_path)

        # Initialize ImageDataSource
        self.datasource = ImageDataSource(self.temp_path)

    def tearDown(self):
        # Clean up and remove the temporary directory
        self.temp_dir.cleanup()

    def test_ingest(self):
        self.datasource.ingest()
        self.assertIsNotNone(self.datasource.images, "Images not ingested correctly.")
        self.assertEqual(len(self.datasource.images), 1, "Incorrect number of images ingested.")

    def test_get_metadata(self):
        self.datasource.ingest()
        metadata = self.datasource.get_metadata()
        self.assertTrue("sample.jpg" in metadata, "Metadata for sample.jpg not found.")
        self.assertEqual(metadata["sample.jpg"]["dimensions"], (512, 512), "Incorrect image dimensions in metadata.")
        self.assertEqual(metadata["sample.jpg"]["format"], "JPEG", "Incorrect image format in metadata.")

if __name__ == '__main__':
    unittest.main()
