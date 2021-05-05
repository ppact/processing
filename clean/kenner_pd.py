from lib.columns import clean_column_names
from lib.path import data_file_path, ensure_data_dir
from lib.clean import clean_names, standardize_desc_cols, clean_dates
import pandas as pd
import sys
sys.path.append('../')


def assign_agency(df):
    df.loc[:, 'data_production_year'] = 2020
    df.loc[:, 'agency'] = 'Kenner PD'
    return df


def split_names(df):
    df.loc[:, 'name'] = df.name.str.strip()
    names = df.name.str.replace(r', ?(Jr\.|III),?', r' \1,', regex=True)\
        .str.lower().str.replace(r' (\w)\.', r' \1')\
        .str.extract(r'^([^,]+), (jo ann|[\w-]+)(?: (.+))?$')
    df.loc[:, 'last_name'] = names[0]
    df.loc[:, 'first_name'] = names[1]
    df.loc[:, 'middle_name'] = names[2]
    df.loc[:, 'middle_initial'] = names[2].fillna('').map(lambda x: x[:1])
    df = df.loc[(df.name != 'unknown') & df.name.notna()]
    # there's already a "Gregory, Jan-Michael" so this row is probably redundant
    df = df.loc[df.name != 'gregory, Jan Michael']
    return df.reset_index(drop=True)


def clean():
    return pd.read_csv(data_file_path(
        'kenner_pd/kenner_pd_pprr_2020.csv'
    ))\
        .pipe(clean_column_names)\
        .rename(columns={
            'id_no': 'employee_id',
            'rank': 'rank_desc',
            'division': 'department_desc',
            'date_hired': 'hire_date',
            'work_classification': 'employment_status',
            'status': 'officer_inactive',
        })\
        .drop(columns=['years_with_dept'])\
        .pipe(clean_employee_id)\
        .pipe(assign_agency)\
        .pipe(split_names)\
        .drop(columns=['name'])\
        .pipe(clean_names, ['first_name', 'last_name', 'middle_name', 'middle_initial'])\
        .pipe(standardize_desc_cols, [
            'gender', 'department_desc', 'rank_desc', 'employment_status', 'officer_inactive', 'sworn'])\
        .pipe(clean_dates, ['hire_date'])


def drop_volunteers(df):
    df = df[df.employee_class != 'volunteer']
    return df.reset_index(drop=True)


def clean_employee_id(df):
    df.loc[:, 'employee_id'] = df.employee_id.str.strip()
    return df


def remove_mr_and_ms_as_rank(df):
    df.loc[:, 'rank_desc'] = df.rank_desc.str.replace(
        r'^(mr|ms|mrs)\.?$', '', regex=True)
    return df


def clean_former_long():
    return pd.read_csv(data_file_path(
        'kenner_pd/kenner_pd_pprr_formeremployees_long.csv'
    ))\
        .pipe(clean_column_names)\
        .rename(columns={
            'title': 'rank_desc',
            'lnam': 'last_name',
            'fnam': 'first_name',
            'hired': 'hire_date',
            'compid': 'employee_id',
            'classifica': 'employee_class'
        })\
        .pipe(clean_names, ['first_name', 'last_name'])\
        .pipe(standardize_desc_cols, ['rank_desc', 'employee_class'])\
        .pipe(clean_employee_id)\
        .pipe(clean_dates, ['hire_date'])


def clean_former_short():
    return pd.read_csv(data_file_path(
        'kenner_pd/kenner_pd_pprr_formeremployees_short.csv'
    )).pipe(clean_column_names)\
        .rename(columns={
            'date_hired': 'hire_date',
            'date_left': 'left_date',
            'division': 'department_desc',
            'rank': 'rank_desc',
            'id_no': 'employee_id'
        })\
        .pipe(clean_employee_id)\
        .drop(columns=['gone', 'reason_left'])\
        .pipe(assign_agency)\
        .pipe(split_names)\
        .drop(columns=['name'])\
        .pipe(clean_names, ['first_name', 'last_name', 'middle_name', 'middle_initial'])\
        .pipe(standardize_desc_cols, ['department_desc', 'rank_desc', 'gender'])\
        .pipe(clean_dates, ['hire_date', 'left_date'])


def combine_pprrs(pprr, former_long, former_short):
    records = pprr.set_index("employee_id", drop=False).to_dict('index')
    for other_df in [former_long, former_short]:
        for idx, row in other_df.set_index("employee_id", drop=False).iterrows():
            if idx in records:
                record = records[idx]
                for k, v in row.to_dict().items():
                    if v == '' or pd.isnull(v):
                        continue
                    if k in record and pd.notnull(record[k]) and record[k] != '':
                        continue
                    record[k] = v
            else:
                records[idx] = row.to_dict()
    return pd.DataFrame.from_records(list(records.values()))


if __name__ == '__main__':
    df = clean()
    ensure_data_dir('clean')
    df.to_csv(data_file_path(
        'clean/pprr_kenner_pd_2020.csv'
    ), index=False)