import math

import PyQt5.QtCore as qtc
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
            args.db: {"header": [0, 1], "index_col": 0},
            args.main_stats: {"index_col": 0},
            args.set_bonus: {"index_col": 0}
        })

        self.gear_names = dfs["struct"].columns.to_list()
        self.stat_names = dfs['struct'].index.to_list()
        self.db = dfs['db']
        self.main_stats = dfs['main_stats'].replace(",", "", regex=True).astype(float)
        self.set_bonus = dfs['set_bonus']
        self.log = log

        # Opening JSON file
        self.char_db = self.logic.read_json(args.out_dir / 'processed_char.json')
        self.ele_list = sorted([x for x in self.char_db.keys()])

        self.thumb = args.out_dir / "thumb"

        self.stat_inputs = {"base": {}, "goal": {}, "final": {}, 'gear': {}}

    def run(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon("./logo.png"))
        self._full()
        self.show()

    def _full(self):
        self.eff_calc = qtw.QGroupBox("Efficiency Calculator")
        grid = self._get_grid()

        eff_layout = qtw.QVBoxLayout()

        # add combobox for gear set Stats
        gear_set_layout = self._set_gear_set_cb()

        eff_layout.addWidget(gear_set_layout)
        eff_layout.addLayout(grid)

        self.eff_calc.setLayout(eff_layout)

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
        wrapper.addWidget(self.eff_calc)

        # Add submit btn
        button = qtw.QPushButton("Submit")
        wrapper.addWidget(button)

        button.clicked.connect(self._compute)

        self.setLayout(wrapper)

    def _set_gear_set_cb(self):
        border = qtw.QGroupBox("Gear Sets")
        layout = qtw.QGridLayout()

        l1 = qtw.QLabel("Set 1:")
        l1.setAlignment(qtc.Qt.AlignRight)
        layout.addWidget(l1, 0, 0)

        cb1 = qtw.QComboBox()
        cb1.addItems(['NA', 'SPD', 'ATK', 'CRIT DMG', 'HP', 'DEF', 'STATUS ACC', 'STATUS RES', 'CRIT', 'COUNTER'])
        layout.addWidget(cb1, 0, 1)
        self.stat_inputs['gear']['set1'] = cb1

        l2 = qtw.QLabel("Set 2:")
        l2.setAlignment(qtc.Qt.AlignRight)
        layout.addWidget(l2, 0, 2)

        cb2 = qtw.QComboBox()
        cb2.addItems(['NA', 'HP', 'DEF', 'STATUS ACC', 'STATUS RES', 'CRIT', 'IMMU'])
        layout.addWidget(cb2, 0, 3)
        self.stat_inputs['gear']['set2'] = cb2

        l3 = qtw.QLabel("Set 3:")
        l3.setAlignment(qtc.Qt.AlignRight)
        layout.addWidget(l3, 0, 4)

        cb3 = qtw.QComboBox()
        cb3.addItems(['NA', 'HP', 'DEF', 'STATUS ACC', 'STATUS RES', 'CRIT', 'IMMU'])
        layout.addWidget(cb3, 0, 5)
        self.stat_inputs['gear']['set3'] = cb3

        border.setLayout(layout)

        # on change dropdown list
        for _set in [cb1, cb2, cb3]:
            _set.currentIndexChanged.connect(self._on_gear_set_change)

        return border

    def _on_gear_set_change(self):
        pass
        # compute()

    def _add_header(self):
        layout = qtw.QHBoxLayout()

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

    def _get_grid(self):
        layout = qtw.QGridLayout()

        # row header 1
        layout.addWidget(qtw.QLabel("Gear Input: "), 0, 0)
        for i, name in enumerate(self.gear_names):
            layout.addWidget(qtw.QLabel(name.upper()), 0, i + 1)

        # Row header 2
        layout.addWidget(qtw.QLabel("Main Stat: "), 1, 0)
        layout.addWidget(qtw.QLabel("ATK"), 1, 1)
        layout.addWidget(qtw.QLabel("HP"), 1, 2)
        layout.addWidget(qtw.QLabel("DEF"), 1, 3)

        booster = qtw.QComboBox()
        booster.addItems(['ATK', 'ATK %', 'HP', 'HP %', 'DEF', 'DEF %', 'SPD'])
        layout.addWidget(booster, 1, 4)
        self.stat_inputs['Booster'] = booster
        scope = qtw.QComboBox()
        scope.addItems(['ATK', 'ATK %', 'HP', 'HP %', 'DEF', 'DEF %', 'CRIT', 'CRIT DMG'])
        layout.addWidget(scope, 1, 5)
        self.stat_inputs['Block'] = scope
        chip = qtw.QComboBox()
        chip.addItems(['ATK', 'ATK %', 'HP', 'HP %', 'DEF', 'DEF %', 'STATUS ACC', 'STATUS RES'])
        layout.addWidget(chip, 1, 6)
        self.stat_inputs['Chip'] = chip

        # Row Efficiency Score
        self.eff_output = {}
        layout.addWidget(qtw.QLabel("Max Efficiency Score=40: "), 2, 0)
        for i, gear_name in enumerate(self.gear_names):
            label = qtw.QLabel("0")
            self.eff_output[gear_name] = label
            layout.addWidget(label, 2, i + 1)

        inputs = self._set_textbox(layout)
        self.stat_inputs.update(inputs)

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
                _input = self.stat_inputs[stat_name][gear_name].text()
                if _input == "":  # if empty field don't compute
                    continue

                if not _input.isnumeric() and not h.is_float(_input):  # if is not a number
                    self.log.error(f"There is a non number @ Gear: {gear_name.upper()} Sub Stat: {stat_name.upper()}")
                    return

                eff[gear_name].append(self.logic.compute_eff(stat_name, float(_input), self.db))

        for gear, scores in eff.items():
            score = round(sum(scores), 2) if sum(scores) >= 0 else 0
            self.eff_output[gear].setText(str(score))

        self._compute_stats()

    def _compute_stats(self):
        # for each stat, get input values
        for stat_name, base_widget in self.stat_inputs["base"].items():
            base_stat = float(base_widget.text()) if h.is_float(base_widget.text()) else 0

            f_sub_stats = self.stat_inputs.get(stat_name)
            if f_sub_stats is None:  # DUAL stat dont have so need to check if is DUAL
                continue

            # Fixed Sub Stat
            f_sub_stats = [
                float(widget.text()) if h.is_float(widget.text()) else 0
                for widget in f_sub_stats.values()
            ]

            # Percentage sub stat
            p_sub_stats = self.stat_inputs.get(stat_name + " %")
            if p_sub_stats is not None:
                p_sub_stats = [
                    float(widget.text()) if h.is_float(widget.text()) else 0
                    for widget in p_sub_stats.values()
                ]
            else:
                p_sub_stats = []

            main_stat, p_main_stat = self._get_main_stat(stat_name)

            set_stat = [
                self.set_bonus['BONUS'][stat_name]
                for _set in ['set1', 'set2', 'set3']
                if self.stat_inputs['gear'][_set].currentText() == stat_name
            ]

            fixed_stats = f_sub_stats + main_stat
            perc_stats = p_sub_stats + set_stat + p_main_stat

            total_stats = base_stat * (sum(perc_stats) / 100) + sum(fixed_stats) + base_stat

    def _get_main_stat(self, stat_name):
        main_stat = [
            self.main_stats[stat_name][gear_name.upper()]
            for gear_name in self.gear_names
            # variable stats - booster/block/chip stat exist
            if (self.stat_inputs.get(gear_name) is not None
                and self.stat_inputs[gear_name].currentText() == stat_name)
            # those with static stats
            or (gear_name in ['Weapon', 'Core', 'Shield']
                and not math.isnan(self.main_stats[stat_name][gear_name.upper()]))
        ]

        perc_stat = [
            float(self.main_stats[stat_name + " %"][gear_name.upper()]) * 100
            if h.is_float(self.main_stats[stat_name + " %"][gear_name.upper()]) else 0
            for gear_name in self.gear_names
            # variable stats - booster/block/chip stat exist
            if (self.stat_inputs.get(gear_name) is not None
                and self.stat_inputs[gear_name].currentText() == stat_name + " %")
        ]

        return main_stat, perc_stat

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

    @staticmethod
    def _char_stats(group_name, data):
        border = qtw.QGroupBox(group_name)
        grid = qtw.QGridLayout()

        for i, (name, widget) in enumerate(data.items()):
            grid.addWidget(widget[0], i, 0)
            grid.addWidget(widget[1], i, 1)

        border.setLayout(grid)
        return border


def run(log, args):
    app = qtw.QApplication([])

    gui = GUI(log, args)
    gui.run()

    # Run the App
    app.exec_()
