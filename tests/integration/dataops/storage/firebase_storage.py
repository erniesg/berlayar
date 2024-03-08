import unittest
from berlayar.dataops.storage.firebase_storage import FirebaseStorage
from berlayar.utils.load_keys import load_environment_variables
import requests

class TestFirebaseStorageIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure that any necessary environment variables are loaded
        load_environment_variables()

    def setUp(self):
        # Initialize FirebaseStorage with potentially required configurations
        self.firebase_storage = FirebaseStorage()

        # Define the URL for the test data and extract the filename
        self.data_url = "https://storage.googleapis.com/thesoundofstories/berlayar/raw_data/fixtures/2008-06923.jpg"
        self.file_name = self.data_url.split('/')[-1]  # Extracts '2008-06923.jpg' from the URL

        # Download the test data to be used in the tests
        response = requests.get(self.data_url)
        self.test_data = response.content
        self.content_type = response.headers['Content-Type']

    def tearDown(self):
        # Attempt to clean up by deleting the test file, suppressing any errors
        try:
            self.firebase_storage.delete_data(self.file_name)
            print(f"Successfully deleted file: {self.file_name}")
        except Exception as e:
            print(f"Error in tearDown when trying to delete {self.file_name}: {e}")

    def test_save_data(self):
        # Test the save_data functionality
        print(f"Testing save_data with file_name: {self.file_name}")
        public_url = self.firebase_storage.save_data(self.file_name, self.test_data, self.content_type)
        self.assertIsNotNone(public_url)
        print(f"File saved successfully, public URL: {public_url}")

    def test_load_data(self):
        # Ensure the file is saved first for the load test
        self.firebase_storage.save_data(self.file_name, self.test_data, self.content_type)
        print(f"Testing load_data with file_name: {self.file_name}")
        result = self.firebase_storage.load_data(self.file_name)
        loaded_data = result['data']
        metadata = result['metadata']

        # Ensure data is loaded successfully and verify metadata
        self.assertIsNotNone(loaded_data)
        self.assertEqual(metadata['content_type'], self.content_type)
        print(f"Loaded data and verified metadata successfully for: {self.file_name}")

    def test_delete_data(self):
        # Ensure the file is saved first for the delete test
        self.firebase_storage.save_data(self.file_name, self.test_data, self.content_type)
        print(f"Testing delete_data with file_name: {self.file_name}")
        self.firebase_storage.delete_data(self.file_name)
        # Attempt to verify deletion by trying to load the deleted file
        try:
            self.firebase_storage.load_data(self.file_name)
            self.fail(f"File {self.file_name} should have been deleted but was still found.")
        except Exception as e:
            print(f"Deletion of file {self.file_name} verified successfully. Caught expected exception: {e}")
