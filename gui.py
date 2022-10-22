import PyQt5.QtWidgets as qtw
import helper as h


class GUI(qtw.QWidget):
    def __init__(self, struct_df, db, log):
        super().__init__()
        self.gear_names = struct_df.columns.to_list()
        self.stat_names = struct_df.index.to_list()
        self.db = db
        self.log = log

    def run(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self._set_layout()
        self.show()

    def _set_layout(self, _type="grid"):
        if _type == "grid":
            self.ly = qtw.QGroupBox("Efficiency Calculator")
            r = self._render()
            self.ly.setLayout(r)

            grid = qtw.QVBoxLayout()
            grid.addWidget(self.ly)

            self.setLayout(grid)

            button = qtw.QPushButton("Submit")
            self.layout().addWidget(button)

            button.clicked.connect(self._compute)

    def _render(self):
        layout = qtw.QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)

        # row header 1
        layout.addWidget(qtw.QLabel("Gear Input: "), 0, 0)
        for i, name in enumerate(self.gear_names):
            layout.addWidget(qtw.QLabel(name.upper()), 0, i+1)

        # Row header 2
        layout.addWidget(qtw.QLabel("Main Stat: "), 1, 0)
        layout.addWidget(qtw.QLabel("ATK"), 1, 1)
        layout.addWidget(qtw.QLabel("HP"), 1, 2)
        layout.addWidget(qtw.QLabel("DEF"), 1, 3)
        layout.addWidget(qtw.QLabel("SPD"), 1, 4)
        layout.addWidget(qtw.QLabel("CRIT"), 1, 5)
        layout.addWidget(qtw.QLabel("ATK %"), 1, 6)

        # Column 1 Sub Stat Type
        for i, name, in enumerate(self.stat_names):
            layout.addWidget(qtw.QLabel(f"{name.upper()}: "), 2 + i, 0)

        self.inputs = self._set_textbox(layout)

        return layout

    def _set_textbox(self, layout, start_row=2, start_col=1):
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

                eff[gear_name].append(self._compute_eff(stat_name, float(_input)))

        for gear, scores in eff.items():
            self.log.info(f"{gear} Efficiency Score: {round(sum(scores), 2)} / 40")

    def _compute_eff(self, stat_name, stat_val):
        """
        compute efficiency of gear for each sub stat
        :return: efficiency val
        """
        # COMPUTE FOR INDIVIDUAL EFFICIENCY SUB STAT USED FOR GEAR
        # 10 * (ATK% - LOWESTSubStatVal) / (MAXSubStatVal - LOWESTSubStatVal)
        min_val = self.db['BLUE']['Min'][stat_name]
        max_val = self.db['GOLD']['Max'][stat_name]
        return 10 * ((stat_val - min_val) / (max_val - min_val))


def run(struct_df, db, log):
    app = qtw.QApplication([])

    gui = GUI(struct_df, db, log)
    gui.run()

    # Run the App
    app.exec_()

