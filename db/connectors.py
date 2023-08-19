import os
import git
import shutil

def ingest_git_repo(repo_url, base_path, token=None):
    """
    Clone or pull a git repository.

    :param repo_url: The URL of the git repository.
    :param base_path: The base path where the repo will be cloned.
    :param token: Optional GitHub personal access token for private repositories.
    :return: The path to the cloned repository.
    """
    # Extract repo name from the URL
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')

    raw_data_path = os.path.join(base_path, 'raw_data', 'git')
    if not os.path.exists(raw_data_path):
        os.makedirs(raw_data_path)

    repo_path = os.path.join(raw_data_path, repo_name)

    # Check if the repository exists locally
    if os.path.exists(repo_path):
        # If the repo directory already exists, pull the latest changes
        repo = git.Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.pull()
    else:
        # Clone the repo
        if token:
            git.cmd.Git().clone(repo_url, repo_path, depth=1, branch='master', config=f"http.extraheader='AUTHORIZATION: bearer {token}'")
        else:
            git.Repo.clone_from(repo_url, repo_path)

    commit_id = str(git.Repo(repo_path).head.commit.hexsha)
    commit_id_path = os.path.join(repo_path, commit_id)

    # Check if the commit_id directory already exists
    if not os.path.exists(commit_id_path):
        shutil.copytree(repo_path, commit_id_path,
                        ignore=shutil.ignore_patterns(commit_id, '.git'))

    return commit_id_path
