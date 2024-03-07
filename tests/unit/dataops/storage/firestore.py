import unittest
from unittest.mock import patch, MagicMock
from berlayar.dataops.storage.firestore import FirestoreStorage

import unittest
from unittest.mock import patch, MagicMock
from berlayar.dataops.storage.firestore import FirestoreStorage

class TestFirestoreStorage(unittest.TestCase):
    @patch('berlayar.dataops.storage.firestore.credentials.Certificate')
    @patch('berlayar.dataops.storage.firestore.initialize_app')
    @patch('berlayar.dataops.storage.firestore.firestore.client')
    def test_load_data(self, mock_client, mock_initialize_app, mock_credentials):
        # Mock setup
        document_mock = MagicMock()
        document_mock.exists = True
        document_mock.to_dict.return_value = {'field': 'new value'}

        collection_ref_mock = mock_client().collection()
        document_ref_mock = collection_ref_mock.document()
        document_ref_mock.get.return_value = document_mock

        storage = FirestoreStorage(credential_path='dummy_path')
        loaded_data = storage.load_data('test_collection', 'test_doc_id')

        self.assertEqual(loaded_data, {'field': 'new value'})
        document_ref_mock.get.assert_called_once()

    @patch('berlayar.dataops.storage.firestore.initialize_app')
    @patch('berlayar.dataops.storage.firestore.credentials.Certificate')
    @patch('berlayar.dataops.storage.firestore.firestore.client')
    def test_save_data(self, mock_client, mock_certificate, mock_initialize_app):
        # Mock setup
        doc_ref_mock = MagicMock()
        doc_ref_mock.id = "test_doc_id"

        collection_ref_mock = MagicMock()
        add_result = MagicMock()  # Create a MagicMock for the add method result
        add_result.id = "test_doc_id"  # Set the id attribute of the add_result
        collection_ref_mock.add.return_value = (doc_ref_mock, add_result)  # Simulate the tuple returned by Firestore

        mock_client.return_value.collection.return_value = collection_ref_mock

        storage = FirestoreStorage(credential_path='dummy_path')
        doc_id = storage.save_data('test_collection', {'field': 'value'})

        self.assertEqual(doc_id, "test_doc_id")
        collection_ref_mock.add.assert_called_once_with({'field': 'value'})

    @patch('berlayar.dataops.storage.firestore.credentials.Certificate')
    @patch('berlayar.dataops.storage.firestore.initialize_app')
    @patch('berlayar.dataops.storage.firestore.firestore.client')
    def test_update_data(self, mock_client, mock_initialize_app, mock_credentials):
        document_ref_mock = mock_client().collection().document()

        storage = FirestoreStorage(credential_path='dummy_path')
        storage.update_data('test_collection', 'test_doc_id', {'field': 'new value'})

        document_ref_mock.update.assert_called_once_with({'field': 'new value'})

    # Repeat similar structure for test_delete_data with the appropriate mock setups and assertions.

if __name__ == "__main__":
    unittest.main()
