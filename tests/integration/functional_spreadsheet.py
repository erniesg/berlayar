import unittest
from pathlib import Path
import pandas as pd
from src.sources.spreadsheet import SpreadsheetDataSource
import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

FIXTURES_PATH = Path(os.environ.get("FIXTURES_PATH"))

class TestSpreadsheetDataSource(unittest.TestCase):

    def setUp(self):
        self.spreadsheet_path = FIXTURES_PATH / "artworks.xlsx"
        self.data_source = SpreadsheetDataSource(self.spreadsheet_path)

    def test_get_artist_by_image_filename(self):
        # Ingest data
        self.data_source.ingest()

        # Fetch artist/maker for the test image file
        test_image_file = "1991-00226.jpg"
        identifier = test_image_file[:-4]  # Remove the .jpg extension
        artist_value = self.data_source.get_column("Artist/Maker", identifier, "Accession No.")

        # Fetch the expected artist value directly using pandas
        df = pd.read_excel(self.spreadsheet_path)
        expected_artist = df[df["Accession No."] == identifier]["Artist/Maker"].values[0]

        # Print both values for clarity
        print(f"Expected Artist/Maker value: {expected_artist}")
        print(f"Actual Artist/Maker value from SpreadsheetDataSource: {artist_value}")

        # Assert that the fetched artist value is correct
        self.assertEqual(artist_value, expected_artist, f"Expected artist {expected_artist}, but got {artist_value}.")

if __name__ == '__main__':
    unittest.main()
