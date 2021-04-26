#!/usr/bin/env python3
# coding=utf-8

"""
    Test for RS Class Register Book scraper.

    Created:  Dmitrii Gusev, 21.03.2021
    Modified: Dmitrii Gusev, 26.04.2021
"""

import unittest
import logging
from scraper.utils.utilities import build_variations_hashmap, build_variations_list, \
    get_hash_bucket_number, add_value_to_hashmap
from pyutilities.pylog import setup_logging

# some useful constants
LOGGER_NAME = 'scraper_rsclassorg_test'


class TestScraperRsClassOrg(unittest.TestCase):

    # static logger initializer
    setup_logging(default_path='../../test_logging.yml')
    log = logging.getLogger(LOGGER_NAME)

    def setUp(self):
        self.log.debug("TestScraperRsClassOrg.setUp()")

    def tearDown(self):
        self.log.debug("TestScraperRsClassOrg.tearDown()")

    @classmethod
    def setUpClass(cls):
        cls.log.debug("TestScraperRsClassOrg.setUpClass()")

    @classmethod
    def tearDownClass(cls):
        cls.log.debug("TestScraperRsClassOrg.tearDownClass()")

    def test_get_hash_bucket_number_empty_value(self):
        self.assertRaises(ValueError, lambda: get_hash_bucket_number(None, 2))
        self.assertRaises(ValueError, lambda: get_hash_bucket_number('', 2))
        self.assertRaises(ValueError, lambda: get_hash_bucket_number('   ', 2))

    def test_get_hash_bucket_number_0_or_less_buckets(self):
        self.assertEqual(0, get_hash_bucket_number('aaa', 0))
        self.assertEqual(0, get_hash_bucket_number('bbb', -1))
        self.assertEqual(0, get_hash_bucket_number('ccc', -19))

    def test_get_hash_bucket_number(self):
        self.assertEqual(9, get_hash_bucket_number('ccc', 10))
        self.assertEqual(4, get_hash_bucket_number('ccc', 5))

    def test_add_value_to_hashmap_empty_or_none_hashmap(self):
        self.assertRaises(ValueError, lambda: add_value_to_hashmap(None, 'aaa', 0))
        self.assertRaises(ValueError, lambda: add_value_to_hashmap(list(), 'aaa', 0))

    def test_add_value_to_hashmap_empty_or_none_value(self):
        self.assertRaises(ValueError, lambda: add_value_to_hashmap(dict(), '', 0))
        self.assertRaises(ValueError, lambda: add_value_to_hashmap(dict(), '   ', 0))
        self.assertRaises(ValueError, lambda: add_value_to_hashmap(dict(), None, 0))

    def test_add_value_to_hashmap(self):
        self.assertEqual({0: ['aaa']}, add_value_to_hashmap(dict(), 'aaa', 0))
        self.assertEqual({0: ['aaa', 'bbb']}, add_value_to_hashmap({0: ['aaa']}, 'bbb', 0))
        self.assertEqual({0: ['aaa', 'bbb'], 4: ['ccc']}, add_value_to_hashmap({0: ['aaa', 'bbb']}, 'ccc', 5))

    def test_build_variations_hashmap_0_buckets(self):
        self.assertEqual(1, len(build_variations_hashmap().keys()))

    def test_build_variations_hashmap(self):
        self.assertEqual(10, len(build_variations_hashmap(10).keys()))

    def test_build_variations_list(self):
        self.assertTrue(isinstance(build_variations_list(), list))
        self.assertEqual(9522, len(build_variations_list()))


if __name__ == '__main__':
    unittest.main()
