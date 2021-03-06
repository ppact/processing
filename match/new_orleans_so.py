import sys

import pandas as pd
from datamatch import ThresholdMatcher, JaroWinklerSimilarity, ColumnsIndex, Swap

from lib.path import data_file_path, ensure_data_dir

sys.path.append('../')


def deduplicate_cprr_personnel(cprr):
    df = cprr.loc[cprr.uid.notna(), ['employee_id', 'first_name', 'last_name', 'uid']]\
        .drop_duplicates().set_index('uid', drop=True)

    matcher = ThresholdMatcher(ColumnsIndex('employee_id'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, df, variator=Swap('first_name', 'last_name'))
    decision = 0.9
    matcher.save_pairs_to_excel(data_file_path(
        "match/new_orleans_so_cprr_dedup.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(decision)
    # canonicalize name and uid
    for uid, al_uid in matches:
        for col in ['uid', 'first_name', 'last_name', 'middle_initial']:
            v = cprr.loc[cprr.uid == uid, col]
            if hasattr(v, 'shape'):
                v = v.iloc[0]
            cprr.loc[cprr.uid == al_uid, col] = v
    return cprr


def assign_uid_from_post(cprr, post):
    dfa = cprr.loc[cprr.uid.notna(), ['uid', 'first_name', 'last_name']].drop_duplicates(subset=['uid'])\
        .set_index('uid', drop=True)
    dfa.loc[:, 'fc'] = dfa.first_name.map(lambda x: x[:1])

    dfb = post[['uid', 'first_name', 'last_name']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfb.loc[:, 'fc'] = dfb.first_name.map(lambda x: x[:1])

    matcher = ThresholdMatcher(ColumnsIndex('fc'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.97
    matcher.save_pairs_to_excel(data_file_path(
        "match/new_orleans_so_cprr_officer_v_post_pprr_2020_11_06.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(decision)
    match_dict = dict(matches)

    cprr.loc[:, 'uid'] = cprr.uid.map(lambda x: match_dict.get(x, x))
    return cprr


def assign_supervisor_uid_from_post(cprr, post):
    dfa = cprr.loc[cprr.supervisor_first_name.notna(), ['supervisor_first_name', 'supervisor_last_name']]\
        .drop_duplicates()
    dfa = dfa.rename(columns={
        'supervisor_first_name': 'first_name',
        'supervisor_last_name': 'last_name'
    })
    dfa.loc[:, 'fc'] = dfa.first_name.map(lambda x: x[:1])

    dfb = post[['uid', 'first_name', 'last_name']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfb.loc[:, 'fc'] = dfb.first_name.map(lambda x: x[:1])

    matcher = ThresholdMatcher(ColumnsIndex('fc'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.95
    matcher.save_pairs_to_excel(data_file_path(
        "match/new_orleans_so_cprr_supervisor_v_post_pprr_2020_11_06.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(decision)
    match_dict = dict(matches)

    cprr.loc[:, 'supervisor_uid'] = cprr.index.map(
        lambda x: match_dict.get(x, ''))
    return cprr


if __name__ == '__main__':
    cprr = pd.read_csv(data_file_path('clean/cprr_new_orleans_so_2019.csv'))
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    post = post[post.agency == 'orleans parish so']
    ensure_data_dir('match')
    cprr = deduplicate_cprr_personnel(cprr)
    cprr = assign_uid_from_post(cprr, post)
    cprr = assign_supervisor_uid_from_post(cprr, post)
    cprr.to_csv(data_file_path(
        'match/cprr_new_orleans_so_2019.csv'), index=False)
