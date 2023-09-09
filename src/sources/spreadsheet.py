from src.base_classes import DataSource
import pandas as pd
from typing import List, Dict, Optional

class SpreadsheetDataSource(DataSource):

    def __init__(self, path: str, id_column_mapping: List[str] = None):
        self.df = None
        self.path = path
        self.id_column_mapping = id_column_mapping if id_column_mapping else ["Accession No.", "ID", "Filename"]

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
        if self.df is None:
            raise ValueError(f"No data ingested from the spreadsheet.")

        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in the spreadsheet.")

        # Remove NaN or missing values and return the list
        return self.df[column_name].dropna().tolist()

    def get_id_column(self) -> Optional[List[str]]:
        for name in self.id_column_mapping:
            try:
                return self.get_column(name)
            except ValueError:
                continue
        raise ValueError(f"None of the possible names {self.id_column_mapping} found in the spreadsheet.")

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

# Usage:

# if __name__ == "__main__":
#     data_source = SpreadsheetDataSource("path_to_spreadsheet.xlsx")
#     data_source.ingest()

#     mappings = {
#         "accession": "Accession No.",
#         "artist": "Artist/Maker",
#         # ... add other mappings as needed
#     }
#     mapped_data = data_source.get_mapped_data(mappings)
#     print(mapped_data)

#     metadata = data_source.get_metadata()
#     print(metadata)
