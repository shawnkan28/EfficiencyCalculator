import pandas as pd
from PyQt5 import QtWidgets as qtw, QtGui as qtg
from ui.char_info import CharInfo
from ui.efficiency import Efficiency
from data.character import Character


class Window(qtw.QWidget):
    def __init__(self, env):
        super().__init__()
        self.e = env
        self.c = Character(self.e.db_char, self.e.db_main)

        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon(str(env.logo)))

        # Set UI
        self._init_ui()

        self._set_location("top_left")
        self._events()
        self._display()

    def _init_ui(self):
        """
        This initializes all widgets into the screen.
        :return:
        """
        layout = qtw.QVBoxLayout()

        # add character info ui
        layout.addWidget(CharInfo(self.e, self.c))
        # add Efficiency score calculator
        layout.addWidget(Efficiency(self.e, self.c))

        self.setLayout(layout)

    def _set_location(self, loc):
        if loc == "top_left":
            top_left = qtw.QApplication.desktop().availableGeometry().topLeft()
            self.move(top_left)
        else:
            self.e.log.warning("selected location dont exist.")

    def _events(self):
        # on character select
        self.c.char_widget.currentIndexChanged.connect(self._on_char_change)

        # on input gear sub stat
        self.c.gear_widgets.apply(lambda x: x.apply(lambda y: y.textChanged.connect(self._compute_eff)))

        # on change variable gear stat
        self.c.variable_gear_widgets.apply(lambda x: x.currentIndexChanged.connect(self._compute_final_stats))

    def _display(self):
        self._on_char_change()

    def _on_char_change(self):
        # Set Thumb Image
        img = qtg.QPixmap(str(self.e.thumb / f"{self.c.char_name}.png"))
        self.c.image_widget.setPixmap(img)
        # set base stats
        self.c.char_stats.apply(lambda x: self.c.stat_widgets.loc['base', x['stat']].setText(str(x['val'])), axis=1)
        # compute final stats
        self._compute_final_stats()

    def _compute_eff(self):
        sub_widgets = self.c.gear_widgets.apply(lambda x: x.apply(lambda y: y.text())).copy()
        sub_stats = sub_widgets.apply(pd.to_numeric)
        sub_stats = sub_stats.apply(self._compute_score)

        self._compute_final_stats()

    def _compute_score(self, sr):
        sr.name = "val"
        df = pd.DataFrame(sr, index=sr.index)
        df['stat'] = df.index
        df.apply(lambda x: (x['val'] -
                            self.e.db_sub.loc[x['stat'], 'Blue']['min']) /
                           (self.e.db_sub.loc[x['stat'], 'Gold']['max'] -
                            self.e.db_sub.loc[x['stat'], 'Blue']['min']), axis=1)
        print(df)

    def _compute_final_stats(self):
        perc_gear_stats = self.c.gear_perc / 100
        base_stats = self.c.char_stats
        base_stats.index = base_stats.pop('stat')

        perc_gear_stats.index = [x.replace("(%)", "").strip() for x in perc_gear_stats.index]
        # add according to stat formula
        perc_df = base_stats.mul(perc_gear_stats, axis=0)
        perc_df.fillna(0, inplace=True)
        final_df = base_stats.add(self.c.gear_non_perc, axis=0)
        final_df = final_df.add(perc_df, axis=0)

        final_df['stat'] = final_df.index
        final_df.apply(lambda x: self.c.stat_widgets.loc['final', x['stat']].setText(str(x['val'])), axis=1)
