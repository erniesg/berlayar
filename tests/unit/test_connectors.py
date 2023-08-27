import os
import unittest
from unittest.mock import patch, Mock
import shutil
import tempfile
from db.connectors import ingest_git_repo

class TestIngestGitRepo(unittest.TestCase):
    # Repository URL and commit ID as class-level constants
    REPO_URL = 'https://github.com/erniesg/berlayar.git'
    FAKE_COMMIT_ID = '0ccd6791cc4a62367cb882a432750b2c8b464790'

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('db.connectors.git.Repo')
    @patch('db.connectors.git.cmd.Git')
    def test_clone_existing_repo(self, mock_Git, mock_Repo):
        repo_name = 'berlayar'
        commit_id_path = os.path.join(self.temp_dir, 'raw_data', 'git', 'test_git', repo_name, self.FAKE_COMMIT_ID)

        # Mock the existence of the repository
        mock_Repo.return_value.exists.return_value = True
        mock_Repo.return_value.remote.return_value = Mock()

        # Call the function
        result = ingest_git_repo(self.REPO_URL, self.temp_dir)

        # Check if the correct paths are returned
        self.assertEqual(result, commit_id_path)
        mock_Git.assert_not_called()
        mock_Repo.assert_called_once_with(commit_id_path)
        mock_Repo.return_value.remote.assert_called_once_with(name='origin')
        mock_Repo.return_value.remote.return_value.pull.assert_called_once()

    @patch('db.connectors.git.Repo')
    @patch('db.connectors.git.cmd.Git')
    def test_clone_new_repo(self, mock_Git, mock_Repo):
        repo_name = 'berlayar'
        commit_id_path = os.path.join(self.temp_dir, 'raw_data', 'git', 'test_git', repo_name, self.FAKE_COMMIT_ID)

        # Mock the non-existence of the repository
        mock_Repo.return_value.exists.return_value = False
        mock_Repo.return_value.remote.return_value = Mock()

        # Call the function
        result = ingest_git_repo(self.REPO_URL, self.temp_dir)

        # Check if the correct paths are returned
        self.assertEqual(result, commit_id_path)
        mock_Git().clone.assert_called_once_with(
            self.REPO_URL, commit_id_path, depth=1, branch='master')
        mock_Repo.assert_called_once_with(commit_id_path)
        mock_Repo.return_value.remote.assert_not_called()

if __name__ == '__main__':
    unittest.main()
