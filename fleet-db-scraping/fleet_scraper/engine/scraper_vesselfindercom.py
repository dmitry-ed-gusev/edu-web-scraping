#!/usr/bin/env python3
# coding=utf-8

"""
    Scraper for VESSEL FINDER Ship Book.

    Created:  Gusev Dmitrii, 29.04.2021
    Modified:
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
