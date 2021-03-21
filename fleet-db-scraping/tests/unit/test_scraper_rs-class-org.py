#!/usr/bin/env python3
# coding=utf-8

"""
    Test for RS Class Register Book scraper.

    Created:  Dmitrii Gusev, 21.03.2021
    Modified:
"""

import unittest
from scraper.engine.scraper_rsclassorg import build_variations_list


class TestScraperRsClassOrg(unittest.TestCase):

    def test_build_variations_list_0_buckets(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
        build_variations_list()

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()
