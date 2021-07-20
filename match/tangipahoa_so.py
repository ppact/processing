import sys
sys.path.append('../')
import pandas as pd
from datamatch import ThresholdMatcher, JaroWinklerSimilarity, ColumnsIndex
from lib.path import data_file_path, ensure_data_dir


def prepare_post_data():
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    return post[post.agency == 'tangipahoa parish so']


def deduplicate_cprr_officers(cprr):
    df = cprr[['uid', 'first_name', 'last_name', 'rank_desc']]
    df = df.drop_duplicates(subset=['uid']).set_index('uid')
    df.loc[:, 'fc'] = df.first_name.fillna('').map(lambda x: x[:1])
    matcher = ThresholdMatcher(ColumnsIndex('fc'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, df)
    decision = .866
    matcher.save_clusters_to_excel(data_file_path(
        'match/tangipahoa_so_cprr_2015_2021_deduplicate.xlsx'
    ), decision, decision)
    clusters = matcher.get_index_clusters_within_thresholds(decision)
    # canonicalize name and uid
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


def match_cprr_post(cprr, post):
    dfa = cprr[['uid', 'first_name', 'last_name']]
    dfa = dfa.drop_duplicates(subset=['uid']).set_index('uid')
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])

    dfb = post[['uid', 'first_name', 'last_name']]
    dfb = dfb.drop_duplicates(subset=['uid']).set_index('uid')
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])

    matcher = ThresholdMatcher(ColumnsIndex('fc'), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = .873
    matcher.save_pairs_to_excel(
        data_file_path('match/tangipahoa_so_cprr_2015_2021_v_pprr_post_2020_11_06.xlsx'), decision)
    matches = matcher.get_index_pairs_within_thresholds(decision)
    match_dict = dict(matches)

    cprr.loc[:, 'uid'] = cprr.uid.map(lambda x: match_dict.get(x, x))
    return cprr


if __name__ == '__main__':
    cprr = pd.read_csv(data_file_path('clean/cprr_tangipahoa_so_2015_2021.csv'))
    cprr = deduplicate_cprr_officers(cprr)
    post = prepare_post_data()
    cprr = match_cprr_post(cprr, post)
    ensure_data_dir('match')
    cprr.to_csv(data_file_path(
        'match/cprr_tangipahoa_so_2015_2021.csv'
    ), index=False)
