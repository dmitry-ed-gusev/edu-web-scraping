#!/usr/bin/env bash

###############################################################################
#
#   Build script for [fleet-db-scraping] utility.
#
#   Created:  Dmitrii Gusev, 23.03.2021
#   Modified:
#
###############################################################################

# - install virtualenv
pip3 install virtualenv

# - create virtual environment
virtualenv .venv

# - activate virtual environment
source .venv/bin/activate

# - install necessary dependencies in virtual environment
pip install -r requirements.txt

# - run unit tests with coverage
python3 -m nose2 -v -s scraper_tests --plugin nose2.plugins.junitxml -X --with-coverage --coverage scraper \
    --coverage-report xml --coverage-report html

# - deactivate virtual environment (exit)
deactivate
