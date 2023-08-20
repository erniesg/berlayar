import os
import random
import git
from langchain.vectorstores import DeepLake
from langchain.embeddings import HuggingFaceEmbeddings
from chunk import process_python_file
import shutil
from dotenv import load_dotenv
from connectors import ingest_git_repo

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
active_loop_token = os.environ.get('ACTIVELOOP_TOKEN')

def save_to_db(repo_url, target_path, base_path, sample=False):
    """
    Save the entire or a sample of Git directory files to DeepLake.

    :param repo_url: The URL of the Git repository.
    :param target_path: The DeepLake target path.
    :param sample: Whether to only process a single sampled file. Default is False.
    :return: None
    """
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)

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

    # Initialize DeepLake with the target path
    db = DeepLake(dataset_path=target_path, token=active_loop_token,
                  embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

    # Process each .py file and extract chunks with metadata
    total_py_files_processed = 0
    all_documents = []

    for file in files_to_process:
        try:
            # Extract code chunks using the process_python_file function
            documents = process_python_file(file, repo=repo_path)

            # Print the file type and a sample document
            if documents:
                doc = documents[0]  # Take the first document as a sample
                file_type = "Valid" if isinstance(doc, dict) and 'page_content' in doc and 'metadata' in doc else "Invalid"
                print(f"File Type: {file_type}")
                print("Sample Document:", doc)

                # Add the documents to the list
                all_documents.extend(documents)
            else:
                print("No valid documents extracted from", file)

        except Exception as e:
            print(f"Error processing file {file}: {e}")

        total_py_files_processed += 1

    # Add the documents (chunks) to the DeepLake dataset
    if all_documents:
        print("Adding documents to DeepLake dataset:", all_documents)
        # Add the documents (chunks) to the DeepLake dataset
        for document in all_documents:
            try:
                page_content = document.get('page_content', '')
                metadata = document.get('metadata', '')

                if page_content:
                    db.add_texts([page_content], metadatas=[metadata])
                    print("Added document to DeepLake:", metadata['name'])

            except Exception as e:
                print("Error adding document to DeepLake:", e)

    print(f"Saved chunks from {total_py_files_processed} files from {repo_url} to DeepLake dataset at {target_path}")
