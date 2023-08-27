from unittest.mock import patch, MagicMock
from src.sources.git import GitRepoSource

def test_process_repo_files():
    # Sample values for the test
    sample_repo_url = "https://github.com/sample/repo.git"
    sample_base_path = "/sample/path"

    # Initialize GitRepoSource
    source = GitRepoSource(sample_repo_url, sample_base_path)
    source.repo_path = "/sample/repo/cloned/path"  # Set a sample repo path

    # Mocking the external functions called within process_repo_files
    with patch("src.processors.git.get_last_processed_commit", return_value="old_commit_id"), \
         patch("os.walk", return_value=[("/sample/dir", [], ["sample.py"])]), \
         patch("src.processors.git.save_last_processed_commit") as mock_save_last_processed_commit:

        mock_processor = MagicMock()
        source.file_processors = {".py": mock_processor}

        source.process_repo_files(commit_id="new_commit_id")

    # Validate the mock function calls
    mock_processor.process.assert_called_once_with("/sample/dir/sample.py", commit_id="new_commit_id")
    mock_save_last_processed_commit.assert_called_once_with("new_commit_id")
