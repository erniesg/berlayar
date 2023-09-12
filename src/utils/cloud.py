import os
import dotenv
from azure.storage.blob import BlobServiceClient
from src.base_classes import AbstractCloudStorage
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError, ResourceExistsError
import sys
from pathlib import Path
from typing import Union, List

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
dotenv.load_dotenv(dotenv_path)

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

class AzureBlobStorage(AbstractCloudStorage):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AzureBlobStorage, cls).__new__(cls)

            try:
                # Try to initialize using the connection string
                cls._instance.client = BlobServiceClient.from_connection_string(connection_string)
            except ValueError:
                print("Failed to initialize using connection string. Trying Azure CLI authentication...")
                # If the connection string is invalid, use Azure CLI authentication
                try:
                    credential = DefaultAzureCredential()
                    cls._instance.client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=credential)
                except ClientAuthenticationError:
                    print("Authentication failed. Please authenticate using 'az login'")
                    sys.exit(1)

            cls._instance.container = cls._instance.client.get_container_client(container_name)

            # Create the container if it doesn't exist
            try:
                cls._instance.container.create_container()
                print(f"Container '{container_name}' created successfully.")
            except ResourceExistsError:
                print(f"Container '{container_name}' already exists.")
            except Exception as e:
                print(f"An error occurred while creating the container: {e}")
                sys.exit(1)

        return cls._instance

    def upload(self, data_source: Union[str, Path, List[Union[str, Path]]], blob_name: str, client=None):
        """Upload data (file or in-memory) to Azure Blob Storage."""
        client = client or self.container

        # Handling directory input
        if isinstance(data_source, (str, Path)) and Path(data_source).is_dir():
            for file in Path(data_source).iterdir():
                with open(file, 'rb') as data_file:
                    client.upload_blob(str(file), data_file)

        # Handling list input (mix of files and directories)
        elif isinstance(data_source, list):
            for item in data_source:
                self.upload(item, blob_name, client)

        # Handling file input
        elif isinstance(data_source, (str, Path)):
            with open(data_source, 'rb') as data_file:
                client.upload_blob(blob_name, data_file)

        # Handling in-memory data
        elif isinstance(data_source, bytes):
            client.upload_blob(blob_name, data_source)

        else:
            raise TypeError("Unsupported data source type.")

        print(f"Data successfully uploaded to blob '{blob_name}'")
        return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"

    def download(self, blob_name: str, file_path: str, client=None):
        client = client or self.container
        blob = client.get_blob_client(blob_name)
        with open(file_path, 'wb') as file:
            blob_data = blob.download_blob()
            blob_data.download_to_stream(file)
        print(f"Blob '{blob_name}' downloaded to '{file_path}'")

    def delete(self, blob_name: str, client=None, blob=None):
        client = client or self.container
        blob = blob or client.get_blob_client(blob_name)
        blob.delete_blob()
        print(f"Blob '{blob_name}' deleted successfully")

    def delete_all_blobs(self):
        blobs = self.container.list_blobs()
        for blob in blobs:
            self.delete(blob.name)

    def count_blobs(self) -> int:
        return len(list(self.container.list_blobs()))

    def list_objects(self, prefix: str = None, client=None):
        client = client or self.container
        blob_list = client.list_blobs(name_starts_with=prefix)
        print(f"Blobs starting with '{prefix}': {[blob.name for blob in blob_list]}")
        return [blob.name for blob in blob_list]

    def delete_container(self):
        try:
            self.container.delete_container()
            print(f"Container '{container_name}' deleted successfully.")
        except Exception as e:
            print(f"An error occurred while deleting the container: {e}")

    @classmethod
    def reset_singleton(cls):
        cls._instance = None
