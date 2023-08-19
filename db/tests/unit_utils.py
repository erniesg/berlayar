import os
import unittest
from unittest.mock import patch
from db.utils import save_to_db

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create a mocked repository directory for testing
        self.repo_path = "./mock_repo"
        os.makedirs(self.repo_path, exist_ok=True)

        # Create some sample files in the mocked repository
        self.sample_files = ["test1.py", "test2.txt", "test3.md"]
        for file in self.sample_files:
            with open(os.path.join(self.repo_path, file), 'w') as f:
                f.write(f"Sample content for {file}")

        self.deeplake_path = "./deeplake_test"

    def tearDown(self):
        # Cleanup after tests
        for file in self.sample_files:
            os.remove(os.path.join(self.repo_path, file))
        os.rmdir(self.repo_path)

    @patch("db.utils.DeepLake")  # Mock the DeepLake class to prevent actual DB calls
    def test_save_to_db(self, MockDeepLake):
        # Create a mock instance of DeepLake
        mock_deeplake = MockDeepLake()

        # Call the save_to_db function
        save_to_db(self.repo_path, self.deeplake_path)

        # Verify that add_documents was called on the mock instance for each file
        self.assertEqual(mock_deeplake.add_documents.call_count, len(self.sample_files))

if __name__ == "__main__":
    unittest.main()
