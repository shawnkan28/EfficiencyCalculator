from PyQt5 import QtWidgets as qtw, QtGui as qtg


class CharInfo(qtw.QGroupBox):
    def __init__(self, gs):
        super().__init__("Character Info")

        # Usable Variables
        self.thumb = gs.thumb_path
        self.log = gs.log
        self.char_df = gs.char_df
        self.stat_names = [x for x in self.char_df.columns if "Name" not in x]
        # used to reference widgets from one function to another
        self.widgets = {}  # TODO: change to dataframe

        # Show User Interface when called by parent
        self._init_ui()

    def _init_ui(self):
        # Declare layout
        self.layout = qtw.QHBoxLayout()

        # character selection/img
        self.layout.addLayout(self._character())
        self.layout.addWidget(self._stats("Base Stats"))
        self.layout.addWidget(self._stats("Goal Stats"))
        self.layout.addWidget(self._stats("Final Stats"))

        # Add to screen
        self.setLayout(self.layout)

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
        # references
        self.widgets['char_cb'] = char_cb

        # Character Image
        char_pix = img_widget(str(self.thumb / f"{char_cb.currentText()}.png"))
        # references
        self.widgets['char_pix'] = char_pix

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
        row = self.char_df.loc[self.widgets['char_cb'].currentText()]
        for i, stat in enumerate(self.stat_names):
            # declare line Edit
            le = qtw.QLineEdit()
            self.widgets[f"{box_name} {stat}_le"] = le
            if is_base:
                le.setText(row[stat])

            # add widget to grid
            grid_layout.addWidget(qtw.QLabel(stat.upper() + " : "), i, 0)
            grid_layout.addWidget(le, i, 1)

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
            self.widgets[f"Base Stats {stat}_le"].setText(row[stat])


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
