import ast
import uuid
import astor

def extract_chunks_from_code(code_string):
    """
    Extracts functions, classes, methods, and global code chunks from the given Python code string.
    """
    class ChunkVisitor(ast.NodeVisitor):
        def __init__(self):
            self.chunks = []
            self.parent_stack = []

        def generic_visit(self, node):
            parent_uuid = self.parent_stack[-1] if self.parent_stack else None

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.process_code_chunk(node, parent_uuid)
            else:
                super().generic_visit(node)

        def process_code_chunk(self, node, parent_uuid):
            chunk_code = astor.to_source(node)
            if isinstance(node, ast.ClassDef):
                chunk_name = f"class_{node.name}"
            else:
                chunk_name = f"func_{node.name}"

            chunk_info = {
                "uuid": str(uuid.uuid4()),
                "name": chunk_name,
                "code": chunk_code,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "parent": parent_uuid
            }
            self.chunks.append(chunk_info)

            # Handle nested chunks
            self.parent_stack.append(chunk_info["uuid"])
            super().generic_visit(node)
            self.parent_stack.pop()

    visitor = ChunkVisitor()
    tree = ast.parse(code_string)
    visitor.visit(tree)

    return visitor.chunks

def append_metadata(chunk, file_path, object_id, commit_id):
    """
    Appends metadata to a chunk.
    """
    chunk["file_path"] = file_path
    if object_id:
        chunk["object_id"] = object_id
    if commit_id:
        chunk["commit_id"] = commit_id

def process_python_file(file_path, repo=None, object_id=None, commit_id=None):
    """
    Processes a Python file to extract its chunks (functions, classes, methods, and global code)
    and generate metadata.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    chunks = extract_chunks_from_code(code)
    documents = []

    for chunk in chunks:
        append_metadata(chunk, file_path, object_id, commit_id)

        # Create a document for the chunk
        document = {
            "page_content": chunk["code"],
            "metadata": chunk
        }
        documents.append(document)

    return documents
