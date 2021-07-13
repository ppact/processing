import pandas as pd
from lib.clean import (
    clean_dates, clean_names, standardize_desc_cols, clean_salaries
)
from lib.path import data_file_path, ensure_data_dir
from lib.columns import clean_column_names, set_values
from lib.uid import gen_uid
from lib import salary
import sys
sys.path.append("../")


def assign_agency(df, year):
    df.loc[:, 'agency'] = 'New Orleans Harbor PD'
    df.loc[:, 'data_production_year'] = year
    return df


def clean_rank_desc(df):
    df.rank_desc = df.rank_desc.str.lower().str.strip()\
        .str.replace(r'(police|policy)?', '', regex=True)\
        .str.replace('admin', 'administrative', regex=False)\
        .str.replace(r' ?(1|2|2$|3|4$)?(-+)?(\ba\b|port)?$', '', regex=True)
    return df


def assign_pay_date_and_rank_date(df):
    df = df.sort_values(['uid', 'effective_date'], ignore_index=True)\
        .drop_duplicates(ignore_index=True)
    uid = None
    rank = None
    sal = None
    for idx, row in df.iterrows():
        if row.uid != uid:
            uid = row.uid
            df.loc[idx, 'rank_date'] = row.effective_date
            df.loc[idx, 'pay_effective_date'] = row.effective_date
        else:
            if row.rank_desc != rank:
                df.loc[idx, 'rank_date'] = row.effective_date
            if row.salary != sal:
                df.loc[idx, 'pay_effective_date'] = row.effective_date
        rank = row.rank_desc
        sal = row.salary
    return df


def clean_personnel_2008():
    df = pd.read_csv(data_file_path(
        "new_orleans_harbor_pd/new_orleans_harbor_pd_pprr_1991-2008.csv"
    ))
    df = clean_column_names(df)
    df = df.dropna(axis=1, how="all")
    df = df.rename(columns={
        "mi": "middle_initial",
        "date_hired": "hire_date",
        "position_rank": "rank_desc",
        "hourly_pay_rate": "salary",
        "term_date": "resign_date",
    })
    return df\
        .pipe(clean_rank_desc)\
        .pipe(standardize_desc_cols, ["rank_desc"])\
        .pipe(set_values, {'salary_freq': salary.HOURLY})\
        .pipe(clean_salaries, ["salary"])\
        .pipe(assign_agency, 2008)\
        .pipe(clean_names, ["first_name", "last_name", "middle_initial"])\
        .pipe(gen_uid, ['agency', 'first_name', 'last_name', 'middle_initial'])\
        .pipe(assign_pay_date_and_rank_date)\
        .pipe(clean_dates, ["hire_date", "resign_date", "pay_effective_date", "rank_date"])


def clean_personnel_2020():
    df = pd.read_csv(data_file_path(
        "new_orleans_harbor_pd/new_orleans_harbor_pd_pprr_2020.csv"))
    df = clean_column_names(df)
    df = df.dropna(how="all")
    df = df[["first_name", "last_name", "position_rank", "date_hired",
             "term_date", "hourly_pay", "mi", "pay_effective_date"]]
    df.rename(columns={
        "date_hired": "hire_date",
        "position_rank": "rank_desc",
        "hourly_pay": "salary",
        "mi": "middle_initial",
        "term_date": "resign_date",
        "pay_effective_date": "effective_date"
    }, inplace=True)
    df = df.drop_duplicates(ignore_index=True)
    return df\
        .pipe(set_values, {'salary_freq': salary.HOURLY})\
        .pipe(clean_salaries, ['salary'])\
        .pipe(clean_rank_desc)\
        .pipe(standardize_desc_cols, ['rank_desc'])\
        .pipe(assign_agency, 2020)\
        .pipe(clean_names, ["last_name", "middle_initial", "first_name"])\
        .pipe(gen_uid, [
            "agency", "first_name", "last_name", "middle_initial", "hire_date"
        ])\
        .pipe(assign_pay_date_and_rank_date)\
        .pipe(gen_uid, ['uid', 'pay_effective_date', 'rank_date'], 'perhist_uid')\
        .pipe(clean_dates, ["resign_date", "hire_date", "pay_effective_date", "rank_date"])


if __name__ == "__main__":
    df20 = clean_personnel_2020()
    df08 = clean_personnel_2008()
    ensure_data_dir("clean")
    df20.to_csv(
        data_file_path("clean/pprr_new_orleans_harbor_pd_2020.csv"),
        index=False)
    df08.to_csv(
        data_file_path("clean/pprr_new_orleans_harbor_pd_1991_2008.csv"),
        index=False)
