import openai
from dotenv import load_dotenv
import os
import re
import json
import glob
import string

# Define the path for the .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '..', '..', '.env')

# Debug: Print the path to check if it's correct
print(f"DEBUG: Loading environment variables from: {env_path}")

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=env_path)

# Assign the API key to openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# Debug: Print if the API key is loaded or not
if openai.api_key:
    print("DEBUG: OpenAI API Key loaded successfully.")
else:
    print("DEBUG: Failed to load OpenAI API Key.")

def contains_chinese(s):
    """Check if a string contains Chinese characters."""
    return bool(re.search('[\u4e00-\u9fa5]', s))

import jieba

def preprocess_mandarin(text):
    # Remove special characters (punctuation)
    text = ''.join(ch for ch in text if ch not in string.punctuation)

    # Remove emojis
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    # Use Jieba to segment the text
    text = ' '.join(jieba.cut(text, cut_all=False))

    return text

def translate_text(text):
    """Translate a given text using OpenAI."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that translates Mandarin content about hotels from Weibo to English."},
        {"role": "user", "content": f"Translate the following content from Mandarin to English: {text}"}
    ]

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content

def process_input(input_data):
    if not isinstance(input_data, dict):
        return {"error": "Expected input data to be a dictionary."}

    for key, value in input_data.items():
        if isinstance(value, str) and contains_chinese(value):
            translated_value = translate_text(value)
            input_data[key] = translated_value
        elif isinstance(value, dict):  # If the value is a nested dictionary, process it recursively
            input_data[key] = process_input(value)

    return input_data

def translate_weibo_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Convert the line string to a dictionary
            weibo_data = json.loads(line.strip())

            # Translate the content using the process_input function
            translated_data = process_input(weibo_data)

            # Write the translated data to the new .jsonl file
            outfile.write(json.dumps(translated_data) + '\n')

    print(f"Translation completed. Output written to: {output_path}")

def get_organisation_and_brand_from_path(path):
    """Extract Organisation Name and Brand Name from the file path."""
    parts = path.split(os.sep)
    # Assuming the structure is always .../Organisation/Brand/filename.jsonl
    organisation_name = parts[-3]
    brand_name = parts[-2]
    return organisation_name, brand_name

def translate_all_files_in_directory():
    # Adjusted path to be relative to project root
    root_dir = os.path.join(script_dir, '..', '..', 'raw_data', 'weibo')

    # Search for all .jsonl files in the directory
    files = glob.glob(os.path.join(root_dir, '**', '*.jsonl'), recursive=True)

    aggregated_data = []

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as infile:
            content = infile.read().strip()
            weibo_data = json.loads(content)
            translated_data = process_input(weibo_data)

            # Extract Organisation and Brand name and add to translated data
            organisation_name, brand_name = get_organisation_and_brand_from_path(file_path)
            translated_data['Organisation Name'] = organisation_name
            translated_data['Brand Name'] = brand_name

            # Save the translated content to a new file in the same directory
            output_path = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).replace('.jsonl', '_en.jsonl'))
            with open(output_path, 'w', encoding='utf-8') as outfile:
                outfile.write(json.dumps(translated_data) + '\n')

            # Add translated data to aggregated data
            aggregated_data.append(translated_data)

    # Save aggregated data to a single .jsonl file in the root_dir
    aggregated_file_path = os.path.join(root_dir, 'aggregated_translated_data.jsonl')
    with open(aggregated_file_path, 'w', encoding='utf-8') as agg_file:
        for data in aggregated_data:
            agg_file.write(json.dumps(data) + '\n')

    print(f"Translation and aggregation completed. Aggregated data written to: {aggregated_file_path}")

# Call the function
translate_all_files_in_directory()
