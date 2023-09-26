from dotenv import dotenv_values, set_key
import config
# Define a dictionary with the environment variables you want to set
env_variables = {
   "JSON_PATH":'../../../raw_data/arm_template/ARMTemplateForFactory.json',
    "DEEPLAKE_PATH":'hub://erniesg/test-search',
    "CLONE_PATH":'erniesg',
    "DEFAULT_REPO_URL" : 'https://github.com/erniesg/berlayar.git',
    "DEFAULT_BASE_PATH" : './',
    "SMTP_SERVER" : 'smtp.office365.com',
    "SMTP_PORT" : 587,
    "EMAIL_USER" : 'ernie@codefor.asia',
    "IMAGE_DIR" : 'raw_data/ngs',
    "PROCESSED_IMAGE_DIR" : 'raw_data/processed',
    "SPREADSHEET_PATH" : 'raw_data',
    "FIXTURES_PATH" : 'tests/fixtures',
    "BPE_PATH" : '../ImageBind/bpe/bpe_simple_vocab_16e6.txt.gz',
    "AZURE_STORAGE_CONTAINER_NAME" : 'berlayar',
    "AZURE_RESOURCE_GROUP_NAME" : 'berlayar-dev',
    "AZURE_STORAGE_ACCOUNT_NAME" : 'berlayar',
    "AZURE_STORAGE_LOCATION" : 'southeastasia',
    "DEFAULT_ID_COLUMNS" : 'Accession No.,ID,Filename',
    "OPENAI_API_KEY":f'{config.OPENAI_API_KEY}',
    "ACTIVELOOP_TOKEN" : f'{config.ACTIVELOOP_TOKEN}',
    "HUGGINGFACE_TOKEN" : f'{config.HUGGINGFACE_TOKEN}',
    "EMAIL_PASSWORD" : f'{config.EMAIL_PASSWORD}',
    "GITHUB_TOKEN" : f'{config.GITHUB_TOKEN}',
    "GITHUB_TEST_TOKEN" : f'{config.GITHUB_TEST_TOKEN}',
    "AZURE_STORAGE_CONNECTION_STRING" : f'{config.AZURE_STORAGE_CONNECTION_STRING}',
    "AZURE_SUBSCRIPTION_ID" : f'{config.AZURE_SUBSCRIPTION_ID}',
    # Add more variables as needed
}

# Path to the .env file you want to generate (create if it doesn't exist)
env_file_path = ".env"

# Load the existing .env file (if any)
existing_env = dotenv_values(env_file_path)

# Update or add the new environment variables
for key, value in env_variables.items():
    value=str(value)
    set_key(env_file_path, key, value)

print("Generated .env file with the following content:")
with open(env_file_path, "r") as file:
    print(file.read())