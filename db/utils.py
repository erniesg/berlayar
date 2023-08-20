import os
import random
from langchain.vectorstores import DeepLake
from langchain.embeddings import HuggingFaceEmbeddings
from chunks import process_python_file
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
active_loop_token = os.environ.get('ACTIVELOOP_TOKEN')
random.seed()

LAST_COMMIT_FILE_PATH = os.path.join(os.path.dirname(__file__), 'last_processed_commit.txt')

def get_last_processed_commit():
    if not os.path.exists(LAST_COMMIT_FILE_PATH):
        with open(LAST_COMMIT_FILE_PATH, 'w') as file:
            file.write("")
        return None

    with open(LAST_COMMIT_FILE_PATH, 'r') as file:
        return file.read().strip() or None

def save_last_processed_commit(commit_id):
    with open(LAST_COMMIT_FILE_PATH, 'w') as file:
        file.write(commit_id)

def save_to_db(repo_url, target_path, base_path, sample=False, commit_id=None):
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)

    last_commit = get_last_processed_commit()
    if last_commit == commit_id:
        print("No new commits found. Exiting...")
        return

    allowed_extensions = ['.py']

    all_files = []
    for dirpath, _, filenames in os.walk(repo_path):
        for file in filenames:
            if os.path.splitext(file)[1] in allowed_extensions:
                all_files.append(os.path.join(dirpath, file))

    print("All files being considered:", all_files)
    print(f"Total .py files found: {len(all_files)}")

    files_to_process = random.sample(all_files, 1) if sample else all_files

    db = DeepLake(dataset_path=target_path, token=active_loop_token,
                  embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

    total_py_files_processed = 0
    chunks_saved = 0  # Counter for the number of chunks saved
    all_documents = []

    for file in files_to_process:
        try:
            documents = process_python_file(file, repo=repo_path, commit_id=commit_id)
            for doc in documents:
                file_type = "Valid" if 'page_content' in doc and 'metadata' in doc else "Invalid"
                print(f"File Type: {file_type}")
                print("Sample Document:", doc)
            all_documents.extend(documents)
        except Exception as e:
            print(f"Error processing file {file}: {e}")

        total_py_files_processed += 1

        if all_documents:
            for document in all_documents:
                try:
                    page_content = document.get('page_content', '')
                    metadata = document.get('metadata', {})
                    if page_content:
                        db.add_texts([page_content], metadatas=[metadata])
                        print("Added document to DeepLake:", metadata['name'])
                        chunks_saved += 1  # Increment the counter when chunk is saved
                except Exception as e:
                    print("Error adding document to DeepLake:", e)

    print(f"Saved {chunks_saved} chunks from {total_py_files_processed} files from {repo_url} to DeepLake dataset at {target_path}")

    # Update the last processed commit ID after successfully processing the files.
    save_last_processed_commit(commit_id)
