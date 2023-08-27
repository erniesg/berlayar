import os
import git
import shutil
from dotenv import load_dotenv, find_dotenv
import random
from src.utils.chunks_common import process_python_file
import traceback

# Load environment variables from .env
load_dotenv(find_dotenv())

def get_repo_name_and_path(repo_url, base_path):
    """
    Extracts the repo name and constructs the repo path based on the provided repo URL and base path.
    """
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)
    return repo_name, repo_path

def get_configurations():
    """
    Loads configuration values from environment or uses default.
    """
    return {
        "DEFAULT_REPO_URL": os.getenv("DEFAULT_REPO_URL"),
        "DEFAULT_BASE_PATH": os.getenv("DEFAULT_BASE_PATH"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
    }

def embed_token_in_url(url, token):
    """
    Embeds the token in the provided repository URL.
    """
    return url.replace("https://", f"https://{token}@")

def copy_py_files(src_dir, dest_dir):
    """
    Recursively copy .py files from source directory to destination directory.
    """
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, os.path.relpath(src_path, src_dir))
                dest_dirname = os.path.dirname(dest_path)
                os.makedirs(dest_dirname, exist_ok=True)
                shutil.copy2(src_path, dest_path)

def ingest_git_repo(repo_url, base_path, token=None, test_mode=False):
    repo_name, repo_base_path = get_repo_name_and_path(repo_url, base_path)
    clone_path = os.path.join(repo_base_path, "clone")

    # Embed token in repo URL if provided
    if token:
        modified_repo_url = embed_token_in_url(repo_url, token)
    else:
        modified_repo_url = repo_url

    if os.path.exists(clone_path):
        repo = git.Repo(clone_path)
        origin = repo.remote(name='origin')
        origin.pull()
    else:
        git.Repo.clone_from(modified_repo_url, clone_path)

    repo = git.Repo(clone_path)
    commit_id = repo.head.commit.hexsha
    default_branch = repo.active_branch.name

    commit_id_directory = os.path.join(repo_base_path, commit_id)
    if os.path.exists(commit_id_directory):
        if test_mode:
            pass
        else:
            response = input(f"The directory for commit ID {commit_id} already exists. Do you want to overwrite? (yes/no): ")
            if response.strip().lower() != "yes":
                print("Skipping copying files to commit ID directory.")
                return

    os.makedirs(commit_id_directory, exist_ok=True)
    copy_py_files(clone_path, commit_id_directory)
    print(f"In ingest_git_repo - commit_id_directory: {commit_id_directory}, clone_path: {clone_path}")
    return commit_id_directory, clone_path


def streamlined_connector_workflow():
    config = get_configurations()
    repo_url = input(f"Enter the repository URL (or press Enter to use default: {config['DEFAULT_REPO_URL']}): ") or config['DEFAULT_REPO_URL']
    base_path = input(f"Enter the base path (or press Enter to use default: {config['DEFAULT_BASE_PATH']}): ") or config['DEFAULT_BASE_PATH']
    token = config["GITHUB_TOKEN"]

    commit_id_directory, clone_path = ingest_git_repo(repo_url, base_path, token)
    process_files_and_print(repo_url, base_path, commit_id_directory, clone_path)

def process_files_and_print(repo_url, base_path, repo_path, clone_path):
    try:
        repo_name, _ = get_repo_name_and_path(repo_url, base_path)
        print(f"Repo Path: {repo_path}")
        repo = git.Repo(clone_path)
        commit_id = repo.head.commit.hexsha

        all_chunks = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    object_id = repo.git.hash_object(file_path)
                    chunks = process_python_file(file_path, repo=repo, object_id=object_id, commit_id=commit_id)
                    all_chunks.extend(chunks)

        # Random chunk printing
        if all_chunks:
            random_chunk = random.choice(all_chunks)
            print_chunk(random_chunk)

        return True  # Successfully processed

    except Exception as e:
        # Print the exception, traceback, and additional context information
        print(f"Error during process_files_and_print for file {file_path}: {e}")
        print(traceback.format_exc())  # Print the traceback for the exception
        return False  # Failed to process

def print_chunk(chunk):
    print(f"Sample Chunk:")

    if 'metadata' in chunk:
        metadata = chunk['metadata']

        uuid = metadata.get('uuid', "UUID not found in chunk.")
        name = metadata.get('name', "Name not found in chunk.")
        code = metadata.get('code', "Code not found in chunk.")
        start_line = metadata.get('start_line', "Start line not found in chunk.")
        end_line = metadata.get('end_line', "End line not found in chunk.")
        parent = metadata.get('parent', "Parent not found in chunk.")
        object_id = metadata.get('object_id', None)
        commit_id = metadata.get('commit_id', None)

        print(f"UUID: {uuid}")
        print(f"Name: {name}")
        print(f"Code:\n{code}")
        print(f"Start Line: {start_line}")
        print(f"End Line: {end_line}")
        print(f"Parent: {parent}")

        if object_id:
            print(f"Object ID: {object_id}")
        if commit_id:
            print(f"Commit ID: {commit_id}")

    else:
        print("Metadata not found in chunk.")

    print("-" * 40)

# If this script is executed directly, run the main workflow
if __name__ == "__main__":
    streamlined_connector_workflow()
