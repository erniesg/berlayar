import os
from src.base_classes import DataSource
from src.utils.connectors import ingest_git_repo, process_files_and_print
from src.utils.metadata_git import get_repository_metadata
from src.processors.git import process_git_repository_files
import git

class GitRepoSource(DataSource):
    """
    Represents a git repository as a data source.
    """

    def __init__(self, repo_url, base_path, token=None, file_processors=None, test_mode=False):
        self.repo_url = repo_url
        self.base_path = base_path
        self.token = token
        self.repo_path = None  # Initialize repo_path to None
        self.clone_path = None  # Initialize clone_path to None
        self.file_processors = file_processors
        self.test_mode = test_mode

    def ingest(self):
        """
        Ingest data from the git repository.
        """
        print(f"Before calling ingest_git_repo, clone_path: {self.clone_path}")
        self.repo_path, self.clone_path = ingest_git_repo(self.repo_url, self.base_path, self.token, self.test_mode)
        print(f"After calling ingest_git_repo, clone_path: {self.clone_path}")

        if self.clone_path:  # If clone path exists, set the commit_id
            repo = git.Repo(self.clone_path)
            self.commit_id = repo.head.commit.hexsha
            # Print the latest commit after fetching
            print("Latest commit after fetching: ", self.commit_id)
            # Print the last few commit messages
            self.print_last_few_commits(self.clone_path)

        success = process_files_and_print(self.repo_url, self.base_path, self.repo_path, self.clone_path)

        if not success:
            print(f"Failed to process files for repository: {self.repo_url} at commit: {self.commit_id}")
        else:
            print(f"Successfully processed files for repository: {self.repo_url} at commit: {self.commit_id}")

        print("Ingestion completed.")
        return success

    def print_last_few_commits(self, repo_path, n=5):
        """Print the last n commits from the repo."""
        repo = git.Repo(repo_path)
        default_branch = repo.head.ref.name  # Get the default branch name
        commits = list(repo.iter_commits(default_branch, max_count=n))
        for commit in commits:
            print(commit.message)

    def get_metadata(self):
        """
        Retrieve metadata for the git repository.
        """
        return get_repository_metadata(self.repo_url, self.base_path)

    def process_repo_files(self, commit_id=None):
        """
        Process files in the git repository.
        """
        process_git_repository_files(self.repo_path, self.file_processors, commit_id)
