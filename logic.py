import pandas as pd


class Logic:
    def __init__(self, args, log):
        self.a = args
        self.lg = log

    def get_db(self, info):
        """
        get csv file into df
        :param info:  a dictionary of key: f_path, value: kwargs
        :return:
        """

        dfs = {}
        for f_path, kwargs in info.items():
            df = self._check_db(f_path, **kwargs)
            dfs[f_path.stem] = df

        return dfs

    @staticmethod
    def compute_eff(stat_name, stat_val, db):
        """
        compute efficiency of gear for each sub stat
        :return: efficiency val
        """
        # COMPUTE FOR INDIVIDUAL EFFICIENCY SUB STAT USED FOR GEAR
        # 10 * (ATK% - LOWESTSubStatVal) / (MAXSubStatVal - LOWESTSubStatVal)
        min_val = db['BLUE']['Min'][stat_name]
        max_val = db['GOLD']['Max'][stat_name]
        return 10 * ((stat_val - min_val) / (max_val - min_val))

    def _check_db(self, path, **kwargs):
        assert path.is_file(), f"Unable to locate csv file. {path}"

        self.lg.info(f"Reading from {path}")
        df = pd.read_csv(path, **kwargs)
        return df
