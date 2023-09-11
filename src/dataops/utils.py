import pandas as pd
from typing import List, Dict
from src.utils.cloud import AzureBlobStorage

def save_metadata_locally(metadata: List[Dict], save_path: str) -> None:
    """
    Save provided metadata as a CSV locally.

    Parameters:
    - metadata: List of dictionaries containing metadata.
    - save_path: Local path to save the generated CSV.
    """
    df = pd.DataFrame(metadata)
    df.to_csv(save_path, index=False)


def save_metadata_to_azure(metadata: List[Dict], blob_name: str) -> None:
    """
    Save provided metadata as a CSV to Azure Blob Storage.

    Parameters:
    - metadata: List of dictionaries containing metadata.
    - blob_name: Name for the blob in Azure Blob Storage.
    """
    df = pd.DataFrame(metadata)
    csv_data = df.to_csv(index=False).encode('utf-8')
    blob_storage = AzureBlobStorage()
    blob_storage.upload(csv_data, blob_name)
