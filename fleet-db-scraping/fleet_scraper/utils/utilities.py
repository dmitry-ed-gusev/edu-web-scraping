#!/usr/bin/env python3
# coding=utf-8

"""
    Common utilities module for Fleet DB Scraper.

    Created:  Gusev Dmitrii, 26.04.2021
    Modified: Gusev Dmitrii, 26.04.2021
"""

import logging
import hashlib

RUS_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ENG_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUM_CHARS = "0123456789"
SPEC_CHARS = "-"

log = logging.getLogger('scraper_utilities')


def get_hash_bucket_number(value, buckets):
    """Generate hash bucket number for the given value, generated bucket number
    will be less than provided buckets count.
    :param value:
    :param buckets:
    :return:
    """
    log.debug('get_hash_bucket_number(): value [{}], buckets [{}].'.format(value, buckets))

    if value is None or len(value.strip()) == 0:  # fail-fast if value is empty
        raise ValueError('Provided empty value!')

    if buckets <= 0:  # if buckets number <= 0 - generated bucket number is always 0
        log.debug('get_hash_bucket_number(): buckets number [{}] is <= 0, return 0!'.format(buckets))
        return 0

    # value is OK and buckets number is > 0
    hex_hash = hashlib.md5(value.encode('utf-8')).hexdigest()  # generate hexadecimal hash
    int_hash = int(hex_hash, 16)                               # convert it to int (decimal)
    bucket_number = int_hash % buckets                         # define bucket number as division remainder
    log.debug('get_hash_bucket_number(): hash: [{}], decimal hash: [{}], generated bucket: [{}].'
              .format(hex_hash, int_hash, bucket_number))

    return bucket_number


def add_value_to_hashmap(hashmap, value, buckets):
    """Add value to the provided hash map with provided total buckets number.
    :param hashmap:
    :param value:
    :param buckets:
    """
    log.debug('add_value_to_hashmap(): hashmap [{}], value [{}], buckets [{}].'
              .format(hashmap, value, buckets))

    if hashmap is None or not isinstance(hashmap, dict):  # fail-fast - hash map type check
        raise ValueError('Provided empty hashmap [{}] or it isn\'t dictionary!'.format(hashmap))
    if value is None or len(value.strip()) == 0:  # fail-fast - empty value
        raise ValueError('Provided empty value [{}]!'.format(value))

    bucket_number = get_hash_bucket_number(value, buckets)  # bucket number for the value
    if hashmap.get(bucket_number) is None:  # bucket is not initialized yet
        hashmap[bucket_number] = list()
    hashmap.get(bucket_number).append(value)  # add value to the bucket

    return hashmap


def build_variations_hashmap(buckets=0):
    """Build hashmap of all possible variations of symbols for further search.
    :param buckets: number of buckets to divide symbols
    :return: list of variations
    """
    log.debug('build_variations_hashmap(): buckets [{}].'.format(buckets))

    result = dict()  # resulting dictionary

    for letter1 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
        for letter2 in RUS_CHARS + ENG_CHARS + NUM_CHARS:
            result = add_value_to_hashmap(result, letter1 + letter2, buckets)  # add value to hashmap

            for spec_symbol in SPEC_CHARS:
                result = add_value_to_hashmap(result, letter1 + spec_symbol + letter2, buckets)  # add value to hashmap

    return result


def build_variations_list():
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


if __name__ == '__main__':
    print('Don\'t run this script directly!')
