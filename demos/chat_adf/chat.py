import streamlit as st
import os
import time
from utils import Embedder, send_email
import json

st.title("Bertrand - I do all the things you don't like")

# Load environment variables
user_key = os.getenv("OPENAI_API_KEY")
deeplake_path = os.getenv("DEEPLAKE_PATH")
json_path = os.getenv("JSON_PATH")
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

# Set environment variables
os.environ['OPENAI_API_KEY'] = user_key
os.environ['DEEPLAKE_PATH'] = deeplake_path
os.environ['JSON_PATH'] = json_path
os.environ['HUGGINGFACE_TOKEN'] = huggingface_token

embedder = Embedder()

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

    # Get assistant response
    response = embedder.retrieve_results(prompt)

    # Debugging: Print the type of the response
    st.write(f"Type of response: {type(response)}")

    if isinstance(response, str):
        response_content = response
    elif isinstance(response, dict) and "content" in response:
        response_content = response["content"]
    else:
        response_content = ""

    # Check for function calls within the response
    if isinstance(response, dict) and "function_call" in response:
        function_name = response["function_call"]["name"]
        if function_name == "send_email":
            chat_log = "\n".join([message["content"] for message in st.session_state.messages])
            arguments = response["function_call"].get("arguments", {})
            to_address = arguments.get("to_address", "enjiao.chen@nationalgallery.sg")
            send_email(chat_log, to_address)
            response_content = "Email sent successfully!"

    # Display assistant's response with streaming effect
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in response_content.split():
            full_response += chunk + " "
            time.sleep(0.1)  # Adjust this value to make the delay longer or shorter
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# Add an email button below chat input
if st.session_state.messages:
    if st.button('Email Log'):
        chat_log = "\n".join([message["content"] for message in st.session_state.messages])
        to_address = "enjiao.chen@nationalgallery.sg"  # Change to the desired default address or get from user input
        send_email(chat_log, to_address)
        st.success("Email sent successfully!")
else:
    st.button('Email Log', disabled=True)
