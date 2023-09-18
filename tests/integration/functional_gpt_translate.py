import os
import json
from src.models import gpt_translate

# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"DEBUG: Current script directory: {script_dir}")

# Set the path for the .jsonl file
fixture_path = os.path.join(script_dir, '..', 'fixtures', 'weibo.jsonl')

def test_process_input_translation():
    print("\n[TEST TRANSLATION]")

    # Print the path for debugging
    print(f"Using fixture path: {fixture_path}\n")

    # Load the .jsonl file
    with open(fixture_path, "r") as file:
        for line_no, line in enumerate(file, 1):
            data = json.loads(line)

            print(f"Processing Line {line_no} for Translation...")

            # Call the process_input function
            try:
                print("\n--- Input Data ---")
                print(data)

                translated_data = gpt_translate.process_input(data)

                print("\n--- Output Data ---")
                print(translated_data)

            except Exception as e:
                print(f"Error processing line {line_no}. Error: {e}")

            print("--------")

if __name__ == "__main__":
    # Run the test
    test_process_input_translation()
