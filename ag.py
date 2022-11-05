import helper as h
from Logger import Logger
from Parameter import Parameters
from data.env import Env
from data.crawler import Crawler
from ui.window import Window

from PyQt5 import QtWidgets

""" Initializing Script Parameters """
args = Parameters(description="Framework project").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()
h.clean_logs(log_path.parent, log=log)


def main():
    env = Env(log)

    c = Crawler(args.base_url, env)

    env.thumb, char_list = args.var_dir / "thumb", args.var_dir / "char_list.pickle"
    db_char, db_main = args.var_dir / "char_info_db.pickle", args.var_dir / "gear_main.pickle"
    db_sub, db_set = args.var_dir / "gear_sub.pickle", args.var_dir / "gear_sets.pickle"
    env.logo, avail_stats = args.asset_dir / "logo.png", args.var_dir / "stats_list.pickle"
    gear_names = args.var_dir / "gear_names.pickle"

    c.extract_character_info(db_char, char_list, env.thumb, avail_stats)
    c.extract_gear_info(db_main, db_sub, gear_names)
    c.extract_gear_set_info(db_set)

    env.char_list, env.db_char = char_list, db_char
    env.db_main, env.db_sub = db_main, db_sub
    env.db_set, env.gear_names = db_set, gear_names

    env.char_stats = [x for x in env.db_char.columns if "fullName" not in x]
    env.gear_stats = env.db_sub.index.to_list()

    app(env)


def app(e):
    q_app = QtWidgets.QApplication([])

    window = Window(e)
    window.show()

    q_app.exec_()


if __name__ == '__main__':
    main()
