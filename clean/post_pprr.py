from lib.columns import clean_column_names
from lib.path import data_file_path, ensure_data_dir
from lib.clean import (
    clean_names, clean_dates, standardize_desc_cols
)
from lib.uid import gen_uid
import pandas as pd
import sys
sys.path.append("../")


def standardize_agency(df):
    df.loc[:, "agency"] = df.agency.str.strip()\
        .str.lower().fillna("").str.replace(r"(\w)\.\s*(\w)\.", r"\1\2")
    return df


def replace_impossible_dates(df):
    df.loc[:, "level_1_cert_date"] = df.level_1_cert_date.str.replace(
        "3201", "2013", regex=False)
    return df


def clean():
    df = pd.read_csv(data_file_path("post_council/post_pprr_11-6-2020.csv"))
    df = clean_column_names(df)
    df.columns = [
        'agency', 'last_name', 'first_name', 'employment_status',
        'hire_date', 'level_1_cert_date', 'last_pc_12_qualification_date']
    df.loc[:, 'data_production_year'] = '2020'
    df = df.dropna(0, "all", subset=["first_name"])
    df = df\
        .pipe(standardize_agency)\
        .pipe(standardize_desc_cols, ["employment_status"])\
        .pipe(clean_dates, ["hire_date"])\
        .pipe(replace_impossible_dates)\
        .pipe(clean_dates, ['level_1_cert_date', 'last_pc_12_qualification_date'], expand=False)\
        .pipe(clean_names, ["first_name", "last_name"])\
        .pipe(gen_uid, ['agency', 'last_name', 'first_name', 'hire_year', 'hire_month', 'hire_day'])\
        .drop_duplicates(subset=['hire_year', 'hire_month', 'hire_day', 'uid'], keep='first')
    return df


if __name__ == '__main__':
    df = clean()
    ensure_data_dir('clean')
    df.to_csv(
        data_file_path('clean/pprr_post_2020_11_06.csv'),
        index=False
    )
