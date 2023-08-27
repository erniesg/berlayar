class PythonChunkProcessor(ChunkProcessor):
    def extract_chunks(self, content):
        return extract_chunks_from_code(content)

    def process(self, file_path, repo=None, object_id=None, commit_id=None):
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()

        chunks = self.extract_chunks(code)
        documents = []

        for chunk in chunks:
            append_metadata(chunk, file_path, object_id, commit_id)
            document = {
                "page_content": chunk["code"],
                "metadata": chunk
            }
            documents.append(document)

        return documents

# Placeholder for future chunk processors
# class JSONChunkProcessor(ChunkProcessor):
#     ...

# class PDFChunkProcessor(ChunkProcessor):
#     ...
