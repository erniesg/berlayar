from base_classes import FileProcessor
from connectors import process_python_file, process_pdf_file

class PythonFileProcessor(FileProcessor):
    """
    Processor for Python files.
    """

    def process(self, file_path, *args, **kwargs):
        return process_python_file(file_path, **kwargs)

class PDFFileProcessor(FileProcessor):
    """
    Processor for PDF files.
    """

    def process(self, file_path, *args, **kwargs):
        return process_pdf_file(file_path, **kwargs)

# Placeholder for JSON file processor
# class JSONFileProcessor(FileProcessor):
#     ...
