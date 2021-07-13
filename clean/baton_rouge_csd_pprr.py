from lib.columns import clean_column_names, set_values
from lib.clean import (
    clean_names, parse_dates_with_known_format, clean_salaries, standardize_desc_cols,
    clean_employment_status
)
from lib.path import data_file_path, ensure_data_dir
from lib.uid import gen_uid
from lib import salary
import pandas as pd
import sys
sys.path.append("../")


def assign_agency(df):
    df.loc[:, "agency"] = "Baton Rouge CSD"
    return df


def assign_rank_year_and_pay_year(df):
    df = df.sort_values(['uid', 'year'])
    uid = None
    sal = None
    rank = None
    dept = None
    for idx, row in df.iterrows():
        if row.uid != uid:
            uid = row.uid
            df.loc[idx, 'pay_effective_year'] = row.year
            df.loc[idx, 'rank_year'] = row.year
            df.loc[idx, 'dept_year'] = row.year
        else:
            if row.salary != sal:
                df.loc[idx, 'pay_effective_year'] = row.year
            if row.rank_desc != rank:
                df.loc[idx, 'rank_year'] = row.year
            if row.department_desc != dept:
                df.loc[idx, 'dept_year'] = row.year
        sal = row.salary
        rank = row.rank_desc
        dept = row.department_desc
    return df


def clean_department_desc(df):
    df.department_desc = df.department_desc.str.lower().str.strip()\
        .str.replace(r'police ?(department)?-', '', regex=True)\
        .str.replace('serv', 'services', regex=False)\
        .str.replace('byrne crim jus innov (bcji)', 'byrne criminal justice innovation program', regex=False)\
        .str.replace('special operations', 'special operations bureau', regex=False)\
        .str.replace(r'^criminal invest(igation)? ?(bureau)?', 'criminal investigations bureau', regex=True)
    return df


def clean_rank_desc(df):
    df.rank_desc = df.rank_desc.str.lower().str.strip()\
        .str.replace(r' \b ?i(i)?-?(42 ?/?hrs)?\b', '', regex=True)\
        .str.replace(r' \(job-?share\)?', '', regex=True)\
        .str.replace(r'\bof police\b', '', regex=True)\
        .str.replace(r'off?cr?', 'officer', regex=True)\
        .str.replace('college student intern/contract', 'college student intern', regex=False)\
        .str.replace(r'\bspec\b', 'specialist', regex=True)\
        .str.replace(r'\bmech\b', 'mechanic', regex=True)\
        .str.replace(r'pol(ice)? ', '', regex=True)\
        .str.replace('exception job code', '', regex=False)\
        .str.replace(r'\bcomm\b', 'communications', regex=True)\
        .str.replace(r'spc$', 'specialist', regex=True)\
        .str.replace(r'^sr', 'senior', regex=True)\
        .str.replace(r'tech$', 'technician', regex=True)\
        .str.replace(r'\binfo\b', 'information', regex=True)\
        .str.replace(r'supvr$', 'supervisor', regex=True)\
        .str.replace(r'prog(rammer)?/?sys(tems)? ?analy(st)?', 'programmer and systems analyst', regex=True)
    return df


def clean_17():
    df = pd.read_csv(data_file_path(
        "baton_rouge_csd/baton_rouge_csd_pprr_2017.csv"
    )).pipe(clean_column_names)
    df = df[[
        'year', 'employee_num', 'last_name', 'first_name', 'middle_init', 'division_num', 'division_name', 'job_code',
        'job_title', 'current_hire_date', 'employment_end_date', 'employment_status', 'gross_pay', 'total_hourly_rate'
    ]].rename(columns={
        "employee_num": "employee_id",
        "middle_init": "middle_initial",
        "division_num": "department_code",
        "division_name": "department_desc",
        "job_code": "rank_code",
        "job_title": "rank_desc",
        "current_hire_date": "hire_date",
        "employment_end_date": "resign_date",
        "gross_pay": "salary",
    }).pipe(set_values, {
        'data_production_year': '2017',
        'salary_freq': salary.YEARLY
    }).pipe(clean_salaries, ["salary"])\
        .pipe(clean_department_desc)\
        .pipe(standardize_desc_cols, ["department_desc", "rank_desc"])\
        .pipe(clean_rank_desc)\
        .pipe(parse_dates_with_known_format, ["hire_date", "resign_date"], "%m/%d/%Y")\
        .pipe(assign_agency)\
        .pipe(clean_names, ["first_name", "last_name", "middle_initial"])\
        .pipe(gen_uid, [
            "agency", "data_production_year", "first_name", "last_name", "middle_initial"])\
        .pipe(assign_rank_year_and_pay_year)
    return df


def clean_19():
    df = pd.read_csv(data_file_path(
        "baton_rouge_csd/baton_rouge_csd_pprr_2019.csv"
    )).pipe(clean_column_names)

    df = df[[
        'year', 'last_name', 'first_name', 'middle_init',
        'pay_location_code', 'pay_location_description',
        'job_code', 'job_title', 'current_hire_date', 'employment_end_date',
        'employment_status', 'gross_pay', 'uniqueid'
    ]].rename(columns={
        "middle_init": "middle_initial",
        "pay_location_code": "department_code",
        "pay_location_description": "department_desc",
        "job_code": "rank_code",
        "job_title": "rank_desc",
        "current_hire_date": "hire_date",
        "employment_end_date": "resign_date",
        "gross_pay": "salary",
        "uniqueid": "employee_id"
    }).pipe(set_values, {
        'data_production_year': '2019',
        'salary_freq': salary.YEARLY
    }).drop_duplicates()\
        .pipe(clean_salaries, ["salary"])\
        .pipe(clean_rank_desc)\
        .pipe(standardize_desc_cols, ["department_desc", "rank_desc"])\
        .pipe(parse_dates_with_known_format, ["hire_date", "resign_date"], "%m/%d/%Y")\
        .pipe(clean_employment_status, ["employment_status"])\
        .pipe(clean_department_desc)\
        .pipe(assign_agency)\
        .pipe(clean_names, ["first_name", "last_name", "middle_initial"])\
        .pipe(gen_uid, ["agency", "data_production_year", "employee_id"])\
        .pipe(assign_rank_year_and_pay_year)
    return df


if __name__ == "__main__":
    df17 = clean_17()
    df19 = clean_19()
    ensure_data_dir("clean")
    df17.to_csv(
        data_file_path("clean/pprr_baton_rouge_csd_2017.csv"),
        index=False)
    df19.to_csv(
        data_file_path("clean/pprr_baton_rouge_csd_2019.csv"),
        index=False)
