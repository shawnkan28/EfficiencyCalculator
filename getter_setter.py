import pathlib
import logging
import helper as h


class GS:
    def __init__(self, thumb_path, char_path, main_path, sub_path, log):
        self._thumb_path = thumb_path
        self._char_df = h.pickle_file("read", fname=char_path)
        self._gm_df = h.pickle_file("read", fname=main_path)
        self._gs_df = h.pickle_file("read", fname=sub_path)
        self._log = log

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
    def gm_df(self):
        return self._gm_df

    @gm_df.setter
    def gm_df(self, df):
        self._gm_df = df

    @property
    def gs_df(self):
        return self._gs_df

    @gs_df.setter
    def gs_df(self, df):
        self._gs_df = df

    @property
    def log(self) -> logging.Logger:
        return self._log

    @log.setter
    def log(self, lg):
        self._log = lg
