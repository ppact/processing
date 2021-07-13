import re
import sys

import pandas as pd

from lib.columns import clean_column_names
from lib.path import data_file_path, ensure_data_dir
from lib.clean import clean_names, clean_dates, clean_salary, float_to_int_str, standardize_desc_cols
from lib.uid import gen_uid
from lib import salary
sys.path.append('../')


def parse_birthdate(df):
    df.loc[:, 'birth_date'] = pd.to_datetime(
        df.birth_date.str.replace(r'^(\d-.+)', r'0\1', regex=True)
        .str.replace(r'^`$', '', regex=True),
        errors='coerce',
        format='%d-%b-%y'
    ).map(lambda x: '' if pd.isnull(x) else x.strftime('%m/%d/%y'))
    return df


def split_rows(df):
    df.loc[:, 'hire_date_raw'] = df.hire_date_raw.fillna('').str.lower().str.replace(
        '\r\n2008 across the board raise', '', regex=False)\
        .str.split(r'\r\n')
    df.loc[:, 'salary_raw'] = df.salary_raw.str.lower().str.split(r'\r\n')
    records = []
    for _, row in df.iterrows():
        rec = row.to_dict()
        rec['hire_date_raw'] = row.hire_date_raw[0].strip()
        rec['salary_raw'] = row.salary_raw[0].strip()
        records.append(rec)
        if len(row.hire_date_raw) == 1 and len(row.salary_raw) == 1:
            continue
        rec = dict(list(rec.items()))
        rec['hire_date_raw'] = (row.hire_date_raw[0] if len(
            row.hire_date_raw) == 1 else row.hire_date_raw[1]).strip()
        rec['salary_raw'] = (row.salary_raw[0] if len(
            row.salary_raw) == 1 else row.salary_raw[1]).strip()
        records.append(rec)
    return pd.DataFrame.from_records(records)


def extract_employment_status(df):
    df.loc[:, 'employment_status'] = ''
    df.loc[df.hire_date_raw.str.match(
        r'full time'), 'employment_status'] = 'full-time'
    df.loc[df.hire_date_raw.str.match(
        r'reserve'), 'employment_status'] = 'reserve'
    df.loc[df.hire_date_raw.str.match(
        r'^(part time|pt)'), 'employment_status'] = 'part-time'
    df.loc[
        df.rank_desc.fillna('').str.lower().str.match(r'part-time'),
        'employment_status'] = 'part-time'
    df.loc[:, 'rank_desc'] = df.rank_desc.fillna('').str.lower()\
        .str.replace(r'part-time ', '', regex=False)
    return df


def extract_rank(df):
    for rank in ['officer', 'sergeant', 'captain', 'detective', 'deputy chief']:
        df.loc[df.rank_desc.isna() & (
            df.hire_date_raw.str.match(r'.*%s' % rank)), 'rank_desc'] = rank
    return df


def extract_hire_date(df):
    pat = re.compile(r'.* (\w+),? (\d+),? (\d+).*')
    df.loc[:, 'hire_date'] = df.hire_date_raw
    df.loc[df.hire_date_raw.str.match(pat), 'hire_date'] = pd.to_datetime(
        df.hire_date_raw.str.replace(pat, r'\1 \2, \3', regex=True),
        errors='coerce',
        format='%B %d, %Y'
    ).map(lambda x: '' if pd.isnull(x) else x.strftime('%m/%d/%Y'))
    return df.drop(columns=['hire_date_raw'])


def extract_pay_effective_date(df):
    pat = re.compile(r'(?:.* |^)(\w+)(?:,| |, )(\d+)(?:,| |, )(\d+).*')
    df.loc[:, 'pay_effective_date'] = pd.to_datetime(
        df.salary_raw.str.replace(pat, r'\1 \2, \3', regex=True),
        errors='coerce',
        format='%B %d, %Y'
    ).map(lambda x: '' if pd.isnull(x) else x.strftime('%m/%d/%Y'))
    df.loc[~df.salary_raw.str.match(pat), 'pay_effective_date'] = df.salary_raw\
        .str.extract(r'(?:.* |^)(\d{4}).+')[0]
    return df


def extract_salary(df):
    df.loc[:, 'salary'] = clean_salary(
        df.salary_raw
        .str.replace('$1 raise', '$10.50', regex=False)
        .str.extract(r'(\$\d{1,2}(?:\.\d{2})?)')[0])
    df.loc[:, 'salary_freq'] = salary.HOURLY
    return df.drop(columns=['salary_raw'])


def assign_agency(df):
    df.loc[:, 'data_production_year'] = 2021
    df.loc[:, 'agency'] = 'Grand Isle PD'
    return df


def clean():
    return pd.read_csv(data_file_path(
        'grand_isle/grand_isle_pd_pprr_2021_byhand.csv'
    ), encoding='latin-1')\
        .pipe(clean_column_names)\
        .rename(columns={
            'hire_date': 'hire_date_raw',
            'hourly_salary': 'salary_raw'
        })\
        .pipe(float_to_int_str, ['salary_raw'])\
        .pipe(clean_names, ['first_name', 'last_name'])\
        .pipe(parse_birthdate)\
        .pipe(clean_dates, ['birth_date'])\
        .pipe(assign_agency)\
        .pipe(gen_uid, ['agency', 'first_name', 'last_name', 'birth_year', 'birth_month', 'birth_day'])\
        .pipe(split_rows)\
        .pipe(extract_employment_status)\
        .pipe(extract_rank)\
        .pipe(extract_hire_date)\
        .pipe(extract_pay_effective_date)\
        .pipe(extract_salary)\
        .pipe(clean_dates, ['hire_date', 'pay_effective_date'])\
        .pipe(standardize_desc_cols, ['rank_desc'])


if __name__ == '__main__':
    df = clean()
    ensure_data_dir('clean')
    df.to_csv(data_file_path(
        'clean/pprr_grand_isle_pd_2021.csv'
    ), index=False)
