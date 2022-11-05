from PyQt5 import QtWidgets as qtw
import ui.widgets as w
import pandas as pd


class Efficiency(qtw.QGroupBox):
    def __init__(self, env, char):
        super().__init__("Efficiency Calculator")
        self.e = env
        self.c = char

        # Show User Interface when called by parent
        self._init_ui()

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
        for i, name in enumerate(self.e.gear_names):  # column
            if i == 0:  # if first column
                self._sub_stat_line_edits(i, name)

            # Row 2 - Main Stat Name
            self.layout.addWidget(qtw.QLabel(name), 0, i + 1)
            # get all non-null stats for each gear
            stat_types = list(self.e.db_main.loc[self.e.db_main[name].notna()].index)

            # Labels + combo box for showing gear base stat types
            if len(stat_types) == 1:  # only have 1 stat
                # add label stat names for gun/core/plate
                self.layout.addWidget(qtw.QLabel(stat_types[0]), 1, i + 1)
            else:  # can have multiple stats
                # add combo box stat names for thruster/scope/chip
                gear_stat_cb = w.cb_widget(stat_types)

                # Add combobox to layout
                self.layout.addWidget(gear_stat_cb, 1, i + 1)
                # Reference
                self.c.variable_gear_widgets[name] = gear_stat_cb

            # Row 3 - add efficiency score
            score = qtw.QLabel("0")
            self.layout.addWidget(score, 2, i + 1)
            # Reference
            self.c.eff_scores[name] = score

            self._sub_stat_line_edits(i + 1, name)

    def _sub_stat_line_edits(self, col_num, gear_name):
        """
        Add Line Edits for user to key in sub stat values
        :param col_num:
        :return:
        """
        # Add line edits for each gear + sub stat combo
        indexes, widgets = [], []
        for i, stat in enumerate(self.e.gear_stats):  # row
            if col_num == 0:
                self.layout.addWidget(qtw.QLabel(stat + " : "), i+3, col_num)
            else:
                eff_le = qtw.QLineEdit()
                indexes.append(f"{gear_name}_{stat}_le"), widgets.append(eff_le)
                # add to layout
                self.layout.addWidget(eff_le, i+3, col_num)

