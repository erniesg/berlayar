import chainlit as cl
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
import aiohttp
import re
from diffusers import AutoPipelineForText2Image
import torch
from chainlit.input_widget import Select  # NEW: Import Select from chainlit.input_widget
import json
from datetime import datetime
from PIL import Image

load_dotenv()

def get_absolute_path(relative_path):
    base_path = os.path.dirname(__file__)  # Get the directory of the current script
    absolute_path = os.path.join(base_path, relative_path)  # Construct the absolute path
    return os.path.abspath(absolute_path)  # Resolve any '..' components

def find_project_root(current_path, identifier):
    """
    Recursively searches for a directory containing the identifier starting from current_path and moving upwards.
    Returns the path to the directory if found, otherwise None.
    """
    if os.path.exists(os.path.join(current_path, identifier)):
        return current_path  # Identifier found, return current path
    parent_path = os.path.dirname(current_path)
    if parent_path == current_path:
        # Root of the filesystem reached without finding identifier
        return None
    return find_project_root(parent_path, identifier)  # Continue search in the parent directory

def get_project_root():
    """
    Finds the 'berlayar' project root based on a unique identifier.
    Adjust 'unique_identifier' as needed to match your project structure.
    """
    script_location = os.path.dirname(os.path.abspath(__file__))
    unique_identifier = '.env'  # Example identifier, change as needed
    project_root = find_project_root(script_location, unique_identifier)
    if project_root is None:
        raise Exception("Project root not found.")
    return project_root

def construct_path_from_root(relative_path):
    """
    Constructs an absolute path given a relative path from the project root.
    """
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)

def load_story_details():
    story_path = construct_path_from_root('raw_data/the_sound_of_stories/story.json')
    with open(story_path, 'r', encoding='utf-8') as file:
        story_data = json.load(file)
        return story_data

def load_instructions():
    instructions_path = construct_path_from_root('raw_data/instructions.json')
    with open(instructions_path, 'r', encoding='utf-8') as file:
        all_instructions = json.load(file)
        return all_instructions.get(current_language, all_instructions.get("en"))

current_language = "en"  # Default language. This should be updated based on user selection.
instructions = {}  # A dictionary to hold instructions based on the selected language
story_data = load_story_details()  # Assuming this loads the entire JSON content
# Initially defined at the global level
story_progress = {
    "current_checkpoint": 0
}

# Declare pipeline_text2image at the top level so it's accessible globally.
global pipeline_text2image
pipeline_text2image = None

def initialize_pipeline():
    global pipeline_text2image
    if pipeline_text2image is None:  # Check if pipeline_text2image has not been initialized
        # Automatically select device: MPS for Apple silicon, CUDA for NVIDIA GPUs, or CPU as a fallback
        if torch.cuda.is_available():
            device = "cuda"
            print("CUDA is available. Using CUDA for processing.")
            torch_dtype = torch.float16  # Use float16 for CUDA to utilize Tensor Cores on compatible GPUs
        elif torch.backends.mps.is_available():
            device = "mps"
            print("MPS is available. Using MPS (Metal Performance Shaders) for Apple silicon.")
            torch_dtype = torch.float32  # Use float16 for MPS (Apple silicon)
        else:
            device = "cpu"
            print("CUDA and MPS not available. Falling back to CPU.")
            torch_dtype = torch.float32  # Use float32 for CPU to avoid 'Half' precision issues

        # Instantiate the pipeline using the .from_pretrained() method
        pipeline_text2image = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch_dtype,
            use_safetensors=True  # Use SafeTensors to reduce memory footprint
        ).to(device)

        if device == "mps":
            # Recommended if your computer has < 64 GB of RAM and using MPS
            pipeline_text2image.enable_attention_slicing()

# Ensure initialize_pipeline is called before generate_and_display_cover_image
initialize_pipeline()

def remove_emojis(text):
    print(f"Before emoji removal: {text}")
    # Updated regex pattern to exclude common textual character ranges
    emoji_pattern = re.compile(
        "("
        "(\ud83d[\ude00-\ude4f])|"  # U+1F600 to U+1F64F emoticons
        "(\ud83c[\udf00-\udfff])|"  # U+1F300 to U+1F5FF symbols & pictographs
        "(\ud83d[\ude80-\udeff])|"  # U+1F680 to U+1F6FF transport & map symbols
        "(\ud83d[\udc00-\uddff])"   # U+1F700 to U+1F7FF alchemical symbols
        ")+", flags=re.UNICODE)
    text_sub = emoji_pattern.sub(r"", text)
    print(f"After emoji removal: {text_sub}")
    return text_sub

# Load environment variables and set the API key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in the .env file!")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

user_data = {}
# story_memory = ConversationBufferMemory(input_key='human_input', output_key='output')
narrative_memory = ConversationBufferMemory(input_key='user_response', output_key='story_segment')
story_started = False

# Update the send_audio function to use ElevenLabs API
async def send_audio(content):
    cleaned_content = remove_emojis(content)
    url = "https://api.elevenlabs.io/v1/text-to-speech/0M23V8kIecNGWiNzhRRn/stream"
    querystring = {"optimize_streaming_latency": "1"}

    model_id = "eleven_multilingual_v2"  # This model supports multiple languages, including Mandarin.

    payload = {
        "text": cleaned_content,
        "model_id": model_id,
    }

    if user_data.get('language') == 'zh':
        payload["language"] = "zh"

    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    if not elevenlabs_api_key:
        raise ValueError("ELEVENLABS API key not found in the .env file!")

    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }

    # Console message indicating that audio generation has started
    print("Starting audio generation...")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, params=querystring) as response:
            if response.status != 200:
                print(f"Error with ElevenLabs API: {await response.text()}")
                return None

            audio_data = await response.read()

            # Console message indicating that audio generation is completed
            print("Audio generation completed.")
            return cl.Audio(name="story_segment.mp3", content=audio_data, display="inline")

@cl.action_callback("begin_button")
async def on_begin_storytelling(action):
    global story_started, story_progress, story_data, user_data
    story_started = True
    # Retrieve the intro and encounter_0 text from the story data
    intro_text = story_data["checkpoints"][0]["text"]
    encounter_0_text = story_data["checkpoints"][1]["text"]
    # Prepare the initial story segment with user data
    initial_story_template = PromptTemplate(
        input_variables=['name', 'age', 'language', 'location', 'intro'],
        template="""
        You are a master storyteller for children aged {age} years old, telling interactive tales in {language},
        tailored to the user {name}'s age and culture, set in {location}. The boy is a fictional character separate to {name}.
        Every story segment you tell is approximately 42-50 words long when read aloud.
        The story is titled "The Boy and the Drum" and typically starts as follows:
        {intro}
        Tell the story from the beginning and adapt the context, location, length of story, language choice
        and where they stay to the user's age of {age} years old,
        location {location} and preferred language {language} and end by asking the user what the boy would like from the market to
        invite their inputs in order to continue the interactive story. The story should be appropriate for a {age} years old.
        Use UK English if language is English. You may use emojis to liven up the narrative. Keep your response to 42-50 words as much as possible.
        Begin.
        """
    )

    # Enable streaming when creating the LLM object
    llm = OpenAI(model_name="gpt-4-0125-preview", temperature=0.45)

    # story_chain = LLMChain(llm=llm, prompt=initial_story_template, verbose=True, output_key='story_segment')
    # res = await llm_math.acall(message.content, callbacks=[cl.LangchainCallbackHandler()])
    story_chain = LLMChain(llm=llm, prompt=initial_story_template, verbose=True, output_key='story_segment')

    initial_story_segment = story_chain.run(
        name=user_data['name'],
        age=user_data['age'],
        language=user_data['language'],
        location=user_data['location'],
        intro=intro_text,
        encounter_0=encounter_0_text
    )

    narrative_memory.save_context({"user_response": "Begin"}, {"story_segment": initial_story_segment})
    # narrative_memory.save_context({"story_segment": initial_story_segment}, {"user_response": ""})
    # Display story segment text immediately
    await cl.Message(content=initial_story_segment, author="Storyteller").send()
    # Attempt to generate audio, but do not wait to display text
    audio_element = await send_audio(initial_story_segment)
    if audio_element is not None:
        # Include a brief description or placeholder text as content
        await cl.Message(content="", elements=[audio_element], author="Storyteller").send()
    else:
        print("Audio generation failed or returned None")

@cl.on_message
async def main(message: cl.Message):
    global story_started, narrative_memory, story_progress, story_data, user_data

    if not story_started:
        # Collect user data if the story hasn't started
        await collect_user_data(message.content)
        return

    # Fetch the current story segment and user's latest response to update the narrative memory
    user_response = message.content
    # Directly appending the user's response to the existing history
    existing_history = narrative_memory.load_memory_variables({}).get("history", "")
    updated_history = f"{existing_history}\Human: {user_response}"

    # Fetch the next story segment based on the current_checkpoint
    current_checkpoint = story_progress["current_checkpoint"]
    next_segment_id = current_checkpoint + 1  # Assuming the next segment follows sequentially

    if next_segment_id < len(story_data["checkpoints"]):
        next_segment_text = story_data["checkpoints"][next_segment_id]["text"]
        story_progress["current_checkpoint"] = next_segment_id  # Update the checkpoint

        # Generate the continuation of the story, incorporating user response and next segment
        continuation_template = PromptTemplate(
            input_variables=['history', 'next_segment', 'name', 'age', 'language', 'location'],
            template=f"""
            Given the ongoing story for "The Boy and the Drum":
            {{history}}
            And the next segment to incorporate:
            {next_segment_text}
            Generate a continuation in {user_data['language']} that transitions smoothly into the next segment of the story.
            Note that after the AI had already generated the intro, so you only need to continue.
            Adapt the context, location, length of story, language choice and items to the user's age of {user_data['age']} years old
            (though user need not feature in the story), location {user_data['location']} and preferred language {user_data['language']}
            and invite their inputs in order to continue the interactive story where suitable.
            The user's name is {user_data['name']} and the vocabulary, language used
            and length of your response should be appropriate for a {user_data['age']} years old.
            The boy is a fictional character separate to {user_data['name']} and {user_data['name']} need not be part of the story.
            Use UK English if language is English. You may use emojis to liven up the narrative.
            """
        )

        user_response = message.content  # Get the user's response directly from the message object

        # Including the user's response in the existing history
        updated_history = f"{existing_history}\Human: {user_response}"

        llm = OpenAI(model_name="gpt-4-0125-preview", temperature=0.45)
        continuation_chain = LLMChain(llm=llm, prompt=continuation_template, verbose=True, output_key='story_continuation')
        continuation_response = continuation_chain.run(
            history=updated_history,
            next_segment=next_segment_text,
            name=user_data['name'],
            age=user_data['age'],
            language=user_data['language'],
            location=user_data['location'])

        # Narrate the continuation before sending it to the user
        await cl.Message(content=continuation_response, author="Storyteller").send()
        audio_element = await send_audio(continuation_response)

        if audio_element is not None:
            # Including the continuation response into the existing history
            final_updated_history = f"{updated_history}\nAI: {continuation_response}"
            narrative_memory.save_context(inputs={"history": final_updated_history, "user_response": user_response}, outputs={"story_segment": continuation_response})
            await cl.Message(content="", elements=[audio_element], author="Storyteller").send()
        else:
            # If audio generation fails, send the text response only
            final_updated_history = f"{updated_history}\nAI: {continuation_response}"
            narrative_memory.save_context({"history": final_updated_history, "user_response": user_response}, outputs={"story_segment": continuation_response})
            await cl.Message(content="Sorry, I couldn't narrate this part. Here's what happens next:", author="Storyteller").send()
            await cl.Message(content=continuation_response, author="Storyteller").send()
    else:
        # Handle end of story or no more segments available
        await cl.Message(content="The story has reached its end. Thank you for participating!", author="Storyteller").send()

@cl.on_chat_start
async def start():
    # Use construct_path_from_root to correctly find the path to avatar images
    storyteller_avatar_path = construct_path_from_root('raw_data/ai.png')
    user_avatar_path = construct_path_from_root('raw_data/user.png')
    print("[Debug] Storyteller avatar path:", storyteller_avatar_path)
    print("[Debug] User avatar path:", user_avatar_path)

    await cl.Avatar(name="Storyteller", path=storyteller_avatar_path).send()
    await cl.Avatar(name="User", path=user_avatar_path).send()

    # Setting the image generation to off by default
    global image_generation_enabled
    image_generation_enabled = False  # Ensure this is false initially
    print("[Debug] Initial image generation enabled status:", image_generation_enabled)

    # Request user to enable/disable image generation
    settings = await cl.ChatSettings(
        [
            Select(
                id="ImageGeneration",
                label="Enable Image Generation",
                values=["On", "Off"],
                initial_index=1,  # Default to 'Off' at the start
            )
        ]
    ).send()

    # Update based on user selection
    image_generation_enabled = settings["ImageGeneration"] == "On"
    print("[Debug] Image generation enabled after selection:", image_generation_enabled)

    if image_generation_enabled:
        # Initialize the image generation pipeline only if enabled
        print("[Debug] Initializing image generation pipeline...")
        initialize_pipeline()
    # await cl.Message(content="Hello! What's your name?", author="Storyteller").send()
    # Send language selection buttons
    global instructions  # Assuming 'instructions' is a global variable
    instructions = load_instructions()  # Load default language instructions first

    # Now it's safe to access instructions["welcome_message"]
    language_action_english = cl.Action(name="select_language", value="English", label="English")
    language_action_mandarin = cl.Action(name="select_language", value="Mandarin", label="中文")
    await cl.Message(content=instructions["welcome_message"], author="Storyteller", actions=[language_action_english, language_action_mandarin]).send()

@cl.on_settings_update
async def setup_agent(settings):
    global image_generation_enabled
    image_generation_enabled = settings.get("ImageGeneration", "Off") == "On"
    print(f"[Debug] on_settings_update - Image generation enabled: {image_generation_enabled}")

    # Optionally, re-initialize or adjust settings related to image generation here
    if image_generation_enabled and pipeline_text2image is None:
        print("[Debug] Re-initializing image generation pipeline due to settings update...")
        initialize_pipeline()

async def collect_user_data(message_text: str):
    global user_data, instructions

    # Directly using message_text as it's the raw string input from the user
    if 'name' not in user_data:
        user_data['name'] = message_text
        await cl.Message(content=instructions["age_prompt"], author="Storyteller").send()
    elif 'age' not in user_data:
        try:
            # Convert the age to an integer or handle it as you see fit
            user_data['age'] = int(message_text)
        except ValueError:
            await cl.Message(content="Please enter a valid age.", author="Storyteller").send()
            return  # Return to await a valid input
        await cl.Message(content=instructions["location_prompt"], author="Storyteller").send()
    elif 'location' not in user_data:
        user_data['location'] = message_text
        print(f"[Debug] Checking image generation flag: {image_generation_enabled}")
        if image_generation_enabled:
            print("[Debug] Triggering generate_and_display_cover_image")
            await generate_and_display_cover_image()
        else:
            await display_begin_button()

async def generate_and_display_cover_image():
    try:
        if not image_generation_enabled:  # Return early if image generation is not enabled
            return

        # Get the current time and format it as a string (e.g., "2023-10-06 12:34:56")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Define the text prompt for the cover image
        prompt = f"The Sound of Stories set in {current_time} in {user_data['location']}, featuring {user_data['age']} year old {user_data['name']}, magical, cute, children illustration style, anime"

        print("Generating image with prompt:", prompt)  # Debugging
        # Generate the cover image using the SDXL model
        async_pipeline_text2image = cl.make_async(pipeline_text2image)
        result = await async_pipeline_text2image(prompt=prompt)
        print(f"Image generation result type: {type(result)}")
        print(f"Number of images in result: {len(result.images)}")
        image = result.images[0]
        print(f"Generated image dimensions: {image.size}")

        # Save the generated cover image to a file
        image_path = "cover_image.png"
        image.save(image_path)
        print(f"Image saved to {image_path}")  # Debugging
        absolute_path = os.path.abspath(image_path)
        print(f"Absolute path of saved image: {absolute_path}")
        try:
            with Image.open(absolute_path) as img:
                print(f"Generated image opened successfully! Dimensions: {img.size}")
        except Exception as e:
            print(f"Failed to open generated image: {e}")
        image_size = os.path.getsize(absolute_path)
        print(f"Generated image size: {image_size} bytes")

        # Display the cover image in your application
        with open(absolute_path, "rb") as f:
            image_bytes = f.read()
        cover_image_display = cl.Image(name="Cover Image", display="inline", content=image_bytes)

        print("Sending image to chat...")  # Debugging
        await cl.Message(content="Here is the cover image for your story:", author="Storyteller", elements=[cover_image_display]).send()
        print("Image sent!")  # Debugging
        await display_begin_button()

    except Exception as e:
        print("Error in generate_and_display_cover_image:", str(e))  # Print any errors that occur

@cl.action_callback("select_language")
async def on_language_selected(action):
    global current_language, instructions, user_data  # Ensure user_data is accessible globally
    if action.value == "English":
        current_language = "en"
    elif action.value == "Mandarin":
        current_language = "zh"
    else:
        # Default to English if an unknown value is encountered
        current_language = "en"

    user_data['language'] = current_language  # Correctly store the selected language in user_data

    instructions = load_instructions()  # Correctly load instructions based on the newly selected language
    await cl.Message(content=instructions["name_prompt"], author="Storyteller").send()

    # Define session directory path
    session_dir = construct_path_from_root(f'raw_data/the_sound_of_stories/session_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
    os.makedirs(session_dir, exist_ok=True)

    # Save the preferred language in a JSON file
    language_preference_path = os.path.join(session_dir, 'user_preferences.json')
    with open(language_preference_path, 'w') as file:
        json.dump({"preferred_language": user_data['language']}, file, indent=4)

async def display_begin_button():  # NEW: Function to display the 'Begin' button
    # Assuming 'instructions' is a global variable already containing the loaded instructions
    global instructions
    begin_prompt = instructions["begin_story"]  # Get the begin prompt based on the selected language
    begin_action = cl.Action(name="begin_button", value="Begin", label="Begin")
    await cl.Message(content=begin_prompt, actions=[begin_action], author="Storyteller").send()
