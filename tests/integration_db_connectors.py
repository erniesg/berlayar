import os
import unittest
import shutil
from db.connectors import ingest_git_repo

class TestIngestGitRepoBehavior(unittest.TestCase):

    def setUp(self):
        self.repo_url = 'https://github.com/erniesg/berlayar.git'
        self.base_path = './test_repos'

    def tearDown(self):
        # Cleanup by removing the specific cloned repo folder after test
        raw_data_path = os.path.join(self.base_path, '..', 'raw_data', 'git')
        repo_name = self.repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_directory = os.path.join(raw_data_path, repo_name)
        if os.path.exists(repo_directory):
            shutil.rmtree(repo_directory)

    def test_ingest_git_repo_behavior(self):
        # Call the ingest function
        commit_folder_path = ingest_git_repo(self.repo_url, self.base_path)

        # Extract repo name from the URL
        repo_name = self.repo_url.rstrip('/').split('/')[-1].replace('.git', '')

        # Extract commit ID from the commit folder path
        commit_id = os.path.basename(commit_folder_path)

        print(f"Fetched repo URL: {self.repo_url}")
        print(f"Fetched latest commit ID: {commit_id}")
        print(f"Cloned to: {commit_folder_path}")
        print("Test completed")
        print("Test files removed")

        # Assert that the cloned repo exists at the returned path
        self.assertTrue(os.path.exists(commit_folder_path))

        # Check the repo directory exists
        raw_data_path = os.path.join(self.base_path, '..', 'raw_data', 'git')
        repo_directory = os.path.join(raw_data_path, repo_name)
        self.assertTrue(os.path.exists(repo_directory))

        # Assert that the commit ID directory exists inside the repo directory
        commit_directory = os.path.join(repo_directory, commit_id)
        self.assertTrue(os.path.exists(commit_directory))

        # Optionally, check for certain known files/structures within the commit ID directory
        # For example:
        # self.assertTrue(os.path.exists(os.path.join(commit_directory, "some_known_file.txt")))
