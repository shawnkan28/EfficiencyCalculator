import argparse
import os
from pathlib import Path


class Parameters:
    def __init__(self, def_param=None, description=None):
        if def_param is None:
            self.def_param = True
        else:
            self.def_param = def_param

        self.parser = argparse.ArgumentParser(description=description)

    def parse(self):
        """
        Add your arguments here.
        :return: parser
        """
        """ Default Arguments """
        if self.def_param:
            self._default_args()

        """ Proj Arguments """
        self.parser.add_argument('--gear_stat', type=lambda x: Path(x).absolute(),
                                 help="csv structure of stats",
                                 default="./struct.csv")

        self.parser.add_argument('--db', type=lambda x: Path(x).absolute(),
                                 help="Database Path",
                                 default="./db.csv")

        self.parser.add_argument('--base_url', type=str,
                                 help="base url to crawl info from. If url not working will use local files",
                                 default="https://www.arterygear.info")

        self.parser.add_argument('--main_stats', type=lambda x: Path(x).absolute(),
                                 help="File for main stat values",
                                 default="./main_stats.csv")

        self.parser.add_argument('--set_bonus', type=lambda x: Path(x).absolute(),
                                 help="File for gear set bonus",
                                 default="./set_bonus.csv")

        return self.parser.parse_args()

    def _default_args(self):
        """
        Add all default arguments here.
        :return: parser
        """
        self.parser.add_argument('--var_dir', type=lambda x: Path(x).absolute(),
                                 help="Location of var folder",
                                 default=Path(os.path.realpath(os.path.dirname(__file__)), "var"))
