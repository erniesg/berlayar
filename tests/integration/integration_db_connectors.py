import os
import unittest
import shutil
from db.connectors import ingest_git_repo  # Adjust the import path based on your project structure

class TestIngestGitRepoBehavior(unittest.TestCase):

    def setUp(self):
        self.repo_url = 'https://github.com/erniesg/berlayar.git'
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Use the directory above the test script as base path
        self.raw_data_path = os.path.join(self.base_path, 'raw_data', 'git')
        self.repo_name = self.repo_url.rstrip('/').split('/')[-1].replace('.git', '')

    def tearDown(self):
        # Cleanup by removing the entire test directory after test
        if os.path.exists(self.raw_data_path):
            shutil.rmtree(self.raw_data_path)

    def test_ingest_git_repo_behavior(self):
        # Call the ingest function
        commit_folder_path = ingest_git_repo(self.repo_url, self.base_path)

        # Extract commit ID from the commit folder path
        commit_id = os.path.basename(commit_folder_path)

        print(f"Fetched repo URL: {self.repo_url}")
        print(f"Fetched latest commit ID: {commit_id}")
        print(f"Cloned to: {commit_folder_path}")
        print("Test completed")

        # Check if the commit ID directory exists inside the repo directory
        commit_id_path = os.path.join(self.raw_data_path, 'git', self.repo_name, commit_id)
        print(f"Commit ID path: {commit_id_path}")
        print(f"Commit folder path: {commit_folder_path}")
        print(f"Commit directory exists: {os.path.exists(commit_id_path)}")

        # Print the contents of the commit directory
        print(f"Contents of {commit_id_path}:")
        for root, dirs, files in os.walk(commit_id_path):
            for name in files:
                print(os.path.join(root, name))
            for name in dirs:
                print(os.path.join(root, name))

        # Assert that the contents of the commit directory match the cloned repo
        for root, _, files in os.walk(commit_id_path):
            for file in files:
                self.assertTrue(os.path.exists(os.path.join(commit_folder_path, file)))

if __name__ == '__main__':
    unittest.main()
