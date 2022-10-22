import math

import numpy as np

import helper as h
from Logger import Logger
from Parameter import Parameters

import pandas as pd

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

    eff = {k: [] for k in gear_df.columns}
    # for each sub stat and each gear, compute efficiency
    for stat_name, r in gear_df.iterrows():
        for col_name in gear_df.columns:
            if math.isnan(r[col_name]):
                continue

            eff[col_name].append(compute_eff(stat_name, r[col_name], db_df))

    for gear, scores in eff.items():
        log.info(f"{gear}: {sum(scores)}")


def compute_eff(stat_name, stat_val, db_df):
    """
    compute efficiency of gear for each sub stat
    :return: efficiency val
    """
    # COMPUTE FOR INDIVIDUAL EFFICIENCY SUB STAT USED FOR GEAR
    # 10 * (ATK% - LOWESTSubStatVal) / (MAXSubStatVal - LOWESTSubStatVal)
    min_val = db_df['BLUE']['Min'][stat_name]
    max_val = db_df['GOLD']['Max'][stat_name]
    return 10 * ((stat_val - min_val) / (max_val - min_val))


if __name__ == '__main__':
    main()
