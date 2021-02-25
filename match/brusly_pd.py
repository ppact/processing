from lib.match import (
    ThresholdMatcher, NoopIndex, JaroWinklerSimilarity
)
from lib.path import data_file_path, ensure_data_dir
import pandas as pd
import sys
sys.path.append("../")


def add_uid_to_complaint(cprr, pprr):
    dfa = cprr[["first_name", "last_name"]]
    dfb = pprr.set_index("uid", drop=True)[["first_name", "last_name"]]

    matcher = ThresholdMatcher(dfa, dfb, NoopIndex(), {
        "first_name": JaroWinklerSimilarity(),
        "last_name": JaroWinklerSimilarity()
    })
    matches = matcher.get_index_pairs_within_thresholds()

    matches = dict(matches)
    cprr.loc[:, "uid"] = cprr.index.map(lambda i: matches[i])
    cprr = cprr.drop(columns=["first_name", "last_name"])

    return cprr


def add_supervisor_uid_to_complaint(cprr, pprr):
    dfa = cprr[["supervisor_first_name", "supervisor_last_name"]]
    dfa.columns = ["first_name", "last_name"]
    dfb = pprr.set_index("uid", drop=True)[["first_name", "last_name"]]

    matcher = ThresholdMatcher(dfa, dfb, NoopIndex(), {
        "first_name": JaroWinklerSimilarity(),
        "last_name": JaroWinklerSimilarity()
    })
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=0.9)

    matches = dict(matches)
    cprr.loc[:, "supervisor_uid"] = cprr.index.map(lambda i: matches[i])
    cprr = cprr.drop(columns=["supervisor_first_name", "supervisor_last_name"])

    return cprr


if __name__ == "__main__":
    cprr = pd.read_csv(data_file_path("clean/cprr_brusly_pd_2020.csv"))
    pprr = pd.read_csv(data_file_path("clean/pprr_brusly_pd_2020.csv"))
    cprr = add_uid_to_complaint(cprr, pprr)
    cprr = add_supervisor_uid_to_complaint(cprr, pprr)
    ensure_data_dir("match")
    cprr.to_csv(data_file_path("match/cprr_brusly_pd_2020.csv"), index=False)
