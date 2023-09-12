import gradio as gr
from db.ops.deeplake import DeepLake
from src.utils.embeddings import get_embeddings, EmbeddingModelFactory
from src.models.imagebind_model_wrapper import ImageBindModelWrapper

model = EmbeddingModelFactory.get_model(ImageBindModelWrapper)
deeplake_instance = DeepLake()  # Assuming default embedding strategy is sufficient

def search(text_query=None, image_query=None, audio_query=None, limit=15):
    embeddings = get_embeddings(model,
                                texts=[text_query] if text_query else None,
                                images=[image_query] if image_query else None,
                                audio=[audio_query] if audio_query else None)

    # Retrieve the results using the embeddings
    results = deeplake_instance.retrieve(embeddings, limit=limit)

    # Convert the results to a readable format for Gradio
    # This step might need adjustment based on the exact structure of your results
    return "\n".join(results)

def launch_gui():
    interface = gr.Interface(
        fn=search,
        inputs=[
            gr.Text(label="Text"),
            gr.Image(label="Image", type="pil"),
            gr.Audio(label="Audio", source="microphone", type="filepath"),
            gr.Slider(minimum=1, maximum=30, value=15, step=1, label="search limit")
        ],
        outputs="text"
    )
    interface.launch()

if __name__ == "__main__":
    launch_gui()
