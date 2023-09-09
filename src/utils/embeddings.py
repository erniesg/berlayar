from src.base_classes import AbstractEmbeddingStrategy

class ImageEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, image_path):
        # Use imagebind or a similar tool to generate embeddings for the image.
        pass

class TextualMetadataEmbeddings(AbstractEmbeddingStrategy):
    def embed(self, text):
        # Generate embeddings for the textual metadata.
        pass
