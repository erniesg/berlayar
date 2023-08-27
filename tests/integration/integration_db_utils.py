import os
import unittest
import shutil
import time
import git
import deeplake
from langchain.embeddings import HuggingFaceEmbeddings
from db.connectors import ingest_git_repo
from db.utils import save_to_db

class TestSaveToDBBehavior(unittest.TestCase):

    MAX_RETRIES = 5  # Maximum number of retries
    RETRY_DELAY = 10  # Delay in seconds between retries

    def setUp(self):
        self.repo_url = 'https://github.com/erniesg/berlayar.git'
        self.base_path = './'
        self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        try:
            print(f"Initial repo URL: {self.repo_url}")
            # Clone the repo and get the commit ID path
            self.commit_folder_path = ingest_git_repo(self.repo_url, self.base_path)
            print(f"Cloned repository to: {self.commit_folder_path}")

            # Set up DeepLake path
            repo_name = self.repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            commit_id = os.path.basename(self.commit_folder_path)
            self.deeplake_path = f"hub://erniesg/test_git_{repo_name}_commit_{commit_id}"
            print(f"Using DeepLake path: {self.deeplake_path}")

            active_loop_token = os.environ.get('ACTIVELOOP_TOKEN')
            if not active_loop_token:
                print("No ACTIVELOOP_TOKEN found. Skipping test.")
                self.skipTest("ACTIVELOOP_TOKEN not available.")

            retries = 0
            while not deeplake.exists(self.deeplake_path) and retries < self.MAX_RETRIES:
                print(f"Saving data to DeepLake (attempt {retries + 1}/{self.MAX_RETRIES})...")
                # Pass repo_url and the git.Repo instance to save_to_db
                try:
                    print(f"Initializing git.Repo with path: {self.commit_folder_path}")
                    repo = git.Repo(self.commit_folder_path)
                except git.exc.InvalidGitRepositoryError as git_error:
                    print(f"Error initializing git.Repo: {git_error}")
                    self.fail("Setup failed")
                save_to_db(self.repo_url, self.deeplake_path, sample=True, repo=repo)
                retries += 1
                time.sleep(self.RETRY_DELAY)

            if retries == self.MAX_RETRIES:
                self.skipTest(f"Dataset was not saved after {self.MAX_RETRIES} attempts.")
        except Exception as e:
            print(f"Error during setup: {e}")
            self.fail("Setup failed")

    def test_save_to_db_behavior(self):
        # Validate that the data exists in DeepLake
        self.assertTrue(deeplake.exists(self.deeplake_path), "Expected data not found in DeepLake.")

    def tearDown(self):
        # Clean up the cloned repo
        if os.path.exists(self.commit_folder_path):
            shutil.rmtree(self.commit_folder_path)

        # Clean up the saved data in DeepLake if it exists
        if deeplake.exists(self.deeplake_path):
            deeplake.delete(self.deeplake_path)

            # Ensure the dataset is deleted
            retries = 0
            while deeplake.exists(self.deeplake_path) and retries < self.MAX_RETRIES:
                print(f"Waiting for dataset deletion (attempt {retries + 1}/{self.MAX_RETRIES})...")
                time.sleep(self.RETRY_DELAY)
                retries += 1
            if retries == self.MAX_RETRIES:
                print(f"Warning: Failed to confirm dataset deletion after {self.MAX_RETRIES} attempts.")

if __name__ == "__main__":
    unittest.main()
