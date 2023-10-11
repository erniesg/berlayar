import os
from dotenv import load_dotenv
from db.connectors import ingest_git_repo
from db.chunks import process_python_file, extract_chunks_from_code
from db.utils import save_to_db, get_last_processed_commit, save_last_processed_commit
import git

def main():
    try:
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(dotenv_path)

        repo_url = input(f"Enter the repository URL (or press Enter to use default: {os.getenv('DEFAULT_REPO_URL')}): ") or os.getenv("DEFAULT_REPO_URL")
        base_path = input(f"Enter the base path (or press Enter to use default: {os.getenv('DEFAULT_BASE_PATH')}): ") or os.getenv("DEFAULT_BASE_PATH")
        token = os.getenv("GITHUB_TOKEN")
        repo_path = ingest_git_repo(repo_url, base_path, token)
        print(f"Copied .py files from repository to: {repo_path}")

        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = os.path.join(os.path.dirname(os.path.abspath(base_path)), 'raw_data', 'git', repo_name)

        repo = git.Repo(os.path.join(repo_path, '.git'))
        commit_id = repo.head.commit.hexsha
        last_commit_id = get_last_processed_commit()

        if commit_id != last_commit_id:
            new_files = []
            sample = True  # Default to sample one file
            if last_commit_id:  # If there's a previously processed commit
                new_files = repo.git.diff('--name-only', last_commit_id, commit_id).split()
                user_input = input("Do you want to process new files? (y/n/1 for sampling one file): ").strip().lower()

                if user_input == 'y':
                    sample = False
                elif user_input == '1':
                    sample = True
                else:
                    print("Exiting without processing.")
                    return
            else:  # If it's the first run
                new_files = [item.path for item in repo.head.commit.tree.traverse() if item.type == 'blob' and item.path.endswith('.py')]
                print("First run detected. Sampling one file by default.")

            if new_files:
                print(f"New commit detected: {commit_id} (Last processed: {last_commit_id or 'None'})")
                print("New files:")
                print('\n'.join(new_files))
                deeplake_path = f"hub://erniesg/test0820_{repo_name}_{commit_id}" if commit_id else None
                save_to_db(repo_url, deeplake_path, base_path, sample=sample, commit_id=commit_id)
                save_last_processed_commit(commit_id)  # Save the commit ID after processing
            else:
                print("No new files detected since the last processed commit.")
        else:
            print("Current commit matches the last processed commit. No new files to process.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
