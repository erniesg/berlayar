import os
import unittest
from unittest.mock import patch, Mock

from db.connectors import ingest_git_repo  # Replace with the appropriate import path

class TestIngestGitRepo(unittest.TestCase):

    FAKE_COMMIT_ID = "0ccd6791cc4a62367cb882a432750b2c8b464790"
    REPO_URL = "https://github.com/sample/repo.git"

    def setUp(self):
        self.temp_dir = "/tmp"  # You can change this to an actual temporary directory

    @patch('db.connectors.git.Repo')
    @patch('db.connectors.git.cmd.Git')
    def test_clone_existing_repo(self, mock_Git, mock_Repo):
        repo_name = 'berlayar'
        commit_id_path = os.path.join(self.temp_dir, 'raw_data', 'git', 'test_git', repo_name, self.FAKE_COMMIT_ID)

        # Mock the existence of the repository
        mock_Repo.return_value.exists.return_value = True
        mock_Repo.return_value.remote.return_value = Mock()
        mock_Repo.return_value.head.commit.hexsha = self.FAKE_COMMIT_ID  # Mock the commit ID

        # Call the function
        result = ingest_git_repo(self.REPO_URL, self.temp_dir)

        # Check if the correct paths are returned
        self.assertEqual(result, commit_id_path)

    # Add more tests as required...

if __name__ == "__main__":
    unittest.main()
