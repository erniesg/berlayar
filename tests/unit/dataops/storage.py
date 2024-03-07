import pytest
from berlayar.dataops.storage import StorageInterface, StorageOperationException
from unittest.mock import Mock

@pytest.fixture
def storage_interface():
    return StorageInterface()

def test_save_data(storage_interface):
    # Define sample data
    data = {"key": "value"}

    # Mock filesystem interface's save method
    storage_interface.filesystem_interface.save = Mock(return_value=True)

    # Attempt to save data
    result = storage_interface.save_data("subdir", "filename", data)

    # Assert that the data was saved successfully
    assert result is True

    # Assert that the filesystem interface's save method was called with the correct parameters
    storage_interface.filesystem_interface.save.assert_called_once_with("subdir", "filename", data)

def test_save_data_invalid_input(storage_interface):
    # Define invalid data (None)
    data = None

    # Attempt to save invalid data
    with pytest.raises(StorageOperationException):
        storage_interface.save_data("subdir", "filename", data)

def test_load_data(storage_interface):
    # Define sample data to be loaded
    loaded_data = {"key": "value"}

    # Mock filesystem interface's load method
    storage_interface.filesystem_interface.load = Mock(return_value=loaded_data)

    # Load data
    data = storage_interface.load_data("subdir", "filename")

    # Assert that the data was loaded successfully
    assert data == loaded_data

    # Assert that the filesystem interface's load method was called with the correct parameters
    storage_interface.filesystem_interface.load.assert_called_once_with("subdir", "filename")

def test_load_data_invalid_input(storage_interface):
    # Attempt to load data from invalid directory
    with pytest.raises(StorageOperationException):
        storage_interface.load_data("", "filename")

def test_update_data(storage_interface):
    # Define sample data
    updated_data = {"key": "new_value"}

    # Mock filesystem interface's update method
    storage_interface.filesystem_interface.update = Mock(return_value=True)

    # Update data
    result = storage_interface.update_data("subdir", "filename", updated_data)

    # Assert that the data was updated successfully
    assert result is True

    # Assert that the filesystem interface's update method was called with the correct parameters
    storage_interface.filesystem_interface.update.assert_called_once_with("subdir", "filename", updated_data)

def test_update_data_invalid_input(storage_interface):
    # Define invalid data (None)
    updated_data = None

    # Attempt to update data with invalid input
    with pytest.raises(StorageOperationException):
        storage_interface.update_data("subdir", "filename", updated_data)

def test_delete_data(storage_interface):
    # Mock filesystem interface's delete method
    storage_interface.filesystem_interface.delete = Mock(return_value=True)

    # Delete data
    result = storage_interface.delete_data("subdir", "filename")

    # Assert that the data was deleted successfully
    assert result is True

    # Assert that the filesystem interface's delete method was called with the correct parameters
    storage_interface.filesystem_interface.delete.assert_called_once_with("subdir", "filename")

def test_delete_data_invalid_input(storage_interface):
    # Attempt to delete data from invalid directory
    with pytest.raises(StorageOperationException):
        storage_interface.delete_data("", "filename")

def test_concurrent_access(storage_interface):
    # Define sample data
    data = {"key": "value"}

    # Define number of concurrent threads/processes
    num_threads = 10

    # Mock filesystem interface's save method to simulate concurrent access
    storage_interface.filesystem_interface.save = lambda subdir, filename, data: True

    # Perform concurrent data saving
    results = []
    for _ in range(num_threads):
        results.append(storage_interface.save_data("subdir", "filename", data))

    # Assert that all save operations were successful
    assert all(results)

def test_storage_interface_initialization(storage_interface):
    # Assert that the filesystem interface is initialized
    assert storage_interface.filesystem_interface is not None
