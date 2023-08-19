import ast
import uuid
import git

def extract_chunks_from_code(code_string):
    """
    Extracts functions, classes, methods, and global code chunks from the given Python code string.

    :param code_string: The Python code string.
    :return: A list of dictionaries containing information about each code chunk.
    """
    class ChunkVisitor(ast.NodeVisitor):
        def __init__(self):
            self.chunks = []
            self.parent_stack = []
            self.global_counter = 1

        def generic_visit(self, node):
            parent_uuid = self.parent_stack[-1] if self.parent_stack else None

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                chunk_code = code_string[node.lineno-1:node.end_lineno]
                if isinstance(node, ast.ClassDef):
                    chunk_name = f"class_{node.name}"
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunk_name = f"func_{node.name}"
                else:
                    chunk_name = node.name
                chunk_info = {
                    "uuid": str(uuid.uuid4()),
                    "name": chunk_name,
                    "code": chunk_code,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "parent": parent_uuid
                }
                self.chunks.append(chunk_info)

                # Push the UUID to the stack as it becomes the parent for nested chunks
                self.parent_stack.append(chunk_info["uuid"])
                super().generic_visit(node)
                # Pop the UUID from the stack after visiting children
                self.parent_stack.pop()
            else:
                super().generic_visit(node)

    visitor = ChunkVisitor()
    tree = ast.parse(code_string)
    visitor.visit(tree)

    lines = code_string.splitlines()
    last_chunk_end = 0
    ordered_chunks = []
    for chunk in sorted(visitor.chunks, key=lambda x: x["start_line"]):
        # Add global code between chunks
        if last_chunk_end < chunk["start_line"] - 1:
            global_chunk = {
                "uuid": str(uuid.uuid4()),
                "name": f"<global_code_{visitor.global_counter}>",
                "code": "\n".join(lines[last_chunk_end:chunk["start_line"]-1]),
                "start_line": last_chunk_end + 1,
                "end_line": chunk["start_line"] - 1,
                "parent": None
            }
            ordered_chunks.append(global_chunk)
            visitor.global_counter += 1
        ordered_chunks.append(chunk)
        last_chunk_end = chunk["end_line"]

    # Add global code after the last chunk
    if last_chunk_end < len(lines):
        global_chunk = {
            "uuid": str(uuid.uuid4()),
            "name": f"<global_code_{visitor.global_counter}>",
            "code": "\n".join(lines[last_chunk_end:]),
            "start_line": last_chunk_end + 1,
            "end_line": len(lines),
            "parent": None
        }
        ordered_chunks.append(global_chunk)

    return ordered_chunks

def process_python_file(file_path, repo=None):  # Add repo parameter
    """
    Processes a Python file to extract its chunks (functions, classes, methods, and global code)
    and generate metadata.

    :param file_path: The path to the Python file.
    :param repo: The git repository object (if available).
    :return: A list of dictionaries containing information about each code chunk in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    chunks = extract_chunks_from_code(code)

    # If the repo object is provided, fetch the file's objectID
    object_id = None
    if repo:
        try:
            # Get the file's blob hash
            object_id = repo.git.hash_object(file_path)
        except Exception as e:
            print(f"Error fetching objectID for {file_path}: {e}")

    for chunk in chunks:
        chunk["file_path"] = file_path
        if object_id:
            chunk["object_id"] = object_id  # Add objectID to the metadata

    return chunks
