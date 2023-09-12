import gradio as gr
from db.ops.deeplake import DeepLake
from dotenv import load_dotenv
from src.utils.embeddings import get_embeddings, EmbeddingModelFactory
from src.utils.embeddings_weighting import dynamic_weighted_embeddings
from src.models.imagebind_model_wrapper import ImageBindModelWrapper
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
import os

# Load Azure Credentials
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

model = EmbeddingModelFactory.get_model(ImageBindModelWrapper)
deeplake_instance = DeepLake()

def generate_sas_url(blob_name):
    print(f"Generating SAS URL for blob_name: {blob_name}")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url_with_sas = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    print(f"Generated URL: {blob_url_with_sas}")
    return blob_url_with_sas

def local_image_path(filename):
    return os.path.join(os.path.dirname(__file__), '..', 'tests', 'fixtures', 'ngs', filename)

def search(text_query=None, image_query=None, audio_query=None, limit=15):
    embeddings = get_embeddings(model,
                                texts=[text_query] if text_query else None,
                                images=[image_query] if image_query else None,
                                audio=[audio_query] if audio_query else None)
    combined_embedding = dynamic_weighted_embeddings(embeddings)
    results = deeplake_instance.retrieve(combined_embedding, limit=limit)

    print(f"Type of results: {type(results)}")
    print(results)

    gallery_data = [(local_image_path(item['filename']),
                     f"<b>{item['title']}</b><br>{item['artist_maker']}<br>{item['accession_no']}") for item in results]

    return gallery_data

def launch_gui():
    interface = gr.Interface(
        fn=search,
        inputs=[
            gr.Text(label="Text"),
            gr.Image(label="Image", type="pil"),
            gr.Audio(label="Audio", source="microphone", type="filepath"),
            gr.Slider(minimum=1, maximum=30, value=15, step=1, label="search limit")
        ],
        outputs=gr.Gallery(label="Search Results")
    )
    interface.launch()

if __name__ == "__main__":
    launch_gui()
