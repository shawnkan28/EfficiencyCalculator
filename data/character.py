import pandas as pd


class Character:
    def __init__(self, stat_df, gear_df, char_name=None):
        self.stat_df = stat_df
        self.char_name = char_name
        self._stat_widgets = pd.DataFrame(index=['base', 'goal', 'final'],
                                          columns=[x for x in stat_df.columns if x != 'fullName'])
        self._gear_widgets = pd.DataFrame(index=gear_df.index, columns=gear_df.columns)
        self._variable_gear_widgets = pd.Series(index=list(gear_df.columns)[-3:], dtype=float)
        self._eff_scores = pd.Series(index=gear_df.columns, dtype=float)

    @property
    def char_stats(self):
        if self.char_name is None:
            return pd.DataFrame(columns=self.stat_df.columns)
        return self.stat_df.loc[self.char_name]

    @property
    def stat_widgets(self):
        return self._stat_widgets

    @stat_widgets.setter
    def stat_widgets(self, val):
        self._stat_widgets = val

    @property
    def gear_widgets(self):
        return self._gear_widgets

    @gear_widgets.setter
    def gear_widgets(self, val):
        self._gear_widgets = val

    @property
    def eff_scores(self):
        return self._eff_scores

    @eff_scores.setter
    def eff_scores(self, val):
        self._eff_scores = val

    @property
    def variable_gear_widgets(self):
        return self._variable_gear_widgets

    @variable_gear_widgets.setter
    def variable_gear_widgets(self, val):
        self._variable_gear_widgets = val
