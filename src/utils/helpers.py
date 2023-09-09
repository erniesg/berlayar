import subprocess
import json
import os
from dotenv import load_dotenv
import shutil
import sys

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

class AzureHelper:
    def __init__(self):
        self.env_file_path = dotenv_path
        self.env_backup_path = os.path.join(os.path.dirname(dotenv_path), '.env_backup')

    def backup_env_file(self):
        try:
            shutil.copy(self.env_file_path, self.env_backup_path)
        except Exception as e:
            print(f"Error backing up .env file: {str(e)}")

    def restore_env_file(self):
        try:
            shutil.copy(self.env_backup_path, self.env_file_path)
        except Exception as e:
            print(f"Error restoring .env file: {str(e)}")

    def login_to_azure_interactively(self):
        try:
            subprocess.run(["az", "login"], check=True)
            print("Azure login successful.")
            return True
        except subprocess.CalledProcessError:
            print("Azure login failed.")
            return False

    def get_azure_subscription_details(self):
        try:
            result = subprocess.run(["az", "account", "show", "--output", "json"], check=True, capture_output=True, text=True)
            subscription_info = result.stdout.strip()
            if subscription_info:
                return json.loads(subscription_info)
            else:
                print("No valid Azure subscription found.")
                return None
        except subprocess.CalledProcessError:
            print("Failed to check Azure subscription.")
            return None

    def validate_azure_connection(self):
        if self.login_to_azure_interactively():
            subscription_details = self.get_azure_subscription_details()
            if subscription_details:
                print("Azure subscription is valid.")
                return subscription_details
        print("Azure connection validation failed.")
        return None

    def update_env_variable(self, key, value):
        with open(self.env_file_path, 'r') as file:
            lines = file.readlines()

        with open(self.env_file_path, 'w') as file:
            for line in lines:
                if line.startswith(key):
                    file.write(f"{key}={value}\n")
                else:
                    file.write(line)

    def update_env_file_with_azure_details(self, subscription_details):
        storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        try:
            result = subprocess.run(["az", "storage", "account", "show-connection-string", "--name", storage_account_name, "--output", "tsv"], check=True, capture_output=True, text=True)
            connection_string = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Failed to retrieve connection string. Error: {e}")
            return

        self.update_env_variable("AZURE_SUBSCRIPTION_ID", subscription_details.get('id'))
        self.update_env_variable("AZURE_STORAGE_CONNECTION_STRING", connection_string)

        self.print_last_four_chars("AZURE_SUBSCRIPTION_ID")
        self.print_last_four_chars("AZURE_STORAGE_CONNECTION_STRING")

    def cleanup_resources(self):
        storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        storage_container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        try:
            subprocess.run(["az", "storage", "container", "delete", "--name", storage_container_name, "--account-name", storage_account_name, "--auth-mode", "key"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during cleanup: {e}")

    def create_azure_resources(self):
        resource_group_name = os.getenv("AZURE_RESOURCE_GROUP_NAME")
        storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        storage_location = os.getenv("AZURE_STORAGE_LOCATION")
        storage_container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        rg_exists = subprocess.run(["az", "group", "exists", "--name", resource_group_name], capture_output=True, text=True).stdout.strip().lower()

        if rg_exists == "false":
            subprocess.run(["az", "group", "create", "--name", resource_group_name, "--location", storage_location], check=True)

        storage_name_check = subprocess.run(["az", "storage", "account", "check-name", "--name", storage_account_name], capture_output=True, text=True).stdout
        storage_name_available = json.loads(storage_name_check)["nameAvailable"]

        if storage_name_available:
            subprocess.run(["az", "storage", "account", "create", "--name", storage_account_name, "--resource-group", resource_group_name, "--location", storage_location, "--sku", "Standard_LRS"], check=True)

        # Fetch the connection string
        try:
            result = subprocess.run(["az", "storage", "account", "show-connection-string", "--name", storage_account_name, "--output", "tsv"], check=True, capture_output=True, text=True)
            connection_string = result.stdout.strip()
            masked_connection_string = '*' * (len(connection_string) - 4) + connection_string[-4:]  # Mask all but the last 4 characters
            print(f"Using connection string: {masked_connection_string}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to retrieve connection string. Error: {e}")
            return

        # Create the storage container using the fetched connection string
        subprocess.run(["az", "storage", "container", "create", "--name", storage_container_name, "--account-name", storage_account_name, "--connection-string", connection_string], check=True)

        print("Azure resources created or already exist.")

    def print_last_four_chars(self, key):
        value = os.getenv(key)
        if value:
            print(f"{key} (last 4 characters): {value[-4:]}")

if __name__ == '__main__':
    azure_helper = AzureHelper()

    azure_helper.backup_env_file()
    subscription_details = azure_helper.validate_azure_connection()

    if subscription_details:
        azure_helper.create_azure_resources()
        azure_helper.update_env_file_with_azure_details(subscription_details)

        # Printing the last 4 characters for both values in all modes.
        azure_helper.print_last_four_chars("AZURE_SUBSCRIPTION_ID")
        azure_helper.print_last_four_chars("AZURE_STORAGE_CONNECTION_STRING")

        if len(sys.argv) > 1 and sys.argv[1] == "test":
            azure_helper.cleanup_resources()
            azure_helper.restore_env_file()
            print("Test mode: Resources cleaned up and .env restored.")

    os.remove(azure_helper.env_backup_path)
