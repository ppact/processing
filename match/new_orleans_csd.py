from lib.path import data_file_path, ensure_data_dir
from lib.match import (
    ThresholdMatcher, ColumnsIndex, JaroWinklerSimilarity, StringSimilarity, DateSimilarity
)
from lib.date import combine_date_columns
import pandas as pd
import sys
sys.path.append("../")


def match_officers(df09, df14):
    # limit number of columns
    dfa = df09[["first_name", "last_name", "rank_code", "mid"]]
    # hire date can be similar to pay prog start date for 2009 data
    dfa.loc[:, "hire_date"] = combine_date_columns(
        df09, "pay_prog_start_year", "pay_prog_start_month", "pay_prog_start_day")
    dfa = dfa.drop_duplicates(["mid"]).set_index("mid", drop=True)

    # limit number of columns
    dfb = df14[["first_name", "last_name", "rank_code", "mid"]]
    dfb.loc[:, "hire_date"] = combine_date_columns(
        df14, "hire_year", "hire_month", "hire_day")
    dfb = dfb.drop_duplicates(["mid"]).set_index("mid", drop=True)

    matcher = ThresholdMatcher(dfa, dfb, ColumnsIndex(["first_name"]), {
        "last_name": JaroWinklerSimilarity(),
        "rank_code": StringSimilarity(),
        "hire_date": DateSimilarity()
    })
    decision = 0.886
    matcher.save_pairs_to_excel(data_file_path(
        "match/new_orleans_csd_pprr_2009_v_pprr_2014.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(decision)

    mid_09_to_uid_dict = dict()
    for mid_09, mid_14 in matches:
        row_09 = dfa.loc[mid_09]
        row_14 = dfb.loc[mid_14]
        if row_09.last_name[0] != row_14.last_name[0]:
            continue

        # correct with longest last_name
        last_name = row_14.last_name
        if len(row_09.last_name) > len(last_name):
            last_name = row_09.last_name
        df09.loc[df09.mid == mid_09, "last_name"] = last_name
        df14.loc[df14.mid == mid_14, "last_name"] = last_name

        # take match id of 2014 data as officer uid
        uid = mid_14
        mid_09_to_uid_dict[mid_09] = uid

    # add uid column to both
    df14.loc[:, "uid"] = df14.mid
    df09.loc[:, "uid"] = df09.mid.map(lambda x: mid_09_to_uid_dict.get(x, x))
    df14 = df14.drop(columns=["mid"])
    df09 = df09.drop(columns=["mid"])

    return df09, df14


if __name__ == "__main__":
    df09 = pd.read_csv(data_file_path(
        "clean/pprr_new_orleans_csd_2009.csv"))
    df14 = pd.read_csv(data_file_path(
        "clean/pprr_new_orleans_csd_2014.csv"))
    df09, df14 = match_officers(df09, df14)
    ensure_data_dir("match")
    df09.to_csv(
        data_file_path("match/pprr_new_orleans_csd_2009.csv"),
        index=False)
    df14.to_csv(
        data_file_path("match/pprr_new_orleans_csd_2014.csv"),
        index=False)
