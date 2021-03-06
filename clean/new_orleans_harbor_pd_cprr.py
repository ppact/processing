from lib.columns import clean_column_names
from lib.path import data_file_path, ensure_data_dir
from lib.clean import (
    clean_dates, clean_names, standardize_desc_cols, clean_sexes, clean_races
)
from lib.uid import gen_uid
import pandas as pd
import sys
sys.path.append("../")


def realign() -> pd.DataFrame:
    df = pd.read_csv(data_file_path(
        "new_orleans_harbor_pd/new_orleans_harbor_pd_cprr_2014-2020.csv"))
    df = df.set_index("Unnamed: 0").transpose().dropna(
        1, how="all").reset_index(drop=True)
    df = clean_column_names(df)
    return df


def split_name(df):
    names = df.full_name.str.split(" ", expand=True)
    df.loc[:, "first_name"] = names.iloc[:, 0]
    df.loc[:, "last_name"] = names.iloc[:, 1]
    df = df.drop(columns="full_name")
    return df


def strip_badge(df):
    df.loc[:, "badge_no"] = df.badge_no.str.strip(
    ).str.replace(r"\s+\(call sign\)$", "")
    return df


def clean_officer_sex(df):
    df.loc[:, "sex"] = df.sex.str.lower()
    return df


def assign_agency(df):
    df.loc[:, "agency"] = "New Orleans Harbor PD"
    df.loc[:, "data_production_year"] = "2020"
    return df


def clean():
    df = realign()\
        .drop(columns=["e_the_recommended_discipline"])\
        .rename(columns={
            "1_name": "full_name",
            "2_badge_number": "badge_no",
            "3_gender": "sex",
            "6_unit_assignment_on_the_date_of_the_complaint_incident": "department_desc",
            "7_rank_on_the_date_of_the_complaint_incident": "rank_desc",
            "8_date_of_appointment": "hire_date",
            "b_rule_violation": "rule_code",
            "c_paragraph_violation": "paragraph_code",
            "e_the_final_discipline_imposed": "action",
            "a_the_incident_type": "incident_type",
            "b_the_complaint_tracking_number": "tracking_number",
            "c_the_date_on_which_the_complaint_incident_took_place": "occur_date",
            "d_the_date_on_which_the_complaint_was_received": "receive_date",
            "e_the_date_on_which_the_complaint_investigation_was_completed": "investigation_complete_date",
            "f_the_classification_of_the_complaint": "disposition",
            "g_the_status_of_the_investigation": "investigation_status",
            "1_gender": "complainant_sex",
            "2_race": "complainant_race",
        })\
        .pipe(split_name)\
        .pipe(clean_names, ["first_name", "last_name"])\
        .pipe(strip_badge)\
        .pipe(clean_officer_sex)\
        .pipe(standardize_desc_cols, [
            "department_desc", "rank_desc", "action", "incident_type", "disposition", "investigation_status"
        ])\
        .pipe(clean_sexes, ["complainant_sex"])\
        .pipe(clean_races, ["complainant_race"])\
        .pipe(clean_dates, ["hire_date", "occur_date", "receive_date", "investigation_complete_date"])\
        .pipe(assign_agency)\
        .pipe(gen_uid, ['agency', 'tracking_number'], 'complaint_uid')
    return df


if __name__ == "__main__":
    df = clean()
    ensure_data_dir("clean")
    df.to_csv(data_file_path("clean/cprr_new_orleans_harbor_pd_2020.csv"))
