from PyQt5 import QtWidgets as qtw, QtGui as qtg
from ui_character_info import CharInfo
from ui_efficiency_info import EffInfo
import pandas as pd


class Window(qtw.QWidget):
    def __init__(self, gs):
        super().__init__()
        self.gs = gs
        self.btn = None

        # UI Design
        self._init_ui()

        # Dataframes
        self.gear_main_df = gs.gm_df

        # Widget Variables
        self.eff_score_lbl = gs.eff_score_widgets
        self.var_gear_widgets = gs.var_gear_widgets

        # Stats
        self.main_gear_stats = pd.Series(dtype=float)

        self._compute_main_gear_stats()

        # Show UI interface
        self._set_location()
        self.show()

    def _init_ui(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon("./logo.png"))

        # add layout
        layout = qtw.QVBoxLayout()

        # Insert UI to layout
        layout.addWidget(CharInfo(self.gs))
        layout.addWidget(EffInfo(self.gs))
        layout.addWidget(self._button())

        self.setLayout(layout)

    def _set_location(self):
        top_left = qtw.QApplication.desktop().availableGeometry().topLeft()
        self.move(top_left)

    def _button(self):
        btn = qtw.QPushButton("Save")
        self.btn = btn
        return btn

    def _compute_main_gear_stats(self):
        data = []
        var_gears = [x.replace("_cb", "") for x in self.var_gear_widgets.index]

        for gear in self.gear_main_df.columns:
            stat = self.gear_main_df.loc[self.gear_main_df[gear].notnull(), gear]

            if gear in var_gears:  # variable stat gears
                stat_type = self.var_gear_widgets.loc[f"{gear}_cb"].currentText()
                stat_val = stat.loc[stat_type]
            else:  # static stat gears (Gun/Core/Plate)
                stat_type, stat_val = stat.index[0], stat.iloc[0]
            # create dataframe data
            data.append({gear: stat_val, "index": stat_type})

        # self.main_gear_stats = pd.concat([self.main_gear_stats, pd.Series()])
        # print(self.var_gear_widgets)
        # print(self.gear_main_df)
        df = pd.DataFrame(data)
        df.set_index('index', inplace=True)
        print(df)
