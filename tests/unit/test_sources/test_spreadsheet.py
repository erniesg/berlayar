import unittest
import pandas as pd
from pathlib import Path
from src.sources.spreadsheet import SpreadsheetDataSource
import tempfile

class TestSpreadsheetDataSource(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory and a mock Excel spreadsheet
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name) / "mock_data.xlsx"

        data = {
            'Accession No.': ['A1', 'A2', 'A3'],
            'Artist/Maker': ['Artist1', 'Artist2', 'Artist3']
            # ... add more columns as needed
        }

        df = pd.DataFrame(data)
        df.to_excel(self.temp_path, index=False)

        self.data_source = SpreadsheetDataSource(self.temp_path)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_ingest(self):
        self.data_source.ingest()
        self.assertIsNotNone(self.data_source.df, "Data was not ingested correctly.")

    def test_get_metadata(self):
        self.data_source.ingest()
        metadata = self.data_source.get_metadata()
        self.assertIn('Accession No.', metadata, "Metadata extraction failed for 'Accession No.'.")
        self.assertIn('Artist/Maker', metadata, "Metadata extraction failed for 'Artist/Maker'.")

    def test_get_column(self):
        self.data_source.ingest()
        column_data = self.data_source.get_column('Artist/Maker')
        self.assertEqual(column_data, ['Artist1', 'Artist2', 'Artist3'], "Column data retrieval failed.")

    def test_get_mapped_data(self):
        self.data_source.ingest()
        mappings = {
            "accession": "Accession No.",
            "artist": "Artist/Maker",
        }
        mapped_data = self.data_source.get_mapped_data(mappings)
        self.assertEqual(mapped_data['accession'], ['A1', 'A2', 'A3'], "Data mapping failed for 'accession'.")
        self.assertEqual(mapped_data['artist'], ['Artist1', 'Artist2', 'Artist3'], "Data mapping failed for 'artist'.")

if __name__ == '__main__':
    unittest.main()
