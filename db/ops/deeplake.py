from langchain.vectorstores import DeepLake
from src.base_classes import AbstractVectorStore, AbstractEmbeddingStrategy
from src.utils.embeddings import generate_image_embeddings, generate_textual_embeddings
from src.utils.embeddings_weighting import compute_weighted_embeddings
import deeplake
import os
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings


class HuggingFaceEmbedder(AbstractEmbeddingStrategy):
    def __init__(self):
        self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

    def embed(self, text):
        return self.hf.embed(text)

class DeepLakeOps(AbstractVectorStore):
    def __init__(self, embedding_strategy: AbstractEmbeddingStrategy):
        self.deeplake_path = os.getenv("DEEPLAKE_PATH")
        self.embedding_strategy = embedding_strategy
        self.setup()

    def setup(self):
        # Check if the dataset already exists
        exists = deeplake.exists(self.deeplake_path)
        if not exists:
            # Create new dataset structure in DeepLake
            ds = deeplake.empty(
                path=self.deeplake_path,
                runtime={"db_engine": True}
            )
            with ds:
                ds.create_tensor(
                    "metadata",
                    htype="json",
                    create_id_tensor=False,
                    create_sample_info_tensor=False,
                    create_shape_tensor=False,
                    chunk_compression="lz4"
                )
                ds.create_tensor("images", htype="image", sample_compression="jpg")
                ds.create_tensor(
                    "embeddings",
                    htype="embedding",
                    dtype=np.float32,
                    create_id_tensor=False,
                    create_sample_info_tensor=False,
                    max_chunk_size=64 * 1024 * 1024,
                    create_shape_tensor=True
                )

    def store(self, data, data_type, metadatas: list = None):
        """
        Store data in DeepLake.

        Parameters:
        - data: The data to be stored. Can be raw data (images, text, etc.) or embeddings.
        - data_type: A string indicating the type of data ('image', 'text', 'embedding', etc.).
        - metadatas: Optional metadata associated with the data.
        """
        db = DeepLake(dataset_path=self.deeplake_path, embedding=self.embedding_strategy, read_only=False)

        embeddings = []
        if data_type == 'image':
            embeddings = generate_image_embeddings(self.embedding_strategy, data)
        elif data_type == 'text':
            embeddings = generate_textual_embeddings(self.embedding_strategy, data)
        elif data_type == 'embedding':
            embeddings = data
        else:
            raise ValueError(f"Unsupported data_type: {data_type}")

        # Store embeddings with associated metadata in DeepLake
        for embedding, metadata in zip(embeddings, metadatas):
            db.append({
                "embeddings": embedding.numpy(),
                "metadata": metadata
            })

        return db

    def retrieve(self, embedding_query, limit=10):
        """Retrieve closest embeddings from DeepLake based on a query embedding."""
        db = DeepLake(dataset_path=self.deeplake_path, embedding=self.embedding_strategy, read_only=True)

        # Construct the query for DeepLake based on the provided embedding
        query = f'select * from (select metadata, cosine_similarity(embeddings, ARRAY{embedding_query.tolist()}) as score from "{self.deeplake_path}") order by score desc limit {limit}'

        query_res = db.query(query, runtime={"tensor_db": True})
        results = query_res.metadata.data(aslist=True)["value"]

        return results
