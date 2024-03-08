from unittest.mock import patch, MagicMock
import unittest
from berlayar.dataops.storage.firebase_storage import FirebaseStorage

class TestFirebaseStorage(unittest.TestCase):
    @patch('berlayar.dataops.storage.firebase_storage.storage.Client')
    def test_save_data(self, mock_client):
        # Mock setup
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Instantiate FirebaseStorage with mocked client
        with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'dummy_bucket_name'}):
            firebase_storage_instance = FirebaseStorage()

        # Test data
        file_path = "user_uploads/2024/03/some_media_file.jpg"
        data = b"binary data representing media file"
        content_type = "image/jpeg"

        # Execute
        firebase_storage_instance.save_data(file_path, data, content_type)

        # Assertions
        mock_client.assert_called_once()  # Ensure the GCS client is instantiated
        mock_bucket.blob.assert_called_once_with(file_path)  # Ensure blob method is called with the correct file path
        mock_blob.upload_from_string.assert_called_once_with(data, content_type=content_type)  # Ensure upload_from_string is called with the correct data and content type

    @patch('berlayar.dataops.storage.firebase_storage.storage.Client')
    def test_load_data(self, mock_client):
        # Mock setup
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Mock the bucket name to return a fixed string
        mock_bucket.name = 'dummy_bucket_name'

        # Continue with your mock setup...
        mock_blob.download_as_bytes.return_value = b"binary data representing media file"
        mock_blob.content_type = "image/jpeg"
        mock_blob.size = 12345
        mock_blob.time_created = "2024-03-01T00:00:00Z"
        mock_blob.updated = "2024-03-02T00:00:00Z"
        mock_blob.storage_class = "STANDARD"
        mock_blob.name = "some_media_file.jpg"

        # Instantiate FirebaseStorage with mocked client
        with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'dummy_bucket_name'}):
            firebase_storage_instance = FirebaseStorage()

        # Test data
        file_path = "user_uploads/2024/03/some_media_file.jpg"

        # Execute
        result = firebase_storage_instance.load_data(file_path)
        loaded_data = result['data']
        metadata = result['metadata']

        # Assertions for client and blob interactions
        mock_client.assert_called_once()  # Ensure the GCS client is instantiated
        mock_bucket.blob.assert_called_once_with(file_path)  # Ensure blob method is called with the correct file path
        mock_blob.download_as_bytes.assert_called_once()  # Ensure download_as_bytes is called to load data

        # Assertions for loaded data and metadata
        self.assertEqual(loaded_data, b"binary data representing media file")  # Ensure loaded data is correct
        self.assertEqual(metadata['content_type'], "image/jpeg")
        self.assertEqual(metadata['size'], 12345)
        self.assertEqual(metadata['created'], "2024-03-01T00:00:00Z")
        self.assertEqual(metadata['modified'], "2024-03-02T00:00:00Z")
        self.assertEqual(metadata['storage_class'], "STANDARD")
        self.assertEqual(metadata['public_url'], f"https://storage.googleapis.com/dummy_bucket_name/{mock_blob.name}")

    @patch('berlayar.dataops.storage.firebase_storage.storage.Client')
    def test_delete_data(self, mock_client):
        # Mock setup
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Instantiate FirebaseStorage with mocked client
        with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'dummy_bucket_name'}):
            firebase_storage_instance = FirebaseStorage()

        # Test data
        file_path = "user_uploads/2024/03/some_media_file.jpg"

        # Execute
        firebase_storage_instance.delete_data(file_path)

        # Assertions
        mock_client.assert_called_once()  # Ensure the GCS client is instantiated
        mock_bucket.blob.assert_called_once_with(file_path)  # Ensure blob method is called with the correct file path
        mock_blob.delete.assert_called_once()  # Ensure delete is called to delete data
