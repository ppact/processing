import sys

import pandas as pd

from lib.path import data_file_path, ensure_data_dir
from lib.columns import rearrange_complaint_columns
from lib.personnel import fuse_personnel
from lib import events

sys.path.append('../')


def fuse_events(cprr, post):
    builder = events.Builder()
    builder.extract_events(cprr, {
        events.COMPLAINT_RECEIVE: {
            'prefix': 'receive', 'parse_date': True, 'keep': ['uid', 'agency', 'complaint_uid'],
        },
        events.INVESTIGATION_START: {
            'prefix': 'investigation_start', 'parse_date': True, 'keep': ['uid', 'agency', 'complaint_uid'],
        },
        events.INVESTIGATION_COMPLETE: {
            'prefix': 'investigation_complete', 'parse_date': True, 'keep': ['uid', 'agency', 'complaint_uid'],
        }
    }, ['uid', 'complaint_uid'])
    builder.extract_events(post, {
        events.OFFICER_LEVEL_1_CERT: {'prefix': 'level_1_cert', 'parse_date': '%Y-%m-%d', 'keep': [
            'uid', 'agency'
        ]},
        events.OFFICER_PC_12_QUALIFICATION: {'prefix': 'last_pc_12_qualification', 'parse_date': '%Y-%m-%d', 'keep': [
            'uid', 'agency'
        ]},
        events.OFFICER_HIRE: {
            'prefix': 'hire', 'keep': ['uid', 'agency']
        }
    }, ['uid'])
    return builder.to_frame()


if __name__ == '__main__':
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    post = post[post.agency == 'orleans parish so']
    post.loc[:, 'agency'] = 'New Orleans SO'
    cprr = pd.read_csv(data_file_path('match/cprr_new_orleans_so_2019.csv'))
    per = fuse_personnel(post, cprr)
    event = fuse_events(cprr, post)
    com = rearrange_complaint_columns(cprr)
    ensure_data_dir('fuse')
    per.to_csv(data_file_path('fuse/per_new_orleans_so.csv'), index=False)
    event.to_csv(data_file_path('fuse/event_new_orleans_so.csv'), index=False)
    com.to_csv(data_file_path('fuse/com_new_orleans_so.csv'), index=False)
