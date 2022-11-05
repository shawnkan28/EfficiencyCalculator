from PyQt5 import QtWidgets as qtw
import ui.widgets as w
import helper as h


class CharInfo(qtw.QGroupBox):
    def __init__(self, env):
        super().__init__("Character Stats")
        self.e = env

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
        border = qtw.QGroupBox(box_name)
        # Declare layout
        grid_layout = qtw.QGridLayout()

        # Add Label and Line Entry into grid
        for i, stat in enumerate(self.e.char_stats):
            # declare line Edit
            le = qtw.QLineEdit()

            # add widget to grid
            grid_layout.addWidget(qtw.QLabel(stat.upper() + " : "), i, 0)
            grid_layout.addWidget(le, i, 1)

        # add layout to widget
        border.setLayout(grid_layout)

        return border

