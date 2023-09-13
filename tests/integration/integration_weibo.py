import unittest
import os
import json
import random
from src.sources.weibo import WeiboSource
from app.config import ORGANIZATIONS

class TestWeiboIntegration(unittest.TestCase):

    def setUp(self):
        self.weibo = WeiboSource()

    def test_brands_and_retrieve_tweets(self):
        # Randomly select one organization
        random_company = random.choice(list(ORGANIZATIONS.keys()))
        details = ORGANIZATIONS[random_company]

        for idx, brand_english in enumerate(details["en"]):
            brand_mandarin = details["zho"][idx]

            # Retrieve tweets
            self.weibo.ingest(random_company, brand_english, "2023-01-01 00:00:00", "2023-01-07 23:59:59")

            # Determine the directory for the JSONL file
            final_directory = os.path.join(self.weibo.base_path, "raw_data", "weibo", random_company, brand_english)

            # Get the latest file in the directory
            list_of_files = [os.path.join(final_directory, file) for file in os.listdir(final_directory) if os.path.isfile(os.path.join(final_directory, file))]
            if not list_of_files:
                self.fail(f"No files found in directory: {final_directory}")

            latest_file = max(list_of_files, key=os.path.getctime)

            # Check the existence of the file
            self.assertTrue(os.path.exists(latest_file), msg=f"No recent file found in {final_directory} for {brand_mandarin}!")

            # Print the head of the JSONL file (Optional for verifying content)
            with open(latest_file, 'r', encoding='utf-8') as f:
                for _ in range(5):  # print first 5 lines as a sample
                    line = f.readline().strip()
                    if line:  # Check if line is not empty
                        tweet = json.loads(line)
                        print(tweet)

if __name__ == '__main__':
    unittest.main()
