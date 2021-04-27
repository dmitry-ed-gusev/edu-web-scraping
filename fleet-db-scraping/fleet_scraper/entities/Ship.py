"""
    Ship entity with base properties.

    Created:  Gusev Dmitrii, 10.01.2021
    Modified: Dmitrii Gusev, 26.04.2021
"""


class Ship(object):

    def __init__(self, imo_number):
        self.imo_number = imo_number
        self.reg_number = ''
        self.flag = ''
        self.main_name = ''
        self.secondary_name = ''
        self.home_port = ''
        self.call_sign = ''

    def __str__(self) -> str:
        return f"IMO #: {self.imo_number}, REG #: {self.reg_number}, flag: {self.flag}, " \
               f"name: {self.main_name}, secondary name: {self.secondary_name}, " \
               f"port: {self.home_port}, call: {self.call_sign}"
