import torch

# Mocked Model that returns random embeddings for images and text
class MockedModel:
    def get_embeddings(self, data_type, data):
        if data_type == 'image':
            return torch.rand((len(data), 512))  # Assuming 512-dimensional embeddings for images
        elif data_type == 'text':
            return torch.rand((len(data), 256))  # Assuming 256-dimensional embeddings for text

# Initialize the mocked model
model = MockedModel()

# Generate embeddings for the image
image_data = ['2001-02488.jpg']
image_embeddings = model.get_embeddings('image', image_data)

# Generate embeddings for the Artist/Maker metadata
artist_maker_data = ['Enjiao Chen']
text_embeddings = model.get_embeddings('text', artist_maker_data)

print("Image Embeddings:", image_embeddings)
print("Text Embeddings:", text_embeddings)
