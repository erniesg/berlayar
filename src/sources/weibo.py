import os
from src.base_classes import DataSource
from dotenv import load_dotenv
from pathlib import Path
from app.config import ORGANIZATIONS

class WeiboSource(DataSource):
    def __init__(self):
        # Load environment variables from .env file two levels up
        dotenv_path = Path("../../.env")
        load_dotenv(dotenv_path=dotenv_path)

        # Load the base path
        self.base_path = os.getenv('DEFAULT_BASE_PATH', './')

    def ingest(self, org_name, brand_name, start_date, end_date):
        # Ensure the provided organization exists in the ORGANIZATIONS dictionary
        if org_name not in ORGANIZATIONS:
            print(f"Organization {org_name} not found in ORGANIZATIONS.")
            return

        # Ensure the provided brand name exists in the "en" list of the given organization
        if brand_name not in ORGANIZATIONS[org_name]["en"]:
            print(f"Brand {brand_name} not found under {org_name} in ORGANIZATIONS.")
            return

        # Get the corresponding index of the English brand name from the "en" list
        brand_index = ORGANIZATIONS[org_name]["en"].index(brand_name)

        # Use the index to get the Chinese keyword from the "zho" list
        keyword_zho = ORGANIZATIONS[org_name]["zho"][brand_index]

        # Run the spider using the Chinese keyword
        self.run_weibo_spider(keyword_zho, start_date, end_date, org_name=org_name, brand_name=brand_name)

    def run_weibo_spider(self, keyword, start_date, end_date, org_name=None, brand_name=None):
        # Change directory to the spider's directory using relative path.
        cmd = f"cd {self.base_path}/../WeiboSpider/weibospider && python run_spider.py tweet_by_keyword \"{keyword}\" \"{start_date}\" \"{end_date}\""
        if org_name:
            cmd += f" --org_name \"{org_name}\""
        if brand_name:
            cmd += f" --brand_name \"{brand_name}\""
        # Print the command for verification
        print(f"Executing command: {cmd}")
        os.system(cmd)

    def get_metadata(self):
        # Just a placeholder. You'd replace this with actual metadata you want to fetch.
        metadata = {
            'API Version': '1.0',
            'Data Volume': 'Large',
            'Source': 'Weibo'
        }
        return metadata

# For testing purposes
# if __name__ == "__main__":
#     ws = WeiboSource()

#     # Call the ingest method with the arguments.
#     ws.ingest("Marriott International", "Ritz-Carlton", "2023-01-01 00:00:00", "2023-01-07 23:59:59")

def run_weibo_job_for_group():
    # Instantiate WeiboSource
    weibo_source = WeiboSource()

    # Fetch details for Marriott International from the ORGANIZATIONS dictionary
    marriott_details = ORGANIZATIONS.get("InterContinental Hotels Group")

    # If the details are found (which they should be in this case), loop through the brands and ingest data for each.
    if marriott_details:
        for brand_english, brand_mandarin in zip(marriott_details["en"], marriott_details["zho"]):
            # Start and end date are hardcoded for the demonstration. Change them accordingly.
            weibo_source.ingest("InterContinental Hotels Group", brand_english, "2023-01-01 00:00:00", "2023-01-07 23:59:59")
            # You'll see the command printed for each brand and, depending on the implementation of the spider, potentially more output.

if __name__ == '__main__':
    run_weibo_job_for_group()
