from src.base_classes import DataSource
import pandas as pd
from typing import List, Dict, Optional

class SpreadsheetDataSource(DataSource):

    def __init__(self, path: str):
        self.df = None
        self.path = path

    def ingest(self):
        """Ingest the spreadsheet data into a pandas DataFrame."""
        self.df = pd.read_excel(self.path)

    def get_metadata(self) -> Optional[Dict[str, List[str]]]:
        """Retrieve all data from the spreadsheet without specific mappings."""
        if self.df is not None:
            return {column: self.df[column].tolist() for column in self.df.columns}
        else:
            print("Warning: Data has not been ingested yet.")
            return None

    def get_column(self, column_name: str) -> Optional[List[str]]:
        if self.df is not None and column_name in self.df.columns:
            return self.df[column_name].tolist()
        else:
            print(f"Warning: {column_name} not found in the spreadsheet or data not ingested.")
            return None

    def get_mapped_data(self, mappings: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Get data mapped by column names.

        Args:
            mappings (Dict[str, str]): Dictionary mapping desired names to spreadsheet column names.

        Returns:
            Dict[str, List[str]]: Dictionary of data.
        """
        data = {}
        for key, value in mappings.items():
            column_data = self.get_column(value)
            if column_data:
                data[key] = column_data

        return data

'''Usage:

data_source = SpreadsheetDataSource("path_to_spreadsheet.xlsx")
data_source.ingest()

mappings = {
    "accession": "Accession No.",
    "artist": "Artist/Maker",
    # ... add other mappings as needed
}
mapped_data = data_source.get_mapped_data(mappings)
print(mapped_data)

metadata = data_source.get_metadata()
print(metadata)

'''
