from lib.clean import names_to_title_case
import sys

import pandas as pd
from datamatch import ThresholdMatcher, JaroWinklerSimilarity, ColumnsIndex, NoopIndex

from lib.path import data_file_path, ensure_data_dir
from lib.post import extract_events_from_post

sys.path.append('../')


def dedup_cprr_uid(cprr):
    df = cprr[['first_name', 'last_name', 'uid']].drop_duplicates()\
        .set_index('uid', drop=True)
    matcher = ThresholdMatcher(NoopIndex(), {
        'first_name': JaroWinklerSimilarity(0.2),
        'last_name': JaroWinklerSimilarity(),
    }, df)
    decision = 0.89
    matcher.save_clusters_to_excel(data_file_path(
        "match/lafayette_pd_cprr_2015_2020_officer_dedup.xlsx"
    ), decision, lower_bound=decision)
    clusters = matcher.get_index_clusters_within_thresholds(lower_bound=decision)

    for cluster in clusters:
        uid, first_name, last_name = None, '', ''
        for idx in cluster:
            row = df.loc[idx]
            if (
                uid is None
                or len(row.first_name) > len(first_name)
                or (len(row.first_name) == len(first_name) and len(row.last_name) > len(last_name))
            ):
                uid, first_name, last_name = idx, row.first_name, row.last_name
        cprr.loc[cprr.uid.isin(cluster), 'uid'] = uid
        cprr.loc[cprr.uid == uid, 'first_name'] = first_name
        cprr.loc[cprr.uid == uid, 'last_name'] = last_name

    return cprr


def dedup_cprr_investigator_uid(cprr):
    # match rows with both first_name and last_name
    df = cprr[['investigator_first_name', 'investigator_last_name', 'investigator_uid']].drop_duplicates()\
        .set_index('investigator_uid', drop=True)
    matcher = ThresholdMatcher(NoopIndex(), {
        'investigator_first_name': JaroWinklerSimilarity(),
        'investigator_last_name': JaroWinklerSimilarity(),
    }, df)
    decision = 0.87
    matcher.save_clusters_to_excel(data_file_path(
        "match/lafayette_pd_cprr_2015_2020_investigator_dedup.xlsx"
    ), decision, lower_bound=decision)
    clusters = matcher.get_index_clusters_within_thresholds(lower_bound=decision)
    for cluster in clusters:
        uid, first_name, last_name = None, '', ''
        for idx in cluster:
            row = df.loc[idx]
            if (
                uid is None
                or len(row.investigator_first_name) > len(first_name)
                or (len(row.investigator_first_name) == len(first_name)
                    and len(row.investigator_last_name) > len(last_name))
            ):
                uid, first_name, last_name = idx, row.investigator_first_name, row.investigator_last_name
        cprr.loc[cprr.investigator_uid.isin(cluster), 'investigator_uid'] = uid
        cprr.loc[cprr.investigator_uid == uid, 'investigator_first_name'] = first_name
        cprr.loc[cprr.investigator_uid == uid, 'investigator_last_name'] = last_name

    # match rows with only last_name against rows with both
    dfa = cprr.loc[
        cprr.investigator_first_name.isna(),
        ['investigator_first_name', 'investigator_last_name', 'investigator_uid'],
    ].drop_duplicates().set_index('investigator_uid', drop=True)
    dfb = cprr.loc[
        cprr.investigator_first_name.notna(),
        ['investigator_first_name', 'investigator_last_name', 'investigator_uid'],
    ].drop_duplicates().set_index('investigator_uid', drop=True)
    matcher = ThresholdMatcher(NoopIndex(), {
        'investigator_last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.87
    matcher.save_pairs_to_excel(data_file_path(
        "match/lafayette_pd_cprr_2015_2020_investigator_only_last_name_dedup.xlsx"
    ), decision)
    matches = matcher.get_index_pairs_within_thresholds(decision)
    for uid_a, uid_b in matches:
        row = cprr.loc[cprr.investigator_uid == uid_b].iloc[0]
        cprr.loc[cprr.investigator_uid == uid_a, 'investigator_first_name'] = row.investigator_first_name
        cprr.loc[cprr.investigator_uid == uid_a, 'investigator_last_name'] = row.investigator_last_name
        cprr.loc[cprr.investigator_uid == uid_a, 'investigator_uid'] = uid_b

    return cprr


def combine_investigator_name(cprr):
    cols = ['investigator_first_name', 'investigator_last_name']
    names = names_to_title_case(cprr[cols], cols)
    cprr.loc[:, 'investigator'] = names.investigator_first_name.fillna('')\
        .str.cat(names.investigator_last_name, sep=' ')\
        .str.strip()
    return cprr


def match_cprr_officers_with_pprr(cprr, pprr):
    dfa = cprr[['first_name', 'last_name', 'uid']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfb = pprr[['first_name', 'last_name', 'uid']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])

    matcher = ThresholdMatcher(ColumnsIndex('fc'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.87
    matcher.save_pairs_to_excel(data_file_path(
        "match/lafayette_pd_cprr_2015_2020_officers_v_pprr_2010_2021.xlsx"
    ), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)

    for uid_a, uid_b in matches:
        row = pprr.loc[pprr.uid == uid_b].iloc[0]
        cprr.loc[cprr.uid == uid_a, 'first_name'] = row.first_name
        cprr.loc[cprr.uid == uid_a, 'last_name'] = row.last_name
        cprr.loc[cprr.uid == uid_a, 'uid'] = uid_b
    return cprr


def match_cprr_investigators_with_pprr(cprr, pprr):
    dfa = cprr[['investigator_first_name', 'investigator_last_name', 'investigator_uid']]\
        .drop_duplicates().set_index('investigator_uid', drop=True)
    dfa = dfa.rename(columns={
        'investigator_first_name': 'first_name',
        'investigator_last_name': 'last_name'
    })
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])

    dfb = pprr[['first_name', 'last_name', 'uid']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])

    matcher = ThresholdMatcher(ColumnsIndex('fc'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.8
    matcher.save_pairs_to_excel(data_file_path(
        "match/lafayette_pd_cprr_2015_2020_investigators_v_pprr_2010_2021.xlsx"
    ), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)

    for uid_a, uid_b in matches:
        row = pprr.loc[pprr.uid == uid_b].iloc[0]
        cprr.loc[cprr.investigator_uid == uid_a, 'investigator_first_name'] = row.first_name
        cprr.loc[cprr.investigator_uid == uid_a, 'investigator_last_name'] = row.last_name
        cprr.loc[cprr.investigator_uid == uid_a, 'investigator_uid'] = uid_b
    return cprr


def extract_post_events(pprr, post):
    post = post.loc[post.agency == 'lafayette pd']

    dfa = pprr[['first_name', 'last_name', 'uid']]
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfa = dfa.drop_duplicates().set_index('uid', drop=True)

    dfb = post[['last_name', 'first_name', 'uid']]
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])
    dfb = dfb.drop_duplicates(subset=['uid']).set_index('uid', drop=True)

    matcher = ThresholdMatcher(ColumnsIndex(['fc']), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.94
    matcher.save_pairs_to_excel(data_file_path(
        "match/lafayette_pd_pprr_2010_2021_v_post_pprr_2020_11_06.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)

    return extract_events_from_post(post, matches, "Lafayette PD")


if __name__ == '__main__':
    cprr = pd.read_csv(data_file_path(
        'clean/cprr_lafayette_pd_2015_2020.csv'
    ))
    pprr = pd.read_csv(data_file_path(
        'clean/pprr_lafayette_pd_2010_2021.csv'
    ))
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    ensure_data_dir('match')
    cprr = dedup_cprr_uid(cprr)\
        .pipe(dedup_cprr_investigator_uid)\
        .pipe(match_cprr_officers_with_pprr, pprr)\
        .pipe(match_cprr_investigators_with_pprr, pprr)\
        .pipe(combine_investigator_name)
    post_events = extract_post_events(pprr, post)
    cprr.to_csv(data_file_path(
        'match/cprr_lafayette_pd_2015_2020.csv'
    ), index=False)
    post_events.to_csv(data_file_path(
        "match/post_event_lafayette_pd_2020.csv"
    ), index=False)
