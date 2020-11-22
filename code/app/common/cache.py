import copy
import glob
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List


class Cache:
    """Cache handling class, storing data in the memory with disk persistence"""
    _modules_timestamp = {}  # to store the modules keys and their last updated timestamp
    _data = {}
    DISK_SYNC_SECONDS = 30

    @staticmethod
    def is_disabled() -> bool:
        """Determine whether the cache is globally disabled or not"""
        return os.environ['CACHE_DISABLED'] == 1 if 'CACHE_DISABLED' in os.environ else False

    @staticmethod
    def list_keys(module: str) -> List:
        """List the cache data keys for a given module"""
        return [key for key in Cache._data[module]] if module in Cache._data else None

    @staticmethod
    def clear_all() -> None:
        """Clear cache data and delete files"""
        Cache._data = {}
        modules_names = [module for module in Cache._modules_timestamp]
        for module in modules_names:
            del(Cache._modules_timestamp[module])
            if module in Cache._data:
                del (Cache._data[module])

            if os.path.isfile(Cache.get_cache_file(module)):
                os.remove(Cache.get_cache_file(module))

    @staticmethod
    def get_cache_file(module: str) -> str:
        """Gets the default cache data file path"""
        filepath = os.path.join(os.environ['DATA_DIR'], 'cache')
        Path(filepath).mkdir(parents=True, exist_ok=True)
        return os.path.join(filepath, '{}.json'.format(module))

    @staticmethod
    def expired(module: str) -> bool:
        """Determines whether the cache has already expired"""
        if module not in Cache._modules_timestamp:
            return True
        return Cache._modules_timestamp[module] + Cache.DISK_SYNC_SECONDS < time.time()

    @staticmethod
    def sync(module: str) -> None:
        """Sync current cache data with the file (auto-generated) if expired"""
        # just sync after expiration
        if not Cache.expired(module):
            return

        filename = Cache.get_cache_file(module)
        with open(filename, 'w') as dump_file:
            json.dump(Cache._data[module], dump_file, indent=4, sort_keys=True)

        Cache._modules_timestamp[module] = time.time()

    @staticmethod
    def load_from_file(module: str) -> Dict:
        """Save current cache instance from a file (auto-generated)"""
        if Cache.is_disabled():
            return {}

        filename = Cache.get_cache_file(module)
        if not os.path.isfile(filename):
            return {}

        with open(filename, 'r') as dump_file:
            return json.load(dump_file)

    @staticmethod
    def get_from_key(module: str, key: str) -> Any:
        """Gets the value for a given key from the cache. None if not exists."""
        if Cache.is_disabled():
            return None
        if module not in Cache._data:
            Cache._data[module] = Cache.load_from_file(module)
        return copy.deepcopy(Cache._data[module][key]) if key in Cache._data[module] else None

    @staticmethod
    def save_to_key(module: str, key: str, value: Any) -> None:
        """Sets the value for a given key into the cache"""
        if Cache.is_disabled():
            return

        # if there's no data for the module, create and empty dict
        if module not in Cache._data:
            Cache._data[module] = Cache.load_from_file(module)

        Cache._data[module][key] = value
        Cache.sync(module)
