import unittest
from berlayar.dataops.storage.local import LocalStorage

class TestLocalStorage(unittest.TestCase):

    def setUp(self):
        # Initialize a LocalStorage instance for testing
        self.storage = LocalStorage()

    def test_save_data(self):
        # Test saving data
        data = {"key": "value"}
        filename = "test_data.json"
        self.storage.save_data(filename, data)
        # Verify that the file was created and contains the correct data
        loaded_data = self.storage.load_data(filename)
        self.assertEqual(data, loaded_data)

    def test_load_data(self):
        # Test loading data
        filename = "test_data.json"
        data = {"key": "value"}
        self.storage.save_data(filename, data)
        loaded_data = self.storage.load_data(filename)
        # Verify that the loaded data matches the expected data
        self.assertEqual(data, loaded_data)
