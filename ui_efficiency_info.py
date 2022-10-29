from PyQt5 import QtWidgets as qtw, QtGui as qtg


class EffInfo(qtw.QGroupBox):
    def __init__(self, gs):
        super().__init__("Efficiency Calculator")

        # Show User Interface when called by parent
        self._init_ui()

    def _init_ui(self):
        # Declare layout
        self.layout = qtw.QGridLayout()

        # Add to screen
        self.setLayout(self.layout)

    def head_labels(self):
        gear_lbl = qtw.QLabel("Gear Input : ")


