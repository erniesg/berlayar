import pytest
import os
import shutil
from dotenv import load_dotenv, find_dotenv
from src.sources.git import GitRepoSource
from src.utils.utils import get_last_processed_commit
import git
import time

# Load environment variables from .env
load_dotenv(find_dotenv())

# Constants
TEST_PUBLIC_REPO_URL = os.getenv("DEFAULT_REPO_URL")
TEST_BASE_PATH = os.getenv("DEFAULT_BASE_PATH")
TEST_PRIVATE_REPO_URL = "https://github.com/NationalGallerySingapore/NationalGalleryDWH-ADF"
TEST_REPO_FOR_NEW_COMMIT = "https://github.com/erniesg/test-repo.git"  # Replace with your test repo
TEST_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_TEST_TOKEN = os.getenv("GITHUB_TEST_TOKEN")  # Ensure this token has write permissions to the test repo

def extract_repo_name_from_url(url):
    """Extracts the repository name from the given URL."""
    return url.rstrip('/').split('/')[-1].replace('.git', '')

def test_ingest_public_repo():
    try:
        source = GitRepoSource(TEST_PUBLIC_REPO_URL, TEST_BASE_PATH, test_mode=True)
        result = source.ingest()
        repo_name = extract_repo_name_from_url(TEST_PUBLIC_REPO_URL)
        expected_sub_path = os.path.join("raw_data", "git", repo_name, "clone")
        print(f"Clone Directory: {source.clone_path}")
        assert result
        assert source.clone_path.endswith(expected_sub_path)
    except Exception as e:
        print(f"Error during test_ingest_public_repo: {e}")
        raise

def test_ingest_private_repo():
    try:
        source = GitRepoSource(TEST_PRIVATE_REPO_URL, TEST_BASE_PATH, token=TEST_TOKEN, test_mode=True)
        result = source.ingest()
        repo_name = extract_repo_name_from_url(TEST_PRIVATE_REPO_URL)
        expected_clone_path = os.path.join("raw_data", "git", repo_name, "clone")
        expected_commit_id_path = os.path.join("raw_data", "git", repo_name, source.commit_id)

        print(f"Clone Directory: {source.clone_path}")
        print(f"Commit ID Directory: {source.repo_path}")

        assert result
        assert source.clone_path.endswith(expected_clone_path)
        assert source.repo_path.endswith(expected_commit_id_path)
    except Exception as e:
        print(f"Error during test_ingest_private_repo: {e}")
        raise

def set_remote_with_token(repo, token, repo_url):
    """
    Set the remote URL to include the token for authentication.
    """
    repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
    repo.remote().set_url(repo_url_with_token)

def test_handle_new_commit():
    try:
        # Initialize the GitRepoSource instance
        source = GitRepoSource(TEST_REPO_FOR_NEW_COMMIT, TEST_BASE_PATH, test_mode=True)
        repo = git.Repo(source.clone_path)  # Get the repo object here
        initial_commit_id = get_last_processed_commit(repo=repo)

        # If initial_commit_id is None, it's the first-time ingestion
        if not initial_commit_id:
            handle_first_time_ingestion(source)
        else:
            # Call the subsequent ingestion function
            handle_subsequent_ingestion(source, initial_commit_id)

        # Compare files in clone and commitID directories
        compare_files_in_clone_and_commitID_directory(source)

    except Exception as e:
        print(f"Error during test_handle_new_commit: {e}")
        raise

def handle_first_time_ingestion(source):
    print("First-time ingestion of the test repository...")

    result = source.ingest()
    if not result:
        raise ValueError("Initial ingestion failed.")

    print(f"Initial ingestion result: {result}")
    commit_id = get_last_processed_commit()
    print(f"Initial commit ID after first-time ingestion: {commit_id}")

def handle_subsequent_ingestion(source, initial_commit_id):
    print("TEST_REPO_FOR_NEW_COMMIT:", TEST_REPO_FOR_NEW_COMMIT)
    print("TEST_BASE_PATH:", TEST_BASE_PATH)

    repo_path = source.clone_path
    print(f"Repo path for programmatically adding a new commit: {repo_path}")
    repo = git.Repo(repo_path)

    # Set the remote with the token for authentication
    set_remote_with_token(repo, GITHUB_TEST_TOKEN, TEST_REPO_FOR_NEW_COMMIT)

    new_file = add_new_python_file_to_repo(repo_path)
    repo.git.add(new_file)
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Added new test file for integration testing at {current_timestamp}"
    repo.git.commit("-m", commit_message)
    print(f"Added new file: {new_file} and committed.")

    # Push the new commit
    origin = repo.remote(name='origin')
    origin.push()
    time.sleep(5)
    source.print_last_few_commits(repo_path)

    result = source.ingest()
    if not result:
        raise ValueError("Subsequent ingestion failed after adding new commit.")

    print(f"Result after ingesting new commit: {result}")
    new_commit_id = get_last_processed_commit()

    # Here we expect that the new commit ID is different from the initial one
    if new_commit_id == initial_commit_id:
        pytest.fail("New commit ID should be different from the initial commit ID.")

def compare_files_in_clone_and_commitID_directory(source):
    repo_path = source.clone_path

    # Ensure we have a valid commit ID
    commit_id = get_last_processed_commit()
    if not commit_id:
        raise ValueError("Failed to retrieve the last processed commit ID.")

    commit_id_path = os.path.join(TEST_BASE_PATH, "raw_data", "git", extract_repo_name_from_url(TEST_REPO_FOR_NEW_COMMIT), commit_id)

    # Ensure the commit_id_path exists
    if not os.path.exists(commit_id_path):
        raise ValueError(f"Commit ID directory {commit_id_path} does not exist.")

    # Check that the new_commit_id directory only contains .py files
    for root, _, files in os.walk(commit_id_path):
        for file in files:
            assert file.endswith(".py"), f"Found non-Python file: {file}"

    # Print the paths being compared
    print(f"Comparing files in clone directory: {repo_path}")
    print(f"With files in commitID directory: {commit_id_path}")

    # Validate that all .py files in clone directory are present in commitID directory
    assert compare_files_in_clone_and_commitID(repo_path, commit_id_path), "Mismatch in .py files between clone and commitID directories"

def add_new_python_file_to_repo(repo_path):
    """
    Adds a new Python file to the repo for testing.
    """
    unique_content = f"""
# This is a test file for integration testing.
# Timestamp: {time.time()}

def test_function():
    return "Test Successful!"

if __name__ == "__main__":
    print(test_function())
"""
    filename = "test_file_{}.py".format(int(time.time()))
    print("Writing to file:", filename)
    print(unique_content)
    with open(os.path.join(repo_path, filename), 'w') as f:
        f.write(unique_content)
    return filename

def compare_files_in_clone_and_commitID(clone_path, commitID_path):
    """
    Compare .py files between clone and commitID directories.
    Returns True if the .py files in both directories are the same, else False.
    """
    clone_files = set()
    commitID_files = set()

    for root, _, files in os.walk(clone_path):
        for file in files:
            if file.endswith(".py"):
                clone_files.add(os.path.relpath(os.path.join(root, file), clone_path))

    for root, _, files in os.walk(commitID_path):
        for file in files:
            if file.endswith(".py"):
                commitID_files.add(os.path.relpath(os.path.join(root, file), commitID_path))

    return clone_files == commitID_files

# Teardown logic
def teardown_module(module):
    """Teardown logic to clean up the cloned repositories after tests."""
    for repo_url in [TEST_PUBLIC_REPO_URL, TEST_PRIVATE_REPO_URL, TEST_REPO_FOR_NEW_COMMIT]:
        repo_name = extract_repo_name_from_url(repo_url)
        path_to_remove = os.path.join(TEST_BASE_PATH, "raw_data", "git", repo_name)
        if os.path.exists(path_to_remove):
            shutil.rmtree(path_to_remove)
