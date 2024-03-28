import openai
from openai import OpenAI  # Import the OpenAI class
from berlayar.adapters.models.interface import GenerationInterface
from berlayar.utils.load_keys import get_api_key
from typing import Dict, Any

class KimiAdapter(GenerationInterface):
    def __init__(self, model_name: str, **kwargs):
        self.api_key = get_api_key(kwargs.get('api_key_env', 'KIMI_API_KEY'))
        self.model_name = model_name
        self.params = kwargs.get('params', {})
        # Use the base_url if provided in kwargs, otherwise default to OpenAI's base URL
        self.base_url = kwargs.get('base_url', 'https://api.openai.com/v1')
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_text(self, prompt: str, additional_params: Dict[str, Any] = None, **kwargs) -> str:
        # Merge params from initialization with any additional parameters provided at runtime
        effective_params = {**self.params, **(additional_params or {})}

        # Construct the messages array with the system message and user prompt
        messages = [
            {"role": "system", "content": effective_params.get('system_message', "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。")},
            {"role": "user", "content": prompt}
        ]

        # Prepare API call parameters, ensuring 'model' is not duplicated
        api_call_params = {
            "model": self.model_name,
            "messages": messages,
            **{k: v for k, v in effective_params.items() if k not in ['system_message', 'model_name']}
        }

        # Make the API call using the OpenAI client
        response = self.client.chat.completions.create(**api_call_params)

        return response.choices[0].message.content.strip()

    def generate_image(self, prompt: str, params: Dict[str, Any] = None) -> str:
        raise NotImplementedError("Kimi does not support image generation.")

    def generate_audio(self, prompt: str, params: Dict[str, Any] = None) -> str:
        raise NotImplementedError("Kimi does not support audio generation.")
