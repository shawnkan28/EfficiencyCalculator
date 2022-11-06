import logging
import pathlib
import pandas as pd
import helper as h


class Env:
    def __init__(self, log):
        self._log = log
        self._thumb = pathlib.Path()
        self._db_char = pd.DataFrame()
        self._db_main = pd.DataFrame()
        self._db_sub = pd.DataFrame()
        self._db_set = pd.DataFrame()
        self._logo = pathlib.Path()
        self._char_list = list()
        self._gear_names = list()
        self._char_stats = list()
        self._gear_stats = list()

    @property
    def log(self) -> logging.Logger:
        return self._log

    @property
    def char_list(self):
        return self._char_list

    @char_list.setter
    def char_list(self, val):
        self._char_list = h.pickle_file("read", val)

    @property
    def gear_names(self):
        return self._gear_names

    @gear_names.setter
    def gear_names(self, val):
        self._gear_names = h.pickle_file("read", val)

    @property
    def thumb(self):
        return self._thumb

    @thumb.setter
    def thumb(self, val):
        self._thumb = val

    @property
    def db_char(self):
        return self._db_char

    @db_char.setter
    def db_char(self, val):
        self._db_char = h.pickle_file("read", val)

    @property
    def db_main(self):
        return self._db_main

    @db_main.setter
    def db_main(self, val):
        self._db_main = h.pickle_file("read", val)

    @property
    def db_sub(self):
        df = self._db_sub.apply(pd.to_numeric)
        return df

    @db_sub.setter
    def db_sub(self, val):
        self._db_sub = h.pickle_file("read", val)

    @property
    def db_set(self):
        return self._db_set

    @db_set.setter
    def db_set(self, val):
        self._db_set = h.pickle_file("read", val)

    @property
    def logo(self):
        return self._logo

    @logo.setter
    def logo(self, val):
        self._logo = val

    @property
    def char_stats(self):
        return self._char_stats

    @char_stats.setter
    def char_stats(self, val):
        self._char_stats = val

    @property
    def gear_stats(self):
        return self._gear_stats

    @gear_stats.setter
    def gear_stats(self, val):
        self._gear_stats = val

    @property
    def stat_mapping(self):
        return {
            'atk': 'Attack',
            'def': 'Defense',
            'hp': 'HP',
            'spd': 'Speed',
            'crit': 'Crit Chance (%)',
            'critDMG': 'Crit Damage (%)',
            'res': 'Status ACC (%)',
            'hit': 'Status RES (%)',
            'dual': 'Dual'
        }




