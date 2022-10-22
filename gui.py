import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from logic import Logic

import helper as h


class GUI(qtw.QWidget):
    def __init__(self, log, args):
        super().__init__()
        self.logic = Logic(args, log)

        dfs = self.logic.get_db({
            args.gear_stat: {"index_col": 0},
            args.db: {"header": [0, 1], "index_col":0}
        })
        self.gear_names = dfs["struct"].columns.to_list()
        self.stat_names = dfs['struct'].index.to_list()
        self.db = dfs['db']
        self.log = log

    def run(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon("./logo.png"))
        self._set_layout()
        self.show()

    def _set_layout(self):
        self.grid = qtw.QGroupBox("Efficiency Calculator")
        r = self._render()
        self.grid.setLayout(r)

        wrapper = qtw.QVBoxLayout()

        # add dropdown list
        cb = qtw.QComboBox()
        cb.addItem("Test")
        cb.addItem("Test2")
        wrapper.addWidget(cb)

        # Grid
        wrapper.addWidget(self.grid)

        # Add submit btn
        button = qtw.QPushButton("Submit")
        wrapper.addWidget(button)

        button.clicked.connect(self._compute)

        self.setLayout(wrapper)

    def _render(self):
        layout = qtw.QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)

        # row header 1
        layout.addWidget(qtw.QLabel("Gear Input: "), 0, 0)
        for i, name in enumerate(self.gear_names):
            layout.addWidget(qtw.QLabel(name.upper()), 0, i + 1)

        # Row header 2
        layout.addWidget(qtw.QLabel("Main Stat: "), 1, 0)
        layout.addWidget(qtw.QLabel("ATK"), 1, 1)
        layout.addWidget(qtw.QLabel("HP"), 1, 2)
        layout.addWidget(qtw.QLabel("DEF"), 1, 3)
        layout.addWidget(qtw.QLabel("SPD"), 1, 4)
        layout.addWidget(qtw.QLabel("CRIT"), 1, 5)
        layout.addWidget(qtw.QLabel("ATK %"), 1, 6)

        # Row Efficiency Score
        self.eff_output = {}
        layout.addWidget(qtw.QLabel("Max Efficiency Score=40: "), 2, 0)
        for i, gear_name in enumerate(self.gear_names):
            label = qtw.QLabel("0")
            self.eff_output[gear_name] = label
            layout.addWidget(label, 2, i + 1)

        self.inputs = self._set_textbox(layout)

        return layout

    def _set_textbox(self, layout, start_row=3, start_col=1):
        # Column 1 Sub Stat Type
        for i, name, in enumerate(self.stat_names):
            layout.addWidget(qtw.QLabel(f"{name.upper()}: "), start_row + i, 0)

        inputs = {k: {} for k in self.stat_names}

        # Rows
        for row_i, stat_name in enumerate(self.stat_names):
            row = row_i + start_row  # 0 + 3, first row start at index 3
            for col_i, gear_name in enumerate(self.gear_names):
                col = start_col + col_i

                tb = qtw.QLineEdit()
                tb.setObjectName(f"{gear_name} {stat_name}")

                inputs[stat_name][gear_name] = tb  # use to pull text data out
                layout.addWidget(tb, row, col)

        return inputs

    def _compute(self):
        eff = {k: [] for k in self.gear_names}

        for stat_name in self.stat_names:
            for gear_name in self.gear_names:
                _input = self.inputs[stat_name][gear_name].text()
                if _input == "":  # if empty field don't compute
                    continue

                if not _input.isnumeric() and not h.is_float(_input):  # if is not a number
                    self.log.error(f"There is a non number @ Gear: {gear_name.upper()} Sub Stat: {stat_name.upper()}")
                    return

                eff[gear_name].append(self.logic.compute_eff(stat_name, float(_input), self.db))

        for gear, scores in eff.items():
            score = round(sum(scores), 2) if sum(scores) >= 0 else 0
            self.eff_output[gear].setText(str(score))


def run(log, args):
    app = qtw.QApplication([])

    gui = GUI(log, args)
    gui.run()

    # Run the App
    app.exec_()
