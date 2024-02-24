from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from berlayar.utils.load_keys import load_environment_variables
from berlayar.model.rave import RAVEModelWrapper

# Load environment variables
load_environment_variables()

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG

app = FastAPI()

# Initialize your RAVE model wrapper here (adjust the path as necessary)
model_wrapper = RAVEModelWrapper(model_path=os.getenv("MODEL_PATH"))

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
