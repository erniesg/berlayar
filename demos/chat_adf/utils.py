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
from dotenv import load_dotenv
load_dotenv()
load_dotenv()  # Load the .env file

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
        self.retriever.search_kwargs['fetch_k'] = 1
        self.retriever.search_kwargs['maximal_marginal_relevance'] = True
        self.retriever.search_kwargs['k'] = 1

    def retrieve_results(self, query):
        chat_history = list(self.MyQueue.queue)
        qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0, model='gpt-3.5-turbo-16k'), chain_type="stuff", retriever=self.retriever)
        result = qa({"question": query, "chat_history": chat_history})
        self.add_to_queue((query, result["answer"]))
        return result['answer']

    def add_to_queue(self, chat):
        if self.MyQueue.full():
            self.MyQueue.get()
        self.MyQueue.put(chat)

# Usage
embedder = Embedder()
# query = "How do I update the GHQ to the latest dataset?"
# print(embedder.retrieve_results(query))
