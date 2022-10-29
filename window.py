from PyQt5 import QtWidgets, QtGui


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def show_(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(QtGui.QIcon("./logo.png"))
        self._set_location()
        self.show()

    def _set_location(self):
        top_left = QtWidgets.QApplication.desktop().availableGeometry().topLeft()
        self.move(top_left)
