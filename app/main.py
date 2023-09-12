import os
from pathlib import Path
from dotenv import load_dotenv
from src.dataops.artwork import ArtworkDataManager
from src.utils.embeddings_weighting import compute_weighted_embeddings
from src.utils.embeddings import generate_embeddings
from src.dataops.utils import save_metadata_locally, save_metadata_to_azure
from src.utils.cloud import AzureBlobStorage
from datetime import datetime
import uuid
from tqdm import tqdm
from src.models.imagebind_model_wrapper import ImageBindModelWrapper

# Load environment variables from .env file
load_dotenv(dotenv_path=Path("..") / ".env")

# Get the base directory (project root)
BASE_DIR = Path(os.getenv('DEFAULT_BASE_PATH')).resolve()

# Load environment variables from .env file
load_dotenv(dotenv_path=Path("..") / ".env")

# Get the base directory (project root)
BASE_DIR = Path(os.getenv('DEFAULT_BASE_PATH')).resolve()

def main():
    # Define paths using environment variables
    image_directory_path = BASE_DIR / "tests/fixtures/ngs"
    spreadsheet_path = BASE_DIR / "tests/fixtures/artworks.csv"

    # Initialize ArtworkDataManager
    print("Initializing Artwork Data Manager...")
    artwork_manager = ArtworkDataManager(image_directory_path, spreadsheet_path)

    # Ingest data
    print("Ingesting data...")
    artwork_manager.ingest_data()

    # Process artworks and obtain metadata
    print("Processing artworks and obtaining metadata...")
    artworks_metadata = process_artworks(artwork_manager)

    # Save the generated metadata locally first (without embeddings)
    local_save_path = "raw_data/generated_metadata.csv"
    print("Saving metadata locally...")
    save_metadata_locally(artworks_metadata, local_save_path)

    # Upload everything to Azure Blob Storage
    blob_storage = AzureBlobStorage()

    print("Uploading data to Azure Blob Storage...")

    # Uploading original images
    for item in image_directory_path.iterdir():
        if item.is_file():  # Ensure we're dealing with files
            blob_url = blob_storage.upload(item, item.name)
            print(f"Uploaded {item.name} to {blob_url}")

    # Uploading processed images
    processed_image_directory = image_directory_path / "processed"
    for item in processed_image_directory.iterdir():
        if item.is_file():  # Ensure we're dealing with files
            blob_url = blob_storage.upload(item, f"processed/{item.name}")
            print(f"Uploaded processed/{item.name} to {blob_url}")

    # Upload metadata to Azure
    save_metadata_to_azure(artworks_metadata, f"generated_metadata.csv")

def process_artworks(artwork_manager: ArtworkDataManager) -> list:
    artworks_metadata = []
    columns = ["ap_Title", "Artist/Maker_y"]

    for idx, image_file in enumerate(tqdm(artwork_manager.image_source.images, desc="Processing artworks")):
        original_image_file = artwork_manager.image_source.original_images[idx]
        image, metadata_dict = artwork_manager.get_artwork_data(original_image_file, columns=columns)

        print(f"\nProcessing: {image_file.name}")
        for col in columns:
            value = metadata_dict.get(col, "N/A")
            print(f"Column: {col}, Value: {value}")

        # Generate image embeddings
        embeddings = generate_embeddings(artwork_manager.embedding_model, image_paths=[image_file])
        print(f"Embedding keys: {embeddings.keys()}")
        image_embedding = embeddings.get('vision', None)
        if image_embedding is not None:
            print(f"Image Embedding Shape: {image_embedding.shape}")
        else:
            print("Image Embedding not generated!")

        # Combine text from desired columns for embedding
        combined_text = ' '.join([metadata_dict[col] for col in columns if metadata_dict.get(col)])
        if combined_text:  # Check to ensure it's not empty
            text_embeddings = generate_embeddings(artwork_manager.embedding_model, text_list=[combined_text])
            text_embedding = text_embeddings.get('text', None)
        else:
            text_embedding = None
            print("No textual data available for this artwork.")

        weighted_embedding, _ = compute_weighted_embeddings(image_embedding, metadata_embedding=text_embedding, metadata_columns=metadata_dict)
        print("Shape of weighted embedding:", weighted_embedding.shape)

        # Construct full metadata
        item_metadata = {
            "uuid": str(uuid.uuid4()),
            "filename": image_file.name,
            "image_path": str(image_file),  # This line stores the full path of the image
            "accession_no": image_file.stem,
            "title": metadata_dict.get("ap_Title") if metadata_dict else None,
            "artist_maker": metadata_dict.get("Artist/Maker_y") if metadata_dict else None,
            "created_date": datetime.now().isoformat(),
        }

        # Store the artwork data (image, embedding, and full metadata) in DeepLake
        artwork_manager.store_artwork_in_deeplake(original_image_file, weighted_embedding, item_metadata)

        artworks_metadata.append(item_metadata)

    return artworks_metadata

if __name__ == "__main__":
    main()
