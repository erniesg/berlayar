import os
import json
from src.models import gpt_semantics

# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"DEBUG: Current script directory: {script_dir}")

# Set the path for the .jsonl file
fixture_path = os.path.join(script_dir, '..', 'fixtures', 'weibo_en.jsonl')

def test_process_input_translation():
    print("\n[TEST SEMANTIC EXTRACTION]")

    # Print the path for debugging
    print(f"Using fixture path: {fixture_path}\n")

    # Load and process each line in the .jsonl file
    with open(fixture_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Convert the line string to a dictionary
            weibo_data = json.loads(line.strip())

            # Extract semantics using the gpt_semantics module
            extracted_data = gpt_semantics.process_weibo_data(weibo_data)

            # Print the input and output data for debugging
            print("=== INPUT ===")
            print(weibo_data)
            print("\n=== OUTPUT ===")
            print(extracted_data)
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_process_input_translation()
