from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def ingest(self):
        pass

    @abstractmethod
    def get_metadata(self):
        pass

class FileProcessor(ABC):
    @abstractmethod
    def process(self, file_path, *args, **kwargs):
        pass

class ChunkProcessor(ABC):
    @abstractmethod
    def extract_chunks(self, content):
        pass

    @abstractmethod
    def process(self, file_path, *args, **kwargs):
        pass

class AbstractEmbeddingStrategy(ABC):
    @abstractmethod
    def embed(self, text):
        pass

class AbstractVectorStore(ABC):
    @abstractmethod
    def store(self, embeddings, *args, **kwargs):
        pass

    @abstractmethod
    def retrieve(self, query, *args, **kwargs):
        pass

class AbstractRetrievalStrategy(ABC):
    @abstractmethod
    def search(self, query, vector_store: AbstractVectorStore, *args, **kwargs):
        pass
