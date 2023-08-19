import unittest
from unittest.mock import patch, MagicMock, call
from db.utils import save_to_db

class TestSaveToDB(unittest.TestCase):
    @patch('db.utils.git.Repo')  # Mock the git.Repo class
    @patch('db.utils.random.sample')  # Mock the random.sample function
    @patch('db.utils.DeepLake')  # Mock the DeepLake class
    @patch('db.utils.HuggingFaceEmbeddings')  # Mock the HuggingFaceEmbeddings class
    @patch('db.utils.process_python_file')  # Mock the process_python_file function
    def test_save_to_db(self, mock_process, mock_embed, mock_deeplake, mock_random, mock_repo):
        # Mock instances and setup
        mock_repo_instance = MagicMock()
        mock_embed_instance = MagicMock()
        mock_deeplake_instance = MagicMock()

        # Mock random.sample to return a predefined repo path
        mock_random.return_value = ['/fake/repo/path']

        mock_repo.return_value = mock_repo_instance
        mock_embed.return_value = mock_embed_instance
        mock_deeplake.return_value = mock_deeplake_instance

        # Set up the mock_process return value
        mock_chunks = [
            {"name": "chunk1", "start_line": 1, "end_line": 5, "code": "code1"},
            {"name": "chunk2", "start_line": 10, "end_line": 15, "code": "code2"}
        ]
        mock_process.return_value = mock_chunks

        # Call the function you want to test
        repo_path = "/fake/repo/path"
        deeplake_path = "/fake/deeplake/path"
        save_to_db(repo_path, deeplake_path, sample=True)

        # Debugging and assertions
        mock_process.assert_called_once_with("/fake/repo/path", repo=mock_repo_instance)
        # ... rest of the assertions ...

if __name__ == '__main__':
    unittest.main()
