from langchain.vectorstores import DeepLake
from berlayar.src.base_classes import AbstractVectorStore, AbstractEmbeddingStrategy
import deeplake
import os

class HuggingFaceEmbedder(AbstractEmbeddingStrategy):
    def __init__(self):
        self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

    def embed(self, text):
        return self.hf.embed(text)

class DeepLakeOps(AbstractVectorStore):
    def __init__(self, embedding_strategy: AbstractEmbeddingStrategy):
        self.deeplake_path = os.getenv("DEEPLAKE_PATH")
        self.embedding_strategy = embedding_strategy
        self.load_db()

    def store(self, texts, metadatas=None):
        db = DeepLake(dataset_path=self.deeplake_path, embedding=self.embedding_strategy, read_only=False)
        db.add_texts(texts, metadatas=metadatas)
        return db

    def retrieve(self, query, retriever_settings=None):
        # ... similar logic as before ...
