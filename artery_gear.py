import gui
import helper as h
from Logger import Logger
from Parameter import Parameters
from logic import Logic

""" Initializing Script Parameters """
args = Parameters(description="Framework project").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
h.clean_logs(log_path.parent)
log = Logger(log_path).get_logger()


def main():
    logic = Logic(args, log)
    try:
        log.info(f"Pulling from Website {args.base_url}")
        logic.get_all_char_info()
    except Exception as e:
        log.debug(e)
        log.warning(f"Failed to pull from Website. Using Local file ...")

    logic.process_char_info()  # to get only important info

    gui.run(log, args)


if __name__ == '__main__':
    main()
