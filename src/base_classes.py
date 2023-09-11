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

class AbstractEmbeddingModel(ABC):
    @abstractmethod
    def get_embeddings(self, *args, **kwargs):
        pass

class AbstractEmbeddingStrategy(ABC):

    def __init__(self, embedding_model: AbstractEmbeddingModel):
        self.embedding_model = embedding_model

    @abstractmethod
    def embed(self, *args, **kwargs):
        pass

class AbstractVectorStore(ABC):

    @abstractmethod
    def setup(self):
        """Set up or initialize the vector store."""
        pass

    @abstractmethod
    def store(self, data, data_type, metadatas: list = None):
        """Store data or embeddings in the vector store."""
        pass

    @abstractmethod
    def retrieve(self, query, retriever_settings=None):
        """Retrieve data from the vector store based on a query."""
        pass

class AbstractRetrievalStrategy(ABC):
    @abstractmethod
    def search(self, query, vector_store: AbstractVectorStore, *args, **kwargs):
        pass

class AbstractCloudStorage(ABC):

    @abstractmethod
    def upload(self, file_path: str, object_name: str, *args, **kwargs):
        pass

    @abstractmethod
    def download(self, object_name: str, file_path: str, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, object_name: str, *args, **kwargs):
        pass

    @abstractmethod
    def list_objects(self, prefix: str = None, *args, **kwargs) -> list:
        pass
