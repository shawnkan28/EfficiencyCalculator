import logging
import pathlib


class Env:
    def __init__(self, log):
        self._log = log
        self._thumb = pathlib.Path()
        self._db_char = pathlib.Path()
        self._db_main = pathlib.Path()
        self._db_sub = pathlib.Path()
        self._db_set = pathlib.Path()
        self._logo = pathlib.Path()

    @property
    def log(self) -> logging.Logger:
        return self._log

    @property
    def thumb(self):
        return self._thumb

    @property
    def db_char(self):
        return self._db_char

    @property
    def db_main(self):
        return self._db_main

    @property
    def db_sub(self):
        return self._db_sub

    @property
    def db_set(self):
        return self._db_set

    @property
    def logo(self):
        return self._logo

    @db_char.setter
    def db_char(self, val):
        self._db_char = val

    @db_main.setter
    def db_main(self, val):
        self._db_main = val

    @db_sub.setter
    def db_sub(self, val):
        self._db_sub = val

    @db_set.setter
    def db_set(self, val):
        self._db_set = val

    @thumb.setter
    def thumb(self, val):
        self._thumb = val

    @logo.setter
    def logo(self, val):
        self._logo = val
