#!/usr/bin/env python3
# coding=utf-8

"""
    Scraper for Clarksons.net site.

    Site(s):
        * https://www.clarksons.net - main url

    Created:  Gusev Dmitrii, 2020
    Modified: Dmitrii Gusev, 04.05.2021
"""

import logging
from pyutilities.pylog import setup_logging


# setup logging for the whole script
# setup_logging(default_path='logging.yml')
log = logging.getLogger('scraper_clarksonsnet')


def scrap():
    """"""
    log.info("scrap(): processing clarksons.net")


# main part of the script
if __name__ == '__main__':
    print('Don\'t run this script directly! Use wrapper script!')
