import math


class Computer:
    def __init__(self, gear, db, log):
        self.gear = gear
        self.db = db
        self.log = log
        self.eff_score = None

    def run(self):
        eff = {k: [] for k in self.gear.columns}
        # for each sub stat and each gear, compute efficiency
        for stat_name, r in self.gear.iterrows():
            for col_name in self.gear.columns:
                if math.isnan(r[col_name]):
                    continue

                eff[col_name].append(self._compute_eff(stat_name, r[col_name]))

        self.eff_score = eff
        self._display()

    def _display(self):
        for gear, scores in self.eff_score.items():
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
