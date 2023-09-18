import os
import json

# Define the base path
BASE_PATH = "/home/erniesg/code/erniesg/berlayar/raw_data/weibo/"

def process_jsonl_file(filepath, organisation, brand):
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())

            # Add the organisation and brand to each entry here
            entry["organisation"] = organisation
            entry["brand"] = brand
            entries.append(entry)
    return entries

def consolidate_all_files(base_path):
    all_entries = []

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith("_en.jsonl"):
                print(f"Processing file: {file}")
                # ... (rest of the code inside this loop remains unchanged)

    return all_entries

# Run the function
all_entries = consolidate_all_files(BASE_PATH)

# Write the consolidated entries to a new JSONL file
output_file_path = "/home/erniesg/code/erniesg/berlayar/raw_data/weibo/consolidated_file.jsonl"
with open(output_file_path, "w", encoding="utf-8") as f:
    for entry in all_entries:
        f.write(json.dumps(entry) + '\n')

print(f"Consolidation complete! File saved at {output_file_path}")
