import os
import shutil
from typing import List
from utils import fetch_file_paths, obj_save, obj_load, path_to_basename


class Cache:

    cache_dir: str

    def __init__(self, file_path: str, cache_location: str):
        """This class acts as a file specific cache."""
        [file_name, file_extension] = path_to_basename(file_path).split('.')
        self.cache_dir = f"{cache_location}/{file_name}_{file_extension}"

        if not self._check_cache_exists():
            self.create_new()

    def _check_cache_exists(self) -> bool:
        """Checks if the cache directory exists."""
        return os.path.isdir(self.cache_dir)

    def create_new(self):
        """This wipes and create a new empty cache directory."""
        try:
            shutil.rmtree(self.cache_dir)
        except FileNotFoundError:
            pass

        os.makedirs(f"{self.cache_dir}/frames", exist_ok=True)

    def get_cache_directory(self) -> str:
        """Return the path to the file specific cache directory."""
        return self.cache_dir

    def get_cached_frames(self, file_extension="png") -> List[str]:
        """Returns files paths of all caches frames, [] if none are  found."""
        target_path = f"{self.cache_dir}/frames"

        # check if target dir "/frames" exists and is not empty
        if os.path.isdir(target_path):
            if os.listdir(target_path):
                return fetch_file_paths(target_path, file_extension)

        return []

    def store_object(self, obj: object, name: str):
        """Store an object in the file cache."""
        obj_save(obj, f"{self.cache_dir}/{name}.pkl")

    def load_object(self, name: str, default=None) -> object:
        """Retrieve an object from the file cache, return default value if not found."""
        obj_path = f"{self.cache_dir}/{name}.pkl"

        if os.path.exists(obj_path):
            return obj_load(f"{self.cache_dir}/{name}.pkl")
        else:
            return default

    def delete_object(self, target: str):
        """Delete an object from the file cache."""
        obj_path = f"{self.cache_dir}/{target}.pkl"
        if os.path.exists(obj_path):
            os.remove(obj_path)

