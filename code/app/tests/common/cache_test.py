import math
import os
import time
import unittest
from typing import Any

from app.common.cache import Cache


def expensive_method(input_data: Any) -> Any:
    """Dummy method that takes 10ms to be executed and bypass the input"""
    time.sleep(10e-3)
    return input_data


class TestCache(unittest.TestCase):
    """UT tests for the Cache class"""

    TEST_MODULE_NAME = 'test_module'
    TEST_KEY = 'test'
    TEST_VALUE = math.pi

    def test_cache_expiration(self):
        Cache.clear_all()
        Cache.save_to_key(self.TEST_MODULE_NAME, self.TEST_KEY, self.TEST_VALUE)
        self.assertFalse(Cache.expired(self.TEST_MODULE_NAME))

        Cache._modules_timestamp[self.TEST_MODULE_NAME] = time.time() - Cache.DISK_SYNC_SECONDS - 1
        self.assertTrue(Cache.expired(self.TEST_MODULE_NAME))

        Cache.clear_all()

    def test_performance_difference(self):
        """UT for testing the cache performance difference"""
        times_to_run = 100
        maximum_ratio = 0.05  # 95% minimum performance difference
        Cache.clear_all()

        # test method with cache
        def run_expensive_method_with_cache():
            if Cache.get_from_key(self.TEST_MODULE_NAME, self.TEST_KEY) is not None:
                return Cache.get_from_key(self.TEST_MODULE_NAME, self.TEST_KEY)
            result = expensive_method(self.TEST_VALUE)
            Cache.save_to_key(self.TEST_MODULE_NAME, self.TEST_KEY, result)
            return result

        # test method without cache
        def run_expensive_method_without_cache():
            return expensive_method(self.TEST_VALUE)

        without_cache_start_time = time.time()
        for index in range(times_to_run):
            run_expensive_method_without_cache()
        without_cache_duration = time.time() - without_cache_start_time

        with_cache_start_time = time.time()
        for index in range(times_to_run):
            run_expensive_method_with_cache()
        with_cache_duration = time.time() - with_cache_start_time

        gain_ratio = with_cache_duration/without_cache_duration

        self.assertTrue(
            gain_ratio < maximum_ratio,
            "Gain ration {:.2f}% did not meet the {:.2f}% performance gain".format(
                (1.0 - maximum_ratio) * 100.0, gain_ratio
            )
        )

        Cache.clear_all()

    def test_cache_store_data_in_memory(self):
        """UT for testing if a key is save into the memory"""
        Cache.clear_all()
        Cache.save_to_key(self.TEST_MODULE_NAME, self.TEST_KEY, self.TEST_VALUE)
        self.assertIn(self.TEST_MODULE_NAME, Cache._data, "Test module wasn't saved into cache memory")

        cache_module_data = Cache._data[self.TEST_MODULE_NAME]
        self.assertIn(self.TEST_KEY, cache_module_data, "Test key wasn't saved into cache module")

        cache_value_data = Cache._data[self.TEST_MODULE_NAME][self.TEST_KEY]
        self.assertEqual(self.TEST_VALUE, cache_value_data, "Test value wasn't saved into cache module key")

        Cache.clear_all()

    def test_cache_store_data_in_file(self):
        """UT for testing if a key is save into the memory"""
        Cache.clear_all()
        Cache.save_to_key(self.TEST_MODULE_NAME, self.TEST_KEY, self.TEST_VALUE)
        self.assertFalse(Cache.expired(self.TEST_MODULE_NAME))

        cache_filename = Cache.get_cache_file(self.TEST_MODULE_NAME)
        self.assertTrue(os.path.isfile(cache_filename))

        module_data = Cache.load_from_file(self.TEST_MODULE_NAME)
        self.assertIn(self.TEST_KEY, module_data, "Test key wasn't saved into cache module")

        cache_value_data = module_data[self.TEST_KEY]
        self.assertEqual(self.TEST_VALUE, cache_value_data, "Test value wasn't saved into cache module key")

        Cache.clear_all()
