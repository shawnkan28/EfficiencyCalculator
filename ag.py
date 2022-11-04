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

    env.thumb = args.var_dir / "thumb"
    env.db_char = args.var_dir / "char_info_db.pickle"
    env.db_main = args.var_dir / "gear_main.pickle"
    env.db_sub = args.var_dir / "gear_sub.pickle"
    env.db_set = args.var_dir / "gear_sets.pickle"
    env.logo = args.asset_dir / "logo.png"

    c.extract_character_info(env.db_char, env.thumb)
    c.extract_gear_info(env.db_main, env.db_sub)
    c.extract_gear_set_info(env.db_set)

    app(env)


def app(e):
    q_app = QtWidgets.QApplication([])

    window = Window(e)
    window.show()

    q_app.exec_()


if __name__ == '__main__':
    main()
