#!/usr/bin/env python3
# coding=utf-8

"""
    Scraper for Vessel Finder ships storage / site.

    Site(s):
        * https://www.vesselfinder.com/ - main url

    Created:  Gusev Dmitrii, 29.04.2021
    Modified: Dmitrii Gusev, 04.05.2021
"""

import logging
from pyutilities.pylog import setup_logging

# setup logging for the whole script
# setup_logging(default_path='logging.yml')
log = logging.getLogger('scraper_vesselfinder')


def scrap():
    """"""
    log.info("scrap(): processing vesselfinder.com")


# main part of the script
if __name__ == '__main__':
    print('Don\'t run this script directly! Use wrapper script!')
