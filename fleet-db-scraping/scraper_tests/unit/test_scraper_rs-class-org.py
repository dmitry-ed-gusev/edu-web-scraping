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

    def setUp(self):
        print("TestScraperRsClassOrg.setUp()")

    def tearDown(self):
        print("TestScraperRsClassOrg.tearDown()")

    @classmethod
    def setUpClass(cls):
        print("TestScraperRsClassOrg.setUpClass()")

    @classmethod
    def tearDownClass(cls):
        print("TestScraperRsClassOrg.tearDownClass()")

    def test_build_variations_list_0_buckets(self):
        self.assertEqual(1, len(build_variations_list().keys()))


if __name__ == '__main__':
    unittest.main()
