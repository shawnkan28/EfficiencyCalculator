from PyQt5 import QtWidgets as qtw, QtGui as qtg
from ui_character_info import CharInfo
from ui_efficiency_info import EffInfo


class Window(qtw.QWidget):
    def __init__(self, gs):
        super().__init__()
        self.gs = gs
        self.btn = None

        self._init_ui()

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
