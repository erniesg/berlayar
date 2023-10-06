import chainlit as cl
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os
from dotenv import load_dotenv
import requests
import aiohttp
import asyncio
import re
import datetime
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline, AutoPipelineForText2Image
import torch
pipeline_text2image = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float32, variant="fp32", use_safetensors=True
).to("cpu")

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
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
        u"\U000024C2-\U0001F251" 
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)
# Load environment variables and set the API key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in the .env file!")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

user_data = {}
story_memory = ConversationBufferMemory(input_key='human_input', output_key='output')
story_started = False

async def generate_and_display_cover_image():
    # Get the current time and format it as a string (e.g., "2023-10-06 12:34:56")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define the text prompt for the cover image
    prompt = f"The Sound of Stories set in {current_time} in {user_data['location']}"

async def send_audio(content):
    cleaned_content = remove_emojis(content)  # remove emojis from content
    print(f'{cleaned_content}')
    url = "https://play.ht/api/v2/tts/stream"

    payload = {
        "text": cleaned_content,
        "voice": "s3://voice-cloning-zero-shot/01e001f3-3ef7-4376-9a3b-34cebdc6ea39/kamini/manifest.json",
        "quality": "draft",
        "output_format": "mp3",
        "speed": 1,
        "sample_rate": 24000,
        "voice_engine": "PlayHT2.0"
    }

    headers = {
        "accept": "audio/mpeg",
        "content-type": "application/json",
        "AUTHORIZATION": os.getenv('PLAYHT_AUTHORIZATION'),
        "X-USER-ID": os.getenv('PLAYHT_X-USER-ID')
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            print(f'Response Status: {response.status}')  # Log the status of the response
            if response.status != 200:
                print(f'Error: {await response.text()}')  # Log the error message if the status is not 200
                return  # Exit the function if there was an error
            audio_data = await response.read()
            print(f'Audio Data: {audio_data[:100]}...')  # Log the first 100 bytes of the audio data
            return cl.Audio(name="story_segment.mp3", content=audio_data, display="inline")  # return the cl.Audio object

@cl.action_callback("begin_button")  # Changed to match the action's name
async def on_begin_storytelling(action):
    global story_started
    story_started = True
    # Story Initialization Chain
    initial_story_template = PromptTemplate(
        input_variables=['name', 'age', 'language'],
        template="""
            You are a master storyteller for children aged {age} years old that tells interactive tales.
            Every story segment you tell is approximately 42-50 words long when read aloud.
            The story is titled "The Boy and the Drum" and typically starts as follows:
            A poor woman had a son. She worked hard as a gardener.
            She could never afford to buy nice clothes or lovely toys for her son.
            The mother was going to the market to sell the grain she had received.
            She asked her son, "What can I get for you from the market, little one?"
            The boy was fascinated with the sound of a drum. So he said,
            "A drum, mother, I would love to have a drum to play with."
            Use the above as inspiration, tell it from the beginning and setting,
            that is, you need to set the story up.
            Tell this story bit by bit, in my preferred {language}
            catered to my {age}, gender and culture.
            Interact with me, my name is {name}, you may use emojis, and
            adapt the story to my response as we go along. Start from the beginning.
            Begin.
            """
    )
    llm = OpenAI(model_name="gpt-4-0613", temperature=0.3)  # Removed streaming=True
    story_chain = LLMChain(llm=llm, prompt=initial_story_template, verbose=True, output_key='story_segment')
    initial_story_segment = story_chain.run(name=user_data['name'], age=user_data['age'], language=user_data['language'])
    
    # Save the AI's initial story segment to the conversation context
    story_memory.save_context({"human_input": "Begin"}, {"output": initial_story_segment})

    audio_element = await send_audio(initial_story_segment)
    await cl.Message(
        content=initial_story_segment,
        elements=[audio_element],
        author="Storyteller"
    ).send()

@cl.on_message
async def main(message: str):
    global story_started
        
    # Save the user's response to the conversation context
    story_memory.save_context({"human_input": message}, {"output": ""})
    
    # Debug: Print the story_memory contents
    print("Story Memory:", story_memory.load_memory_variables({}))
    
    if not story_started:
        await collect_user_data(message)
    else:
        # Conversational Story Chain
        history = story_memory.load_memory_variables({}).get("history", "")
        
        # Debug: Print the history variable
        print("History:", history)
        
        conversational_template = PromptTemplate(
            input_variables=['history'],
            template="""The following is an ongoing interactive tale:
    {history}
    Continue the story based on the above conversation. Respond directly and use emojis as necessary."""
        )
        llm = OpenAI(model_name="gpt-4-0613", temperature=0.3)  # Removed streaming=True
        conversational_chain = LLMChain(llm=llm, prompt=conversational_template, verbose=True, output_key='output', memory=story_memory)
        
        response = conversational_chain.run(human_input=history)  # Not streaming, so we can just run it directly
        print(f'Type of response: {type(response)}')
        print(f'Content of response: {response}')
        if "AI: " in response:
            msg_content = response.replace("AI: ", "")
        else:
            msg_content = response
        
        # Save the AI's response to the conversation context
        print(f"msg_content: {msg_content}")
        story_memory.save_context({"human_input": message}, {"output": msg_content})

        audio_element = await send_audio(msg_content)
        await cl.Message(
            content=msg_content,
            elements=[audio_element],
            author="Storyteller"
        ).send()

@cl.on_chat_start
async def start():
    await cl.Avatar(
        name="Storyteller",
        path="/Users/enjiaochen/code/erniesg/berlayar/raw_data/bot.png",
    ).send()
    
    await cl.Avatar(
        name="User",
        path="/Users/enjiaochen/code/erniesg/berlayar/raw_data/avatar.png",
    ).send()
    
    await cl.Message(content="Hello! What's your name?", author="Storyteller").send()

async def collect_user_data(message: str):
    if 'name' not in user_data:
        user_data['name'] = message
        await cl.Message(content="How old are you?", author="Storyteller").send()
    elif 'age' not in user_data:
        user_data['age'] = message
        await cl.Message(content="What's your preferred language?", author="Storyteller").send()
    elif 'language' not in user_data:
        user_data['language'] = message
        await cl.Message(content="Where are you located?", author="Storyteller").send()
    elif 'location' not in user_data:
        user_data['location'] = message
        # Instead of starting the story directly, generate and display the cover image
        await generate_and_display_cover_image()

async def generate_and_display_cover_image():
    # Get the current time and format it as a string (e.g., "2023-10-06 12:34:56")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define the text prompt for the cover image
    prompt = f"The Sound of Stories set in {current_time} in {user_data['location']}"

    # Generate the cover image using the SDXL model
    result = pipeline_text2image(prompt=prompt)
    image = result.images[0]

    # Save the generated cover image to a file
    image.save("cover_image.png")

    # Display the cover image in your application
    cover_image_display = cl.Image(name="Cover Image", display="inline", path="cover_image.png")
    await cl.Message(content="Here is the cover image for your story:", elements=[cover_image_display]).send()
    
    # Show the 'Begin' button
    begin_action = cl.Action(name="begin_button", value="Begin", label="Begin")
    await cl.Message(content="Click 'Begin' to start the story.", actions=[begin_action], author="Storyteller").send()
