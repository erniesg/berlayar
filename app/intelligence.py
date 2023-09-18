import os
import json
import jieba
import re
import requests
import uuid

# Constants for translation API， update the below
# KEY = "{}"
# ENDPOINT = "{}"
# LOCATION = "southeastasia"
# PATH = "/translate"
CONSTRUCTED_URL = ENDPOINT + PATH

BASE_DIR = "/home/erniesg/code/erniesg/berlayar/raw_data/weibo"

def translate_text(text):
    params = {
        'api-version': '3.0',
        'from': 'zh',
        'to': ['en']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': KEY,
        'Ocp-Apim-Subscription-Region': LOCATION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': text}]
    response = requests.post(CONSTRUCTED_URL, params=params, headers=headers, json=body)

    if response.status_code != 200:
        print(f"Translation API error: {response.text}")
        return text

    result = response.json()
    if result and 'translations' in result[0] and result[0]['translations']:
        return result[0]['translations'][0]['text']
    else:
        print(f"Unexpected response structure: {result}")
        return text

def clean_and_segment_content(data):
    content = data.get("content", "")

    content_segmented = ' '.join(jieba.cut(content, cut_all=False))
    content_cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', content_segmented)

    data["content"] = translate_text(content_cleaned)

    # Iterate over other key-value pairs and translate if the value is in Mandarin
    for key, value in data.items():
        if isinstance(value, str) and any('\u4e00' <= char <= '\u9fff' for char in value):
            data[key] = translate_text(value)

    return data

def process_jsonl_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    translated_lines = []
    for line in lines:
        data = json.loads(line.strip())
        translated_data = clean_and_segment_content(data)
        translated_lines.append(json.dumps(translated_data))

    output_file = filepath.replace('.jsonl', '_en.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in translated_lines:
            f.write(f"{line}\n")

def process_all_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".jsonl") and not file.endswith("_en.jsonl"):  # Avoid processing already processed files
                filepath = os.path.join(root, file)
                print(f"Processing file: {filepath}")
                process_jsonl_file(filepath)

if __name__ == "__main__":
    process_all_files(BASE_DIR)
