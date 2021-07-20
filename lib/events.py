from datetime import datetime, timedelta

import pandas as pd
from pandas.api.types import CategoricalDtype

from lib.clean import clean_date, clean_datetime, float_to_int_str
from lib.uid import ensure_uid_unique, gen_uid_from_dict
from lib.exceptions import InvalidEventKindException, InvalidEventDateException, InvalidSalaryFreqException
from lib.columns import rearrange_event_columns
from lib.date import combine_date_columns
from lib import salary

OFFICER_LEVEL_1_CERT = "officer_level_1_cert"
OFFICER_PC_12_QUALIFICATION = "officer_pc_12_qualification"
OFFICER_RANK = "officer_rank"
OFFICER_DEPT = "officer_dept"
OFFICER_HIRE = "officer_hire"
OFFICER_LEFT = "officer_left"
OFFICER_PAY_PROG_START = "officer_pay_prog_start"
OFFICER_PAY_EFFECTIVE = "officer_pay_effective"

COMPLAINT_INCIDENT = "complaint_incident"
COMPLAINT_RECEIVE = "complaint_receive"
ALLEGATION_CREATE = "allegation_create"
INVESTIGATION_START = "investigation_start"
INVESTIGATION_COMPLETE = "investigation_complete"
SUSPENSION_START = "suspension_start"
SUSPENSION_END = "suspension_end"

APPEAL_FILE = "appeal_file"
APPEAL_HEARING = "appeal_hearing"
APPEAL_RENDER = "appeal_render"

UOF_INCIDENT = "uof_incident"
UOF_RECEIVE = "uof_receive"
UOF_ASSIGNED = "uof_assigned"
UOF_COMPLETED = "uof_completed"
UOF_CREATED = "uof_created"
UOF_DUE = "uof_due"

AWARD_RECEIVE = "award_receive"


cat_type = CategoricalDtype(categories=[
    OFFICER_LEVEL_1_CERT,
    OFFICER_PC_12_QUALIFICATION,
    OFFICER_RANK,
    OFFICER_DEPT,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_PROG_START,
    OFFICER_PAY_EFFECTIVE,
    COMPLAINT_INCIDENT,
    COMPLAINT_RECEIVE,
    ALLEGATION_CREATE,
    INVESTIGATION_START,
    INVESTIGATION_COMPLETE,
    SUSPENSION_START,
    SUSPENSION_END,
    APPEAL_FILE,
    APPEAL_HEARING,
    APPEAL_RENDER,
    UOF_INCIDENT,
    UOF_RECEIVE,
    UOF_ASSIGNED,
    UOF_COMPLETED,
    UOF_CREATED,
    UOF_DUE,
    AWARD_RECEIVE,
], ordered=True)


class Builder(object):
    """Builder build an event DataFrame by collecting event records.
    """

    def __init__(self):
        self._records = []

    def _extract_date(self, fields, raw_date, strptime_format=None):
        if strptime_format is not None:
            dt = datetime.strptime(raw_date, strptime_format)
            fields["year"] = dt.year
            fields["month"] = dt.month
            fields["day"] = dt.day
        else:
            fields["year"], fields["month"], fields["day"] = clean_date(
                raw_date
            )
        fields["raw_date"] = raw_date

    def _extract_datetime(self, fields, raw_datetime, strptime_format=None):
        if strptime_format is not None:
            dt = datetime.strptime(raw_datetime, strptime_format)
            fields["year"] = dt.year
            fields["month"] = dt.month
            fields["day"] = dt.day
            fields["time"] = dt.strftime("%H:%M")
        else:
            fields["year"], fields["month"], fields["day"], fields["time"] = clean_datetime(
                raw_datetime)
        fields["raw_date"] = raw_datetime

    def append_record(
        self,
        event_kind: str,
        id_cols: list[str],
        raw_date_str: str or None = None,
        raw_datetime_str: str or None = None,
        strptime_format: str or None = None,
        ignore_bad_date: bool = False,
        **kwargs
    ) -> None:
        """Append an event and optionally parse datetime of the event.

        If `raw_date_str` is passed then Builder try to extract `year`, `month`, `day` from it. If `raw_datetime_str`
        is passed instead then Builder try to extract `year`, `month`, `day` and `time` from it. If `strptime_format`
        is passed along with `raw_date_str` or `raw_datetime_str` then the date is parsed with that format. By default
        if `year` isn't passed-in or can't be extracted from `raw_date_str` or `raw_datetime_str` then an error is
        raised. If `ignore_bad_date` is True then an error isn't raised and the event is simply ignored. Any other
        keyword arguments passed to this method will become a column in the final DataFrame.

        Args
            event_kind (str):
                kind of event
            id_cols (list of str):
                list of columns to generate event_uid from (in addition to ['kind', 'year', 'month', 'day', 'time'])
            raw_date_str (str):
                raw date string to extract `year`, `month` and `day` from
            raw_datetime_str (str):
                raw datetime string to extract `year`, `month`, `day` and `time` from
            strptime_format (str):
                format string to extract datetime with.
            ignore_bad_date (bool):
                if True then ignore events with bad date instead of raising error

        Returns:
            no value

        Raises:
            InvalidEventKindException:
                `event_kind` is invalid
            InvalidSalaryFreqException:
                `salary_freq` is passed in and it's not one of the categories defined in lib.salary
            InvalidEventDateException:
                `year` isn't passed in or can't be extracted from raw date string.
        """
        if event_kind not in cat_type.categories:
            raise InvalidEventKindException(event_kind)
        if 'salary_freq' in kwargs:
            if 'salary' not in kwargs or pd.isnull(kwargs['salary']) or kwargs['salary'] == '':
                del kwargs['salary_freq']
            elif kwargs['salary_freq'] not in salary.cat_type.categories:
                raise InvalidSalaryFreqException(kwargs['salary_freq'])
        kwargs["kind"] = event_kind
        try:
            if raw_date_str is not None:
                self._extract_date(kwargs, raw_date_str, strptime_format)
            elif raw_datetime_str is not None:
                self._extract_datetime(kwargs, raw_datetime_str, strptime_format)
        except ValueError:
            if ignore_bad_date:
                return
            raise
        if 'year' not in kwargs or pd.isnull(kwargs["year"]) or kwargs["year"] == "":
            if ignore_bad_date:
                return
            raise InvalidEventDateException(
                "year column cannot be empty:\n\t%s" % kwargs)
        kwargs["event_uid"] = gen_uid_from_dict(
            kwargs, ['kind', 'year', 'month', 'day', 'time'] + id_cols)
        self._records.append(kwargs)

    def _assign_kwargs_func(self, cols, kwargs_funcs, flatten_date_cols, kind, obj):
        if "parse_date" in obj:
            col = "%s_date" % obj["prefix"]
            strptime_format = None if obj["parse_date"] is True else obj["parse_date"]
            kwargs_funcs[kind] = lambda row: [
                ("raw_date_str", row[col]),
                ("strptime_format", strptime_format)
            ]
            flatten_date_cols.append(col)
        elif "parse_datetime" in obj:
            col = "%s_datetime" % obj["prefix"]
            strptime_format = None if obj["parse_datetime"] is True else obj["parse_datetime"]
            kwargs_funcs[kind] = lambda row: [
                ("raw_datetime_str", row[col]),
                ("strptime_format", strptime_format)
            ]
            flatten_date_cols.append(col)
        else:
            col_pairs = []
            for event_col in ['year', 'month', 'day', 'time', 'raw_date']:
                col = '%s_%s' % (obj["prefix"], event_col)
                if col in cols:
                    col_pairs.append((col, event_col))
                    flatten_date_cols.append(col)

            kwargs_funcs[kind] = lambda row: [
                (event_col, row[col]) for col, event_col in col_pairs
            ]

    def extract_events(self, df: pd.DataFrame, event_dict: dict, id_cols: list[str]) -> None:
        """Extract event records from a DataFrame.

        Multiple kinds of event can be extracted. Each defined as a single key in `event_dict`.
        Each value in `event_dict` is a dictionary with following keys:
        - prefix: Prefix of columns to extract date from .E.g. if prefix = "hire" then hire_year, hire_month
          hire_day, hire_time, hire_date, hire_datetime, hire_raw_date are looked up depending on other keys.
        - keep: List of columns to keep in each event.
        - drop: Alternatively use "drop" to specify which columns to drop from each event.
        - parse_date: If set to True then extract date from column "{prefix}_date". If set to a string then
          it is used as strptime format string.
        - parse_datetime: Same as "parse_date" but extract from column "{prefix}_datetime" instead. And time
          is also extracted.
        - ignore_bad_date: If set to True then ignore events with bad date instead of raising error
        - id_cols: Overwrite `id_cols` for this event kind.

        Args:
            df (pd.DataFrame):
                the frame to extract events from
            event_dict (dict):
                event kinds to extract. E.g.:
                {
                    events.COMPLAINT_INCIDENT: {"prefix": "occur", "keep": ["uid", "complaint_uid", "agency"]},
                    events.COMPLAINT_RECEIVE: {"prefix": "receive", "keep": ["uid", "complaint_uid", "agency"]},
                    ...
                }
            id_cols (list of str):
                list of columns to generate event_uid from (in addition to ['kind', 'year', 'month', 'day', 'time'])

        Returns:
            no value
        """
        cols = set(df.columns)
        kwargs_funcs = dict()
        flatten_date_cols = []
        for kind, obj in event_dict.items():
            self._assign_kwargs_func(
                cols, kwargs_funcs, flatten_date_cols, kind, obj)

        for _, row in df.iterrows():
            common_fields = row.drop(flatten_date_cols).to_dict()
            for kind, obj in event_dict.items():
                if "parse_date" in obj:
                    anchor_col = '%s_date' % obj['prefix']
                elif "parse_datetime" in obj:
                    anchor_col = '%s_datetime' % obj['prefix']
                else:
                    anchor_col = '%s_year' % obj['prefix']
                if row[anchor_col] == '' or pd.isnull(row[anchor_col]):
                    continue
                if 'keep' in obj:
                    fields = dict(
                        [(k, v) for k, v in common_fields.items() if k in obj['keep']])
                elif 'drop' in obj:
                    fields = dict(
                        [(k, v) for k, v in common_fields.items() if k not in obj['drop']])
                else:
                    fields = dict(list(common_fields.items()))
                fields = dict(
                    list(fields.items()) + kwargs_funcs[kind](row))
                self.append_record(
                    kind,
                    id_cols if 'id_cols' not in obj else obj['id_cols'],
                    ignore_bad_date=obj.get('ignore_bad_date', False),
                    **fields,
                )

    def to_frame(self, output_duplicated_events: bool = False) -> pd.DataFrame:
        """Create a DataFrame out of collected events.

        This also ensure all event kinds are valid and generate `event_uid` column from `id_cols`

        Args:
            output_duplicated_events (bool):
                if True then output duplicated events to file data/duplicates.csv.
                Defaults to False

        Returns:
            collected events as a data frame

        Raises:
            NonUniqueEventIDException:
                event_uid is not unique.
        """
        df = pd.DataFrame.from_records(self._records)\
            .pipe(float_to_int_str, ["year", "month", "day"], True)
        df.loc[:, 'kind'] = df.kind.astype(cat_type)
        if 'salary_freq' in df.columns:
            df.loc[:, 'salary_freq'] = df.salary_freq.astype(salary.cat_type)
        df = rearrange_event_columns(df)
        ensure_uid_unique(df, 'event_uid', output_duplicated_events)
        return df


def discard_events_occur_more_than_once_every_30_days(df: pd.DataFrame, kind: str, groupby: list[str]) -> pd.DataFrame:
    """Discards events that occur more frequent than once every 30 days.

    Args:
        df (pd.DataFrame):
            the frame to process
        kind (str):
            event kind to filter
        groupby (list of str):
            list of columns to group by

    Returns:
        the processed frame
    """
    df.loc[:, 'date'] = combine_date_columns(df, 'year', 'month', 'day')
    event_uids = []
    for _, frame in df[df.kind == kind].groupby(groupby):
        if frame.shape[0] == 1:
            continue
        frame = frame.sort_values(['date'])
        prev_date = None
        prev_event_uid = None
        for _, row in frame.iterrows():
            if pd.isnull(row.date):
                continue
            if prev_date is not None and (prev_date == row.date or prev_date + timedelta(days=30) >= row.date):
                event_uids.append(prev_event_uid)
            prev_date = row.date
            prev_event_uid = row.event_uid
    df = df.loc[~df.event_uid.isin(event_uids)]
    return df.drop(columns=['date']).reset_index(drop=True)
