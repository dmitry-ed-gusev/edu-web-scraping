#!/usr/bin/env python3
# coding=utf-8

"""
    Scraper for RMRS Register Book :)

    Created:  Gusev Dmitrii, 10.01.2021
    Modified: Gusev Dmitrii, 20.03.2021
"""


import logging
import ssl
import xlwt
from urllib import request, parse
from bs4 import BeautifulSoup
from pyutilities.pylog import setup_logging

# characters for search engine
RUS_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ENG_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUM_CHARS = "0123456789"
SPEC_SYMBOLS = "-"

# scraper configuration
MAIN_URL = "https://lk.rs-class.org/regbook/regbookVessel?ln=ru"
FORM_PARAM = "namer"
ENCODING = "utf-8"
ERROR_OVER_1000_RECORDS = "Результат запроса более 1000 записей! Уточните параметры запроса"
OUTPUT_FILE = "regbook.xls"

# setup logging for the whole script
setup_logging(default_path='../logging.yml')
log = logging.getLogger('scrap_book')


# todo: implement save / load variations to / from file (cache)
def build_variations_list():
    """Build list of all possible variations of symbols for further search.
    :return: list of variations
    """
    variations = list()
    # - process russian characters
    for letter1 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
        for letter2 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
            variations.append(letter1 + letter2)
            for spec_symbol in SPEC_SYMBOLS:
                variations.append(letter1 + spec_symbol + letter2)

    # # - process english characters
    # for letter1 in ENG_CHARS:
    #     for letter2 in ENG_CHARS:
    #         variations.append(letter1 + letter2)
    #
    # # - process mix russian / english
    # for letter1 in RUS_CHARS:
    #     for letter2 in ENG_CHARS:
    #         variations.append(letter1 + letter2)
    #
    # # - process mix russian / english + numbers
    # for letter1 in RUS_CHARS + ENG_CHARS:
    #     for letter2 in NUM_CHARS:
    #         variations.append(letter1 + letter2)

    # - sort list before return
    variations.sort()

    return variations


def perform_request(request_param):
    """Perform one HTTP POST request with one form parameter for search.
    :return: HTML output with found data
    """
    my_dict = {FORM_PARAM: request_param}             # dictionary for POST request
    data = parse.urlencode(my_dict).encode(ENCODING)  # perform encoding of request
    req = request.Request(MAIN_URL, data=data)        # this will make the method "POST" request
    context = ssl.SSLContext()                        # new SSLContext -> to bypass security certificate check
    response = request.urlopen(req, context=context)  # perform request itself
    return response.read().decode(ENCODING)           # read response and perform decode


def parse_data(html):
    """Parse HTML with search results.
    :return: dictionary () with ships parsed from HTML response
    """

    if not html:  # empty html response provided - return empty dictionary
        log.error("Returned empty HTML response!")
        return {}

    if html and ERROR_OVER_1000_RECORDS in html:
        log.error("Found over 1000 records!")
        return {}

    soup = BeautifulSoup(html, "html.parser")
    table_body = soup.find("tbody", {"id": "myTable0"})  # find <tbody> tag - table body

    ships_dict = {}

    if table_body:
        table_rows = table_body.find_all('tr')  # find all rows <tr> inside a table body
        #print("Found row(s): {}".format(len(table_rows)))

        for row in table_rows:  # iterate over all found rows
            #print("\nROW ===> ", row)

            if row:  # if row is not empty - process it
                ship_dict = {}
                cells = row.find_all('td')  # find all cells in the table row <tr>

                # for col in cells:  # process all cells in the table row <tr>
                #     print("COL ===> ", col, "val -> ", col.text)

                # get ship parameters
                ship_dict['flag'] = cells[0].img['title']        # get attribute 'title' of tag <img>
                ship_dict['main_name'] = cells[1].contents[0]    # get 0 element fro the cell content
                ship_dict['secondary_name'] = cells[1].div.text  # get value of the tag <div> inside the cell
                ship_dict['home_port'] = cells[2].text           # get tag content (text value)
                ship_dict['callsign'] = cells[3].text            # get tag content (text value)
                ship_dict['reg_number'] = cells[4].text          # get tag content (text value)
                imo_number = cells[5].text                       # get tag content (text value)
                ship_dict['imo_number'] = imo_number

                ships_dict[imo_number] = ship_dict

    return ships_dict


def perform_ships_search(symbols_variations):
    """Process list of strings for the search.
    :param symbols_variations: symbols variations for search
    :return: ships dictionary for the given list of symbols variations
    """
    local_ships = {}
    counter = 1
    variations_length = len(variations)
    for search_string in symbols_variations:
        log.debug("Currently processing: {} ({} out of {})".format(search_string, counter, variations_length))
        html = perform_request(search_string)  # request site and get HTML
        ships = parse_data(html)               # parse received data and get ships dictionary
        local_ships.update(ships)              # update main dictionary with found data
        log.debug("Found ship(s): {}, total: {}, search string: {}"
                  .format(len(ships), len(local_ships), search_string))
        counter += 1  # increment counter

    return local_ships


def save_ships(xls_file, ships_map):
    """Save search results into xls file
    :param xls_file:
    :param ships_map:
    :return:
    """
    if not ships_map:
        log.warning("Provided empty ships map!")
        return

    book = xlwt.Workbook()              # create workbook
    sheet = book.add_sheet("reg_book")  # create new sheet

    # create header
    row = sheet.row(0)
    row.write(0, 'flag')
    row.write(1, 'main_name')
    row.write(2, 'secondary_name')
    row.write(3, 'home_port')
    row.write(4, 'callsign')
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
        row.write(4, ship['callsign'])
        row.write(5, ship['reg_number'])
        row.write(6, ship['imo_number'])
        row_counter += 1

    book.save(xls_file)  # save created workbook


# main part of the script
main_ships = {}

log.info('Starting [scrap_book] module...')
log.debug('Ready to parse the site :)')

# build list of variations for search strings
variations = build_variations_list()
log.debug("Built list of variations: {}".format(variations))
log.debug("# of built variations: {}".format(len(variations)))

# process search variations strings
main_ships.update(perform_ships_search(variations))
log.debug("Processed all characters.")
log.info("Found total ship(s): {}".format(len(main_ships)))

#
# # process english characters
# main_ships.update(process_chars(ENG_CHARS))
# log.debug("Processed english characters.")
# log.info("Found ship(s): {}".format(len(main_ships)))
#
# # process numbers
# main_ships.update(process_chars(NUM_CHARS))
# log.debug("Processed numbers.")
# log.info("Found ship(s): {}".format(len(main_ships)))
#
# # save to excel file
# save_ships(OUTPUT_FILE, main_ships)
# log.info("Saved ships to file {}".format(OUTPUT_FILE))
