import unittest
import os
from firebase_admin import firestore
from berlayar.utils.load_keys import load_environment_variables
from berlayar.dataops.storage.firestore import FirestoreStorage
from berlayar.dataops.user_repository import UserRepository

# Load environment variables for the test
load_environment_variables()

class TestFirestoreIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Firestore for the entire test class"""
        # Initialize FirestoreStorage with actual Firestore client
        cls.firestore_storage = FirestoreStorage(os.getenv('FIREBASE_KEY'))
        cls.user_repo = UserRepository(cls.firestore_storage)

    def setUp(self):
        """Set up for each test method"""
        # Optionally, you can set up any test-specific data here
        pass

    def test_get_user(self):
        # Create a test user in Firestore
        test_user_data = {
            "preferred_name": "John",
            "age": 30,
            "country": "USA",
            "mobile_number": "1234567890"
            # Add other fields as needed
        }
        user_id = self.user_repo.create_user(test_user_data)

        # Retrieve the user from Firestore
        retrieved_user = self.user_repo.get_user(user_id)

        # Assert that the retrieved user matches the test user data
        self.assertEqual(retrieved_user["preferred_name"], test_user_data["preferred_name"])
        self.assertEqual(retrieved_user["age"], test_user_data["age"])
        # Add assertions for other fields

    def test_create_user(self):
        # Create a test user
        test_user_data = {
            "preferred_name": "John",
            "age": 30,
            "country": "USA",
            "mobile_number": "1234567890"
            # Add other fields as needed
        }
        print("Test user data:", test_user_data)

        # Save the user to Firestore
        user_id = self.user_repo.create_user(test_user_data)
        print("User ID:", user_id)

        # Retrieve the user from Firestore
        retrieved_user = self.user_repo.get_user(user_id)
        print("User ID:", user_id)

        # Assert that the retrieved user matches the test user data
        self.assertEqual(retrieved_user["preferred_name"], test_user_data["preferred_name"])
        self.assertEqual(retrieved_user["age"], test_user_data["age"])
        # Add assertions for other fields

    def test_update_user(self):
        # Create a test user
        test_user_data = {
            "preferred_name": "John",
            "age": 30,
            "country": "USA",
            "mobile_number": "1234567890"
            # Add other fields as needed
        }
        user_id = self.user_repo.create_user(test_user_data)

        # Update the user data
        updated_user_data = {
            "preferred_name": "John Doe",
            "age": 35,
            "country": "Canada",
            "mobile_number": "9876543210"
            # Add other fields as needed
        }
        self.user_repo.update_user(user_id, updated_user_data)

        # Retrieve the updated user from Firestore
        retrieved_user = self.user_repo.get_user(user_id)

        # Assert that the retrieved user matches the updated data
        self.assertEqual(retrieved_user["preferred_name"], updated_user_data["preferred_name"])
        self.assertEqual(retrieved_user["age"], updated_user_data["age"])
        # Add assertions for other fields

if __name__ == "__main__":
    unittest.main()
