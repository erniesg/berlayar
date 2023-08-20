import os
import git
import shutil
from dotenv import load_dotenv, find_dotenv
import random
from chunks import process_python_file

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

def ingest_git_repo(repo_url, base_path, token=None):
    """
    Clone or pull the latest from a git repository, copy only .py files, and return the path to the location where they are saved.
    """
    repo_name, repo_path = get_repo_name_and_path(repo_url, base_path)

    # Check if the repo already exists
    if os.path.exists(repo_path):
        # If the repo exists, perform a git pull to get the latest
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.pull()
    else:
        # If the repo doesn't exist, clone it
        if token:
            git.cmd.Git().clone(repo_url, repo_path, depth=1, branch='master', config=f"http.extraheader='AUTHORIZATION: bearer {token}'")
        else:
            git.Repo.clone_from(repo_url, repo_path)

    # Copy .py files to a separate directory
    commit_id = git.Repo(repo_path).head.commit.hexsha
    commit_id_directory = os.path.join(os.path.dirname(repo_path), commit_id)
    if not os.path.exists(commit_id_directory):
        os.makedirs(commit_id_directory)
    copy_py_files(repo_path, commit_id_directory)

    return commit_id_directory

def streamlined_connector_workflow():
    config = get_configurations()
    repo_url = input(f"Enter the repository URL (or press Enter to use default: {config['DEFAULT_REPO_URL']}): ") or config['DEFAULT_REPO_URL']
    base_path = input(f"Enter the base path (or press Enter to use default: {config['DEFAULT_BASE_PATH']}): ") or config['DEFAULT_BASE_PATH']
    token = config["GITHUB_TOKEN"]

    repo_path = ingest_git_repo(repo_url, base_path, token)
    process_files_and_print(repo_url, base_path, repo_path)

def process_files_and_print(repo_url, base_path, repo_path):
    repo_name, _ = get_repo_name_and_path(repo_url, base_path)
    repo = git.Repo(os.path.join(repo_path, '.git'))
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

def print_chunk(chunk):
    print(f"Sample Chunk:")
    print(f"UUID: {chunk['uuid']}")
    print(f"Name: {chunk['name']}")
    print(f"Code:\n{chunk['code']}")
    print(f"Start Line: {chunk['start_line']}")
    print(f"End Line: {chunk['end_line']}")
    print(f"Parent: {chunk['parent']}")
    if 'object_id' in chunk:
        print(f"Object ID: {chunk['object_id']}")
    if 'commit_id' in chunk:
        print(f"Commit ID: {chunk['commit_id']}")
    print("-" * 40)

# If this script is executed directly, run the main workflow
if __name__ == "__main__":
    streamlined_connector_workflow()
