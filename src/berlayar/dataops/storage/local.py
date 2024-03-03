import os
import json
from berlayar.utils.path import construct_path_from_root

class LocalStorage:
    def __init__(self, base_dir="raw_data"):
        self.base_dir = base_dir

    def save_data(self, filename, data, subdirectory=None):
        save_dir = self.base_dir
        if subdirectory:
            save_dir = os.path.join(save_dir, subdirectory)
        save_dir = construct_path_from_root(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def load_data(self, filename, subdirectory=None):
        load_dir = self.base_dir
        if subdirectory:
            load_dir = os.path.join(load_dir, subdirectory)
        load_dir = construct_path_from_root(load_dir)
        file_path = os.path.join(load_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return None
