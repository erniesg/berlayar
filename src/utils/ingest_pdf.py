import os
from pathlib import Path
from log_init import logger
from chunks_pdf import extract_chunks_from_pdf

def ingest_pdfs(path):
    """
    Ingests PDFs from a single file, list of files, or a directory.
    """
    all_chunks = []
    paths = []

    # Determine the type of input and create a list of paths
    if isinstance(path, str) and os.path.isdir(path):
        paths.extend([p for p in Path(path).glob("*.pdf")])
    elif isinstance(path, list):
        paths.extend([Path(p) for p in path])
    else:
        paths.append(Path(path))

    # Load and process each PDF path
    for p in paths:
        chunks = extract_chunks_from_pdf(p)
        all_chunks.extend(chunks)
        logger.info(f"Processed {p}, total chunks added: {len(chunks)}")

    return all_chunks

if __name__ == "__main__":
    pdf_path = input("Enter the path (directory or file) of the PDFs: ")
    chunks = ingest_pdfs(pdf_path)

    # Display some statistics and info
    for chunk in chunks[:3]:  # Displaying info for first 3 chunks as an example
        logger.info(f"Chunk Name: {chunk['name']}")
        logger.info(f"UUID: {chunk['uuid']}")
        logger.info(f"Type: {chunk['type']}")
        logger.info(f"On Page: {chunk['page_num']}")
        if chunk['type'] == "text_block":
            logger.info(f"Content:\n{chunk['content'][:100]}...")  # Displaying first 100 characters of the chunk
        elif chunk['type'] == "image":
            logger.info(f"Image Path: {chunk['image_path']}")
        logger.info("-" * 40)
