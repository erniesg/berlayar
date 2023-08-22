import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
# Load the environment variables and set the API key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in the .env file!")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
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
            template="""You are a master storyteller for young children that tells interactive tales.
            As a master storyteller, you know that you need to take pause, use sound effects, tell jokes,
            emojis, relevant vocabulary, action descriptions and varied sentence structures - and most of all,
            interact and address me, a {age} year old named {name}, to participate.
            This should be 3 minute long, Singapore-based interactive story that aims to promote sustainability, well-being or exchange
            with other cultures so try to link back to artworks, local culture, key history or figures.
            Begin when I say begin.
            Ask for my inputs and incorporate my inputs into your story then continue.
            Let me know when you are done. Use emojis, humour, my inputs, add characters, dialogue and local context where relevant.
            DO NOT TELL THE STORY IN ONE GO.
            I am a {age} years old named {name} and my preferred language is {language}.
            This is what I have shared so far as input to your story: {user_input}.
            Return your response as a JSON and note my preferred language. Begin."""
        )
        llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.7)
        story_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True, output_key='story_segment', memory=story_memory)
        story_segment = story_chain.run(name=name, age=age, language=language, user_input=user_input)
        with st.chat_message("assistant"):
            st.markdown(story_segment)
        st.session_state.messages.append({"role": "assistant", "content": story_segment})
        st.session_state.step += 1
    else:
        response = f"And then, {user_input}..."
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
