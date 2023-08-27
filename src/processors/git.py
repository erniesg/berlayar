from src.utils.utils import get_last_processed_commit, save_last_processed_commit
import os

def process_git_repository_files(repo_path, file_processors, commit_id=None):
    """
    Process files in the git repository.
    """
    if repo_path is None:
        raise ValueError("You must ingest the repository before processing its files.")

    last_commit = get_last_processed_commit()
    if last_commit == commit_id:
        print("No new commits found. Exiting...")
        return

    all_files = [os.path.join(dirpath, file) for dirpath, _, filenames in os.walk(repo_path) for file in filenames]

    for file_path in all_files:
        file_extension = os.path.splitext(file_path)[1]
        if file_extension in file_processors:
            processor = file_processors[file_extension]
            documents = processor.process(file_path, commit_id=commit_id)
            # Handle saving of documents to database or any other operation

    # Update the last processed commit ID after successfully processing the files.
    save_last_processed_commit(commit_id)
