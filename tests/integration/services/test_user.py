import pytest
from unittest.mock import MagicMock
from berlayar.services.user import UserService, UserNotFoundException, UserAlreadyExistsException

@pytest.fixture
def local_storage():
    # Mock local storage interface
    local_storage_interface = MagicMock()
    return local_storage_interface

@pytest.fixture
def firestore_client():
    # Mock Firestore client
    firestore_client = MagicMock()
    return firestore_client

@pytest.fixture
def user_service(local_storage, firestore_client):
    # Create UserService instances with different storage interfaces
    local_user_service = UserService(local_storage)
    firestore_user_service = UserService(firestore_client)
    return local_user_service, firestore_user_service

def test_integration_create_user_local(user_service, local_storage):
    # Define user data
    user_data = {
        "preferred_name": "Alice",
        "age": 25,
        "country": "USA",
        "mobile_number": "1234567890"
    }

    # Call create_user method
    user_id = user_service.create_user(user_data)

    # Assert that the local storage interface's save_data method was called with the correct parameters
    local_storage.save_data.assert_called_once()
    call_args = local_storage.save_data.call_args
    assert call_args[0][0] == user_id  # User ID should be passed correctly
    assert call_args[0][1] == user_data  # User data should be passed correctly

def test_integration_create_user_firestore(user_service, firestore_client):
    # Define user data
    user_data = {
        "preferred_name": "Alice",
        "age": 25,
        "country": "USA",
        "mobile_number": "1234567890"
    }

    # Call create_user method
    user_id = user_service.create_user(user_data)

    # Assert that the Firestore client's collection method was called with the correct parameters
    firestore_client.collection.assert_called_once_with('users')

    # Assert that the Firestore client's add method was called with the correct parameters
    firestore_client.collection().add.assert_called_once()
    call_args = firestore_client.collection().add.call_args
    assert call_args[0][0] == user_data  # User data should be passed correctly

def test_integration_get_user_local(user_service, local_storage):
    # Define user ID and user data
    user_id = "123abc"
    expected_user_data = {
        "preferred_name": "Alice",
        "age": 25,
        "country": "USA",
        "mobile_number": "1234567890"
    }

    # Mock local storage interface's load_data method to return user data
    local_storage.load_data.return_value = expected_user_data

    # Call get_user method
    retrieved_user_data = user_service.get_user(user_id)

    # Assert that the local storage interface's load_data method was called with the correct parameters
    local_storage.load_data.assert_called_once_with(user_id)

    # Assert that the retrieved user data matches the expected user data
    assert retrieved_user_data == expected_user_data

def test_integration_get_user_firestore(user_service, firestore_client):
    # Define user ID and user data
    user_id = "123abc"
    expected_user_data = {
        "preferred_name": "Alice",
        "age": 25,
        "country": "USA",
        "mobile_number": "1234567890"
    }

    # Mock Firestore client's document method to return user data
    firestore_client.collection().document().get.return_value.to_dict.return_value = expected_user_data

    # Call get_user method
    retrieved_user_data = user_service.get_user(user_id)

    # Assert that the Firestore client's collection method was called with the correct parameters
    firestore_client.collection.assert_called_once_with('users')

    # Assert that the Firestore client's document method was called with the correct parameters
    firestore_client.collection().document.assert_called_once_with(user_id)

    # Assert that the retrieved user data matches the expected user data
    assert retrieved_user_data == expected_user_data

def test_integration_update_user_local(user_service, local_storage):
    # Define user ID and updated user data
    user_id = "123abc"
    updated_user_data = {
        "preferred_name": "Alice",
        "age": 26,
        "country": "USA",
        "mobile_number": "1234567890"
    }

    # Call update_user method
    user_service.update_user(user_id, updated_user_data)

    # Assert that the local storage interface's save_data method was called with the correct parameters
    local_storage.save_data.assert_called_once()
    call_args = local_storage.save_data.call_args
    assert call_args[0][0] == user_id  # User ID should be passed correctly
    assert call_args[0][1] == updated_user_data  # Updated user data should be passed correctly

def test_integration_update_user_firestore(user_service, firestore_client):
    # Define user ID and updated user data
    user_id = "123abc"
    updated_user_data = {
        "preferred_name": "Alice",
        "age": 26,
        "country": "USA",
        "mobile_number": "1234567890"
    }

    # Call update_user method
    user_service.update_user(user_id, updated_user_data)

    # Assert that the Firestore client's collection method was called with the correct parameters
    firestore_client.collection.assert_called_once_with('users')

    # Assert that the Firestore client's document method was called with the correct parameters
    firestore_client.collection().document.assert_called_once_with(user_id)

    # Assert that the Firestore client's set method was called with the correct parameters
    firestore_client.collection().document().set.assert_called_once_with(updated_user_data)

def test_integration_delete_user_local(user_service, local_storage):
    # Define user ID
    user_id = "123abc"

    # Call delete_user method
    user_service.delete_user(user_id)

    # Assert that the local storage interface's delete_data method was called with the correct parameters
    local_storage.delete_data.assert_called_once_with(user_id)

def test_integration_delete_user_firestore(user_service, firestore_client):
    # Define user ID
    user_id = "123abc"

    # Call delete_user method
    user_service.delete_user(user_id)

    # Assert that the Firestore client's collection method was called with the correct parameters
    firestore_client.collection.assert_called_once_with('users')

    # Assert that the Firestore client's document method was called with the correct parameters
    firestore_client.collection().document.assert_called_once_with(user_id)

    # Assert that the Firestore client's delete method was called once
    firestore_client.collection().document().delete.assert_called_once()
