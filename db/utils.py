import os
import random
from langchain.document_loaders import TextLoader
from langchain.vectorstores import DeepLake
from langchain.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
active_loop_token = os.environ.get('ACTIVELOOP_TOKEN')

def save_to_db(repo_path, deeplake_path, sample=False):
    """
    Save the entire or a sample of Git directory files to DeepLake.

    :param repo_path: The path to the cloned repository.
    :param deeplake_path: The DeepLake dataset path.
    :param sample: Whether to only process a single sampled file. Default is False.
    :return: None
    """
    # List of file extensions to be considered
    allowed_extensions = ['.py', '.ipynb', '.md', '.txt', '.json', '.csv']  # Add more if needed

    # Get all files from the repo directory
    all_files = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        for file in filenames:
            file_extension = os.path.splitext(file)[1]
            if file_extension in allowed_extensions:
                all_files.append(os.path.join(dirpath, file))

    # If sample flag is set, randomly choose a file
    files_to_process = random.sample(all_files, 1) if sample else all_files

    # Load files and save to DeepLake
    db = DeepLake(dataset_path=deeplake_path, token=active_loop_token, embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

    for file in files_to_process:
        loader = TextLoader(file, encoding='utf-8')
        try:
            texts = loader.load_and_split()
            db.add_documents(texts)
        except Exception as e:
            print(f"Error loading file {file}: {e}")

    print(f"Saved {len(files_to_process)} files from {repo_path} to DeepLake dataset at {deeplake_path}")
