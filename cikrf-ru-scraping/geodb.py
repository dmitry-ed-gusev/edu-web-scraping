#!/usr/bin/env python
# coding=utf-8

"""
    DB utilities module (persistance layer). This is a library module.

    Created: Gusev Dmitrii, 02.02.2017
    Modified: Gusev Dmitrii, 11.02.2017
"""

import logging
import sqlite3 as sql

# init module logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# common constants
# DB_NAME = 'geodata.sqlite'
DB_NAME = 'geodb.sqlite'

# database script
DB_SCRIPT = """
    -- drop tables
    DROP TABLE IF EXISTS areas;
    DROP TABLE IF EXISTS commissions;
    DROP TABLE IF EXISTS addresses;
    DROP TABLE IF EXISTS geo_points;
    -- create tables
    CREATE TABLE areas (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT);
    CREATE TABLE commissions(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, city TEXT, 
      territory_commission TEXT, sector_commission TEXT, people_count INTEGER);
    CREATE TABLE addresses(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, street TEXT, buildings TEXT, 
      commission_id INTEGER REFERENCES commissions(id) ON DELETE RESTRICT);
    -- geo points from CIK RF database
    CREATE TABLE geo_points(geo_point_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, id INTEGER, 
      intid INTEGER, cik_text TEXT, levelid INTEGER, children TEXT, 
      parent_id INTEGER REFERENCES geo_points(geo_point_id) ON DELETE RESTRICT, processed INTEGER DEFAULT 0);
    CREATE UNIQUE INDEX geo_point_id_unique ON geo_points(id);
"""


class GeoDB(object):
    """ Class for utilizing sqlite3 connection. """
    def __init__(self, dbname):
        # init logger
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())
        self.log.debug('Creating GeoDB instance.')
        self.__dbname = dbname
        self.__connection = None
        self.__cursor = None

    # todo: create decorator for closing connection on exception
    # todo: create executor method for utilizing with all other methods
    def db_mark_geo_point_as_processed(self, dbname, geo_point_id, processed_status=1):
        """"""
        log.debug('GeoDB.db_mark_geo_point_as_processed(): mark point [{}] as processed with status [{}].'
                  .format(geo_point_id, processed_status))
        update_sql = "UPDATE geo_points SET processed = {} WHERE geo_point_id = {}" \
            .format(processed_status, geo_point_id)
        # check connection
        if not self.__connection:
            self.__connection = sql.connect(dbname)
            self.__cursor = self.__connection.cursor()
        try:
            # performing db operations
            self.__cursor.execute(update_sql)
            self.__connection.commit()
        except StandardError as se:
            self.log.error('Error occured: {}'.format(se.message))
            self.__connection.close()

    def db_add_multiple_geo_points(self, dbname, list_of_geo_points):
        """"""
        # log.debug('db_add_multiple_geo_points(): adding multiple geo points.')  # <- too much output
        # if list is empty - quick return
        if not list_of_geo_points or len(list_of_geo_points) == 0:
            self.log.debug('List of geo points is empty. Nothing to add.')
            return
        # list isn't empty - processing
        sql_list = []
        insert_sql = "INSERT INTO geo_points(id, intid, cik_text, levelid, children, parent_id, processed) " \
                     "VALUES ({}, {}, '{}', {}, '{}', {}, {})"
        # process all specified geo points
        for geo_point in list_of_geo_points:
            # get info from list entry
            id = geo_point[0]
            intid = geo_point[1]
            cik_text = geo_point[2]
            levelid = geo_point[3]
            children = geo_point[4]
            parent_id = geo_point[5]
            processed = geo_point[6]
            # add values to query and add query to list
            sql_list.append(insert_sql.format(id, intid, cik_text, levelid, children, parent_id, processed))
        # check connection
        if not self.__connection:
            self.__connection = sql.connect(dbname)
            self.__cursor = self.__connection.cursor()
        # execute multip[le sqls
        for query in sql_list:
            self.__cursor.execute(query)
        # commit all added points
        self.__connection.commit()
        self.log.debug('Geo points list [len = {}] has been added.'.format(len(list_of_geo_points)))


# todo: add exceptions handling for db operations (in case of exception close connection etc.)

def db_create(dbname):
    """
    Create DB by executing DDL SQL script.
    :param dbname:
    :return:
    """
    log.debug('db_create: creating database structure.')
    # connect to sqlite db
    conn = sql.connect(dbname)
    cur = conn.cursor()
    log.debug('Connected to DB [{}].'.format(dbname))
    # execute db setup script
    for query in DB_SCRIPT.split(';'):
        cur.execute(query)
    log.debug('DB structure created.')


def db_add_areas(dbname, areas_list):
    """
    Add multiple areas at a time.
    :param dbname:
    :param areas_list:
    :return:
    """
    log.debug('db_add_areas(): adding areas {}.'.format(areas_list))
    insert_sql = 'INSERT INTO areas(name) VALUES ("{}")'
    # connect to db and in cycle insert records
    connection = sql.connect(dbname)
    cursor = connection.cursor()
    log.debug('Connected to DB [{}].'.format(dbname))
    for area in areas_list:
        cursor.execute(insert_sql.format(area))
    connection.commit()
    log.debug('All areas added.')


def db_add_commissions(dbname, commissions_list):
    """
    Add multiple commissions at a time.
    :param dbname:
    :param commissions_list:
    :return:
    """
    log.debug('db_add_commissions(): adding commissions.')
    raise StandardError('Not implemented!')


def db_add_commission(dbname, city, territory_commission, sector_commission, people_count):
    """
    Add one commission at a time, return inserted id.
    :param dbname:
    :param city:
    :param territory_commission:
    :param sector_commission:
    :param people_count:
    :return:
    """
    log.debug('db_add_commission(): adding commission [{}, {}, {}, {}].'
              .format(city, territory_commission, sector_commission, people_count))
    insert_sql = "INSERT INTO commissions(city, territory_commission, sector_commission, people_count) " \
                 "VALUES ('{}', '{}', '{}', {})".format(city, territory_commission, sector_commission, people_count)
    connection = sql.connect(dbname)
    cursor = connection.cursor()
    log.debug('Connected to DB [{}].'.format(dbname))
    cursor.execute(insert_sql)
    last_id = cursor.lastrowid
    connection.commit()
    log.debug('Last inserted id = [{}].'.format(last_id))
    return last_id


def db_add_address(dbname, street, buildings, commission_id):
    """
    Add one address at a time, return inserted id.
    :param dbname:
    :param street:
    :param buildings:
    :param commission_id:
    :return:
    """
    log.debug('db_add_address(): adding address [{}, {}, {}].'
              .format(street, buildings, commission_id))
    insert_sql = "INSERT INTO addresses(street, buildings, commission_id) VALUES ('{}', '{}', '{}')" \
        .format(street, buildings, commission_id)
    connection = sql.connect(dbname)
    cursor = connection.cursor()
    log.debug('Connected to DB [{}].'.format(dbname))
    cursor.execute(insert_sql)
    last_id = cursor.lastrowid
    connection.commit()
    log.debug('Last inserted id = [{}].'.format(last_id))
    return last_id


def db_add_single_geo_point(dbname, id, intid, cik_text, levelid, children, parent_id, processed=0):
    """"""
    if not intid:
        intid = 'NULL'
    insert_sql = "INSERT INTO geo_points(id, intid, cik_text, levelid, children, parent_id, processed) " \
                 "VALUES ({}, {}, '{}', {}, '{}', {}, {})"\
        .format(id, intid, cik_text, levelid, children, parent_id, processed)
    log.debug('db_add_geo_point(): adding geopoint.\n\tSQL -> [{}].'.format(insert_sql))

    connection = sql.connect(dbname)
    try:
        cursor = connection.cursor()
        cursor.execute(insert_sql)
        last_id = cursor.lastrowid
        connection.commit()
        log.debug('Geo point has been added. Last inserted id = [{}].'.format(last_id))
        return last_id
    finally:
        connection.close()


# todo: remove this method - it has been moved to GeoDB object
def db_add_multiple_geo_points(dbname, list_of_geo_points):
    """"""
    # log.debug('db_add_multiple_geo_points(): adding multiple geo points.')  # <- too much output

    # if list is empty - quick return
    if not list_of_geo_points or len(list_of_geo_points) == 0:
        log.debug('List of geo points is empty. Nothing to add.')
        return

    # list isn't empty - processing
    sql_list = []
    insert_sql = "INSERT INTO geo_points(id, intid, cik_text, levelid, children, parent_id, processed) " \
                 "VALUES ({}, {}, '{}', {}, '{}', {}, {})"
    # process all specified geo points
    for geo_point in list_of_geo_points:
        # get info from list entry
        id = geo_point[0]
        intid = geo_point[1]
        cik_text = geo_point[2]
        levelid = geo_point[3]
        children = geo_point[4]
        parent_id = geo_point[5]
        processed = geo_point[6]
        # add values to query and add query to list
        sql_list.append(insert_sql.format(id, intid, cik_text, levelid, children, parent_id, processed))

    # execute multip[le sqls
    connection = sql.connect(dbname)
    cursor = connection.cursor()
    for query in sql_list:
        cursor.execute(query)
    # commit all added points
    connection.commit()
    log.debug('Geo points list [len = {}] has been added.'.format(len(list_of_geo_points)))


def db_get_not_processed_geo_points_ids(dbname):
    """"""
    log.debug('db_get_not_processed_geo_points_ids(): processing.')
    select_sql = "SELECT geo_point_id, id, intid, cik_text FROM geo_points WHERE processed = 0"
    connection = sql.connect(dbname)
    cursor = connection.cursor()
    cursor.execute(select_sql)
    # iterate over rows and put them into result
    result = []
    for row in cursor:
        result.append(row)
    return result


def db_get_geo_point_id(dbname, id, intid, cik_text, levelid):
    """"""
    if not intid:
        intid = 'is NULL'
    else:
        intid = '= {}'.format(intid)
    select_sql = "SELECT geo_point_id FROM geo_points WHERE id = {} AND intid {} AND cik_text = '{}' AND levelid = {}"\
        .format(id, intid, cik_text, levelid)
    log.debug('db_get_geo_point_id(): selecting id.\n\tSQL -> [{}]'.format(select_sql))
    connection = sql.connect(dbname)
    cursor = connection.cursor()
    cursor.execute(select_sql)

    # process result
    result = cursor.fetchone()
    if result:  # something found
        id = result[0]
    else:  # nothing found
        id = -1

    connection.close()
    # cursor.close()
    return id


if __name__ == '__main__':
    print("Don't execute library as an application!")
