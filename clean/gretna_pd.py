import sys

import pandas as pd

from lib.columns import clean_column_names, set_values
from lib.path import data_file_path, ensure_data_dir
from lib.clean import clean_names, clean_salaries, clean_dates, standardize_desc_cols
from lib.uid import gen_uid
from lib import salary

sys.path.append('../')


def split_names(df):
    names = df.name.fillna('').str.lower().str.strip()\
        .str.replace(r',? (iii|iv|v|jr\.?),?', r' \1,', regex=True)\
        .str.replace(r' +\.$', '', regex=True)\
        .str.replace(r'(\w{3,})\. (\w+)', r'\1, \2', regex=True)\
        .str.extract(r'^([^,]+), (\w+)(?: (\w+))?$')
    df.loc[:, 'first_name'] = names[1]
    df.loc[:, 'middle_name'] = names[2]
    df.loc[:, 'last_name'] = names[0]
    df.loc[:, 'middle_initial'] = names[2].fillna('').map(lambda x: x[:1])
    return df[df.name.notna()].reset_index(drop=True).drop(columns=['name'])


def assign_agency(df):
    df.loc[:, 'data_production_year'] = 2018
    df.loc[:, 'agency'] = 'Gretna PD'
    return df


def clean_rank_desc(df):
    df.rank_desc = df.rank_desc.str.lower().str.strip()\
        .str.replace(r' \(d.\)$', '', regex=True)\
        .str.replace(r'sergeant ?(officer)?', 'sargeant', regex=True)
    return df


def clean():
    return pd.read_csv(data_file_path(
        'gretna_pd/gretna_pd_pprr_2018.csv'
    )).pipe(clean_column_names)\
        .rename(columns={
            'rank': 'rank_desc',
            '2018_salary': 'salary',
        })\
        .pipe(set_values, {'salary_freq': salary.YEARLY})\
        .pipe(split_names)\
        .pipe(clean_names, ['first_name', 'middle_name', 'last_name'])\
        .pipe(clean_salaries, ['salary'])\
        .pipe(clean_dates, ['hire_date'])\
        .pipe(standardize_desc_cols, ['rank_desc'])\
        .pipe(clean_rank_desc)\
        .pipe(assign_agency)\
        .pipe(gen_uid, ['agency', 'first_name', 'middle_name', 'last_name'])


if __name__ == '__main__':
    df = clean()
    ensure_data_dir('clean')
    df.to_csv(data_file_path(
        'clean/pprr_gretna_pd_2018.csv'
    ), index=False)
