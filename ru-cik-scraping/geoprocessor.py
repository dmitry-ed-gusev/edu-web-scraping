#!/usr/bin/env python
# coding=utf-8

"""
    Script for loading commissions data from excel into db (sqlite).
    Pandas isn't enough for this script (suitable for xslx).
    xlrd - for reading, xlwt - fro writing excel files (suitable for xls).

    Created: Gusev Dmitrii, 01.02.2017
    Modified:
"""

import os
import logging
import xlrd  # most suitable for xls
from pyutilities.utils import setup_logging, get_str_val, get_int_val
from geodb import DB_NAME, db_create, db_add_commission, db_add_address

# common constants
LOGGER_NAME = 'geoprocessor'
LOGGER_CONFIG = 'logging.yml'
XLS_SOURCE_FILE = 'nw-uiks.xls'
DEFAULT_ENCODING = 'utf-8'
# module initialization
setup_logging(default_path='logging.yml')
log = logging.getLogger(LOGGER_NAME)


def load_one_sheet(sheet):
    log.debug('load_one_sheet(): processing sheet [{}].'.format(sheet.name.encode(DEFAULT_ENCODING)))

    # special actions for SPb and Novgorod
    is_spb_novg = False
    people_count_index = 4
    sheet_name = sheet.name.encode(DEFAULT_ENCODING)
    if sheet_name in 'Санкт-Петербург' or sheet_name in 'Новгород':
        is_spb_novg = True
        people_count_index = 5

    city = ''
    territory_commission = ''
    # sector_commission = ''
    people_count = 0
    last_commission_id = 0
    street = ''
    # building_number = 0
    for rownumber in range(sheet.nrows):
        if rownumber == 0:  # skip first row
            continue
        if rownumber == 1 and (is_spb_novg or sheet_name in 'Вологда'):
            continue

        for colnumber in range(sheet.ncols):
            value = sheet.cell_value(rownumber, colnumber)
            value_type = sheet.cell_type(rownumber, colnumber)

            if value and value_type != xlrd.XL_CELL_EMPTY:  # cell isn't empty
                # commission information
                if colnumber == 0:  # city name
                    city = get_str_val(value, value_type, DEFAULT_ENCODING)
                elif colnumber == 1:  # territory commission
                    territory_commission = get_str_val(value, value_type, DEFAULT_ENCODING)
                    # calculate people count for commission / todo: move check to db module
                    people_count = get_int_val(sheet.cell_value(rownumber, people_count_index),
                                               sheet.cell_type(rownumber, people_count_index), DEFAULT_ENCODING)
                elif colnumber == 2:  # sector commission (end of cells for commission)
                    sector_commission = get_int_val(value, value_type, DEFAULT_ENCODING)
                    # insert new commission into db
                    last_commission_id = db_add_commission(DB_NAME, city, territory_commission,
                                                           sector_commission, people_count)
                # address information
                elif colnumber == 3:
                    street = get_str_val(value, value_type, DEFAULT_ENCODING)
                    if not is_spb_novg:
                        building_number = ''
                        db_add_address(DB_NAME, street, building_number, last_commission_id)
                elif colnumber == 4 and is_spb_novg:  # read buildings numbers only for SPb and Novgorod
                    building_number = get_str_val(value, value_type, DEFAULT_ENCODING)
                    db_add_address(DB_NAME, street, building_number, last_commission_id)

            # just debug
            #log.debug('cell[{}, {}]: type -> {}, value -> {}'.format(rownumber, colnumber, value_type,
            #                                                         get_str_val(value, value_type, DEFAULT_ENCODING)))
            #print '\n===============================================\n'


def load_xls_data(xls_file):
    log.debug('load_xls_data(): loading data from source file [{}].'.format(xls_file))

    # Load the whole spreadsheet
    excel_book = xlrd.open_workbook(XLS_SOURCE_FILE, encoding_override='cp1251')

    # load areas in database
    # sheets_names = []
    # sheets = []

    for sheet in excel_book.sheet_names():
        log.debug('Loading sheet [{}] from source file.'.format(sheet.encode(DEFAULT_ENCODING)))
        load_one_sheet(excel_book.sheet_by_name(sheet))
        # sheets_names.append(sheet.encode(DEFAULT_ENCODING))  # encode value to UTF-8
        # sheet_object = excel_book.sheet_by_name(sheet)
        # sheets.append(sheet_object)

    # sheet = excel_book.sheet_by_index(0)
    # load_one_sheet(sheet)


if __name__ == '__main__':
    log.info('Starting GeoProcessor module...')

    if not os.path.exists(DB_NAME):
        log.warn("Database [{}] doesn't exist! Creating...".format(DB_NAME))
        db_create(DB_NAME)  # create target db

    # load data from xls file
    load_xls_data(XLS_SOURCE_FILE)
