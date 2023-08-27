import logging
import os

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("ingest_pdf.log"),  # Log to a file named ingest_pdf.log
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger("ingest_pdf")  # Name of the logger
