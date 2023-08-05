import streamlit as st
import os
from dotenv import load_dotenv
from utils import Embedder

load_dotenv()

st.title("Arthur: ask me anything about your ADF")

# Load environment variables
user_key = os.getenv("OPENAI_API_KEY")
# If your Embedder class requires these environment variables, load them as well
deeplake_path = os.getenv("DEEPLAKE_PATH")
json_path = os.getenv("JSON_PATH")
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

if user_key:
    os.environ['OPENAI_API_KEY'] = user_key
    st.success("OpenAI Key successfully loaded!")

# If needed, set these environment variables and display their values
if deeplake_path and json_path:
    os.environ['DEEPLAKE_PATH'] = deeplake_path
    os.environ['JSON_PATH'] = json_path
    st.write("Using DeepLake path:", deeplake_path)
    st.write("Using JSON path:", json_path)

# Initialize Embedder
os.environ['HUGGINGFACE_TOKEN'] = huggingface_token
embedder = Embedder()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your question here."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Get and display assistant response
    response = embedder.retrieve_results(prompt)
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
