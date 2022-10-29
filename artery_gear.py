from PyQt5 import QtWidgets

import helper as h
from Logger import Logger
from Parameter import Parameters
from crawler import Crawler
from window import Window

""" Initializing Script Parameters """
args = Parameters(description="Framework project").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()
h.clean_logs(log_path.parent, log=log)


def main():
    try:
        Crawler(args.base_url, log).all_characters(args.var_dir / "character_db.json", args.var_dir / "thumb")
    except Exception as e:
        log.debug(e)
        log.warning(f"Failed to pull from website. Using Local File ...")

    app()


def app():
    q_app = QtWidgets.QApplication([])

    window = Window()
    window.show_()

    # Run the App
    q_app.exec_()


if __name__ == '__main__':
    main()
