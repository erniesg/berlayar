import unittest
import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from berlayar.dataops.user_repository import UserRepository
from berlayar.schemas.user import UserModel

class TestUserRepository(unittest.TestCase):
    def setUp(self):
        # Mock FirestoreStorage
        self.storage_mock = MagicMock()
        self.user_repo = UserRepository(self.storage_mock)

    def test_get_user_valid_mobile_number(self):
        # Mock data
        mock_user_data = {
            "user_id": "12345",
            "preferred_name": "John",
            "age": 30,
            "country": "USA",
            "mobile_number": "1234567890"
            # Other user data fields...
        }

        # Mock storage method to return user data
        self.storage_mock.load_data.return_value = mock_user_data

        # Test with valid mobile number identifier
        mobile_number = "1234567890"
        result = self.user_repo.get_user(mobile_number)

        # Assert that the method returns the expected user data
        self.assertEqual(result, mock_user_data)

    def test_get_user_invalid_identifier(self):
        # Test with invalid mobile number identifier
        invalid_mobile_number = "invalid_mobile_number"
        self.storage_mock.load_data.return_value = None

        result = self.user_repo.get_user(invalid_mobile_number)

        # Assert that None is returned for invalid identifier
        self.assertIsNone(result)

    def test_create_user_valid_data(self):
        # Mock data for a valid user
        mock_user_data = {'preferred_name': 'John', 'age': 30, 'country': 'USA', 'mobile_number': '1234567890'}

        # Mock storage method
        self.storage_mock.save_data.return_value = "document_id"

        # Call create_user with valid data
        result = self.user_repo.create_user(mock_user_data)

        # Assert that the method returns True
        self.assertTrue(result)

        # Assert that the storage method was called with the correct arguments
        self.storage_mock.save_data.assert_called_once_with(self.user_repo.user_collection_name, mock_user_data)

    def test_create_user_invalid_data(self):
        # Incorrect mock data to simulate invalid input scenario
        # Directly pass a dictionary to simulate the input from an external source
        mock_user_data = {'preferred_name': 'John', 'age': 30, 'country': 'USA'}  # 'mobile_number' is missing

        # Attempt to create user with invalid data should raise ValueError
        with self.assertRaises(ValueError) as exc_info:
            self.user_repo.create_user(mock_user_data)

        # Optionally, assert the message content if specific error messaging is important
        assert "Missing required fields" in str(exc_info.exception)

    def test_update_user_partial_user_name(self):
        # Mock data
        user_id = "12345"
        partial_user_data = {"user_name": "new_user_name"}

        # Mock the storage method to ensure it behaves as expected
        self.storage_mock.load_data.return_value = {"existing_field": "existing_value"}  # Simulate existing user data

        # Call the update_user method with partial data
        self.user_repo.update_user(user_id, partial_user_data)

        # Assert that the update_data method of the storage interface is called with the correct arguments
        expected_updated_data = {"existing_field": "existing_value", "user_name": "new_user_name"}  # Merged data
        self.storage_mock.update_data.assert_called_once_with("users", user_id, expected_updated_data)

if __name__ == "__main__":
    unittest.main()
