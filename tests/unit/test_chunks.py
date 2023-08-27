import os
import unittest
from db.chunks import process_python_file, extract_chunks_from_code

class TestChunkFunctions(unittest.TestCase):

    def count_chunks_in_file(self, file_path):
        """Utility method to count the number of chunks in a given file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            code_string = f.read()
            chunks = extract_chunks_from_code(code_string)
            return len(chunks)

    def test_function_extraction(self):
        """Test that functions are correctly extracted from a code string."""
        code_string = """
def foo():
    return "bar"
"""
        chunks = extract_chunks_from_code(code_string)
        self.assertEqual(len(chunks), 2)  # Adjusted for global code
        self.assertEqual(chunks[1]['name'], 'func_foo')  # Adjusted index and name
        self.assertIn('uuid', chunks[1])  # Adjusted index
        self.assertIn('start_line', chunks[1])  # Adjusted index
        self.assertIn('end_line', chunks[1])  # Adjusted index

    def test_global_code_extraction(self):
        """Test that global code (import statements, print statements, etc.) is correctly extracted."""
        code_string = """
import os

def foo():
    return "bar"

print("Hello World")
"""
        chunks = extract_chunks_from_code(code_string)
        self.assertEqual(len(chunks), 3)  # 1 import statement, 1 function, 1 print statement

    def test_process_python_file(self):
        """Test processing of a python file and extraction of its chunks."""
        file_path = "db/chunks.py"  # Testing chunk.py
        if not os.path.exists(file_path):
            self.fail(f"chunk.py does not exist at the specified location: {os.path.abspath(file_path)}")

        chunks = process_python_file(file_path)
        expected_chunk_count = self.count_chunks_in_file(file_path)
        self.assertEqual(len(chunks), expected_chunk_count)

if __name__ == "__main__":
    unittest.main()
