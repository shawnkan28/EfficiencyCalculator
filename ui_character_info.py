from PyQt5 import QtWidgets as qtw, QtGui as qtg
import pandas as pd


class CharInfo(qtw.QGroupBox):
    def __init__(self, gs):
        super().__init__("Character Info")

        # Usable Variables
        self.thumb = gs.thumb_path
        self.log = gs.log
        self.char_df = gs.char_df
        self.stat_names = [x for x in self.char_df.columns if "Name" not in x]
        # used to reference widgets from one function to another
        self.widgets = pd.Series(dtype=object)

        # Show User Interface when called by parent
        self._init_ui()

    def _init_ui(self):
        # Declare layout
        layout = qtw.QHBoxLayout()

        # character selection/img
        layout.addLayout(self._character())
        # Character stats
        layout.addWidget(self._stats("Base Stats"))
        layout.addWidget(self._stats("Goal Stats"))
        layout.addWidget(self._stats("Final Stats"))

        # Add to screen
        self.setLayout(layout)

    def _character(self):
        """
        Select character drop down list + Character Display Image
        :return: Qtw Layout
        """
        # Declare layout
        layout = qtw.QVBoxLayout()

        # Character Drop down list
        char_cb = cb_widget(sorted(self.char_df.index.to_list()))
        # Events
        char_cb.currentIndexChanged.connect(self._character_select_onChange)

        # Character Image
        char_pix = img_widget(str(self.thumb / f"{char_cb.currentText()}.png"))

        # Add References
        self.widgets = pd.concat([self.widgets, pd.Series([char_cb, char_pix], index=['char_cb', 'char_pix'])])

        # Add widget
        layout.addWidget(char_cb)
        layout.addWidget(char_pix)

        return layout

    def _stats(self, box_name):
        is_base = "Base" in box_name

        border = qtw.QGroupBox(box_name)
        # Declare layout
        grid_layout = qtw.QGridLayout()

        # Add Label and Line Entry into grid
        wid, indexes = [], []
        row = self.char_df.loc[self.widgets['char_cb'].currentText()]
        for i, stat in enumerate(self.stat_names):
            # declare line Edit
            le = qtw.QLineEdit()
            wid.append(le)
            indexes.append(f"{box_name.split(' ')[0].lower()}_{stat}_le")
            if is_base:
                le.setText(row[stat])

            # add widget to grid
            grid_layout.addWidget(qtw.QLabel(stat.upper() + " : "), i, 0)
            grid_layout.addWidget(le, i, 1)

        # References
        self.widgets = pd.concat([self.widgets, pd.Series(wid, index=indexes)])

        # add layout to widget
        border.setLayout(grid_layout)

        return border

    """
    On Change Events / Listener Events
    """
    def _character_select_onChange(self):
        name = self.widgets['char_cb'].currentText()

        img = qtg.QPixmap(str(self.thumb / f"{name}.png"))
        self.widgets['char_pix'].setPixmap(img)

        row = self.char_df.loc[name]
        for stat in self.stat_names:
            self.widgets[f"base_{stat}_le"].setText(row[stat])


"""
Simplify Widgets
"""


def img_widget(path):
    img = qtg.QPixmap(path)
    img_lbl = qtw.QLabel()
    img_lbl.setPixmap(img)
    img_lbl.resize(img.width(), img.height())
    return img_lbl


def cb_widget(_list):
    cb = qtw.QComboBox()
    cb.addItems(_list)
    # make searchable
    cb.setEditable(True)
    cb.setInsertPolicy(qtw.QComboBox.NoInsert)
    cb.completer().setCompletionMode(qtw.QCompleter.PopupCompletion)
    return cb
