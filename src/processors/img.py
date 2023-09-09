from src.base_classes import FileProcessor
from pathlib import Path
import os
from PIL import Image
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
PROCESSED_DIR = Path(os.environ.get("PROCESSED_IMAGE_DIR"))

class ImageFileProcessor(FileProcessor):
    PROCESSED_DIR = PROCESSED_DIR
    def process(self, file_path, *args, **kwargs):
        # Logic to preprocess and maybe also generate embeddings for images.
        resized_image_path = self.resize_image(file_path)
        # You can further extend this to generate embeddings or any other operations.
        return resized_image_path

    def resize_image(self, image_path):
        '''Resize a single image to 256x256
        Args:
            image_path: source image path
        Returns:
            resized_image_path: path to the resized image
        '''
        image = Image.open(image_path)
        image = image.resize((256, 256), Image.LANCZOS)
        resized_image_path = PROCESSED_DIR / Path(image_path).name
        if not resized_image_path.parent.exists():
            resized_image_path.parent.mkdir(parents=True)
        image.save(resized_image_path)
        return resized_image_path

    def resize_images(self, input_dir: Path, output_dir: Path = None):
        """
        Resize images from the input directory and save them to the output directory.

        Args:
            input_dir (Path): Directory containing the images to be resized.
            output_dir (Path): Directory where resized images will be saved. Defaults to None.

        Returns:
            str: Message indicating the number of images processed.
        """
        if output_dir is None:
            output_dir = PROCESSED_DIR / input_dir.name

        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        counter = 0
        for image_path in tqdm(list(input_dir.glob("*"))):
            with Image.open(image_path) as img:
                resized_img = img.resize((256, 256), Image.LANCZOS)
                resized_img.save(output_dir / image_path.name)
                counter += 1

        return f"{counter} images resized and saved to {output_dir}"
