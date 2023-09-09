import unittest
from pathlib import Path
from PIL import Image
import tempfile
from src.processors.img import ImageFileProcessor

class TestImageFileProcessor(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a sample image
        img = Image.new('RGB', (512, 512), color = (73, 109, 137))
        self.sample_image_path = self.temp_path / "sample.jpg"
        img.save(self.sample_image_path)

        # Initialize ImageFileProcessor
        self.processor = ImageFileProcessor()

    def tearDown(self):
        # Clean up and remove the temporary directory
        self.temp_dir.cleanup()

    def test_resize_image(self):
        resized_image_path = self.processor.resize_image(self.sample_image_path)
        with Image.open(resized_image_path) as img:
            self.assertEqual(img.size, (256, 256), "Image was not resized to the expected dimensions.")

    def test_resize_images(self):
        # Create a few more sample images for batch processing
        for i in range(5):
            img = Image.new('RGB', (512, 512), color = (i*50, i*10, 137))
            img.save(self.temp_path / f"sample_{i}.jpg")

        result_message = self.processor.resize_images(self.temp_path)
        expected_message = f"6 images resized and saved to {self.processor.PROCESSED_DIR / self.temp_path.name}"
        self.assertEqual(result_message, expected_message, "Unexpected result message from resize_images.")

        # Check if all images in the output directory are of size 256x256
        output_dir = self.processor.PROCESSED_DIR / self.temp_path.name
        for image_path in output_dir.glob("*"):
            with Image.open(image_path) as img:
                self.assertEqual(img.size, (256, 256), f"Image {image_path.name} was not resized to the expected dimensions.")

if __name__ == '__main__':
    unittest.main()
