import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='../../.env')

# Assign the API key to openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai_function(messages, functions):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    return response["choices"][0]["message"]

def translate_with_openai(content, source_language="zh", target_language="en"):
    functions = [
        {
            "name": "translate_text",
            "description": "Translate the given text from source to target language.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate."
                    },
                    "source_language": {
                        "type": "string",
                        "description": "Source language code."
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Target language code."
                    }
                },
                "required": ["text", "source_language", "target_language"]
            }
        }
    ]
    messages = [
        {"role": "user", "content": content},
        {"role": "system", "content": f"Translate from {source_language} to {target_language}"}
    ]
    response = call_openai_function(messages, functions)
    return response["content"]

def extract_semantics_with_openai(content):
    functions = [
        {
            "name": "extract_semantics",
            "description": "Extract sentiment and related information from the content for cultural insights in the hotel industry",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Translated text to process for sentiment and entities"
                    }
                },
                "required": ["text"],
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "gen_semantics": {
                            "type": "object",
                            "properties": {
                                "entities": {
                                    "type": "object",
                                    "properties": {
                                        "people": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "location": {
                                            "type": "object",
                                            "properties": {
                                                "country": {"type": "string"},
                                                "province": {"type": "string"},
                                                "city": {"type": "string"},
                                                "village": {"type": "string"},
                                                "street": {"type": "string"}
                                            }
                                        },
                                        "events": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "brands": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                },
                                "semantic_info": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "number", "minimum": 1, "maximum": 5, "description": "Content sentiment towards the establishment, from 1 (very negative) to 5 (very positive)"},
                                        "confidence": {"type": "number"}
                                    }
                                },
                                "ad": {
                                    "type": "object",
                                    "properties": {
                                        "is_ad": {"type": "number"},
                                        "confidence": {"type": "number"}
                                    }
                                },
                                "spam": {
                                    "type": "object",
                                    "properties": {
                                        "is_spam": {"type": "number"},
                                        "confidence": {"type": "number"}
                                    }
                                },
                                "user_type": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["person", "government", "company", "celebrity", "unknown"], "description": "Estimated Weibo account type based on the context of the conversation"},
                                        "confidence": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ]
    messages = [{"role": "user", "content": content}]
    response = call_openai_function(messages, functions)
    # Extract semantic data from the response
    return response
