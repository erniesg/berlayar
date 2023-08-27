# berlayar > tests > unit > test_sources > test_git.py

import pytest
from src.sources.git import GitRepoSource
from unittest.mock import patch, Mock

def test_ingest():
    # Arrange
    repo_url = "mock_repo_url"
    base_path = "mock_base_path"
    token = "mock_token"
    mock_ingested_repo_path = "mock_ingested_repo_path"

    source = GitRepoSource(repo_url, base_path, token)

    # Mock the ingest_git_repo function to return our mock_ingested_repo_path
    with patch("src.sources.git.ingest_git_repo", return_value=mock_ingested_repo_path) as mock_ingest_git_repo, \
         patch("src.sources.git.process_files_and_print") as mock_process_files_and_print:

        # Act
        result = source.ingest()

        # Assert
        mock_ingest_git_repo.assert_called_once_with(repo_url, base_path, token)
        mock_process_files_and_print.assert_called_once_with(repo_url, base_path, mock_ingested_repo_path)
        assert source.repo_path == mock_ingested_repo_path
