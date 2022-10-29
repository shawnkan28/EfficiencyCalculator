from PyQt5 import QtWidgets

import helper as h
from Logger import Logger
from Parameter import Parameters
from crawler import Crawler
from ui_window import Window
from getter_setter import GS

""" Initializing Script Parameters """
args = Parameters(description="Framework project").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()
h.clean_logs(log_path.parent, log=log)


def main():
    f_path = args.var_dir / "character_db.pickle"
    thumb_path = args.var_dir / "thumb"
    # pull and save character information from Server in a file
    try:
        Crawler(args.base_url, log).all_characters(f_path, thumb_path)
    except Exception as e:
        log.debug(e)
        log.warning(f"Failed to pull from website. Using Local File ...")

    gs = GS()
    gs.thumb_path = thumb_path
    gs.char_df = h.pickle_file('read', fname=f_path)
    gs.log = log

    app(gs)


def app(gs):
    q_app = QtWidgets.QApplication([])

    # set GUI
    window = Window(gs)
    window.show()

    # Run the App
    q_app.exec_()


if __name__ == '__main__':
    main()
