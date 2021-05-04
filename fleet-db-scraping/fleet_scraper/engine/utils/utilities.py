# coding=utf-8

"""
    Common utilities module for Fleet DB Scraper.

    Created:  Gusev Dmitrii, 26.04.2021
    Modified: Gusev Dmitrii, 02.05.2021
"""

import xlwt
import logging
import hashlib
from datetime import datetime

RUS_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ENG_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUM_CHARS = "0123456789"
SPEC_CHARS = "-"

log = logging.getLogger('scraper_utilities')


def get_hash_bucket_number(value: str, buckets: int) -> int:
    """Generate hash bucket number for the given value, generated bucket number
    will be less than provided buckets count.
    :param value:
    :param buckets:
    :return:
    """
    log.debug(f'get_hash_bucket_number(): value [{value}], buckets [{buckets}].')

    if value is None or len(value.strip()) == 0:  # fail-fast if value is empty
        raise ValueError('Provided empty value!')

    if buckets <= 0:  # if buckets number <= 0 - generated bucket number is always 0
        log.debug(f'get_hash_bucket_number(): buckets number [{buckets}] <= 0, return 0!')
        return 0

    # value is OK and buckets number is > 0
    hex_hash = hashlib.md5(value.encode('utf-8')).hexdigest()  # generate hexadecimal hash
    int_hash = int(hex_hash, 16)                               # convert it to int (decimal)
    bucket_number = int_hash % buckets                         # define bucket number as division remainder
    log.debug(f'get_hash_bucket_number(): hash: [{hex_hash}], decimal hash: [{int_hash}], '
              f'generated bucket: [{bucket_number}].')

    return bucket_number


def add_value_to_hashmap(hashmap: dict, value: str, buckets: int) -> dict:
    """Add value to the provided hash map with provided total buckets number.
    :param hashmap:
    :param value:
    :param buckets:
    """
    log.debug(f'add_value_to_hashmap(): hashmap [{hashmap}], value [{value}], buckets [{buckets}].')

    if hashmap is None or not isinstance(hashmap, dict):  # fail-fast - hash map type check
        raise ValueError(f'Provided empty hashmap [{hashmap}] or it isn\'t dictionary!')
    if value is None or len(value.strip()) == 0:  # fail-fast - empty/zero-length value
        raise ValueError(f'Provided empty value [{value}]!')

    bucket_number = get_hash_bucket_number(value, buckets)  # bucket number for the value
    if hashmap.get(bucket_number) is None:  # bucket is not initialized yet
        hashmap[bucket_number] = list()
    hashmap.get(bucket_number).append(value)  # add value to the bucket

    return hashmap


def build_variations_hashmap(buckets: int = 0) -> dict:
    """Build hashmap of all possible variations of symbols for further search.
    :param buckets: number of buckets to divide symbols
    :return: list of variations
    """
    log.debug(f'build_variations_hashmap(): buckets [{buckets}].')

    result = dict()  # resulting dictionary

    for letter1 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
        for letter2 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
            result = add_value_to_hashmap(result, letter1 + letter2, buckets)  # add value to hashmap

            for spec_symbol in SPEC_CHARS:
                result = add_value_to_hashmap(result, letter1 + spec_symbol + letter2, buckets)  # add value to hashmap

    return result


def build_variations_list() -> list:
    """Build list of possible variations of symbols for search.
    :return: list of variations
    """
    log.debug('build_variations_list(): processing.')

    result = list()  # resulting list

    for letter1 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
        for letter2 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
            result.append(letter1 + letter2)  # add value to resulting list

            for spec_symbol in SPEC_CHARS:
                result.append(letter1 + spec_symbol + letter2)  # add value to resulting list

    return result


# todo: implement unit tests!
def generate_timed_filename():
    """"""

    # get current datetime
    current_datetime = datetime.now()

    print(current_datetime.strftime('%d'))

    # todo: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    # todo: implementation! should be smthg like: dd-MM-yyyy-hh_mm_ss-rsclassorg
    # todo: check - is generated name unique for the givel catalog? - extract to different method?
    pass


# todo: implement unit tests!
# todo: finish implementation!
def save_ships_to_excel(ships: dict, xls_file: str, xls_sheet_name: str = "ships", xls_override: bool = False):
    """Save provided list of ships entities to xls file.
    :param xls_file: excel file to save provided ships
    :param xls_sheet_name: sheet name for ships save in excel workbook
    :param xls_override: override existing excel file or not? if not and file exists - exception will be raised
    :param ships: ships list to save
    :return:
    """
    log.debug(f'save_ships(): save provided ships map into file: {xls_file}.')

    if ships is None or not ships:  # fail-fast - check provided ships dictionary
        log.warning("Provided empty ships map! Nothing to save!")
        return

    if xls_file is None or len(xls_file.strip()) == 0:  # fail-fast - check provided xls file name
        raise ValueError('Provided empty excel file name - can\'t save!')

    # todo: check xls sheet name - if is empty - back to default

    # todo: check if excel file exists and override is False - exception!

    book = xlwt.Workbook()              # create workbook
    sheet = book.add_sheet("reg_book")  # create new sheet

    # create header
    row = sheet.row(0)
    row.write(0, 'flag')
    row.write(1, 'main_name')
    row.write(2, 'secondary_name')
    row.write(3, 'home_port')
    row.write(4, 'call_sign')
    row.write(5, 'reg_number')
    row.write(6, 'imo_number')

    row_counter = 1
    for key in ships_map:  # iterate over ships map with keys / values
        row = sheet.row(row_counter)  # create new row
        ship = ships_map[key]         # get ship from map
        # write cells values
        row.write(0, ship['flag'])
        row.write(1, ship['main_name'])
        row.write(2, ship['secondary_name'])
        row.write(3, ship['home_port'])
        row.write(4, ship['call_sign'])
        row.write(5, ship['reg_number'])
        row.write(6, ship['imo_number'])
        row_counter += 1

    book.save(xls_file)  # save created workbook


# todo: implement unit tests that module isn't runnable directly!
if __name__ == '__main__':
    # print('Don\'t run this utility script directly!')
    generate_timed_filename()
