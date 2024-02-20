from dotenv import load_dotenv
from google.cloud import secretmanager
import os

# Set the working directory to the directory where the .env file is located
os.chdir("/Users/erniesg/code/erniesg/berlayar")

# Load .env file to retrieve the project ID
load_dotenv()

# Retrieve the project ID from the environment variables
project_id = os.getenv('GOOGLE_PROJECT_ID')

# Check if the project ID is retrieved successfully
if project_id:
    print(f"Google Cloud project ID: {project_id}")
else:
    raise ValueError("GOOGLE_PROJECT_ID environment variable not found in .env file.")

class GoogleSecretsConfigLoader:
    def __init__(self, project_id):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

    def get(self, key: str) -> str:
        try:
            # Build the secret name using the provided project ID and secret ID
            secret_name = f"projects/{self.project_id}/secrets/{key}/versions/latest"
            # Access the latest version of the secret
            response = self.client.access_secret_version(request={"name": secret_name})
            # Return the decoded secret payload
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error fetching secret '{key}' from Google Secrets: {e}")
            return ""
