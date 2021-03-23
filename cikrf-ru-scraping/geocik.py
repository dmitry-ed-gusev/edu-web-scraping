#!/usr/bin/env python
# coding=utf-8

"""
    Parser for CIK geo information for election commissions.
    Created: Gusev Dmitrii, 05.02.2017
    Modified: Gusev Dmitrii, 11.02.2017
"""

import os
import logging
import json
import urllib2
from sqlite3 import IntegrityError
from pyutilities.utils import setup_logging, save_file_with_path
from geodb import DB_NAME, db_create, db_add_single_geo_point, db_get_not_processed_geo_points_ids, \
    db_add_multiple_geo_points, db_get_geo_point_id, GeoDB

# todo: add cmd line parameters/argparse

# some useful constants
JSON_ENCODING = 'windows-1251'
DATA_ENCODING = 'utf-8'
USE_PROXY = False
PROXY_SERVER = 'webproxy.merck.com:8080'
LOGGING_CONFIG = 'logging.yml'
LOGGER_NAME = 'geocik'
# useful URLs for processing
URL_TOP = 'http://cikrf.ru/services/lk_tree'
URL_POINT = 'http://cikrf.ru/services/lk_tree/?id={}'
URL_MSK = 'http://cikrf.ru/services/lk_tree/?ret=0&id={}'
URL_SPB = 'http://cikrf.ru/services/lk_tree/?ret=1&id={}'
URL_SPB_AREA = 'http://cikrf.ru/services/lk_tree/?ret=0&id={}'


def add_geo_points(json_points, parent_id, batching=True, geodb_instance=None, text_filter=None):
    # log.debug('add_geo_points(): adding geo points to db')  # <- too much output

    # iterate over children and put them to db
    points_list = []
    for point in json_points:
        point_id = point['id']
        point_text = point['text'].encode(DATA_ENCODING)
        point_children = point['children']
        point_intid = point['a_attr']['intid']
        if not point_intid:
            point_intid = 'NULL'
        point_levelid = point['a_attr']['levelid']

        # if we use filtering by text - apply it
        if batching:  # if batching -> add point to list

            if text_filter:  # apply text filtering
                if text_filter in point_text:
                    points_list.append([point_id, point_intid, point_text, point_levelid, point_children, parent_id, 0])
            else:
                points_list.append([point_id, point_intid, point_text, point_levelid, point_children, parent_id, 0])

        else:  # if not batching -> directly add geo point (one by one)

            if text_filter:  # apply text filter
                if text_filter in point_text:
                    try:
                        db_add_single_geo_point(DB_NAME, point_id, point_intid, point_text, point_levelid,
                                                point_children, parent_id)
                    except IntegrityError as ie:
                        log.warn('Geo point already exists! Message: {}'.format(ie.message))
            else:
                try:
                    db_add_single_geo_point(DB_NAME, point_id, point_intid, point_text, point_levelid,
                                            point_children, parent_id)
                except IntegrityError as ie:
                    log.warn('Geo point already exists! Message: {}'.format(ie.message))

    if batching:
        # add a bunch of points (batch)
        if geodb_instance:
            geodb_instance.db_add_multiple_geo_points(DB_NAME, points_list)
        else:
            db_add_multiple_geo_points(DB_NAME, points_list)


def init_geo_points(pretty_debug=False, text_filter=None):
    """
    Initializing existing (!) geo points db. Initializes top of geo points hierarchy.
    Operation is idempotent!
    :param pretty_debug:
    :return:
    """
    log.debug('init_geo_points(): initializing.')

    # get top level json from cikrf web-site
    myjson = json.load(urllib2.urlopen(URL_TOP), encoding=JSON_ENCODING)

    # pretty print json (just debug)
    if pretty_debug:
        print(json.dumps(myjson, sort_keys=True, indent=4, encoding=JSON_ENCODING))

    # get first geo point from json
    id = myjson[0]['id']
    text = myjson[0]['text'].encode(DATA_ENCODING)
    children = 'True'
    intid = myjson[0]['a_attr']['intid']
    levelid = myjson[0]['a_attr']['levelid']

    # just debug
    log.debug('id -> {}, text -> {}, children -> {}, intid -> {}, levelid -> {}'
              .format(id, text, type(children), intid, levelid))

    # add first (top-level) point to db
    try:
        last_id = db_add_single_geo_point(DB_NAME, id, intid, text, levelid, children, 0, processed=1)
    except IntegrityError as ie:
        log.warn('Top level element already added! Message: {}'.format(ie.message))
        last_id = db_get_geo_point_id(DB_NAME, id, intid, text, levelid)

    # add top-level points to db (without batching, one by one). if we use batching and adding one by one, we
    # won't miss any top level point that isn't exist in db (we will add missed and won't touch existing)
    add_geo_points(myjson[0]['children'], last_id, batching=False, text_filter=text_filter)


# todo: add starting point for processing (for top level)
def process_geo_points():
    """
    Process (fill in with necessary data/fetch data) geo points db, can be executed multiple times - will
    continue add data to existing database.
    """
    log.debug('process_geo_points(): processing geo points.')

    # use GeoDB instance
    geodb = GeoDB(DB_NAME)

    http_response = ''  # initialization of variable
    # get not processed from db and process them
    not_processed = db_get_not_processed_geo_points_ids(DB_NAME)
    while len(not_processed) > 0:

        # process not processed points one by one
        for geo_point in not_processed:
            # get current point info
            geo_point_id = geo_point[0]
            id = geo_point[1]
            # intid = geo_point[2]
            cik_text = geo_point[3]

            # select url
            if u'Санкт-Петербург' in cik_text:
                url = URL_SPB
            elif u'Москва' in cik_text:
                url = URL_MSK
            else:
                url = URL_POINT

            try:
                # get source data
                http_response = urllib2.urlopen(url.format(id)).read()  # open url
                myjson = json.loads(http_response, encoding=JSON_ENCODING)  # parse json
                # process data
                add_geo_points(myjson, geo_point_id, geodb_instance=geodb)  # add all found geo points to db

                geodb.db_mark_geo_point_as_processed(DB_NAME, geo_point_id)
                # db_mark_geo_point_as_processed(DB_NAME, geo_point_id)  # mark current point as processed (= 1)

            except ValueError as ve:
                log.error('Error processing object id = [{}]! Message: {}'.format(id, ve.message))

                # mark current geo point as processed with errors (= 2)
                geodb.db_mark_geo_point_as_processed(DB_NAME, geo_point_id, processed_status=2)
                # db_mark_geo_point_as_processed(DB_NAME, geo_point_id, processed_status=2)

                # save on disk only erroneous objects (ids)
                save_file_with_path('json_errors/{}.json'.format(id), http_response)  # save response to file

        # after processing first part - get new not processed points
        not_processed = db_get_not_processed_geo_points_ids(DB_NAME)

    log.info('All points have been processed.')
    return True


# module initialization
setup_logging(default_path='geopython/logging.yml')
log = logging.getLogger('geocik')
# starting point for [geocik] module
log.info('Starting [geocik] module...')

if USE_PROXY:  # setup proxy if needed
    proxy = urllib2.ProxyHandler({'http': PROXY_SERVER, 'https': PROXY_SERVER})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    log.info('Proxy for http/https has been installed.')

# create db if not exists
if not os.path.exists(DB_NAME):
    log.warn("Database [{}] doesn't exist! Creating...".format(DB_NAME))
    db_create(DB_NAME)  # create target db

# init db first time
# init_geo_points(text_filter='Санкт-Петербург')
init_geo_points(text_filter='Ленинградская область')

# process/continue with geo points information (in case of error - re-try)
tries_count = 10
tries = 0
finished = False
while tries < tries_count and not finished:
    try:
        finished = process_geo_points()
    except Exception as e:
        log.error('Something went wrong! Message: {}'.format(e.message))
    tries += 1
