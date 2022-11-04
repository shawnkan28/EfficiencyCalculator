from PyQt5 import QtWidgets as qtw, QtGui as qtg


class Window(qtw.QWidget):
    def __init__(self, env):
        super().__init__()
        self.e = env

        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon(str(env.logo)))

        # Set UI
        self._init_ui()

        self._set_location("top_left")

    def _init_ui(self):
        """
        This initializes all widgets into the screen.
        :return:
        """
        pass

    def _set_location(self, loc):
        if loc == "top_left":
            top_left = qtw.QApplication.desktop().availableGeometry().topLeft()
            self.move(top_left)
        else:
            self.e.log.warning("selected location dont exist.")
