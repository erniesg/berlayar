# berlayar/dataops/storage/firebase_storage.py
from google.cloud import storage
from google.oauth2 import service_account
from berlayar.dataops.interface import StorageInterface
from berlayar.utils.load_keys import load_environment_variables
from berlayar.dataops.storage.firestore import FirestoreStorage  # Import FirestoreStorage
import os

class FirebaseStorage(StorageInterface):
    def __init__(self, bucket_name: str = None) -> None:
        # Load environment variables
        load_environment_variables()

        # Load the service account key from the FIREBASE_KEY environment variable
        firebase_key_path = os.getenv('FIREBASE_KEY')
        if not firebase_key_path:
            raise ValueError("FIREBASE_KEY environment variable not set.")

        # Depending on how you're setting FIREBASE_KEY, it could be a path or the credentials JSON itself
        # Try to load it as a file path first
        try:
            credentials = service_account.Credentials.from_service_account_file(firebase_key_path)
        except FileNotFoundError:
            # If the file is not found, assume FIREBASE_KEY is the credentials JSON itself
            credentials = service_account.Credentials.from_service_account_info(json.loads(firebase_key_path))

        # Instantiate the client with the credentials
        self.client = storage.Client(credentials=credentials)

        # Set or get the bucket name
        if bucket_name is None:
            bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
            if not bucket_name:
                raise ValueError("Bucket name must be provided or set in FIREBASE_STORAGE_BUCKET environment variable.")
        self.bucket = self.client.bucket(bucket_name)
        print(f"Using bucket name: {bucket_name}")

    def save_data(self, file_name, data, content_type='application/octet-stream'):  # Corrected argument order
        blob = self.bucket.blob(file_name)
        blob.upload_from_string(data, content_type=content_type)
        return blob.public_url

    def load_data(self, file_name):
        blob = self.bucket.blob(file_name)
        data = blob.download_as_bytes()
        metadata = {
            "content_type": blob.content_type,
            "size": blob.size,
            "created": blob.time_created,
            "modified": blob.updated,
            "storage_class": blob.storage_class,
            "public_url": f"https://storage.googleapis.com/{self.bucket.name}/{blob.name}"
        }
        return {"data": data, "metadata": metadata}

    def delete_data(self, file_name):
        blob = self.bucket.blob(file_name)
        blob.delete()

    def update_data(self, identifier, data):
        raise NotImplementedError("update_data method is not implemented for FirebaseStorage")
