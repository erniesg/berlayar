import openai
from openai import OpenAI  # Import the OpenAI class
from berlayar.adapters.models.interface import GenerationInterface
from berlayar.utils.load_keys import get_api_key
from typing import Dict, Any

class GPT4Adapter(GenerationInterface):
    def __init__(self, model_name: str, **kwargs):
        self.api_key = get_api_key('OPENAI_API_KEY')
        self.model_name = model_name
        self.params = kwargs.get('params', {})
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str, additional_params: Dict[str, Any] = None, **kwargs) -> str:
        # Merge params from initialization with any additional parameters provided at runtime
        effective_params = {**self.params, **(additional_params or {})}

        # Construct the messages array with the system message and user prompt
        messages = [
            {"role": "system", "content": effective_params.get('system_message', "You are a helpful assistant.")},
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
        raise NotImplementedError("GPT-4 does not support image generation.")

    def generate_audio(self, prompt: str, params: Dict[str, Any] = None) -> str:
        raise NotImplementedError("GPT-4 does not support audio generation.")
