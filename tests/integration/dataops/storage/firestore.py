import unittest
import os
from firebase_admin import firestore
from berlayar.utils.load_keys import load_environment_variables
from berlayar.dataops.storage.firestore import FirestoreStorage

# Load environment variables for the test
load_environment_variables()

class FirestoreStorageIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up for the entire test class"""
        # Initialize FirestoreStorage
        cls.storage = FirestoreStorage(os.getenv('FIREBASE_KEY'))
        cls.test_collection_name = 'testCollection'

        # Check Firestore connection and print database name
        cls.db = cls.storage.db
        print("Firestore database name:", cls.db._database_string)

        # Create the test collection if it doesn't exist
        cls.create_test_collection()

        # Optional: Setup test data or prerequisites here

    @classmethod
    def create_test_collection(cls):
        """Create the test collection if it doesn't exist"""
        if not cls.db.collection(cls.test_collection_name).document("dummy_doc").get().exists:
            cls.db.collection(cls.test_collection_name).document("dummy_doc").set({})

    def setUp(self):
        """Set up for each test method"""
        # Define a unique document ID for each test to prevent collisions
        self.test_doc_id = 'testDocument'

    def test_save_data(self):
        """Test the save_data method of FirestoreStorage"""
        test_data = {'name': 'Test Name', 'value': 123}

        # Save data using the FirestoreStorage instance
        doc_id = self.storage.save_data(self.test_collection_name, test_data)

        # Fetch the saved document to verify its contents
        saved_doc = self.storage.db.collection(self.test_collection_name).document(doc_id).get()

        self.assertTrue(saved_doc.exists)
        self.assertEqual(saved_doc.to_dict(), test_data)

    def test_load_data(self):
        """Test the load_data method of FirestoreStorage"""
        # Define test data
        test_data = {'name': 'Test Name', 'value': 123}

        # Save test data to Firestore
        doc_ref = self.storage.db.collection(self.test_collection_name).add(test_data)
        doc_id = doc_ref[1].id

        # Load data using the FirestoreStorage instance
        loaded_data = self.storage.load_data(self.test_collection_name, doc_id)

        self.assertEqual(loaded_data, test_data)

    def test_update_data(self):
        """Test the update_data method of FirestoreStorage"""
        # Define test data
        test_data = {'name': 'Test Name', 'value': 123}

        # Save test data to Firestore
        doc_ref = self.storage.db.collection(self.test_collection_name).add(test_data)
        doc_id = doc_ref[1].id

        # Update data using the FirestoreStorage instance
        updated_data = {'name': 'Updated Name', 'value': 456}
        self.storage.update_data(self.test_collection_name, doc_id, updated_data)

        # Fetch the updated document to verify its contents
        updated_doc = self.storage.db.collection(self.test_collection_name).document(doc_id).get()

        self.assertEqual(updated_doc.to_dict(), updated_data)

    def test_delete_data(self):
        """Test the delete_data method of FirestoreStorage"""
        # Define test data
        test_data = {'name': 'Test Name', 'value': 123}

        # Save test data to Firestore
        doc_ref = self.storage.db.collection(self.test_collection_name).add(test_data)
        doc_id = doc_ref[1].id

        # Delete data using the FirestoreStorage instance
        self.storage.delete_data(self.test_collection_name, doc_id)

        # Fetch the deleted document to verify its existence
        deleted_doc = self.storage.db.collection(self.test_collection_name).document(doc_id).get()

        self.assertFalse(deleted_doc.exists)

    @classmethod
    def tearDownClass(cls):
        """Tear down after all tests in this class have run"""
        # Optionally delete the test collection or documents to clean up
        # Be cautious with deletion to avoid affecting production data
        test_docs = cls.storage.db.collection(cls.test_collection_name).stream()
        for doc in test_docs:
            doc.reference.delete()

if __name__ == '__main__':
    unittest.main()
