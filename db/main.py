import os
import random
import git
from dotenv import load_dotenv
from connectors import ingest_git_repo
from chunk import process_python_file, extract_chunks_from_code
from utils import save_to_db

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    repo_url = input(f"Enter the repository URL (or press Enter to use default: {os.getenv('DEFAULT_REPO_URL')}): ") or os.getenv("DEFAULT_REPO_URL")
    base_path = input(f"Enter the base path (or press Enter to use default: {os.getenv('DEFAULT_BASE_PATH')}): ") or os.getenv("DEFAULT_BASE_PATH")

    token = os.getenv("GITHUB_TOKEN")  # Optional, set in .env if needed
    repo_path = ingest_git_repo(repo_url, base_path, token)
    print(f"Copied .py files from repository to: {repo_path}")
    # Construct the target path for saving the chunks
    commit_id = None

    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)

    try:
        # Initialize repo from the .git directory
        repo = git.Repo(os.path.join(repo_path, '.git'))
        commit_id = repo.head.commit.hexsha
    except git.InvalidGitRepositoryError:
        pass  # Handle the case where the repo is not available
    # Save chunks to DeepLake
    deeplake_path = f"hub://erniesg/dev_{repo_name}_{commit_id}" if commit_id else None
    save_to_db(repo_url, deeplake_path, base_path, sample=True)  # Pass the base_path

if __name__ == "__main__":
    main()
