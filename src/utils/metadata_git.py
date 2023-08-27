import git
from src.utils.connectors import get_repo_name_and_path
import os

def get_repository_metadata(repo_url, base_path):
    """
    Retrieve metadata for the git repository.
    """
    repo_name, _ = get_repo_name_and_path(repo_url, base_path)
    repo = git.Repo(os.path.join(base_path, '.git'))
    return {
        "repo_name": repo_name,
        "commit_id": repo.head.commit.hexsha
    }
