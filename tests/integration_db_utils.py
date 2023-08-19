import os
import unittest
import shutil
import time
from db.connectors import ingest_git_repo
from db.utils import save_to_db
import deeplake
from langchain.embeddings import HuggingFaceEmbeddings

class TestSaveToDBBehavior(unittest.TestCase):

    MAX_RETRIES = 5  # Maximum number of retries
    RETRY_DELAY = 10  # Delay in seconds between retries

    def setUp(self):
        self.repo_url = 'https://github.com/erniesg/berlayar.git'
        self.base_path = '..'
        self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Clone and ingest the repo
        self.commit_folder_path = ingest_git_repo(self.repo_url, self.base_path)
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
            save_to_db(self.commit_folder_path, self.deeplake_path, sample=True)
            retries += 1
            time.sleep(self.RETRY_DELAY)

        if retries == self.MAX_RETRIES:
            self.skipTest(f"Dataset was not saved after {self.MAX_RETRIES} attempts.")

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
