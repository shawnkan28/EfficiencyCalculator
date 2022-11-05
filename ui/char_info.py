from PyQt5 import QtWidgets as qtw
import ui.widgets as w


class CharInfo(qtw.QGroupBox):
    def __init__(self, env, char):
        super().__init__("Character Stats")
        self.e = env
        self.c = char

        self.placeholder = self.e.thumb / "no-image.png"

        self._init_ui()

    def _init_ui(self):
        """
        Set up Character Information
         - Character selection
         - Character image
         - Character base/goal/final Stats
        :return:
        """
        # Declare layout
        layout = qtw.QHBoxLayout()

        # character selection/img
        layout.addLayout(self._character())
        # # Character stats
        layout.addWidget(self._stats("base"))
        layout.addWidget(self._stats("goal"))
        layout.addWidget(self._stats("final"))

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
        char_cb = w.cb_widget(sorted(self.e.char_list), searchable=True)

        # Character Image
        char_pix = w.img_widget(str(self.placeholder))

        # Add widget
        layout.addWidget(char_cb)
        layout.addWidget(char_pix)

        return layout

    def _stats(self, box_name):
        """
        Display stats + textbox for base/goal/final
        :param box_name:
        :return: layout
        """
        border = qtw.QGroupBox(f"{box_name.title()} Stats")
        # Declare layout
        grid_layout = qtw.QGridLayout()

        # Add Label and Line Entry into grid
        for i, stat in enumerate(self.e.char_stats):
            # declare line Edit
            le = qtw.QLineEdit()

            # add widget to grid
            grid_layout.addWidget(qtw.QLabel(stat + " : "), i, 0)
            grid_layout.addWidget(le, i, 1)

            # add reference
            self.c.stat_widgets.loc[box_name, stat] = le

        # add layout to widget
        border.setLayout(grid_layout)

        return border
