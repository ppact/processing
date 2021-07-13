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
    matcher.save_pairs_to_excel(
        data_file_path('match/tangipahoa_so_cprr_2015_2021_deduplicate.xlsx'), decision
    )
    matches = matcher.get_index_pairs_within_thresholds(decision)
    match_dict = dict(matches)

    cprr.loc[:, 'uid'] = cprr.uid.map(lambda x: match_dict.get(x, x))
    cprr = cprr.sort_values(['uid', 'first_name', 'last_name'], ascending=[True, False, False])
    names = dict()
    for idx, row in cprr.iterrows():
        if row.uid in names:
            cprr.loc[idx, 'first_name'], cprr.loc[idx, 'last_name'] = names[row.uid]
        else:
            names[row.uid] = (row.first_name, row.last_name)
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
