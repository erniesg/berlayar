import uuid
from pdfminer.layout import LAParams, LTTextBox, LTImage
from pdfminer.high_level import extract_pages
from pathlib import Path

def extract_chunks_from_pdf(pdf_path):
    """
    Extracts chunks from a given PDF, including text blocks and images.
    """
    chunks = []
    for page_layout in extract_pages(pdf_path, laparams=LAParams()):
        order_on_page = 0  # Order of chunks on a given page
        for element in page_layout:
            chunk_info = {
                "uuid": str(uuid.uuid4()),
                "page_num": page_layout.pageid,
                "order_on_page": order_on_page,
                "file_path": pdf_path
            }

            if isinstance(element, LTTextBox):
                content = element.get_text()
                if content.strip():  # Check if the content isn't just whitespace
                    chunk_info["type"] = "text_block"
                    chunk_info["name"] = f"text_block_{element.index}"  # Using index as a way to name chunks.
                    chunk_info["content"] = content
                    chunks.append(chunk_info)
                    order_on_page += 1

            elif isinstance(element, LTImage):
                # Handle the image. We'll save the image to disk and note the path in the chunk info.
                image_path = Path(pdf_path).parent / f"{chunk_info['uuid']}.png"
                with open(image_path, "wb") as img_file:
                    img_file.write(element.stream.get_data())
                chunk_info["type"] = "image"
                chunk_info["name"] = f"image_{element.index}"
                chunk_info["image_path"] = str(image_path)
                # TODO: Handling image captions would need a more advanced heuristic, possibly based on proximity.
                chunks.append(chunk_info)
                order_on_page += 1

    return chunks

def append_metadata(chunk, file_path, object_id, commit_id):
    """
    Appends metadata to a chunk.
    """
    chunk["file_path"] = file_path
    if object_id:
        chunk["object_id"] = object_id
    if commit_id:
        chunk["commit_id"] = commit_id

def process_pdf_file(pdf_path, object_id=None, commit_id=None):
    """
    Processes a PDF file to extract its chunks (text blocks, images)
    and generate metadata.
    """
    chunks = extract_chunks_from_pdf(pdf_path)
    documents = []

    for chunk in chunks:
        append_metadata(chunk, pdf_path, object_id, commit_id)

        if chunk['type'] == 'text_block':
            document_content = chunk['content']
        else:
            # Image chunk: you can decide how to represent an image in your vector store.
            # For now, I'm just placing the image path as content, but this might need adjustment based on your embedding method.
            document_content = chunk["image_path"]

        # Create a document for the chunk
        document = {
            "page_content": document_content,
            "metadata": chunk
        }
        documents.append(document)

    return documents
