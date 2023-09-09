import unittest
from unittest.mock import patch, Mock, ANY
from src.utils.cloud import AzureBlobStorage

class TestAzureBlobStorage(unittest.TestCase):

    @patch('src.utils.cloud.BlobServiceClient')
    def setUp(self, MockBlobServiceClient):
        self.mock_client = MockBlobServiceClient.return_value
        self.mock_container = Mock()
        self.mock_client.get_container_client.return_value = self.mock_container
        self.mock_container.create_container.return_value = None

        AzureBlobStorage.reset_singleton()
        self.storage = AzureBlobStorage()

    def tearDown(self):
        AzureBlobStorage.reset_singleton()

    def test_upload(self):
        test_file_path = 'test_path'
        test_blob_name = 'test_blob'
        self.storage.upload(test_file_path, test_blob_name, client=self.mock_container)
        self.mock_container.upload_blob.assert_called_with(test_blob_name, ANY)

    def test_download(self):
        mock_blob = Mock()
        self.mock_container.get_blob_client.return_value = mock_blob
        test_blob_name = 'test_blob'
        test_file_path = 'test_path'
        self.storage.download(test_blob_name, test_file_path, client=self.mock_container)
        mock_blob.download_blob.assert_called()

    def test_delete(self):
        mock_blob = Mock()
        self.mock_container.get_blob_client.return_value = mock_blob
        test_blob_name = 'test_blob'
        self.storage.delete(test_blob_name, client=self.mock_container, blob=mock_blob)
        mock_blob.delete_blob.assert_called()

    def test_list_objects(self):
        mock_blob1 = Mock()
        mock_blob1.name = 'blob1'
        mock_blob2 = Mock()
        mock_blob2.name = 'blob2'
        self.mock_container.list_blobs.return_value = [mock_blob1, mock_blob2]
        blobs = self.storage.list_objects(client=self.mock_container)
        self.assertEqual(blobs, ['blob1', 'blob2'])

if __name__ == '__main__':
    unittest.main()
