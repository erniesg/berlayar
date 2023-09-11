import pandas as pd
from src.base_classes import DataSource
from typing import List, Dict, Optional, Union
import os
from pathlib import Path

class SpreadsheetDataSource(DataSource):

    def __init__(self, path: str, id_column_mapping: List[str] = None):
        self.df = None
        self.path = Path(path)  # Ensure path is a Path object
        self.id_column_mapping = id_column_mapping if id_column_mapping else os.environ.get("DEFAULT_ID_COLUMNS", "Accession No.,ID,Filename").split(",")

    def ingest(self):
        """Ingest the spreadsheet data into a pandas DataFrame."""
        if self.path.suffix == '.csv':
            self.df = pd.read_csv(self.path)
        elif self.path.suffix == '.xlsx':
            self.df = pd.read_excel(self.path)
        else:
            raise ValueError(f"Unsupported file type: {self.path.suffix}")

    def get_metadata(self) -> Optional[Dict[str, List[str]]]:
        """Retrieve all data from the spreadsheet without specific mappings."""
        if self.df is not None:
            return {column: self.df[column].tolist() for column in self.df.columns}
        else:
            print("Warning: Data has not been ingested yet.")
            return None

    def get_column(self, column_name: str, identifier: str = None, identifier_column: Optional[str] = None) -> Union[List[str], str]:
        if self.df is None:
            raise ValueError(f"No data ingested from the spreadsheet.")
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in the spreadsheet.")
        if identifier:
            if not identifier_column:
                identifier_column = self._get_default_identifier_column()
            value = self.df[self.df[identifier_column] == identifier][column_name].values[0]
            return value
        return self.df[column_name].dropna().tolist()

    def _get_default_identifier_column(self) -> str:
        for col in self.id_column_mapping:
            if col in self.df.columns:
                return col
        raise ValueError(f"None of the default identifier columns found in the spreadsheet: {self.id_column_mapping}")

    def get_mapped_data(self, mappings: Dict[str, str]) -> Dict[str, List[str]]:
        data = {}
        for key, value in mappings.items():
            column_data = self.get_column(value)
            if column_data:
                data[key] = column_data
        return data

    def get_id_column(self) -> Optional[List[str]]:
        for name in self.id_column_mapping:
            try:
                return self.get_column(name)
            except ValueError:
                continue
        raise ValueError(f"None of the possible names {self.id_column_mapping} found in the spreadsheet.")

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
