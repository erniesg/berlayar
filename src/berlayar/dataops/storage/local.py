import os
import json
import aiofiles
from berlayar.utils.path import construct_path_from_root

class LocalStorage:
    def __init__(self, base_dir="raw_data"):
        self.base_dir = base_dir

    async def save_data(self, filename, data, subdirectory=None):
        save_dir = self.base_dir
        if subdirectory:
            save_dir = os.path.join(save_dir, subdirectory)
        save_dir = construct_path_from_root(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        async with aiofiles.open(file_path, 'w') as file:
            await file.write(json.dumps(data, indent=4))

    async def load_data(self, filename, subdirectory=None):
        load_dir = self.base_dir
        if subdirectory:
            load_dir = os.path.join(load_dir, subdirectory)
        load_dir = construct_path_from_root(load_dir)
        file_path = os.path.join(load_dir, filename)
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, 'r') as file:
                return json.loads(await file.read())
        else:
            return None
