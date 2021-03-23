#!/usr/bin/env bash

###############################################################################
#
#   Build script for [fleet-db-scraping] utility.
#
#   Created:  Dmitrii Gusev, 23.03.2021
#   Modified:
#
###############################################################################

# todo: review and rework!!!

# install necessary requirements
pip install -r requirements.txt

# create virtual environment
virtualenv .venv

# activate environment
source .venv/bin/activate

# install necessary dependencies
pip install -r requirements.txt

# run unit tests with coverage
python3 -m nose2 -v -s pyutilities/tests --plugin nose2.plugins.junitxml -X --with-coverage --coverage pyutilities \
    --coverage-report xml --coverage-report html

# deactivate virtual environment (exit)
deactivate
