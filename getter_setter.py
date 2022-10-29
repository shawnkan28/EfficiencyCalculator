import pandas as pd
import pathlib
import logging


class GS:
    def __init__(self):
        self._thumb_path = pathlib.Path()
        self._char_df = pd.DataFrame()
        self._log = logging.getLogger()

    @property
    def thumb_path(self) -> pathlib.PurePath:
        return self._thumb_path

    @thumb_path.setter
    def thumb_path(self, path):
        self._thumb_path = path

    @property
    def char_df(self):
        return self._char_df

    @char_df.setter
    def char_df(self, df):
        self._char_df = df

    @property
    def log(self) -> logging.Logger:
        return self._log

    @log.setter
    def log(self, lg):
        self._log = lg
