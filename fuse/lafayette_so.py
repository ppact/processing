import sys
sys.path.append('../')
from lib.path import data_file_path, ensure_data_dir
from lib.columns import (
    rearrange_complaint_columns,
)
from lib import events
from lib.uid import ensure_uid_unique
from lib.personnel import fuse_personnel
import pandas as pd


def prepare_post():
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    return post[post.agency == 'lafayette parish so']


def fuse_events(cprr, post):
    builder = events.Builder()
    builder.extract_events(cprr, {
        events.INVESTIGATION_START: {
            'prefix': 'receive', 'keep': ['uid', 'agency', 'complaint_uid']
        },
    },
        ['uid', 'complaint_uid'],
    )
    builder.extract_events(post, {
        events.OFFICER_LEVEL_1_CERT: {
            'prefix': 'level_1_cert', 'parse_date': '%Y-%m-%d', 'keep': ['uid', 'agency', 'employment_status']
        },
        events.OFFICER_HIRE: {
            'prefix': 'hire', 'keep': ['uid', 'agency', 'employment_status']
        },
        events.OFFICER_PC_12_QUALIFICATION: {
            'prefix': 'last_pc_12_qualification', 'parse_date': '%Y-%m-%d', 'keep':
            ['uid', 'agency', 'employment_status'],
        }
    }, ['uid'])
    return builder.to_frame()


if __name__ == '__main__':
    cprr = pd.read_csv(data_file_path('clean/cprr_lafayette_so_2015_2020.csv'))
    post = prepare_post()
    complaints = rearrange_complaint_columns(cprr)
    ensure_uid_unique(complaints, 'complaint_uid')
    event = fuse_events(cprr, post)
    personnel_df = fuse_personnel(cprr, post)
    ensure_data_dir('fuse')
    personnel_df.to_csv(data_file_path('fuse/per_lafayette_so.csv'), index=False)
    event.to_csv(data_file_path('fuse/event_lafayette_so.csv'), index=False)
    complaints.to_csv(data_file_path('fuse/com_lafayette_so.csv'), index=False)
