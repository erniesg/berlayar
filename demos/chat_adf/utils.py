from langchain.document_loaders import JSONLoader
from pprint import pprint
import json
import os
import deeplake
import logging
from queue import Queue
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from openai import ChatCompletion
import openai
from langchain.callbacks import get_openai_callback
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Load the environment variables and set the API key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

def send_email(chat_log, to_address):
    """Send an email containing the chat log."""
    msg = EmailMessage()
    msg.set_content(chat_log)
    msg["Subject"] = "Chat Log"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to_address

    with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()  # Upgrade the connection to encrypted TLS
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)

class Embedder:
    def __init__(self) -> None:
        self.deeplake_path = os.getenv("DEEPLAKE_PATH")  # Get the DEEPLAKE_PATH from the environment variables
        self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
        self.MyQueue = Queue(maxsize=2)
        self.load_db()

    def chunk_json_objects(self, json_data):
        json_objects = []
        for obj in json_data:
            json_objects.append((json.dumps(obj), {})) # assuming you don't have specific metadata to add
        return json_objects

    def embed_json_data(self, documents):
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]  # if metadata exists, or use [{} for _ in documents]
        db = DeepLake(dataset_path=self.deeplake_path, embedding=self.hf, read_only=False)
        db.add_texts(texts, metadatas=metadatas)
        return db

    def load_db(self):
        exists = deeplake.exists(self.deeplake_path)
        if exists:
            self.db = DeepLake(
                dataset_path=self.deeplake_path,
                read_only=True,
                embedding_function=self.hf,
            )
        else:
            file_path = os.getenv("JSON_PATH")  # Get the JSON_PATH from the environment variables

            try:
                loader_parameters = JSONLoader(file_path, '.parameters', text_content=False)
                data_parameters = loader_parameters.load()
                print("Parameters loaded successfully.")
            except Exception as e:
                print(f"Error loading parameters: {e}")

            try:
                loader_variables = JSONLoader(file_path, '.variables', text_content=False)
                data_variables = loader_variables.load()
                print("Variables loaded successfully.")
            except Exception as e:
                print(f"Error loading variables: {e}")

            try:
                loader_resources = JSONLoader(file_path, '.resources[]', text_content=False)
                data_resources = loader_resources.load()
                print("Resources loaded successfully.")
            except Exception as e:
                print(f"Error loading resources: {e}")

            # Process all data (parameters, variables, resources) together
            all_data = data_parameters + data_variables + data_resources
            self.db = self.embed_json_data(all_data)

        self.retriever = self.db.as_retriever()
        self.retriever.search_kwargs['distance_metric'] = 'cos'
        self.retriever.search_kwargs['fetch_k'] = 2
        self.retriever.search_kwargs['maximal_marginal_relevance'] = True
        self.retriever.search_kwargs['k'] = 2

    def retrieve_results(self, query):
        print("Starting retrieve_results function...")
        chat_history = list(self.MyQueue.queue)
        print(f"Chat history: {chat_history}")

        # Wrap both the ConversationalRetrievalChain and ChatCompletion API calls with the callback context manager
        with get_openai_callback() as cb:
            # Step 1: Use ConversationalRetrievalChain for the initial response
            qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0, model='gpt-3.5-turbo-16k', streaming=True, callbacks=[StreamingStdOutCallbackHandler()]), chain_type="stuff", retriever=self.retriever)
            result = qa({"question": query, "chat_history": chat_history})
            print(f"Initial result from ConversationalRetrievalChain: {result}")
            self.add_to_queue((query, result["answer"]))

            # Check if a function call is present in the initial result
            if "function_call" not in result:
                response = result['answer']
            else:
                # Step 2: Use GPT-3.5-turbo with streaming enabled
                functions = [
                    {
                        "name": "send_email",
                        "description": "Send an email containing the chat log.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "to_address": {
                                    "type": "string",
                                    "description": "The recipient email address."
                                },
                            }
                        }
                    }
                ]
                messages = [{"role": "user", "content": query}] + [{"role": role, "content": content} for role, content in chat_history]
                response = ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    functions=functions,
                    function_call="auto",
                    streaming=True,
                    callbacks=[StreamingStdOutCallbackHandler()]
                )
                print(f"GPT-3.5-turbo response: {response}")

            # Print token and cost info after processing both API calls
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")

        # Handle different types of response
        if isinstance(response, dict) and "function_call" in response:
            function_name = response["function_call"]["name"]
            # ... your function handling logic ...

        elif isinstance(response, dict) and "choices" in response:
            response = response["choices"][0]["message"]

        elif isinstance(response, str):
            # If the response is directly a string, you can leave it as it is
            pass

        else:
            print(f"Unexpected response type: {type(response)}")
            response = "Sorry, I couldn't understand the response."

        return response

    def add_to_queue(self, chat):
        if self.MyQueue.full():
            self.MyQueue.get()
        self.MyQueue.put(chat)

# Usage
embedder = Embedder()
# query = "How do I update the GHQ to the latest dataset?"
# print(embedder.retrieve_results(query))
