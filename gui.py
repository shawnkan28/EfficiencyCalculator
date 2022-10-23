import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

import helper as h
from logic import Logic


class GUI(qtw.QWidget):
    def __init__(self, log, args):
        super().__init__()
        self.logic = Logic(args, log)

        dfs = self.logic.get_db({
            args.gear_stat: {"index_col": 0},
            args.db: {"header": [0, 1], "index_col": 0}
        })
        self.gear_names = dfs["struct"].columns.to_list()
        self.stat_names = dfs['struct'].index.to_list()
        self.db = dfs['db']
        self.log = log

        # Opening JSON file
        self.char_db = self.logic.read_json(args.out_dir / 'processed_char.json')
        self.ele_list = sorted([x for x in self.char_db.keys()])

        self.thumb = args.out_dir / "thumb"

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
        self.cb = qtw.QComboBox()
        self._add_cb_elements(self.cb)
        self.cb.currentIndexChanged.connect(self._on_cb_change)
        # Set to searchable combo box
        self.cb.setEditable(True)
        # completer only work for editable combo boxes. QComboBox.NoInsert prevents insertion of the search text
        self.cb.setInsertPolicy(qtw.QComboBox.NoInsert)
        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.cb.completer().setCompletionMode(qtw.QCompleter.PopupCompletion)
        wrapper.addWidget(self.cb)

        # header includes character icon and character base stats
        header = self._add_header()
        wrapper.addLayout(header)

        # Grid
        wrapper.addWidget(self.grid)

        # Add submit btn
        button = qtw.QPushButton("Submit")
        wrapper.addWidget(button)

        button.clicked.connect(self._compute)

        self.setLayout(wrapper)

    def _add_header(self):
        layout = qtw.QHBoxLayout()
        self.stat_inputs = {"base": {}, "goal": {}, "final": {}}

        # Set character icon
        pixmap = qtg.QPixmap(str(self.thumb / f"{self.ele_list[0]}.png"))
        self.char_label = qtw.QLabel()
        self.char_label.setPixmap(pixmap)
        self.char_label.resize(pixmap.width(), pixmap.height())
        layout.addWidget(self.char_label)

        # Character Base Stats
        attr = self.char_db[self.ele_list[0]]['attr']
        for name, val in attr.items():
            tb = qtw.QLineEdit()
            tb.setObjectName(f"base {name}")
            tb.setText(val)
            self.stat_inputs["base"][name] = tb
            attr[name] = [qtw.QLabel(name.upper() + ":"), tb]
        b_stats = self._char_stats("Base Stats", attr)

        # Character Goal Stats
        goal_attr = attr.copy()
        for name, val in goal_attr.items():
            tb = qtw.QLineEdit()
            tb.setObjectName(f"goal {name}")
            self.stat_inputs["goal"][name] = tb
            tb.setText("0")
            goal_attr[name] = [qtw.QLabel(name.upper() + ":"), tb]
        g_stats = self._char_stats("Goal Stats", goal_attr)

        # Character Final Stats
        final_attr = attr.copy()
        for name, val in final_attr.items():
            tb = qtw.QLineEdit()
            tb.setObjectName(f"final {name}")
            self.stat_inputs["final"][name] = tb
            total_stat = int(attr[name][1].text())
            tb.setText(str(total_stat))
            final_attr[name] = [qtw.QLabel(name.upper() + ":"), tb]
        f_stats = self._char_stats("Final Stats", final_attr)

        layout.addWidget(b_stats)
        layout.addWidget(g_stats)
        layout.addWidget(f_stats)

        return layout

    @staticmethod
    def _char_stats(group_name, data):
        border = qtw.QGroupBox(group_name)
        grid = qtw.QGridLayout()
        grid.setColumnStretch(1, 4)

        for i, (name, widget) in enumerate(data.items()):
            grid.addWidget(widget[0], i, 0)
            grid.addWidget(widget[1], i, 1)

        border.setLayout(grid)
        return border

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
            gear_vals = []

            for gear_name in self.gear_names:
                _input = self.inputs[stat_name][gear_name].text()
                if _input == "":  # if empty field don't compute
                    continue

                if not _input.isnumeric() and not h.is_float(_input):  # if is not a number
                    self.log.error(f"There is a non number @ Gear: {gear_name.upper()} Sub Stat: {stat_name.upper()}")
                    return

                gear_vals.append(float(_input))
                eff[gear_name].append(self.logic.compute_eff(stat_name, float(_input), self.db))

            self._compute_stats(gear_vals, stat_name)

        for gear, scores in eff.items():
            score = round(sum(scores), 2) if sum(scores) >= 0 else 0
            self.eff_output[gear].setText(str(score))

    def _compute_stats(self, stats, name):
        if "%" in name:
            pass
        else:
            return sum(stats) + self.stat_inputs['base'][name]



    def _add_cb_elements(self, cb):
        for ele in self.ele_list:
            cb.addItem(ele)

    def _on_cb_change(self):
        # change image
        char_name = self.cb.currentText()
        pixmap = qtg.QPixmap(str(self.thumb / f"{char_name}.png"))
        self.char_label.setPixmap(pixmap)

        # change base stat
        for stat_name, val in self.char_db[char_name]['attr'].items():
            tb = self.stat_inputs['base'][stat_name]
            tb.setText(val)


def run(log, args):
    app = qtw.QApplication([])

    gui = GUI(log, args)
    gui.run()

    # Run the App
    app.exec_()
