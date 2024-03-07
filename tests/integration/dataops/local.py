import unittest
import os
from berlayar.services.user import User
from berlayar.dataops.storage.local import LocalStorage
from berlayar.schemas.user import UserModel
import json

class TestUserIntegration(unittest.TestCase):

    def setUp(self):
        # Initialize a LocalStorage instance for testing
        self.base_dir = "raw_data/user_test"
        self.storage = LocalStorage(base_dir=self.base_dir)

        # Initialize a User instance
        self.user_service = User(storages=[self.storage])  # Pass the storage instance as a list

    def test_create_user_invalid_data(self):
        # Create a new user with invalid data (missing required fields)
        invalid_user_data = {
            "age": 25
        }

        # Attempt to create the user with invalid data
        with self.assertRaises(ValueError):
            self.user_service.create_user(invalid_user_data)

    def test_create_user_and_storage(self):
        # Create a new user with valid data
        valid_user_data = {
            "preferred_name": "test_user",
            "age": 25,
            "email": "test@example.com",
            "location": "Test Location",
            "mobile_number": "1234567890",
            "preferences": {
                "image_gen_model": "Model A",
                "language": "English"
            }
        }

        # Create the user
        new_user = self.user_service.create_user(valid_user_data)

        # Check if the user file was created
        user_filename = f"{new_user.user_id}.json"
        user_file_path = os.path.join(self.base_dir, user_filename)
        self.assertTrue(os.path.exists(user_file_path), "User file was not created")

        # Check if the content of the user file matches the expected data
        with open(user_file_path, 'r') as file:
            user_file_contents = json.load(file)  # Load file contents as JSON
            self.assertEqual(user_file_contents, new_user.dict(), "User data does not match")

    def test_update_preferences_and_storage(self):
        # Create a new user with valid data
        valid_user_data = {
            "preferred_name": "test_user",
            "age": 25,
            "email": "test@example.com",
            "location": "Test Location",
            "mobile_number": "1234567890",
            "preferences": {
                "image_gen_model": "Model A",
                "language": "English"
            }
        }

        # Create the user
        new_user = self.user_service.create_user(valid_user_data)

        # Update user preferences
        new_preferences = {
            "image_gen_model": "Model B",
            "language": "French"
        }
        updated_user_data = self.user_service.update_preferences(new_user.user_id, new_preferences)

        # Check if the user file was updated with the new preferences
        user_filename = f"{new_user.user_id}.json"
        user_file_path = os.path.join(self.base_dir, user_filename)
        self.assertTrue(os.path.exists(user_file_path), "User file does not exist")

        # Check if the content of the user file matches the updated preferences
        with open(user_file_path, 'r') as file:
            user_file_contents = file.read()
            self.assertIn(new_preferences["image_gen_model"], user_file_contents)
            self.assertIn(new_preferences["language"], user_file_contents)

    def tearDown(self):
        # Remove the raw_data/user_test directory and its contents
        os.system(f"rm -rf {self.base_dir}")

if __name__ == "__main__":
    unittest.main()
