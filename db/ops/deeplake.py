import deeplake
import os
import numpy as np
from typing import Optional, List, Dict
from src.base_classes import AbstractVectorStore, AbstractEmbeddingStrategy
from src.utils.embeddings import generate_embeddings

class DeepLake(AbstractVectorStore):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DeepLake, cls).__new__(cls)
        return cls._instance

    def __init__(self, embedding_strategy: Optional[AbstractEmbeddingStrategy] = None):
        if not hasattr(self, 'is_initialized') or not self.is_initialized:
            self.deeplake_path = os.getenv("DEEPLAKE_PATH")
            self.embedding_strategy = embedding_strategy
            self.ds = None  # To store the dataset instance
            self.setup()
            self.is_initialized = True

    def setup(self):
        if self.ds is not None:
            print("Dataset is already set up.")
            return

        try:
            # Try to load the dataset first
            self.ds = deeplake.load(self.deeplake_path, read_only=True)

            # If dataset is successfully loaded, ask the user for overwriting
            user_input = input(f"Dataset at {self.deeplake_path} exists. Do you want to overwrite? (yes/no): ").strip().lower()

            if user_input == 'yes':
                print(f"Overwriting dataset at {self.deeplake_path}...")
                self.ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=True)
            else:
                print(f"Using existing dataset at {self.deeplake_path}...")
                return

        except Exception as e:
            # If dataset doesn't exist or any other error occurs, create a new one
            print(f"Creating a new dataset at {self.deeplake_path}...")
            self.ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True})

        with self.ds:
            self.ds.create_tensor(
                "metadata",
                htype="json",
                create_id_tensor=False,
                create_sample_info_tensor=False,
                create_shape_tensor=False,
                chunk_compression="lz4"
            )
            self.ds.create_tensor("images", htype="image", sample_compression="jpg")
            self.ds.create_tensor(
                "embeddings",
                htype="embedding",
                dtype=np.float32,
                create_id_tensor=False,
                create_sample_info_tensor=False,
                max_chunk_size=64 * 1024 * 1024,
                create_shape_tensor=True
            )
        print("Dataset setup complete.")
        assert "metadata" in self.ds.tensors, "Failed to create 'metadata' tensor!"
        assert "images" in self.ds.tensors, "Failed to create 'images' tensor!"
        assert "embeddings" in self.ds.tensors, "Failed to create 'embeddings' tensor!"

    def store(self, data, data_type, metadatas: Optional[List[dict]] = None, embeddings: Optional[List[np.array]] = None):
        if self.ds is None:
            raise ValueError("Dataset is not initialized. Please call setup method first.")

        # Unified embeddings generation
        if embeddings is None:
            if data_type == 'image':
                embeddings_data = {'image_paths': data}
            elif data_type == 'text':
                embeddings_data = {'text_list': data}
            else:
                raise ValueError(f"Unsupported data_type: {data_type}")

            embeddings = generate_embeddings(self.embedding_strategy, **embeddings_data) if self.embedding_strategy else data

        if isinstance(data, list):  # Check if data is a list
            entries = []
            for i, embedding in enumerate(embeddings):
                image_data = deeplake.read(str(data[i]))
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                entry = {"embeddings": embedding, "metadata": metadata, "images": image_data}
                entries.append(entry)
            self.ds.append(entries)

        else:
            image_data = deeplake.read(data)
            metadata = metadatas[0] if metadatas else {}
            entry = {"embeddings": embeddings[0], "metadata": metadata, "images": image_data}
            self.ds.append(entry)

    def delete_dataset(self):
        ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False)
        try:
            ds.delete(large_ok=True)
            print("Deleted the entire dataset from DeepLake.")
        except Exception as e:
            print(f"Error deleting dataset from DeepLake: {e}")

    def delete_branch(self, branch_name):
        ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False)
        try:
            ds.delete_branch(name=branch_name)
            print(f"Deleted branch {branch_name} from DeepLake.")
        except Exception as e:
            print(f"Error deleting branch {branch_name} from DeepLake: {e}")

    def retrieve(self, embedding_query, limit=10):
        ds = deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False)
        flattened_embedding_list = embedding_query.flatten().tolist()
        query = f'select * from (select metadata, cosine_similarity(embeddings, ARRAY{flattened_embedding_list}) as score from "{self.deeplake_path}") order by score desc limit {limit}'
        query_res = ds.query(query, runtime={"tensor_db": True})
        results = query_res.metadata.data(aslist=True)["value"]
        return results

    def append(self, data):
        with deeplake.dataset(path=self.deeplake_path, runtime={"db_engine": True}, overwrite=False) as ds:
            ds.append(data)
