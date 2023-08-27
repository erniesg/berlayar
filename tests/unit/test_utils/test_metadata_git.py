import pytest
from src.sources.git import GitRepoSource
from unittest.mock import patch

def test_get_metadata():
    # Sample values for the test
    sample_repo_url = "https://github.com/sample/repo.git"
    sample_base_path = "/sample/path"

    # Initialize GitRepoSource
    source = GitRepoSource(sample_repo_url, sample_base_path)

    # Mocking the external functions called within get_metadata
    with patch("src.utils.metadata_git.get_repo_name_and_path", return_value=("sample_repo", "/sample/repo/path")), \
         patch("git.Repo", return_value=MockRepo()):

        result = source.get_metadata()

    # Validate the results
    assert result == {
        "repo_name": "sample_repo",
        "commit_id": "sample_commit_id"
    }

class MockRepo:
    """A mock class to simulate the git.Repo class."""

    class Head:
        class Commit:
            hexsha = "sample_commit_id"

        commit = Commit()

    head = Head
