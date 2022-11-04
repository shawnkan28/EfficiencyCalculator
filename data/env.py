import logging
import pathlib
import pandas as pd
import helper as h


class Env:
    def __init__(self, log):
        self._log = log
        self._char_list = list()
        self._thumb = pathlib.Path()
        self._db_char = pd.DataFrame()
        self._db_main = pd.DataFrame()
        self._db_sub = pd.DataFrame()
        self._db_set = pd.DataFrame()
        self._logo = pathlib.Path()
        self._avail_stats = list()

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
        return self._db_sub

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
    def avail_stats(self):
        return self._avail_stats

    @avail_stats.setter
    def avail_stats(self, val):
        self._avail_stats = h.pickle_file("read", val)







