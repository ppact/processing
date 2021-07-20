import sys

import pandas as pd

from lib.columns import clean_column_names, set_values
from lib.path import data_file_path, ensure_data_dir
from lib.clean import (
    clean_names, clean_salaries, clean_sexes, clean_races, float_to_int_str
)
from lib.uid import gen_uid
from lib import salary
from lib.standardize import standardize_from_lookup_table

sys.path.append('../')


def split_names(df):
    names = df.name.str.strip().str.lower()\
        .str.replace(r'^(.+), pete,', r'pete, \1,', regex=True)\
        .str.replace(r'^(\w) (\w{3,}),(.+)', r'\2,\3, \1', regex=True)\
        .str.replace(r'^(\w+) (\w), (\w+)$', r'\1, \3, \2', regex=True)\
        .str.replace(r'^(\w+), (\w+) (\w)$', r'\1, \2, \3', regex=True)\
        .str.replace(r'^(\w+) (\w{2}), (\w+)$', r'\1, \3 \2', regex=True)\
        .str.extract(r'^(\w+), ([^,]+)(?:, ([^ ]+))?$')
    df.loc[:, 'last_name'] = names[1]
    df.loc[:, 'first_name'] = names[0]
    df.loc[:, 'middle_initial'] = names[2]
    return df[df.name.notna()].drop(columns=['name'])


def standardize_rank(df):
    df.loc[:, 'rank_desc'] = df.rank_desc.str.lower().str.strip()\
        .str.replace(r'\bdept\b', 'department', regex=True)\
        .str.replace(r'\brec\b', 'records', regex=True)\
        .str.replace('-level ', ' ', regex=False)\
        .str.replace(r'\bcomm\b', 'communications', regex=True)\
        .str.replace(r'\bsupv\b', 'supervisor', regex=True)\
        .str.replace(r'\badmin\b', 'administrative', regex=True)\
        .str.replace(r'\basst\b', 'assistant', regex=True)\
        .str.replace(r'\baccredi?ation\b', 'accreditation', regex=True)\
        .str.replace('/', ' to ', regex=False)
    return df


def clean_pprr():
    return pd.read_csv(data_file_path(
        'lafayette_pd/lafayette_pd_pprr_2010_2021.csv'
    )).pipe(clean_column_names)\
        .drop(columns=['assigned_zone', 'badge_number'])\
        .rename(columns={
            'gender': 'sex',
            'year_of_birth': 'birth_year',
            'rank': 'rank_desc',
            'date_of_termination': 'left_date',
            'date_of_hire': 'hire_date',
        })\
        .pipe(clean_sexes, ['sex'])\
        .pipe(clean_races, ['race'])\
        .pipe(clean_salaries, ['salary'])\
        .pipe(set_values, {
            'salary_freq': salary.YEARLY,
            'data_production_year': '2021',
            'agency': 'Lafayette PD'
        })\
        .pipe(float_to_int_str, ['birth_year'])\
        .pipe(standardize_rank)\
        .pipe(split_names)\
        .pipe(clean_names, ['first_name', 'last_name', 'middle_initial'])\
        .pipe(gen_uid, ['agency', 'first_name', 'last_name', 'middle_initial'])


def clean_tracking_number(df):
    df.loc[:, 'tracking_number'] = df.tracking_number.str.strip()\
        .str.replace(' ', '', regex=False)
    return df[df.tracking_number != '\x1a'].reset_index(drop=True)


def split_rows_with_multiple_officers(df):
    df.loc[:, 'officer'] = df.officer.str.lower().str.strip()\
        .str.replace(r'\.(\w)', r'. \1', regex=True)\
        .str.replace(r'- +', r'-', regex=True)\
        .str.replace('reserve officer', 'reserve-officer', regex=False)

    # split rows where officers are clearly delineated
    for pat in [
        r', *', r'/ *', r' (?=\w{3}\.)', r'; *'
    ]:
        df = df.set_index([col for col in df.columns if col != 'officer'])\
            .officer.str.split(pat=pat, expand=True).stack()\
            .reset_index(drop=False)\
            .drop(columns=['level_6'])\
            .rename(columns={0: 'officer'})

    # split rows where there are no token to split
    pat = r'^(.*[^ ]+ [^ ]+) ([^ ]+ [^ ]+)$'
    rows = df\
        .set_index([col for col in df.columns if col != 'officer'])\
        .officer.str.extract(pat).stack()\
        .reset_index(drop=False)\
        .drop(columns=['level_6'])\
        .rename(columns={0: 'officer'})
    return pd.concat([
        df[~df.officer.str.match(pat)],
        rows,
    ]).sort_values('tracking_number').reset_index(drop=True)


def extract_rank(df):
    df.loc[:, 'officer'] = df.officer.str.lower().str.strip()\
        .str.replace(r'^and +', '', regex=True)\
        .str.replace(r'^cpl\.? ', 'corporal ', regex=True)\
        .str.replace(r'^det\.? ', 'detective ', regex=True)\
        .str.replace(r'^sgt\.? ', 'sergeant ', regex=True)\
        .str.replace(r'^lt\.? ', 'lieutenant ', regex=True)\
        .str.replace(r'^po ', 'officer ', regex=True)\
        .str.replace(r'^capt\.? ', 'captain ', regex=True)\
        .str.replace(r'^off\.? ', 'officer ', regex=True)\
        .str.replace(r'^officers ', 'officer ', regex=True)\
        .str.replace('reserve-officer', 'reserve officer', regex=False)

    ranks = [
        'corporal', 'sergeant', 'lieutenant', 'officer', 'captain', 'reserve officer',
        'pco', 'detective'
    ]
    rank_name = df.officer.str.extract(r'^(?:(%s) )?(.+)' % '|'.join(ranks))
    df.loc[:, 'rank_desc'] = rank_name[0]
    df.loc[:, 'name'] = rank_name[1]
    return df[df.name != 'and'].drop(columns=['officer'])


def split_cprr_name(df):
    names = df.name.str.strip()\
        .str.replace('unknown', '', regex=False)\
        .str.replace(' (3d)', '', regex=False)\
        .str.extract(r'^(?:([^ ]+) )?([^ ]+)$')
    df.loc[:, 'first_name'] = names[0]
    df.loc[:, 'last_name'] = names[1]
    return df.drop(columns=['name'])


def split_investigator(df):
    df.loc[:, 'investigator'] = df.investigator.str.lower().str.strip()\
        .str.replace(r'^det\. ?', 'detective ', regex=True)\
        .str.replace(r'^lt\. ?', 'lieutenant ', regex=True)\
        .str.replace(r'^sgt\. ?', 'sergeant ', regex=True)\
        .str.replace(r'^capt\. ?', 'captain ', regex=True)

    ranks = [
        'detective', 'lieutenant', 'sergeant', 'captain', 'major'
    ]
    parts = df.investigator.str.extract(r'^(?:(%s) )?(?:([^ ]+) )?([^ ]+)$' % '|'.join(ranks))
    df.loc[:, 'investigator_rank'] = parts[0]
    df.loc[:, 'investigator_first_name'] = parts[1]
    df.loc[:, 'investigator_last_name'] = parts[2]
    return df


def lower_strip(df, cols):
    for col in cols:
        df.loc[:, col] = df[col].str.lower().str.strip()
    return df


def split_disposition(df):
    # splitting for 'AD2015-005': 'sustained-benoit-3 days, all others letter of reprimand'
    df.loc[
        (df.tracking_number == 'AD2015-005') & (df.last_name == 'benoit'),
        'disposition',
    ] = 'sustained-3 days'
    df.loc[
        (df.tracking_number == 'AD2015-005') & (df.last_name != 'benoit'),
        'disposition',
    ] = 'sustained-letter of reprimand'

    # splitting for 'AD2015-015': 'sustained- bajat- loc; allred- counseling form'
    df.loc[
        (df.tracking_number == 'AD2015-015') & (df.last_name == 'bajat'),
        'disposition',
    ] = 'sustained-loc'
    df.loc[
        (df.tracking_number == 'AD2015-015') & (df.last_name != 'allred'),
        'disposition',
    ] = 'sustained-counseling form'

    # 'AD2019-004': 'excessive force - not sustained att. to duty - sustained/deficiency'
    df.loc[
        (df.tracking_number == 'AD2019-004') & (df.allegation == 'excessive force'),
        'disposition',
    ] = 'not sustained'
    df.loc[
        (df.tracking_number == 'AD2019-004') & (df.allegation != 'attention to duty'),
        'disposition',
    ] = 'sustained/deficiency'

    # 'AD2019-005': 'terminated - trent (overturned - 10 days) kyle 3 days susp.'
    df.loc[
        (df.tracking_number == 'AD2019-005') & (df.first_name == 'trent'),
        'disposition',
    ] = '10 days'
    df.loc[
        (df.tracking_number == 'AD2019-005') & (df.first_name != 'kyle'),
        'disposition',
    ] = '3 days susp'

    # 'CC1801': 'thibodeaux - counseling form; brasseaux - counseling form'
    df.loc[
        (df.tracking_number == 'CC1801') & (
            (df.last_name == 'thibodeaux') | (df.last_name == 'brasseaux')
        ),
        'disposition',
    ] = 'counseling form'
    df.loc[
        (df.tracking_number == 'CC1801') & ~(
            (df.last_name == 'thibodeaux') | (df.last_name == 'brasseaux')
        ),
        'disposition',
    ] = ''

    return df


def clean_cprr_dates(df):
    df.loc[:, 'complete_date'] = df.complete_date.str.strip()\
        .str.replace('2B', '28', regex=False)\
        .str.replace(r'/(\d)(\d{2})$', r'/\1/\2', regex=True)\
        .str.replace(r'/(1\d$)', r'/20\1', regex=True)
    df.loc[:, 'receive_date'] = df.receive_date.str.strip()\
        .str.replace('i', '/', regex=False)
    return df


def clean_cprr():
    return pd.read_csv(data_file_path(
        'lafayette_pd/lafayette_pd_cprr_2015_2020.csv'
    )).pipe(clean_column_names)\
        .dropna(how='all')\
        .rename(columns={
            'cc_number': 'tracking_number',
            'complaint': 'allegation',
            'date_received': 'receive_date',
            'date_completed': 'complete_date',
            'assigned_investigator': 'investigator',
            'focus_officer_s': 'officer',
        })\
        .pipe(clean_tracking_number)\
        .pipe(split_rows_with_multiple_officers)\
        .pipe(extract_rank)\
        .pipe(split_cprr_name)\
        .pipe(split_investigator)\
        .pipe(clean_cprr_dates)\
        .pipe(lower_strip, ['allegation', 'disposition'])\
        .pipe(standardize_from_lookup_table, 'allegation', [
            ['attention to duty', 'att. to duty', 'attention', 'atd'],
            ['professional conduct', 'prof. conduct', 'prof conduct', 'pc'],
            ['violation of pursuit policy', 'pursuit violation', 'pursuit policy'],
            ['rude and unprofessional', 'rude & unprofessional', 'rude/unprofessi onal', 'unprof'],
            ['excessive force'],
            ['cubo'],
            ['bwc'],
            ['untruthful'],
            ['tech management'],
            ['lt. scott morgan'],
            ['use of force'],
            ['disobey direct order', 'disobeyed direct order'],
            ['vehicle crashes', 'vehicle crash'],
            ['accident review'],
            ['failure to report accident'],
            ['handling of evidence'],
            ['vehicle pursuit'],
            ['social media'],
            ['insubordination'],
            ['arrest'],
            ['misappropriation of funds'],
            ['threats'],
            ['officer involved shooting'],
            ['racial profiling'],
            ['substance abuse policy'],
            ['off duty security'],
            ['general conduct fighting'],
            ['criminal violation'],
            [
                'professional conduct and responsibilities', 'professional conduct & resp.',
                'professional conduct  & responsibilities', 'prof. conduct & resp.',
                'prof. conduct & responsibilities',
            ],
            ['residency requirement'],
            ['theft'],
            ['late reports'],
            ['oen conduct sick leave'],
            ['falsifying records'],
            ['drug policy'],
            ['managing recovered, found, or seized property', 'managing recovered property'],
            ['failure to supervise'],
            ['civil rights violation'],
            ['failed to attend inservice'],
            ['ois'],
            ['reckless driving', 'speeding'],
            ['operation of police vehicle'],
            ['destruction of evidence'],
            ['violation of informant policy'],
            ['policy nol.'],
            ['reports'],
            ['rumors'],
        ]).pipe(split_disposition)\
        .pipe(standardize_from_lookup_table, 'disposition', [
            ['sustained', 'sust.'],
            ['not sustained'],
            ['unfounded'],
            ['exonerated'],
            ['justified use of force', 'justified uof', 'j.u.f.'],
            ['letter of reprimand', 'lor'],
            ['letter of counseling'],
            ['letter of caution', 'loc'],
            ['termination', 'terminated'],
            ['training issue', 'trainin g issue'],
            ['counseling form', 'cf', 'c.f.'],
            ['suspension 1 day', '1 day suspension', '1 day'],
            ['suspension 2 days', '2 day sus'],
            ['suspension 3 days', '3 days', '3 days susp'],
            ['suspension 5 days', 'suspended 5 days', '5 day suspension', '5 days'],
            ['suspension 7 days', '7 day sus'],
            ['suspension 10 days', '10 day sus', '10 days'],
            ['suspension 14 days', '14 day suspension'],
            ['suspension 30 days', '3oday', '30 days'],
            ['suspension 45 days', '45'],
            ['suspension 60 days', '60 day suspension'],
            ['suspension 90 days', '90 suspension'],
            ['suspension', 'sus'],
            ['6 months probation', '6months probation'],
            ['sensitivity training'],
            ['1 year no vehicle'],
            ['40 hours driving course', '40 hr. driving course'],
            ['resigned', 'res.', 'res'],
            ['justified'],
            ['retired'],
            ['deficiency', 'def.'],
            ['excessive force'],
            ['cubo'],
            ['eap'],
            ['disobey direct order'],
            ['terminated overturned by civil service'],
            ['demotion', 'demontion'],
            ['performance log'],
            ['justified shooting'],
            ['counseling form for not using necessary force'],
            ['complaint withdrawn', 'withdrawn'],
            ['bwc'],
            ['special evaluation', 'special eval'],
            ['proffessional conduct', 'prof conduct'],
            ['evidence'],
        ]).pipe(set_values, {
            'data_production_year': 2020,
            'agency': 'Lafayette PD'
        }).pipe(clean_names, ['first_name', 'last_name', 'investigator_first_name', 'investigator_last_name'])\
        .pipe(gen_uid, ['agency', 'first_name', 'last_name'])\
        .pipe(gen_uid, ['agency', 'investigator_first_name', 'investigator_last_name'], 'investigator_uid')\
        .pipe(gen_uid, ['agency', 'tracking_number', 'allegation', 'uid'], 'complaint_uid')


if __name__ == '__main__':
    pprr = clean_pprr()
    cprr = clean_cprr()
    ensure_data_dir('clean')
    cprr.to_csv(data_file_path(
        'clean/cprr_lafayette_pd_2015_2020.csv'
    ), index=False)
    pprr.to_csv(data_file_path(
        'clean/pprr_lafayette_pd_2010_2021.csv'
    ), index=False)
