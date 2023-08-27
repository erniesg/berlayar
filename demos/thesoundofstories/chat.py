import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
import time  # For the streaming effect
from dotenv import load_dotenv
import sys
import subprocess
import re

# Load the environment variables and set the API key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in the .env file!")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

def extract_text(text):
    """Extract only text characters and punctuation from the given text."""
    # This pattern matches sequences of word characters, spaces, hyphen, and the specified punctuation.
    return ''.join(re.findall(r'[\w\s.,!?;\'"-]+', text))

def generate_audio_filename(target_language):
    """Generate a filename based on the current time and target language."""
    timestamp = int(time.time())
    return f"response_audio_{timestamp}_{target_language}.mp3"

# Streamlit UI
st.title("The Sound of Stories")

# Initialize chat history and interaction step
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.step = 0

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio_path" in message:
            st.audio(message["audio_path"])

prompts = [
    "Hello! What's your name?",
    "Great! How old are you?",
    "And what's your preferred language?",
    "Awesome! Enter '1' to begin the story."
]

# If it's the assistant's turn to ask a question and the last message wasn't from the assistant
if not st.session_state.messages or st.session_state.messages[-1]["role"] == "user":
    if st.session_state.step < len(prompts):
        with st.chat_message("assistant"):
            st.markdown(prompts[st.session_state.step])
        st.session_state.messages.append({"role": "assistant", "content": prompts[st.session_state.step]})

# Get user input
user_input = st.chat_input()

# Process the input
if user_input:
    print(f"User entered: {user_input}")
    print(f"Interaction step: {st.session_state.step}")

    # Only append user input to chat history if it's not an audio command
    if "read to me" not in user_input and "read to me in mandarin" not in user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.step < len(prompts) - 1:
        st.session_state.step += 1
    elif st.session_state.step == len(prompts) - 1 and user_input == '1':
        print("Waiting for response from API...")
        name = st.session_state.messages[1]["content"]  # First user input after assistant's greeting
        age = st.session_state.messages[3]["content"]   # Second user input
        language = st.session_state.messages[5]["content"]  # Third user input
        # Initialize the storytelling components
        story_memory = ConversationBufferMemory(input_key='user_input', memory_key='chat_history')
        prompt_template = PromptTemplate(
            input_variables=['name', 'age', 'language', 'user_input'],
            template="""You are a master storyteller for children aged {age} years old that tells interactive tales.
            Every story segment you tell is approximately 20 seconds or 42-50 words long when read aloud
            As a master storyteller, you know that you need to take pause, use sound effects, tell jokes,
            use emojis, relevant vocabulary, action descriptions and varied sentence structures where relevant,
            and involve my inputs and decisions and use my preferred {language} in your interactive tale.
            This should be a Singapore-based interactive story that aims to promote sustainability, well-being or exchange
            with other cultures so try to link back to artworks, local culture, key history or figures.
            Begin your storytelling to me when I say begin.
            Let me know when you are done.
            DO NOT TELL THE STORY IN ONE GO. Tell it in segments and ask for my inputs.
            I am a {age} years old named {name} and my preferred language is {language}.
            This is what I have shared so far as input to your story: {user_input}.
            Return your response as a JSON and tell the story in my preferred language. Begin."""
        )
        llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.3)
        story_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True, output_key='story_segment', memory=story_memory)
        story_segment = story_chain.run(name=name, age=age, language=language, user_input=user_input)
        print(f"Generated Story Chunk: {story_segment}")  # Printing the generated story chunk

        # Display the story segment with streaming effect
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in story_segment.split():
                full_response += chunk + " "
                time.sleep(0.1)  # Adjust this value to make the delay longer or shorter
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        # Store the last generated story chunk in session state
        st.session_state.last_story_chunk = story_segment

        st.session_state.messages.append({"role": "assistant", "content": story_segment})
        st.session_state.step += 1
    else:
        response = f"{user_input}"
        with st.chat_message("user"):
            st.markdown(response)
        st.session_state.messages.append({"role": "user", "content": response})

    # Check for user request to read the previous story chunk
    if "read to me" in user_input or "read to me in mandarin" in user_input:
        # Use the stored last story chunk for generating the audio
        previous_response = st.session_state.get("last_story_chunk", "")

        # Determine target language based on user input
        target_language = "eng"
        if "in mandarin" in user_input:
            target_language = "cmn"

        # Directory to save audio files
        audio_dir = os.path.join(os.path.dirname(__file__), "audio")
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)  # Create the directory if it doesn't exist

        # Construct the path for the new audio file based on target language and current time
        audio_filename = generate_audio_filename(target_language)
        audio_path = os.path.join(audio_dir, audio_filename)

        # Before calling the m4t_predict script
        cleaned_input_text = extract_text(previous_response)
        print(f"Cleaned Input Text for Audio Generation: {cleaned_input_text}")  # Printing the cleaned input text
        command = [
            "python3",
            "/home/erniesg/code/erniesg/seamless_communication/scripts/m4t/predict/predict.py",
            cleaned_input_text,
            "t2st",
            target_language,
            "--src_lang",  # Add this line
            "eng",        # Add this line for the default source language
            "--output_path",
            audio_path
        ]

        # Inform the user that the audio is being generated
        with st.spinner('Generating audio...'):
            subprocess.run(command, check=True)  # Runs the command and waits for it to complete

        # Embed the audio in Streamlit
        st.audio(audio_path)

        # Instead of appending the filename to the session state messages
        # Append a placeholder message that will contain the embedded audio player
        audio_message = {
            "role": "assistant",
            "content": "Let me read it for you:",
            "audio_path": audio_path
        }
        st.session_state.messages.append(audio_message)
