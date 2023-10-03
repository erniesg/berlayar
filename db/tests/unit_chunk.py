import os
import unittest
from ..chunks import process_python_file, extract_chunks_from_code

class TestChunkFunctions(unittest.TestCase):

    def count_chunks_in_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            code_string = f.read()
            chunks = extract_chunks_from_code(code_string)
            return len(chunks)

    def test_function_extraction(self):
        code_string = """
def foo():
    return "bar"
"""
        chunks = extract_chunks_from_code(code_string)
        self.assertEqual(len(chunks), 1)  # Adjusted for global code
        self.assertEqual(chunks[0]['name'], 'func_foo')  # Adjusted index and name
        self.assertIn('uuid', chunks[0])  # Adjusted index
        self.assertIn('start_line', chunks[0])  # Adjusted index
        self.assertIn('end_line', chunks[0])  # Adjusted index

    def test_global_code_extraction(self):
        code_string = """
import os

def foo():
    return "bar"

print("Hello World")
"""
        chunks = extract_chunks_from_code(code_string)
        self.assertEqual(len(chunks), 1)  # 1 import statement, 1 function, 1 print statement

    def test_process_python_file(self):
        file_path = "../chunks.py"  # Testing chunk.py
        if not os.path.exists(file_path):
            print(f"Trying to access chunk.py at: {os.path.abspath(file_path)}")
            print("The file does not exist at the specified location!")
        chunks = process_python_file(file_path)

        # Print out the metadata for each chunk
        for chunk in chunks:
            print(f"Chunk Name: {chunk['name']}")
            print(f"UUID: {chunk['uuid']}")
            print(f"Start Line: {chunk['start_line']}")
            print(f"End Line: {chunk['end_line']}")
            print(f"File Path: {chunk['file_path']}")
            if 'parent' in chunk and chunk['parent']:
                print(f"Parent UUID: {chunk['parent']}")
            print("-------------------------------")

        # Print out the total number of chunks
        print(f"Total number of chunks: {len(chunks)}")

        # Count the number of chunks directly in the file
        expected_chunk_count = self.count_chunks_in_file(file_path)
        self.assertEqual(len(chunks), expected_chunk_count)

if __name__ == "__main__":
    unittest.main()
