import os
from pathlib import Path
from dotenv import load_dotenv
from src.dataops.artwork import ArtworkDataManager
from src.utils.embeddings_weighting import compute_weighted_embeddings
from src.utils.embeddings import generate_image_embeddings, generate_textual_embeddings
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
    local_save_path = "./generated_metadata.csv"
    print("Saving metadata locally...")
    save_metadata_locally(artworks_metadata, local_save_path)

    # Upload everything to Azure Blob Storage
    blob_storage = AzureBlobStorage()
    blob_base_path = blob_storage.generate_blob_path(artwork_manager.image_source.directory)
    print("Uploading data to Azure Blob Storage...")
    for item in tqdm(artworks_metadata, desc="Uploading"):
        blob_storage.upload(item['image_file'], f"{blob_base_path}/{item['filename']}")
    save_metadata_to_azure(artworks_metadata, f"{blob_base_path}/generated_metadata.csv")

def process_artworks(artwork_manager: ArtworkDataManager) -> list:
    artworks_metadata = []
    columns = ["ap_Title", "Artist/Maker"]

    for image_file in tqdm(artwork_manager.image_source.images, desc="Processing artworks"):
        image, metadata_dict = artwork_manager.get_artwork_data(image_file, columns=columns)

        # Generate image embeddings
        image_embedding = generate_image_embeddings(ImageBindModelWrapper, [image])[0]
        print("Shape of image embeddings:", image_embedding.shape)

        # Generate textual embeddings only if there's valid metadata
        text_values = [metadata_dict[col] for col in columns if metadata_dict[col]]
        text_embedding = generate_textual_embeddings(ImageBindModelWrapper, text_values)[0]
        print("Shape of text embeddings:", text_embedding.shape)

        # Compute weighted embeddings
        weighted_embedding, _ = compute_weighted_embeddings(image_embedding, text_embedding, metadata_dict)

        # Construct full metadata
        item_metadata = {
            "uuid": str(uuid.uuid4()),
            "filename": image_file.name,
            "accession_no": metadata_dict.get("Accession No.") if metadata_dict else None,
            "title": metadata_dict.get("ap_Title") if metadata_dict else None,
            "artist_maker": metadata_dict.get("Artist/Maker") if metadata_dict else None,
            "storage_path": None,
            "created_date": datetime.now().isoformat(),
            **metadata_dict  # Merge the spreadsheet metadata
        }

        # Store the artwork data (image, embedding, and full metadata) in DeepLake
        artwork_manager.store_artwork_in_deeplake(image, weighted_embedding, item_metadata)

        artworks_metadata.append(item_metadata)

    return artworks_metadata



if __name__ == "__main__":
    main()
