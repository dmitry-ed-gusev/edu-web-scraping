#!/usr/bin/env bash

###############################################################################
#
#   Build and test script for [fleet-db-scraping] utility.
#
#   Created:  Dmitrii Gusev, 23.03.2021
#   Modified: Dmitrii Gusev, 27.04.2021
#
###############################################################################

# - install virtualenv
pip3 install virtualenv

# - create virtual environment
virtualenv --verbose .venv

# - activate virtual environment
source .venv/bin/activate

# - upgrade pip3 in virtual environment
#python3 -m pip3 install --upgrade pip

# - install necessary dependencies in virtual environment (according to requirements)
pip3 install -r requirements.txt

# - run unit tests with coverage and XML/HTML reports
python3 -m nose2 --verbose --start-dir fleet_scraper_tests --plugin nose2.plugins.junitxml \
    -X --with-coverage --coverage fleet_scraper \
    --coverage-report xml --junit-xml-path .coverage/nose2-junit.xml --coverage-report html

# - deactivate virtual environment (exit)
deactivate
