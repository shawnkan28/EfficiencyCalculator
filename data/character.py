import re

import pandas as pd


class Character:
    def __init__(self, stat_df, gear_df):
        self.stat_df = stat_df[[x for x in stat_df.columns if x != 'fullName']]
        self._char_widget = None
        self._stat_widgets = pd.DataFrame(index=['base', 'goal', 'final'],
                                          columns=self.stat_df.columns)
        self._gear_widgets = pd.DataFrame(index=gear_df.index, columns=gear_df.columns)
        self._variable_gear_widgets = pd.Series(index=list(gear_df.columns)[-3:], dtype=float)
        self._eff_scores = pd.Series(index=gear_df.columns, dtype=float)
        self._image_widget = None
        self.gear_df = gear_df

    @property
    def char_stats(self):
        if self._char_widget is None:
            return pd.DataFrame(columns=self.stat_df.columns)
        index = self.stat_df.loc[self._char_widget.currentText()].index
        data = self.stat_df.loc[self._char_widget.currentText()].tolist()
        df = pd.DataFrame({"stat": index, "val": data})
        df['val'] = pd.to_numeric(df['val'], errors='coerce')
        return df

    @property
    def char_name(self):
        if self._char_widget is None:
            return None
        return self._char_widget.currentText()

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

    @property
    def char_widget(self):
        return self._char_widget

    @char_widget.setter
    def char_widget(self, val):
        self._char_widget = val

    @property
    def image_widget(self):
        return self._image_widget

    @image_widget.setter
    def image_widget(self, val):
        self._image_widget = val

    @property
    def gear_perc(self):
        # Get Sub Stat Percentage Efficiency
        gear_perc_df = self._get_fixed_stats()

        # Get Main Stat Percentage
        var_df = self._get_var_stats()

        gear_perc_df = pd.concat([gear_perc_df, var_df])
        gear_perc_df['gear'] = pd.to_numeric(gear_perc_df['gear'], errors='coerce')
        return gear_perc_df.groupby(gear_perc_df.index)['gear'].sum()

    @property
    def gear_non_perc(self):
        var_df = self._get_var_stats(r"[a-zA-Z]+\s[a-zA-Z]+\s.%.|^[a-zA-Z]*$")
        fixed_df = self._get_fixed_stats(r"[a-zA-Z]+\s[a-zA-Z]+\s.%.|^[a-zA-Z]*$")

        gear_fixed_df = pd.concat([fixed_df, var_df])
        gear_fixed_df['gear'] = pd.to_numeric(gear_fixed_df['gear'], errors='coerce')
        gear_fixed_df = pd.concat([gear_fixed_df, pd.DataFrame({"gear": 0}, index=['Dual'])])
        return gear_fixed_df.groupby(gear_fixed_df.index)['gear'].sum()

    def _get_fixed_stats(self, regex=r"^[a-zA-Z]+\s.%.$"):
        df = self._gear_widgets.loc[self._gear_widgets.index.str.contains(regex)]
        n_df = pd.DataFrame(columns=['gear'], index=df.index)
        dfs = [df[[x]].rename(columns={x: 'gear'}) for x in df.columns] + [n_df]
        df = pd.concat(dfs).dropna()
        df['gear'] = df['gear'].apply(lambda x: x.text())
        return df

    def _get_var_stats(self, regex=r"^[a-zA-Z]+\s.%.$"):
        var_sr = self._variable_gear_widgets.apply(lambda x: x.currentText())
        var_sr.name = "stat"
        var_df = var_sr.to_frame()
        var_df['gear'] = var_df.index
        var_df.index = var_df['stat']
        var_df = var_df.loc[var_df.index.str.contains(regex)]
        var_df = var_df.apply(lambda x: self.gear_df.loc[x['stat'], x['gear']].replace("%", ""), axis=1)
        if isinstance(var_df, pd.Series):
            var_df.name = "gear"
            var_df = var_df.to_frame()
        return var_df
