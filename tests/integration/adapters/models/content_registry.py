import pytest
from berlayar.registry.content_strategy import ContentStrategyRegistry

@pytest.fixture
def content_registry():
    return ContentStrategyRegistry()

def test_gpt4_text_generation_default_params(content_registry):
    prompt = "What is the capital of France?"
    generated_text = content_registry.generate_text(prompt, "en")
    assert generated_text is not None
    assert isinstance(generated_text, str)
    assert len(generated_text.strip()) > 0
    print(f"GPT-4 generated text with default params: {generated_text}")

def test_gpt4_text_generation_custom_params(content_registry):
    prompt = "What is the capital of France?"
    params = {"max_tokens": 50, "temperature": 0.8}
    generated_text = content_registry.generate_text(prompt, "en", params)
    assert generated_text is not None
    assert isinstance(generated_text, str)
    assert len(generated_text.strip()) > 0
    print(f"GPT-4 generated text with custom params: {generated_text}")

def test_gpt4_text_generation_empty_prompt(content_registry):
    prompt = ""
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        content_registry.generate_text(prompt, "en")
    print("GPT-4 text generation with empty prompt handled correctly")

def test_kimi_text_generation_default_params(content_registry):
    prompt = "中国的首都是哪里?"
    generated_text = content_registry.generate_text(prompt, "zh")
    assert generated_text is not None
    assert isinstance(generated_text, str)
    assert len(generated_text.strip()) > 0
    print(f"Kimi generated text with default params: {generated_text}")

def test_kimi_text_generation_custom_params(content_registry):
    prompt = "中国的首都是哪里?"
    params = {"max_tokens": 50, "temperature": 0.8}
    generated_text = content_registry.generate_text(prompt, "zh", params)
    assert generated_text is not None
    assert isinstance(generated_text, str)
    assert len(generated_text.strip()) > 0
    print(f"Kimi generated text with custom params: {generated_text}")

def test_kimi_text_generation_empty_prompt(content_registry):
    prompt = ""
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        content_registry.generate_text(prompt, "zh")
    print("Kimi text generation with empty prompt handled correctly")

def test_dalle3_image_generation_default_params(content_registry):
    prompt = "A beautiful sunset over the ocean"
    generated_image_url = content_registry.generate_image(prompt)
    assert generated_image_url is not None
    assert isinstance(generated_image_url, str)
    assert len(generated_image_url.strip()) > 0
    print(f"DALL-E 3 generated image URL with default params: {generated_image_url}")

def test_dalle3_image_generation_custom_params(content_registry):
    prompt = "A beautiful sunset over the ocean"
    params = {"n": 2, "size": "512x512"}
    generated_image_url = content_registry.generate_image(prompt, params)
    assert generated_image_url is not None
    assert isinstance(generated_image_url, str)
    assert len(generated_image_url.strip()) > 0
    print(f"DALL-E 3 generated image URL with custom params: {generated_image_url}")
