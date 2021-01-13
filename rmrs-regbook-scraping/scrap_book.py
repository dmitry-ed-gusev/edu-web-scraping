#!/usr/bin/env python
# coding=utf-8

"""
    Scraper for RMRS Register Book :)

    Created:  Gusev Dmitrii, 10.01.2021
    Modified: Gusev Dmitrii, 12.01.2021
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

# scraper configuration
MAIN_URL = "https://lk.rs-class.org/regbook/regbookVessel?ln=ru"
FORM_PARAM = "namer"
ENCODING = "utf-8"
ERROR_OVER_1000_RECORDS = "Результат запроса более 1000 записей! Уточните параметры запроса"
OUTPUT_FILE = "regbook.xls"

# setup logging for the whole script
setup_logging(default_path='logging.yml')
log = logging.getLogger('scrap_book')


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
    :return: list of ships parsed from HTML response
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


def process_chars(characters):
    """Process characters paired from the provided string.
    :param characters:
    :return:
    """
    local_ships = {}
    for letter1 in characters:
        log.debug("Currently processing: " + letter1)
        for letter2 in characters:
            html = perform_request(letter1 + letter2)  # request site and get HTML
            ships = parse_data(html)  # parse data and get ships dictionary
            local_ships.update(ships)  # update main dictionary with found data
            log.debug("Found ship(s): {}, total: {}, search string: {}"
                      .format(len(ships), len(local_ships), letter1 + letter2))
    return local_ships


def save_ships(xls_file, ships_map):
    """Save search results into xls file
    :param xls_file:
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

# process russian characters
main_ships.update(process_chars(RUS_CHARS))
log.debug("Processed russian characters.")
log.info("Found ship(s): {}".format(len(main_ships)))

# process english characters
main_ships.update(process_chars(ENG_CHARS))
log.debug("Processed english characters.")
log.info("Found ship(s): {}".format(len(main_ships)))

# process numbers
main_ships.update(process_chars(NUM_CHARS))
log.debug("Processed numbers.")
log.info("Found ship(s): {}".format(len(main_ships)))

# save to excel file
save_ships(OUTPUT_FILE, main_ships)
log.info("Saved ships to file {}".format(OUTPUT_FILE))
