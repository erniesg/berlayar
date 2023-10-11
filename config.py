
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = "https://berlayar-test.vault.azure.net/"
# Authentication
credentials = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credentials)

# Fetch secrets
ACTIVELOOP_TOKEN = client.get_secret("ACTIVELOOP-TOKEN").value;
OPENAI_API_KEY = client.get_secret("OPENAI-API-KEY").value;
HUGGINGFACE_TOKEN = client.get_secret("HUGGINGFACE-TOKEN").value
EMAIL_PASSWORD = client.get_secret("EMAIL-PASSWORD").value
GITHUB_TOKEN = client.get_secret("GITHUB-TOKEN").value
GITHUB_TEST_TOKEN = client.get_secret("GITHUB-TEST-TOKEN").value
AZURE_STORAGE_CONNECTION_STRING = client.get_secret("AZURE-STORAGE-CONNECTION-STRING").value
AZURE_SUBSCRIPTION_ID = client.get_secret("AZURE-SUBSCRIPTION-ID").value

# Constants (These are not secrets, so we define them directly)
JSON_PATH = '../../../raw_data/arm_template/ARMTemplateForFactory.json'
DEEPLAKE_PATH = 'hub://erniesg/test-search'
CLONE_PATH = 'erniesg'
DEFAULT_REPO_URL = 'https://github.com/erniesg/berlayar.git'
DEFAULT_BASE_PATH = './'
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_USER = 'ernie@codefor.asia'
IMAGE_DIR = 'raw_data/ngs'
PROCESSED_IMAGE_DIR = 'raw_data/processed'
SPREADSHEET_PATH = 'raw_data'
FIXTURES_PATH = 'tests/fixtures'
BPE_PATH = '../ImageBind/bpe/bpe_simple_vocab_16e6.txt.gz'
AZURE_STORAGE_CONTAINER_NAME = 'berlayar'
AZURE_RESOURCE_GROUP_NAME = 'berlayar-dev'
AZURE_STORAGE_ACCOUNT_NAME = 'berlayar'
AZURE_STORAGE_LOCATION = 'southeastasia'
DEFAULT_ID_COLUMNS = 'Accession No.,ID,Filename'