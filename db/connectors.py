import os
import git
import shutil

def ingest_git_repo(repo_url, base_path, token=None):
    """
    Clone a git repository and store it in the desired structure.

    :param repo_url: The URL of the git repository.
    :param base_path: The base path where the repo will be cloned.
    :param token: Optional GitHub personal access token for private repositories.
    :return: The path to the cloned repository.
    """
    # Extract repo name from the URL
    print(f"Received repo URL: {repo_url}")

    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')

    # Create the raw_data > git > repo_name > clone structure
    repo_path = os.path.join(base_path, 'raw_data', 'git', repo_name, 'clone')
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    # Clone the repo into the repo_name > clone folder
    if token:
        git.cmd.Git().clone(repo_url, repo_path, depth=1, branch='master', config=f"http.extraheader='AUTHORIZATION: bearer {token}'")
    else:
        git.Repo.clone_from(repo_url, repo_path)

    # Get the latest commit ID
    repo = git.Repo(repo_path)
    commit_id = repo.head.commit.hexsha

    # Create the repo_name > commit_id structure
    commit_id_path = os.path.join(base_path, 'raw_data', 'git', repo_name, commit_id)
    os.makedirs(commit_id_path)

    # Move the cloned contents to the commit_id folder
    for item in os.listdir(repo_path):
        item_path = os.path.join(repo_path, item)
        if '.git' in item:
            print(f"Skipping: {item}")
        else:
            destination_path = os.path.join(commit_id_path, item)
            if os.path.isdir(item_path):
                print(f"Moving directory: {item_path} to {destination_path}")
                shutil.move(item_path, destination_path)
            else:
                print(f"Moving file: {item_path} to {destination_path}")
                shutil.move(item_path, destination_path)

    # Remove the clone directory
    shutil.rmtree(repo_path)

    return commit_id_path
