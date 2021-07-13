import sys
sys.path.append('../')
import pandas as pd
from lib.path import data_file_path, ensure_data_dir
from lib.columns import clean_column_names, set_values
from lib.clean import clean_dates, standardize_desc_cols
from lib.uid import gen_uid


def clean_names(df):
    df.name = df.name.str.lower().str.strip().str.replace(',', '').fillna('')\
        .str.replace('auzennejames', 'auzenne james', regex=False)\
        .str.replace('st.cyrneil', 'st.cyr neil', regex=False)\
        .str.replace('anceletjordan', 'ancelet jordan', regex=False)\
        .str.replace('suarezrichard', 'suarez richard')\
        .str.replace('file for records', '', regex=False)
    parts = df.name.str.extract(r'(?:(\w+|\w+\.\w+) )?(?:([^ ]+) )?(.*)')
    df.loc[:, 'last_name'] = parts[0]
    df.loc[:, 'middle_name'] = parts[1]
    df.loc[:, 'first_name'] = parts[2]
    return df.drop(columns='name')


def clean_complaint(df):
    df.loc[:, 'charges'] = df.complaint.str.lower().str.strip()\
        .str.replace(',', '', regex=False)\
        .str.replace(r'(^file for records ?(only)?)', '', regex=True)\
        .str.replace('unable to locate', '', regex=False)\
        .str.replace('with drew complaint', '', regex=False)\
        .str.replace(r'^courtesy/ identification$', 'courtesy/identification', regex=True)
    return df.drop(columns='complaint')


def clean_disposition(df):
    df.disposition = df.disposition.str.lower().str.strip()\
        .str.replace('non-sustained', 'unsustained', regex=False)\
        .str.replace(r'^policy fail$', 'policy failure', regex=True)\
        .str.replace(r'(^file for records ?(only)?)', '', regex=True)
    return df


def clean_action(df):
    df.loc[:, 'action'] = df.leave.str.lower().str.strip()\
        .str.replace(r'l?e?t\.', '', regex=True)\
        .str.replace('n/a', '', regex=False)\
        .str.replace(r' ?\.? ?rep', 'reprimand', regex=True)\
        .str.replace('verbalreprimand', 'verbal reprimand', regex=False)\
        .str.replace(r'^rem\.?(edial)? ?(train)?', 'remedial training', regex=True)\
        .str.replace('suspension', 'suspended', regex=False)\
        .str.replace('termination', 'terminated', regex=False)\
        .str.replace(r'^ ?counsel', 'counsel', regex=True)
    return df.drop(columns='leave')


def drop_rows_undefined_charges_and_disposition(df):
    return df[~((df.charges == '') & (df.disposition == ''))]


def clean_complete(df):
    df.loc[:, 'investigation_status'] = df.complete.str.lower().str.strip()\
        .str.replace('x', 'complete', regex=False)
    return df.drop(columns='complete')


def clean_days(df):
    df.loc[:, 'duration_of_action'] = df.days.str.lower().str.strip().fillna('')\
        .str.replace('1', '1 day', regex=False)\
        .str.replace('3', '3 days', regex=False)\
        .str.replace('inlieu', 'in lieu', regex=False)
    return df.drop(columns='days')


def clean():
    df = pd.read_csv(data_file_path('lafayette_so/lafayette_so_cprr_2015_2020.csv'))\
        .pipe(clean_column_names)
    df = df\
        .rename(columns={
            'case': 'tracking_number',
            'date': 'receive_date',
            'emp_assign': 'department_desc',
        })\
        .pipe(clean_names)\
        .pipe(clean_complaint)\
        .pipe(clean_dates, ['receive_date'])\
        .pipe(standardize_desc_cols, ['department_desc'])\
        .pipe(clean_disposition)\
        .pipe(drop_rows_undefined_charges_and_disposition)\
        .pipe(clean_action)\
        .pipe(clean_complete)\
        .pipe(clean_days)\
        .pipe(set_values, {
            'agency': 'Lafayette SO',
            'data_production_year': '2021',
        })\
        .pipe(gen_uid, ['first_name', 'last_name', 'agency'])\
        .pipe(gen_uid, ['uid', 'charges', 'action', 'tracking_number'], 'complaint_uid')
    return df


if __name__ == "__main__":
    df = clean()
    ensure_data_dir("clean")
    df.to_csv(
        data_file_path('clean/cprr_lafayette_so_2015_2020.csv'),
        index=False
    )
