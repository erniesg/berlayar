import deeplake
import os
import numpy as np
from typing import Optional, List, Dict

from src.base_classes import AbstractVectorStore, AbstractEmbeddingStrategy
from src.utils.embeddings import generate_image_embeddings, generate_textual_embeddings


class DeepLake(AbstractVectorStore):
    def __init__(self, embedding_strategy: Optional[AbstractEmbeddingStrategy] = None):
        self.deeplake_path = os.getenv("DEEPLAKE_PATH")
        self.embedding_strategy = embedding_strategy
        self.setup()

    def setup(self):
        if deeplake.exists(self.deeplake_path):
            print(f"Dataset at {self.deeplake_path} exists. Overwriting...")
            ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=True)
        else:
            print(f"Creating a new dataset at {self.deeplake_path}...")
            ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True})

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
        print("Dataset setup complete.")
        assert "metadata" in ds.tensors, "Failed to create 'metadata' tensor!"
        assert "images" in ds.tensors, "Failed to create 'images' tensor!"
        assert "embeddings" in ds.tensors, "Failed to create 'embeddings' tensor!"

    def store(self, data, data_type, metadatas: Optional[List[dict]] = None, embeddings: Optional[List[np.array]] = None):
        ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False)

        if embeddings is None:
            if data_type == 'image':
                embeddings = generate_image_embeddings(self.embedding_strategy, data) if self.embedding_strategy else data
            elif data_type == 'text':
                embeddings = generate_textual_embeddings(self.embedding_strategy, data) if self.embedding_strategy else data
            else:
                raise ValueError(f"Unsupported data_type: {data_type}")

        if isinstance(data, list):  # Check if data is a list
            for i, embedding in enumerate(embeddings):
                # Check the shape and dtype of the embedding
                assert embedding.dtype == np.float32, f"Expected dtype float32, but got {embedding.dtype}"
                assert len(embedding.shape) in [1, 2], f"Unexpected embedding shape: {embedding.shape}"

                image_data = deeplake.read(data[i])

                entry = {
                    "embeddings": embedding,
                    "metadata": metadatas[i],
                    "images": image_data
                }
                if "embeddings" not in ds.tensors or "metadata" not in ds.tensors or "images" not in ds.tensors:
                    raise ValueError("Required tensors are not present in the dataset!")
                ds.append(entry)

        else:  # If data is a single PosixPath object
            # Check the shape and dtype of the first embedding
            assert embeddings[0].dtype == np.float32, f"Expected dtype float32, but got {embeddings[0].dtype}"
            assert len(embeddings[0].shape) in [1, 2], f"Unexpected embedding shape: {embeddings[0].shape}"

            image_data = deeplake.read(data)

            entry = {
                "embeddings": embeddings[0],
                "metadata": metadatas[0],
                "images": image_data
            }
            if "embeddings" not in ds.tensors or "metadata" not in ds.tensors or "images" not in ds.tensors:
                raise ValueError("Required tensors are not present in the dataset!")
            ds.append(entry)

    def retrieve(self, embedding_query, limit=10):
        ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False)
        query = f'select * from (select metadata, cosine_similarity(embeddings, ARRAY{embedding_query.tolist()}) as score from "{self.deeplake_path}") order by score desc limit {limit}'
        query_res = ds.query(query, runtime={"tensor_db": True})
        results = query_res.metadata.data(aslist=True)["value"]
        return results

    def append(self, data):
        ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False)
        ds.append(data)
