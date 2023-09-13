import json
import re
import os
from typing import List
from src.base_classes import FileProcessor
from dotenv import load_dotenv, find_dotenv

class Janitor(FileProcessor):
    def __init__(self, key_to_clean: str):
        self.key_to_clean = key_to_clean

    def process(self, file_path: str, *args, **kwargs) -> List[str]:
        cleaned_texts = []

        with open(file_path, 'r', encoding="utf-8") as file:
            for line in file:
                data = json.loads(line)
                text_content = data.get(self.key_to_clean, "")

                print(f"Input Text: {text_content}")

                cleaned_text = self._clean_text(text_content)
                print(f"Cleaned Text: {cleaned_text}\n")

                cleaned_texts.append(cleaned_text)

        return cleaned_texts

    def _clean_text(self, text: str) -> str:
        # Remove URLs
        text = re.sub(r'http\S+', '', text)

        # Remove any non-Chinese characters
        text = re.sub(r'[^\u4e00-\u9fff\s]', '', text)

        # Remove extra spaces
        text = ' '.join(text.split())

        return text

def main():
    # Locate the .env file
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("Error: .env file not found.")
        return

    # Load .env file
    load_dotenv(dotenv_path)
    print(f"Located .env file at: {dotenv_path}")

    # Use environment variables to construct file path
    DEFAULT_BASE_PATH = os.getenv("DEFAULT_BASE_PATH")
    if not DEFAULT_BASE_PATH:
        print("Error: BASE_DIR not found in the .env file or its value is empty.")
        return

    relative_path = "raw_data/weibo_old/InterContinental Hotels Group/Holiday Inn/tweet_spider_by_keyword_20230914024410.jsonl"
    file_path = os.path.join(DEFAULT_BASE_PATH, relative_path)

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Specify the key to clean
    key_to_clean = "content"
    if not key_to_clean:
        print("Error: Key to clean is not specified.")
        return

    # Instantiate the Janitor class and call process on the desired file
    janitor = Janitor(key_to_clean)
    try:
        cleaned_texts = janitor.process(file_path)
    except Exception as e:
        print(f"Error while processing file: {e}")

if __name__ == "__main__":
    main()
