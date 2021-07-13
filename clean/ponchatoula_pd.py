import sys

import pandas as pd

from lib.columns import clean_column_names, set_values
from lib.clean import clean_dates, clean_names, clean_salaries, clean_sexes, standardize_desc_cols
from lib.path import data_file_path, ensure_data_dir
from lib.uid import gen_uid

sys.path.append('../')


def clean():
    return pd.read_csv(data_file_path(
        'ponchatoula_pd/ponchatoula_pd_pprr_2010_2020.csv'
    )).pipe(clean_column_names)\
        .drop(columns=['class', 'status_code'])\
        .rename(columns={
            'employee': 'employee_id',
            'middle_init': 'middle_initial',
            'regular_rate': 'salary',
            'work_center': 'department_desc',
        })\
        .pipe(clean_names, ['first_name', 'middle_initial', 'last_name'])\
        .pipe(clean_salaries, ['salary'])\
        .pipe(standardize_desc_cols, ['salary_freq', 'department_desc'])\
        .pipe(clean_sexes, ['sex'])\
        .pipe(clean_dates, ['hire_date'])\
        .pipe(set_values, {
            'data_production_year': '2020',
            'agency': 'Ponchatoula PD'
        })\
        .pipe(gen_uid, ['agency', 'employee_id'])


if __name__ == '__main__':
    df = clean()
    ensure_data_dir('clean')
    df.to_csv(data_file_path(
        'clean/pprr_ponchatoula_pd_2010_2020.csv'
    ), index=False)
