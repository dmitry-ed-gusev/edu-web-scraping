#!/usr/bin/env python3
# coding=utf-8

"""
    Scraper for RMRS (RS-CLASS.ORG) Register Book.

    Created:  Gusev Dmitrii, 10.01.2021
    Modified: Gusev Dmitrii, 26.04.2021
"""

import logging
import ssl
import xlwt
import concurrent.futures
import requests
import threading
import time
from urllib import request, parse
from bs4 import BeautifulSoup
from pyutilities.pylog import setup_logging
from scraper.utils.utilities import build_variations_list
from scraper.entities.Ship import Ship

# scraper configuration - useful constants
MAIN_URL = "https://lk.rs-class.org/regbook/regbookVessel?ln=ru"
FORM_PARAM = "namer"
ENCODING = "utf-8"
ERROR_OVER_1000_RECORDS = "Результат запроса более 1000 записей! Уточните параметры запроса"
OUTPUT_FILE = "regbook.xls"
WORKERS_COUNT = 20

# setup logging for the whole script
setup_logging(default_path='logging.yml')
log = logging.getLogger('scraper_rsclassorg')

# setup for multithreading processing
thread_local = threading.local()  # thread local storage
futures = []  # list to store future results of threads


def get_session():
    """Return local thread attribute - http session."""
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def perform_request(request_param):
    """Perform one HTTP POST request with one form parameter for search.
    :return: HTML output with found data
    """
    # log.debug('perform_request(): request param [{}].'.format(request_param))  # <- too much output

    if request_param is None or len(request_param.strip()) == 0:  # fail-fast - empty value
        raise ValueError('Provided empty value [{}]!'.format(request_param))

    my_dict = {FORM_PARAM: request_param}             # dictionary for POST request
    data = parse.urlencode(my_dict).encode(ENCODING)  # perform encoding of request
    req = request.Request(MAIN_URL, data=data)        # this will make the method "POST" request
    context = ssl.SSLContext()                        # new SSLContext -> to bypass security certificate check
    response = request.urlopen(req, context=context)  # perform request itself

    return response.read().decode(ENCODING)           # read response and perform decode


def parse_data(html):
    """Parse HTML with one search request results and return dictionary with found ships, using
    IMO number as a key.
    :return: dictionary with ships parsed from HTML response
    """
    # log.debug('parse_data(): processing.')  # <- too much output

    if not html:  # empty html response provided - return empty dictionary
        log.error("Got empty HTML response - returns empty dictionary!")
        return {}

    if html and ERROR_OVER_1000_RECORDS in html:
        log.error("Found over 1000 records - returns empty dictionary!")
        return {}

    soup = BeautifulSoup(html, "html.parser")
    table_body = soup.find("tbody", {"id": "myTable0"})  # find <tbody> tag - table body

    ships_dict = {}  # resulting dictionary with Ships

    if table_body:
        table_rows = table_body.find_all('tr')  # find all rows <tr> inside a table body
        # log.debug("Found row(s): {}".format(len(table_rows)))

        for row in table_rows:  # iterate over all found rows
            # log.debug("Processing row: [{}]".format(row))  # <- too much output

            if row:  # if row is not empty - process it
                cells = row.find_all('td')  # find all cells in the table row <tr>

                # get base ship parameters
                ship_dict = {}
                ship = Ship(123)
                # print(f"===> Ship: {ship}")
                # log.debug(f"---> Ship: {ship}")

                ship_dict['flag'] = cells[0].img['title']        # get attribute 'title' of tag <img>
                ship_dict['main_name'] = cells[1].contents[0]    # get 0 element fro the cell content
                ship_dict['secondary_name'] = cells[1].div.text  # get value of the tag <div> inside the cell
                ship_dict['home_port'] = cells[2].text           # get tag content (text value)
                ship_dict['call_sign'] = cells[3].text           # get tag content (text value)
                ship_dict['reg_number'] = cells[4].text          # get tag content (text value)
                imo_number = cells[5].text                       # get tag content (text value)
                ship_dict['imo_number'] = imo_number

                ships_dict[imo_number] = ship_dict

    return ships_dict


def perform_one_request(search_string):
    """Perform one request to RSCLASS.ORG and parse the output."""
    ships = parse_data(perform_request(search_string))
    log.info("Found ship(s): {}, search string: {}".format(len(ships), search_string))
    return ships


def perform_ships_search_single_thread(symbols_variations):
    """Process list of strings for the search in single thread.
    :param symbols_variations: symbols variations for search
    :return: ships dictionary for the given list of symbols variations
    """
    log.debug("perform_ships_search_single_thread(): perform single-threaded search.")

    if symbols_variations is None or not isinstance(symbols_variations, dict):
        raise ValueError('Provided empty dictionary [{}] or it isn\'t dictionary!'.format(symbols_variations))

    local_ships = {}
    counter = 1

    variations_length = len(symbols_variations[0])

    for search_string in symbols_variations[0]:
        log.debug("Currently processing: {} ({} out of {})".format(search_string, counter, variations_length))
        ships = perform_one_request(search_string)  # request and get HTML + parse received data + get ships dict
        local_ships.update(ships)                   # update main dictionary with found data

        log.info("Found ship(s): {}, total: {}, search string: {}".format(len(ships), len(local_ships), search_string))
        counter += 1  # increment counter

    return local_ships


def perform_ships_search_multiple_threads(symbols_variations):
    """Process list of strings for the search in multiple threads.
    :param symbols_variations: symbols variations for search
    :return: ships dictionary for the given list of symbols variations
    """
    log.debug("perform_ships_search_multiple_threads(): perform multi-threaded search.")

    if symbols_variations is None or not isinstance(symbols_variations, list):
        raise ValueError('Provided empty list [{}] or it isn\'t a list!'.format(symbols_variations))

    local_ships = {}

    # run processing in multiple threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS_COUNT) as executor:
        for symbol in symbols_variations:
            future = executor.submit(perform_one_request, symbol)
            futures.append(future)

        # directly loop over futures to wait for them in the order they were submitted
        for future in futures:
            result = future.result()
            local_ships.update(result)

        log.info(f"Found total ships: {len(local_ships)}.")

        return local_ships


def save_ships(xls_file, ships_map):
    """Save provided search results into xls file.
    :param xls_file:
    :param ships_map:
    :return:
    """
    log.debug('save_ships(): save provided ships map into file: {}.'.format(xls_file))

    if ships_map is None:
        log.warning("Provided empty ships map! Nothing to save!")
        return

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


# main part of the script
# if __name__ == '__main__':
#     print('Don\'t run this script directly! Use wrapper script!')

main_ships = {}
log.info('Starting [scrap_book] module...')

# build list of variations for search strings
start_time = time.time()
variations = build_variations_list()
log.debug("# of built variations: {}".format(len(variations)))
build_variations_duration = time.time() - start_time
log.info(f"Built variations in {build_variations_duration} seconds.")

# process search variations strings
# main_ships.update(perform_ships_search_single_thread(variations))
start_time = time.time()
main_ships.update(perform_ships_search_multiple_threads(variations))
search_duration = time.time() - start_time
log.info(f"Found total ship(s): {len(main_ships)} in {search_duration} seconds.")

# save to excel file
save_ships(OUTPUT_FILE, main_ships)
log.info("Saved ships to file {}".format(OUTPUT_FILE))
