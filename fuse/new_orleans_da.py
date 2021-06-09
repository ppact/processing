from lib.path import data_file_path, ensure_data_dir
from lib.columns import (
    rearrange_complaint_columns, rearrange_event_columns
)
from lib.personnel import fuse_personnel
from lib import events
from lib.uid import ensure_uid_unique
import pandas as pd
import sys
sys.path.append('../')


def fuse_events(pprr, cprr, post):
    builder = events.Builder()
    builder.extract_events(pprr, {
        events.OFFICER_HIRE: {
            'prefix': 'hire', 'keep': ['uid', 'badge_no' 'agency', 'rank_desc']
        },
        events.OFFICER_LEFT: {
            'prefix': 'term', 'keep': ['uid', 'badge_no', 'agency', 'rank_desc']
        },
        events.OFFICER_RANK: {'prefix': 'rank', 'keep': [ 'uid', 'agency', 'rank_code', 'rank_desc']},
        events.OFFICER_DEPT: {'prefix': 'dept', 'keep': [
            'uid', 'agency', 'department_code', 'department_desc']},
    }, ['uid'])
    builder.extract_events(cprr, {
        events.COMPLAINT_INCIDENT: {
            'prefix': 'receive', 'keep': ['uid', 'agency', 'complaint_uid']
        }
    }, ['uid', 'complaint_uid'])
    return builder.to_frame()


if __name__ == '__main__':
    cprr = pd.read_csv(data_file_path(
        'match/cprr_new_orleans_da_2021.csv'
    ))
    pprr = pd.read_csv(data_file_path(
        'clean/pprr_new_orleans_pd_1946_2018.csv'
    ))
    post_event = pd.read_csv(data_file_path(
        'match/post_event_new_orleans_da_2021.csv'))
    so_per = pd.read_csv(data_file_path('match/per_new_orleans_so.csv'))
    personnels = fuse_personnel(pprr, cprr, so_per)
    complaints = rearrange_complaint_columns(cprr)
    ensure_uid_unique(complaints, 'complaint_uid', True)
    events_df = fuse_events(pprr, cprr, post)
    events_df = rearrange_event_columns(pd.concat([
        post_event,
        events_df
    ]))
    ensure_uid_unique(events_df, 'event_uid', True)
    ensure_data_dir('fuse')
    personnels.to_csv(data_file_path(
        'fuse/per_new_orleans_da.csv'), index=False)
    events_df.to_csv(data_file_path(
        'fuse/event_new_orleans_da.csv'), index=False)
    complaints.to_csv(data_file_path(
        'fuse/com_new_orleans_da.csv'), index=False)