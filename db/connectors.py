import os
import git
import shutil
from dotenv import load_dotenv, find_dotenv
from chunk import process_python_file
import random

# Load environment variables from .env
load_dotenv(find_dotenv())

def copy_py_files(src_dir, dest_dir):
    """
    Recursively copy .py files from source directory to destination directory.

    :param src_dir: Source directory containing .py files.
    :param dest_dir: Destination directory.
    """
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, os.path.relpath(src_path, src_dir))
                dest_dirname = os.path.dirname(dest_path)
                os.makedirs(dest_dirname, exist_ok=True)
                shutil.copy2(src_path, dest_path)

def ingest_git_repo(repo_url=None, base_path=None, token=None):
    """
    Clone a git repository and copy only .py files into the desired structure.

    :param repo_url: The URL of the git repository.
    :param base_path: The base path where the repo will be cloned.
    :param token: Optional GitHub personal access token for private repositories.
    :return: The path to the cloned repository.
    """
    # Use default values from .env if not provided
    repo_url = repo_url or os.getenv("DEFAULT_REPO_URL")
    base_path = base_path or os.getenv("DEFAULT_BASE_PATH")

    if not repo_url or not base_path:
        raise ValueError("Repo URL and base path must be provided or set in .env")

    print(f"Using repo URL: {repo_url}")
    print(f"Using base path: {base_path}")

    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)

    print(f"Repo name: {repo_name}")
    print(f"Repo path: {repo_path}")

    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    # Clone the repo
    if token:
        print(f"Cloning with token")
        git.cmd.Git().clone(repo_url, repo_path, depth=1, branch='master', config=f"http.extraheader='AUTHORIZATION: bearer {token}'")
    else:
        print(f"Cloning without token")
        git.Repo.clone_from(repo_url, repo_path)

    # Move .py files to the commit_id directory one level up from repo_path
    commit_id = git.Repo(repo_path).head.commit.hexsha
    commit_id_directory = os.path.join(os.path.dirname(repo_path), commit_id)
    if not os.path.exists(commit_id_directory):
        os.makedirs(commit_id_directory)

    copy_py_files(repo_path, commit_id_directory)

    return commit_id_directory

# Usage example:
if __name__ == "__main__":
    repo_url = input(f"Enter the repository URL (or press Enter to use default: {os.getenv('DEFAULT_REPO_URL')}): ") or os.getenv("DEFAULT_REPO_URL")
    base_path = input(f"Enter the base path (or press Enter to use default: {os.getenv('DEFAULT_BASE_PATH')}): ") or os.getenv("DEFAULT_BASE_PATH")
    token = os.getenv("GITHUB_TOKEN")  # Optional, set in .env if needed
    repo_path = ingest_git_repo(repo_url, base_path, token)
    print(f"Copied .py files from repository to: {repo_path}")

    # Counters for tracking
    total_py_files_processed = 0
    total_chunks = 0
    all_chunks = []

    # Construct the repo path using the original logic
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)

    # Initialize repo from the .git directory
    repo = git.Repo(os.path.join(repo_path, '.git'))
    commit_id = repo.head.commit.hexsha

    # Process each .py file and extract chunks with metadata
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                total_py_files_processed += 1
                file_path = os.path.join(root, file)

                # Get the object ID for the file
                object_id = repo.git.hash_object(file_path)

                chunks = process_python_file(file_path, repo=repo, object_id=object_id, commit_id=commit_id)
                total_chunks += len(chunks)
                all_chunks.extend(chunks)

    print(f"Total number of .py files processed: {total_py_files_processed}")
    print(f"Total number of chunks generated: {total_chunks}")

    # Choose a random chunk for printing
    if all_chunks:
        random_chunk = random.choice(all_chunks)
        print(f"Sample Chunk:")
        print(f"UUID: {random_chunk['uuid']}")
        print(f"Name: {random_chunk['name']}")
        print(f"Code:\n{random_chunk['code']}")
        print(f"Start Line: {random_chunk['start_line']}")
        print(f"End Line: {random_chunk['end_line']}")
        print(f"Parent: {random_chunk['parent']}")
        if 'object_id' in random_chunk:
            print(f"Object ID: {random_chunk['object_id']}")
        if 'commit_id' in random_chunk:
            print(f"Commit ID: {random_chunk['commit_id']}")
        print("-" * 40)
