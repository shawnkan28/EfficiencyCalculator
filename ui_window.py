from PyQt5 import QtWidgets as qtw, QtGui as qtg
from ui_character_info import CharInfo


class Window(qtw.QWidget):
    def __init__(self, gs):
        super().__init__()
        self.gs = gs
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon("./logo.png"))

        # add layout
        layout = qtw.QVBoxLayout()

        # Insert UI to layout
        layout.addWidget(CharInfo(self.gs))

        self.setLayout(layout)
        self._set_location()
        self.show()

    def _set_location(self):
        top_left = qtw.QApplication.desktop().availableGeometry().topLeft()
        self.move(top_left)