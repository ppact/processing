import sys

from datamatch import ThresholdMatcher, JaroWinklerSimilarity, ColumnsIndex
import pandas as pd

from lib.path import data_file_path, ensure_data_dir
from lib.post import extract_events_from_post

sys.path.append('../')


def match_pprr_post(pprr, post):
    dfa = pprr[['first_name', 'last_name', 'uid']]
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfa = dfa.drop_duplicates().set_index('uid', drop=True)

    dfb = post[['first_name', 'last_name', 'uid']]
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])
    dfb = dfb.drop_duplicates().set_index('uid', drop=True)

    matcher = ThresholdMatcher(ColumnsIndex(['fc']), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = 0.9
    matcher.save_pairs_to_excel(data_file_path(
        "match/grand_isle_pd_pprr_2021_v_post.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)
    return extract_events_from_post(post, matches, 'Grand Isle PD')


if __name__ == '__main__':
    pprr = pd.read_csv(data_file_path('clean/pprr_grand_isle_pd_2021.csv'))
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    post = post[post.agency == 'grand isle pd']
    post_event = match_pprr_post(pprr, post)
    ensure_data_dir('match')
    post_event.to_csv(data_file_path(
        'match/post_event_grand_isle_pd.csv'), index=False)
