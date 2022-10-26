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
        self.save_file = args.out_dir / "saved_stats.json"

        self.stat_inputs = {"base": {}, "goal": {}, "final": {}, 'gear': {}, 'eff_label': {}}

    def run(self):
        self.setWindowTitle("Artery Gear Efficiency Calculator")
        self.setWindowIcon(qtg.QIcon("./logo.png"))
        self._full()
        self._add_listener()
        self._load_data()
        self.show()

    def _add_listener(self):
        self.selected_eff = None
        for key, widgets in self.stat_inputs.items():
            if key == 'final':
                for widget in widgets.values():
                    widget.setReadOnly(True)
                continue
            elif key == 'eff_label':
                continue

            if type(widgets) is dict:
                for gear, gear_widget in widgets.items():
                    if "set" in gear:
                        gear_widget.currentIndexChanged.connect(self._on_value_change)
                    else:  # efficiency text box + stats
                        gear_widget.textChanged.connect(self._on_value_change)
                        # if key not in ['base', 'goal', 'final']:
                        #     self.selected_eff = key
                        #     gear_widget.clicked.connect(self._highlight_header)
            else:
                widgets.currentIndexChanged.connect(self._on_value_change)

    def _highlight_header(self):
        print(self.selected_eff)
        self.stat_inputs['eff_label'][self.selected_eff].setStyleSheet("QLabel{background: green;}")

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

        # Add Save btn
        button = qtw.QPushButton("Save")
        wrapper.addWidget(button)

        button.clicked.connect(self._save_char)

        self.setLayout(wrapper)
        self._compute()

    def _save_char(self):
        char_name = self.cb.currentText()

        if self.save_file.is_file():
            j_data = self.logic.read_json(self.save_file)
            json_data = h.nested_dict()
            for key, val in j_data.items():
                for key2, val2 in val.items():
                    for key3, val3 in val2.items():
                        json_data[key][key2][key3] = val3
        else:
            json_data = h.nested_dict()

        for key, widgets in self.stat_inputs.items():
            if key == "final":
                continue
            if type(widgets) is dict:
                if key in ['base', 'goal']:  # save stats
                    json_data = self._save_stats(widgets, json_data, char_name, key)
                elif key == 'gear':  # save gear set
                    for _set, set_widget in widgets.items():
                        json_data[char_name.lower()]['sets'][_set] = set_widget.currentText()
                else:
                    for gear, gear_widget in widgets.items():
                        json_data[char_name.lower()]['gear'][gear.lower()][key.lower()] = gear_widget.text()
            else:
                json_data[char_name.lower()]['gear'][key.lower()]['cb_val'] = widgets.currentText()

        self.logic.write_json(self.save_file, json_data)
        self.log.info("Saved Character Stats.")

    def _load_data(self):
        char_name = self.cb.currentText().lower()

        if not self.save_file.is_file():
            self.log.warning(f"Unable to find path. No data to load. {self.save_file}")
            return

        saved_data = self.logic.read_json(self.save_file)
        char = saved_data.get(char_name)
        if char is None:
            self.log.warning(f"No Save Data for Character: {char_name}")
            return

        self.log.info(f"Loading Character: {char_name}")

        # set stats
        for stat_type in ['base', 'goal']:
            self.log.info(f"Loading Stats: {stat_type}")
            for stat, val in char['stat'][stat_type].items():
                self.stat_inputs[stat_type][stat.upper()].setText(val)

        # set gear sets
        for set_num in ['set1', 'set2', 'set3']:
            self.log.info(f"Loading Sets: {set_num}")
            self.stat_inputs['gear'][set_num].setCurrentText(char['sets'][set_num])

        # set Gear SubStats
        for gear in self.gear_names:
            self.log.info(f"Loading Gear: {gear}")
            if gear.upper() in ['BOOSTER', 'BLOCK', 'CHIP']:
                self.stat_inputs[gear].setCurrentText(char['gear'][gear.lower()]['cb_val'])

            for stat, val in char['gear'][gear.lower()].items():
                if stat == 'cb_val':
                    continue
                self.stat_inputs[stat.upper()][gear].setText(val)

        self._compute()

    @staticmethod
    def _save_stats(data, j_data, char_name, stat_type):
        for stat, val in data.items():
            j_data[char_name.lower()]['stat'][stat_type][stat.lower()] = val.text()
        return j_data

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

        return border

    def _on_value_change(self):
        """
        On change any text value,
        :return:
        """
        self._compute()

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
            label = qtw.QLabel(f"{name.upper()}: ")
            layout.addWidget(label, start_row + i, 0)
            self.stat_inputs['eff_label'][name] = label

        inputs = {k: {} for k in self.stat_names}

        # Rows
        for row_i, stat_name in enumerate(self.stat_names):
            row = row_i + start_row  # 0 + 3, first row start at index 3
            for col_i, gear_name in enumerate(self.gear_names):
                col = start_col + col_i

                tb = ClickableLineEdit()
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
                    self.stat_inputs[stat_name][gear_name].setStyleSheet("QLineEdit{background: white;}")
                    continue

                if not _input.isnumeric() and not h.is_float(_input):  # if is not a number
                    self.log.error(f"There is a non number @ Gear: {gear_name.upper()} Sub Stat: {stat_name.upper()}")
                    self.stat_inputs[stat_name][gear_name].setStyleSheet("QLineEdit{background: #FFCCCB;}")
                    return

                self.stat_inputs[stat_name][gear_name].setStyleSheet("QLineEdit{background: white;}")
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
            if f_sub_stats is None:  # DUAL stat don't have so needed to check if is DUAL
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

            p_set_stat = [
                self.set_bonus['BONUS'][stat_name]
                for _set in ['set1', 'set2', 'set3']
                if self.stat_inputs['gear'][_set].currentText() == stat_name
                   and stat_name in ['SPD', 'ATK', 'HP', 'DEF']
            ]

            f_set_stat = [
                self.set_bonus['BONUS'][stat_name]
                for _set in ['set1', 'set2', 'set3']
                if self.stat_inputs['gear'][_set].currentText() == stat_name
                   and stat_name in ['CRIT DMG', 'STATUS ACC', 'STATUS RES', 'CRIT']
            ]

            fixed_stats = f_sub_stats + main_stat + f_set_stat
            perc_stats = p_sub_stats + p_set_stat + p_main_stat

            total_stats = base_stat * (sum(perc_stats) / 100) + sum(fixed_stats) + base_stat

            self.stat_inputs['final'][stat_name].setText(str(round(total_stats, 2)))

            goal_text = self.stat_inputs['goal'][stat_name].text()
            goal_stat = float(goal_text) if h.is_float(goal_text) else 0

            if goal_stat == 0:
                self.stat_inputs['final'][stat_name].setStyleSheet("QLineEdit{background: white;}")
            elif total_stats >= goal_stat:
                self.stat_inputs['final'][stat_name].setStyleSheet("QLineEdit{background: lightgreen;}")
            else:
                self.stat_inputs['final'][stat_name].setStyleSheet("QLineEdit{background: #FFCCCB;}")

    def _get_main_stat(self, stat_name):
        main_stat = [
            self.main_stats[stat_name][gear_name.upper()]
            for gear_name in self.gear_names
            # variable stats - booster/block/chip stat exist
            if (self.stat_inputs.get(gear_name) is not None
                and self.stat_inputs[gear_name].currentText() == stat_name)  # those with static stats
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
        self.log.info(f"Changing Character: {char_name}")
        pixmap = qtg.QPixmap(str(self.thumb / f"{char_name}.png"))
        self.char_label.setPixmap(pixmap)

        # change base stat
        for stat_name, val in self.char_db[char_name]['attr'].items():
            tb = self.stat_inputs['base'][stat_name]
            tb.setText(val)

        self._load_data()
        self._compute()

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


class ClickableLineEdit(qtw.QLineEdit):
    clicked = qtc.pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.LeftButton:
            self.clicked.emit()
        else:
            super().mousePressEvent(event)
