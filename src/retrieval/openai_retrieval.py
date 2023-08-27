from berlayar.src.base_classes import AbstractRetrievalStrategy
from berlayar.db.deeplake import DeepLakeOps, HuggingFaceEmbedder

class BerlayarRetrieval(AbstractRetrievalStrategy):

    def __init__(self, vector_store: AbstractVectorStore):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        self.vector_store = vector_store
        self.queue = Queue(maxsize=2)

    def search(self, query, vector_store=None, *args, **kwargs):
        if not vector_store:
            vector_store = self.vector_store

        # ... similar logic to the retrieve_results from before ...
