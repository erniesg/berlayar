import os
import json
from src.models import gpt
from dotenv import load_dotenv
import openai

# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the path for the .env file
env_path = os.path.join(script_dir, '..', '..', '.env')

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set the path for the .jsonl file
fixture_path = os.path.join(script_dir, '..', 'fixtures', 'weibo.jsonl')

# ------------------- Test for Translation -------------------

def test_translation():
    # Print the path for debugging
    print(f"Using fixture path: {fixture_path}")

    # Load the .jsonl file
    with open(fixture_path, "r") as file:
        for line_no, line in enumerate(file, 1):
            data = json.loads(line)
            content = data["content"]

            print(f"Processing Line {line_no} for Translation...")

            # Call the translation function
            try:
                translated_content = gpt.translate_with_openai(content)

                # Print results for validation
                print("Original Content:", content)
                print("Translated Content:", translated_content)

            except Exception as e:
                print(f"Error processing line {line_no} for translation. Error: {e}")

            print("--------")


# ------------------- Test for Semantic Generation -------------------

def test_semantic_extraction():
    # Print the path for debugging
    print(f"Using fixture path: {fixture_path}")

    # Load the .jsonl file
    with open(fixture_path, "r") as file:
        for line_no, line in enumerate(file, 1):
            data = json.loads(line)
            content = data["content"]

            print(f"Processing Line {line_no} for Semantic Extraction...")

            # Call the translation function (assuming semantics is based on translated content)
            try:
                translated_content = gpt.translate_with_openai(content)

                # Call the semantics extraction function on the translated content
                semantics = gpt.extract_semantics_with_openai(translated_content)

                # Print results for validation
                print("Translated Content:", translated_content)
                print("Semantics:", semantics)

            except Exception as e:
                print(f"Error processing line {line_no} for semantic extraction. Error: {e}")

            print("--------")

if __name__ == "__main__":
    # Run the tests
    print("Starting Translation Test...\n")
    test_translation()

    print("\nStarting Semantic Extraction Test...\n")
    test_semantic_extraction()
