from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from berlayar.utils.load_keys import load_environment_variables
from berlayar.model.rave import RAVEModelWrapper, audio_sample_to_mp3_bytes
from neutone_sdk.audio import AudioSample

# Load environment variables
load_environment_variables()

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG

app = FastAPI()

# Initialize the RAVE model wrapper
model_path = os.getenv("MODEL_PATH")
model_wrapper = RAVEModelWrapper(model_path=model_path)

class TransformRequest(BaseModel):
    input_audio_path: str
    output_audio_path: str
    params: dict

@app.post("/transform")
async def transform_audio(request: TransformRequest):
    try:
        logging.debug("Received audio transformation request.")

        # Perform the audio transformation
        model_wrapper.transform_audio(
            request.input_audio_path,
            request.output_audio_path,
            request.params
        )

        logging.debug("Audio transformation completed successfully.")
        return {"message": "Audio transformation completed successfully."}
    except Exception as e:
        logging.error(f"Error during audio transformation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render")
async def render_audio(request: TransformRequest):
    try:
        logging.debug("Received audio rendering request.")

        # Load the input audio file and create an AudioSample object
        input_audio_path = request.input_audio_path
        input_audio_sample = AudioSample.from_file(input_audio_path)

        # Perform the audio rendering
        output_audio_path = request.output_audio_path
        output_audio_sample = model_wrapper.render_audio_sample(input_audio_sample, request.params)
        with open(output_audio_path, "wb") as f:
            f.write(audio_sample_to_mp3_bytes(output_audio_sample))

        logging.debug(f"Rendered audio sample saved to {output_audio_path}.")
        return {"message": f"Rendered audio sample saved to {output_audio_path}."}
    except Exception as e:
        logging.error(f"Error during audio rendering: {e}")
        raise HTTPException(status_code=500, detail=str(e))
