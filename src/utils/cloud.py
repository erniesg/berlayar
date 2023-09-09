import os
import dotenv
from azure.storage.blob import BlobServiceClient
from src.base_classes import AbstractCloudStorage
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
import sys

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
            except:
                # The container already exists or there was another error.
                pass

        return cls._instance

    def upload(self, file_path: str, blob_name: str, client=None):
        client = client or self.container
        with open(file_path, 'rb') as data:
            client.upload_blob(blob_name, data)

    def download(self, blob_name: str, file_path: str, client=None):
        client = client or self.container
        blob = client.get_blob_client(blob_name)
        with open(file_path, 'wb') as file:
            blob_data = blob.download_blob()
            blob_data.download_to_stream(file)

    def delete(self, blob_name: str, client=None, blob=None):
        client = client or self.container
        blob = blob or client.get_blob_client(blob_name)
        blob.delete_blob()

    def list_objects(self, prefix: str = None, client=None):
        client = client or self.container
        blob_list = client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blob_list]

    @classmethod
    def reset_singleton(cls):
        cls._instance = None
