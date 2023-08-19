import os
import random
import git
from langchain.document_loaders import TextLoader
from langchain.vectorstores import DeepLake
from langchain.embeddings import HuggingFaceEmbeddings
from db.chunk import process_python_file
import shutil
from dotenv import load_dotenv
from db.connectors import ingest_git_repo

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
active_loop_token = os.environ.get('ACTIVELOOP_TOKEN')

def save_to_db(repo_url, deeplake_path, sample=False):
    """
    Save the entire or a sample of Git directory files to DeepLake.

    :param repo_url: The URL of the Git repository.
    :param deeplake_path: The DeepLake dataset path.
    :param sample: Whether to only process a single sampled file. Default is False.
    :return: None
    """
    # Clone the git repository
    repo_path = ingest_git_repo(repo_url, base_path='./temp')  # Temporary base_path
    print(f"Cloned repository to: {repo_path}")

    # List of file extensions to be considered
    allowed_extensions = ['.py']  # Considering only Python files for now

    # Get all files from the repo directory
    all_files = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        for file in filenames:
            file_extension = os.path.splitext(file)[1]
            if file_extension in allowed_extensions:
                all_files.append(os.path.join(dirpath, file))

    # If sample flag is set, randomly choose a file
    files_to_process = random.sample(all_files, 1) if sample else all_files

    # Initialize DeepLake
    db = DeepLake(dataset_path=deeplake_path, token=active_loop_token,
                  embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

    for file in files_to_process:
        try:
            # Extract code chunks using the process_python_file function
            chunks = process_python_file(file, repo=repo_path)  # Updated this line

            # Save each chunk with its metadata to DeepLake
            for chunk in chunks:
                # Convert chunk metadata and code to text format for saving
                text = f"{chunk['name']} ({chunk['start_line']} - {chunk['end_line']}):\n{chunk['code']}"
                print("Chunk Metadata:", chunk)  # Add this line
                db.add_documents([text], metadata=chunk)  # Save with metadata

        except Exception as e:
            print(f"Error processing file {file}: {e}")

    # Clean up the cloned repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    print(f"Saved chunks from {len(files_to_process)} files from {repo_url} to DeepLake dataset at {deeplake_path}")
