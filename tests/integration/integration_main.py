from dotenv import load_dotenv
from pathlib import Path
from app.main import main
from src.utils.cloud import AzureBlobStorage
import deeplake
import os

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

def test_integration():
    print("Starting the integration test...")

    # 1. Execute the main function
    print("Executing main function...")
    main()

    # 2. Load the created DeepLake dataset
    deeplake_path = os.getenv("DEEPLAKE_PATH")
    ds = deeplake.load(deeplake_path)

    # 3. Print DeepLake dataset information for verification
    print("DeepLake Dataset Info:", ds.info)

    # 4. Print out Azure blob URIs
    azure_storage = AzureBlobStorage()
    all_blobs = azure_storage.list_objects()
    print("Azure Blob URIs:")
    for blob in all_blobs:
        print(f"https://{account_name}.blob.core.windows.net/{container_name}/{blob}")

    # 5. Print the first few lines of the CSV uploaded
    local_csv_path = "raw_data/generated_metadata.csv"
    print("First 5 lines of the uploaded CSV:")
    with open(local_csv_path, "r") as f:
        lines = f.readlines()
    print("".join(lines[:5]))

    # 6. Teardown: Delete the DeepLake database and Azure blob container when done
    print("Starting teardown...")
    deeplake.delete(large_ok=True)  # Delete the DeepLake database
    azure_storage.delete_container()  # Delete the Azure blob container
    print("Teardown completed.")

if __name__ == "__main__":
    test_integration()
