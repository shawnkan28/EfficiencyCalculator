from PyQt5 import QtWidgets as qtw
import pandas as pd
import widgets as w
import helper as h


class EffInfo(qtw.QGroupBox):
    def __init__(self, gs):
        super().__init__("Efficiency Calculator")

        # Variables
        self.stat_names = gs.gm_df.index.to_list()
        self.gear_names = list(gs.gm_df.columns)
        self.main_df = gs.gm_df
        self.widgets = pd.Series(dtype=object)
        self.gear_main_comp = pd.Series({stat: 0 for stat in gs.gm_df.index.to_list()})

        # Show User Interface when called by parent
        self._init_ui()

        # add getter setter references
        s_list = []
        for gear_name in self.gear_names:
            s = h.change_indexing(self.widgets[self.widgets.index.str.contains("le")], gear_name)
            s_list.append(s)
        gs.eff_widgets = pd.concat(s_list, axis=1)

        # getter and setter
        gs.var_gear_widgets = self.widgets[self.widgets.index.str.contains("_cb")]
        gs.eff_score_widgets = self.widgets[self.widgets.index.str.contains("_eff_lbl")]

    def _init_ui(self):
        # Declare layout
        self.layout = qtw.QGridLayout()

        self._eff_info()

        # Add to screen
        self.setLayout(self.layout)

    def _eff_info(self):
        self.layout.addWidget(qtw.QLabel("Gear Input : "), 0, 0)
        self.layout.addWidget(qtw.QLabel("Main Stat : "), 1, 0)
        self.layout.addWidget(qtw.QLabel("Eff Score (Max 40) : "), 2, 0)

        # add gear label columns + stat labels + line edits
        indexes, widgets = [], []
        for i, name in enumerate(self.gear_names):  # column
            if i == 0:  # if first column
                self._sub_stat_line_edits(i, name)

            # Row 2 - add
            self.layout.addWidget(qtw.QLabel(name), 0, i+1)
            # get all non-null stats for each gear
            stat_types = list(self.main_df.loc[self.main_df[name].notna()].index)

            # Labels + combo box for showing gear base stat types
            if len(stat_types) == 1:  # only have 1 stat
                # add label stat names for gun/core/plate
                self.layout.addWidget(qtw.QLabel(stat_types[0]), 1, i+1)
            else:  # can have multiple stats
                # add combo box stat names for thruster/scope/chip
                gear_stat_cb = w.cb_widget(stat_types)
                indexes.append(f'{name}_cb'), widgets.append(gear_stat_cb)

                # Add combobox to layout
                self.layout.addWidget(gear_stat_cb, 1, i+1)

            # Row 3 - add efficiency score
            score = qtw.QLabel("0")
            self.layout.addWidget(score, 2, i+1)
            indexes.append(f"{name}_eff_lbl"), widgets.append(score)

            self._sub_stat_line_edits(i+1, name)

        # add widgets for reference
        self.widgets = pd.concat([self.widgets, pd.Series(widgets, index=indexes)])

    def _sub_stat_line_edits(self, col_num, gear_name):
        """
        Add Line Edits for user to key in sub stat values
        :param col_num:
        :return:
        """
        # Add line edits for each gear + sub stat combo
        indexes, widgets = [], []
        for i, stat in enumerate(self.stat_names):  # row
            if col_num == 0:
                self.layout.addWidget(qtw.QLabel(stat + " : "), i+3, col_num)
            else:
                eff_le = qtw.QLineEdit()
                indexes.append(f"{gear_name}_{stat}_le"), widgets.append(eff_le)
                # add to layout
                self.layout.addWidget(eff_le, i+3, col_num)

        # add reference
        self.widgets = pd.concat([self.widgets, pd.Series(widgets, index=indexes, dtype=object)])
