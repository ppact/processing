import pandas as pd
from lib.path import data_file_path, ensure_data_dir
from lib.columns import (
    rearrange_complaint_columns, rearrange_personnel_columns, rearrange_event_columns
)
from lib import events
from lib.uid import ensure_uid_unique
import sys
sys.path.append("../")


def fuse_events(pprr, cprr):
    builder = events.Builder()
    builder.extract_events(pprr, {
        events.OFFICER_HIRE: {
            'prefix': 'hire', 'keep': ['uid', 'agency', 'badge_no']},
        events.OFFICER_PAY_EFFECTIVE: {
            'prefix': 'pay_effective', 'keep': ['uid', 'agency', 'badge_no', 'salary', 'salary_freq']
        }
    }, ['uid'])
    builder.extract_events(cprr, {
        events.COMPLAINT_INCIDENT: {
            'prefix': 'incident', 'keep': ['uid', 'agency', 'complaint_uid']
        }
    }, ['uid', 'complaint_uid'])
    return builder.to_frame()


if __name__ == "__main__":
    cprr = pd.read_csv(data_file_path(
        "match/cprr_madisonville_pd_2010_2020.csv"))
    pprr = pd.read_csv(data_file_path("clean/pprr_madisonville_csd_2019.csv"))
    pprr.loc[:, 'agency'] = 'Madisonville PD'
    post_event = pd.read_csv(data_file_path(
        "match/post_event_madisonville_csd_2019.csv"))
    per = rearrange_personnel_columns(pprr)
    com = rearrange_complaint_columns(cprr)
    ensure_uid_unique(com, 'complaint_uid')
    event = fuse_events(pprr, cprr)
    event = rearrange_event_columns(pd.concat([
        post_event,
        event
    ]))
    ensure_uid_unique(event, 'event_uid', True)
    ensure_data_dir("fuse")
    per.to_csv(data_file_path("fuse/per_madisonville_pd.csv"), index=False)
    event.to_csv(data_file_path(
        "fuse/event_madisonville_pd.csv"), index=False)
    com.to_csv(data_file_path("fuse/com_madisonville_pd.csv"), index=False)
