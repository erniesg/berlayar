import unittest
from unittest.mock import patch, MagicMock, ANY  # <-- Import ANY here
import os

# Import the ingest_git_repo function from connectors.py
from db.connectors import ingest_git_repo

class TestIngestGitRepo(unittest.TestCase):

    @patch('db.connectors.git.Repo')
    @patch('db.connectors.git.cmd.Git')
    @patch('db.connectors.os')
    @patch('db.connectors.shutil.copytree')  # Mock the shutil.copytree method
    def test_ingest_git_repo(self, mock_copytree, mock_os, mock_git_cmd, mock_git_repo):
        # Mock the necessary methods and attributes
        mock_os.path.exists.return_value = False
        mock_git_repo.return_value.head.commit.hexsha = '1234567890abcdef'
        mock_os.path.join.side_effect = os.path.join

        # Call the function
        repo_url = "https://github.com/example/testrepo.git"
        base_path = "/path/to/base"
        final_path = ingest_git_repo(repo_url, base_path)

        # Assert that the returned path is not None
        self.assertIsNotNone(final_path)

        # Assert that the copytree function was called to copy the repo contents to the commit_id folder
        expected_repo_path = os.path.join(base_path, '..', 'raw_data', 'git', 'testrepo')
        expected_commit_id_path = os.path.join(expected_repo_path, '1234567890abcdef')
        mock_copytree.assert_called_once_with(expected_repo_path, expected_commit_id_path, ignore=ANY)

if __name__ == '__main__':
    unittest.main()
