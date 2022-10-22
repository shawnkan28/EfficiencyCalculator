import helper as h
from Logger import Logger
from Parameter import Parameters

import pandas as pd

from compute import Computer
import gui

""" Initializing Script Parameters """
args = Parameters(description="Framework project").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()


def main():
    if not args.gear_stat.is_file():
        log.error("Unable to locate csv file of gear stats.")
        gear_df = pd.DataFrame()
    else:
        log.info(f"Reading Gear Stats from {args.gear_stat}")
        gear_df = pd.read_csv(args.gear_stat, index_col=0)

    if not args.db.is_file():
        log.error("Unable to locate csv file of gear stats.")
        db_df = pd.DataFrame()
    else:
        log.info(f"Reading Gear Stats from {args.db}")
        db_df = pd.read_csv(args.db, header=[0, 1], index_col=0)

    assert not gear_df.empty
    assert not db_df.empty

    gui.run(gear_df, db_df, log)


if __name__ == '__main__':
    main()
