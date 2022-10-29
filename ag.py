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
    f_path = args.var_dir / "character_db.pickle"
    thumb_path = args.var_dir / "thumb"
    # pull and save character information from Server in a file
    try:
        Crawler(args.base_url, log).all_characters(f_path, thumb_path)
    except Exception as e:
        log.debug(e)
        log.warning(f"Failed to pull from website. Using Local File ...")

    app(h.pickle_file('read', fname=f_path))


def app(char_df):
    q_app = QtWidgets.QApplication([])

    window = Window()
    window.show_()

    # Run the App
    q_app.exec_()


if __name__ == '__main__':
    main()
