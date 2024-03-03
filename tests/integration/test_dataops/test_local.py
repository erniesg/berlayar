import unittest
import os
from berlayar.dataops.storage.local import LocalStorage
from berlayar.services.user import User  # Adjust the import path as needed

class TestUserIntegration(unittest.TestCase):

    def setUp(self):
        # Initialize a LocalStorage instance for testing
        self.storage = LocalStorage(base_dir="raw_data/user_test")  # Use a different directory for testing
        # Provide dummy user data
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "age": 25
        }
        self.user_service = User(user_data=user_data, storage=self.storage)

    def test_save_new_user(self):
        # Create a new user
        self.user_service.create_user()

        # Check if the user file was created
        user_filename = "test_user.json"
        user_file_path = os.path.join("raw_data/user_test", user_filename)
        self.assertTrue(os.path.exists(user_file_path), "User file was not created")

        # Check if the user file is non-empty
        with open(user_file_path, 'r') as file:
            user_file_contents = file.read()
            self.assertTrue(user_file_contents.strip(), "User file is empty")

        # Check if the content of the user file matches the expected data
        user_data_loaded = self.storage.load_data(user_filename)
        self.assertEqual(user_data_loaded, self.user_service.info, "User data does not match")

    def test_load_user(self):
        # Load an existing user
        user_data = {
            "username": "existing_user",
            "email": "existing@example.com",
            "age": 30
        }
        self.user_service.create_user(user_data)
        loaded_user_data = self.user_service.load_user()

        # Check if the loaded user data is not empty
        self.assertTrue(loaded_user_data, "Loaded user data is empty")

        # Check if the loaded user data matches the expected data
        self.assertEqual(loaded_user_data, user_data, "Loaded user data does not match")

    def test_update_user_preferences(self):
        # Update user preferences
        new_preferences = {
            "theme": "dark",
            "language": "English"
        }
        self.user_service.update_preferences(new_preferences)

        # Check if the preferences are updated correctly
        updated_preferences = self.user_service.info["preferences"]
        self.assertEqual(updated_preferences, new_preferences, "User preferences not updated correctly")

    def tearDown(self):
        # Clean up any resources used for testing
        user_filename = "test_user.json"
        user_file_path = os.path.join("raw_data/user_test", user_filename)
        if os.path.exists(user_file_path):
            os.remove(user_file_path)
