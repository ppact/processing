import re
import json
import pandas as pd
import numpy as np
import datetime

from lib.date import combine_date_columns, combine_datetime_columns


mdy_date_pattern_1 = re.compile(r"^\d{1,2}/\d{1,2}/\d{2}$")
mdy_date_pattern_2 = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
mdy_date_pattern_3 = re.compile(r"^\d{1,2}-\d{1,2}-\d{2}$")
dmy_date_pattern = re.compile(r'^\d{1,2}-\w{3}-\d{2}$')
year_pattern = re.compile(r"^(19|20)\d{2}$")
year_month_pattern = re.compile(r"^(19|20)\d{4}$")
month_day_pattern = re.compile(r"^[A-Z][a-z]{2}-\d{1,2}$")


def clean_date(val) -> tuple[str, str, str]:
    """Try parsing date with a few known patterns

    Args:
        val (str):
            the date string to parse

    Returns:
        a tuple of (year, month, day)

    Raises:
        ValueError:
            date string format is unknown
    """
    if val == "" or pd.isnull(val):
        return "", "", ""
    m = mdy_date_pattern_2.match(val)
    if m is not None:
        [month, day, year] = val.split("/")
        if int(month) > 12 and int(day) <= 12:
            month, day = day, month
        return year, month.lstrip("0"), day.lstrip("0")
    m = mdy_date_pattern_1.match(val)
    if m is not None:
        [month, day, year] = val.split("/")
        if year[0] in ["1", "2", "0"]:
            year = "20" + year
        else:
            year = "19" + year
        if int(month) > 12 and int(day) <= 12:
            month, day = day, month
        return year, month.lstrip("0"), day.lstrip("0")
    m = mdy_date_pattern_3.match(val)
    if m is not None:
        [month, day, year] = val.split("-")
        if year[0] in ["1", "2", "0"]:
            year = "20" + year
        else:
            year = "19" + year
        if int(month) > 12 and int(day) <= 12:
            month, day = day, month
        return year, month.lstrip("0"), day.lstrip("0")
    m = dmy_date_pattern.match(val)
    if m is not None:
        [day, month, year] = val.split("-")
        month = str(datetime.datetime.strptime(month, '%b').month)
        if year[0] in ["1", "2", "0"]:
            year = "20" + year
        else:
            year = "19" + year
        return year, month, day
    m = year_month_pattern.match(val)
    if m is not None:
        return val[:4], val[4:], ""
    m = year_pattern.match(val)
    if m is not None:
        return val, "", ""
    m = month_day_pattern.match(val)
    if m is not None:
        dt = datetime.datetime.strptime(val, "%b-%d")
        return "", str(dt.month).zfill(2), str(dt.day).zfill(2)
    raise ValueError("unknown date format \"%s\"" % val)


def clean_dates(df: pd.DataFrame, cols: list[str], expand: bool = True) -> pd.DataFrame:
    """Parses date columns using a few known patterns.

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            the date columns. Each column must end with "_date"
        expand (bool):
            whether the result should be expanded to _year, _month and
            _day columns. Defaults to True.

    Returns:
        the updated frame
    """
    for col in cols:
        assert col.endswith("_date")
        dates = pd.DataFrame.from_records(
            df[col].str.strip().str.replace(
                r'//', r'/', regex=False
            ).map(clean_date)
        )
        if expand:
            prefix = col[:-5]
            dates.columns = [prefix+"_year", prefix+"_month", prefix+"_day"]
            df = pd.concat([df, dates], axis=1)
        else:
            df.loc[:, col] = combine_date_columns(dates, 0, 1, 2)
    if expand:
        df = df.drop(columns=cols)
    return df


datetime_pattern_1 = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{1,2}$")


def clean_datetime(val) -> tuple[str, str, str, str]:
    """Parses datetime string using known patterns

    Args:
        val (str):
            the datetime string to parse

    Returns:
        a tuple of year, month, day and time string

    Raises:
        ValueError:
            datetime string format is unknown
    """
    if val == "" or pd.isnull(val):
        return "", "", "", ""
    m = datetime_pattern_1.match(val)
    if m is not None:
        [date, time] = re.split(r"\s+", val)
        [hour, minute] = time.split(":")
        year, month, day = clean_date(date)
        return year, month, day, "%s:%s" % (hour.zfill(2), minute.zfill(2))
    raise ValueError("unknown datetime format \"%s\"" % val)


def clean_datetimes(df: pd.DataFrame, cols: list[str], expand: bool = True) -> pd.DataFrame:
    """Parses datetime columns using known patterns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            datetime column names. Each column name must end with "_datetime"
        expand (bool):
            whether result should be expanded into 4 columns: _year, _month,
            _day and _time. Defaults to True

    Returns:
        the updated frame
    """
    for col in cols:
        assert col.endswith("_datetime")
        dates = pd.DataFrame.from_records(
            df[col].str.strip().map(clean_datetime))
        if expand:
            prefix = col[:-9]
            dates.columns = [prefix+"_year", prefix +
                             "_month", prefix+"_day", prefix+"_time"]
            df = pd.concat([df, dates], axis=1)
        else:
            df.loc[:, col] = combine_datetime_columns(dates, 0, 1, 2, 3)
    if expand:
        df = df.drop(columns=cols)
    return df


def parse_dates_with_known_format(df: pd.DataFrame, cols: list[str], format: str) -> pd.DataFrame:
    """Parses dates using strptime format and expands into _year, _month, _day columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            list of date columns. Each column name must end with "_date"
        format (str):
            strptime format string.

    Returns:
        the updated frame
    """
    for col in cols:
        assert col.endswith("_date")
        dates = pd.DataFrame.from_records(pd.to_datetime(df[col], format=format).map(lambda x: (
            "", "", "") if pd.isnull(x) else (str(x.year), str(x.month), str(x.day))))
        prefix = col[:-5]
        dates.columns = [prefix+"_year", prefix+"_month", prefix+"_day"]
        df = pd.concat([df, dates], axis=1)
    df = df.drop(columns=cols)
    return df


def clean_sexes(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardizes gender columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            gender columns

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = df[col].str.strip().str.lower()\
            .str.replace(r"^m$", "male", regex=True).str.replace(r"^f$", "female", regex=True)\
            .str.replace(r"^unknown.*", "", regex=True)
    return df


def clean_races(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardize race columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            race columns

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = df[col].str.strip().str.lower()\
            .str.replace(r"^w$", "white", regex=True).str.replace(r"^b(lack.+)?$", "black", regex=True)\
            .str.replace(r"^h$", "hispanic", regex=True).str.replace(r"^unknown.*", "", regex=True)
    return df


def clean_employment_status(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardize employment status columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            employment status columns

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = df[col].str.strip().str.lower()\
            .str.replace(r"^i$", "inactive", regex=True).str.replace(r"^a$", "active", regex=True)
    return df


def clean_salary(series: pd.Series) -> pd.Series:
    """Cleans and standardize salary series

    Args:
        series (pd.Series):
            the series to process

    Returns:
        the updated series
    """
    return series.str.strip().str.replace(r"[^\d\.]", "", regex=True).astype("float64")


def clean_salaries(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardize salary columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            salary columns

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = clean_salary(df[col])
    return df


def clean_name(series: pd.Series) -> pd.Series:
    """Cleans and standardize name series

    Args:
        series (pd.Series):
            the series to process

    Returns:
        the updated series
    """
    return series.str.strip().str.replace(r"[^\w-]+", " ", regex=True)\
        .str.replace(r"\s+", " ", regex=True).str.replace(r"\s*-\s*", "-", regex=True)\
        .str.lower().str.strip().fillna("").str.strip("-")


def names_to_title_case(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Converts name columns to title case

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            name columns

    Returns:
        the updated frame
    """
    cols_set = set(df.columns)
    for col in cols:
        if col not in cols_set:
            continue
        df.loc[:, col] = df[col].str.title()\
            .str.replace(r" I(i|ii|v|x)$", lambda m: " I"+m.group(1).upper(), regex=True)\
            .str.replace(r" V(i|ii|iii)$", lambda m: " V"+m.group(1).upper(), regex=True)
    return df


def clean_names(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardize name columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            name columns

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = clean_name(df[col])
    return df


name_pattern_1 = re.compile(r"^(\w{2,}) (\w\.) (\w{2,}.+)$")
name_pattern_2 = re.compile(r"^([-\w\']+), (\w{2,})$")
name_pattern_3 = re.compile(r'^(\w{2,}) ("\w+") ([-\w\']+)$')
name_pattern_4 = re.compile(
    r'^(\w{2,}) ([-\w\']+ (?:i|ii|iii|iv|v|jr|sr)\W?)$')
name_pattern_5 = re.compile(r'^([\w-]{2,}) (\w+) ([-\w\']+)$')
name_pattern_6 = re.compile(r"^([\w-]{2,}) ([-\w\']+)$")
name_pattern_7 = re.compile(r"^\w+$")


def split_names(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Split name column using known patterns

    Args:
        df (pd.DataFrame):
            the frame to process
        col (str):
            name column

    Returns:
        the updated frame with new columns: 'first_name',
        'middle_name' and 'last_name'
    """
    def split_name(val):
        if pd.isnull(val) or not val:
            return "", "", ""
        m = name_pattern_1.match(val)
        if m is not None:
            first_name = m.group(1)
            middle_name = m.group(2)
            last_name = m.group(3)
            return first_name, middle_name, last_name
        m = name_pattern_2.match(val)
        if m is not None:
            first_name = m.group(2)
            last_name = m.group(1)
            return first_name, "", last_name
        m = name_pattern_3.match(val)
        if m is not None:
            first_name = m.group(1)
            last_name = m.group(3)
            return first_name, "", last_name
        m = name_pattern_4.match(val)
        if m is not None:
            first_name = m.group(1)
            last_name = m.group(2)
            return first_name, "", last_name
        m = name_pattern_5.match(val)
        if m is not None:
            first_name = m.group(1)
            middle_name = m.group(2)
            last_name = m.group(3)
            return first_name, middle_name, last_name
        m = name_pattern_6.match(val)
        if m is not None:
            first_name = m.group(1)
            last_name = m.group(2)
            return first_name, "", last_name
        m = name_pattern_7.match(val)
        if m is not None:
            return "", "", val
        raise ValueError('unrecognized name format %s' % json.dumps(val))

    df = df.reset_index(drop=True)
    names = pd.DataFrame.from_records(
        df[col].fillna('').str.strip().str.replace(r' +', ' ', regex=True)
        .str.lower().map(split_name).to_list())
    names.columns = ['first_name', 'middle_name', 'last_name']
    return pd.concat([df, names], axis=1)


def standardize_desc(series: pd.Series) -> pd.Series:
    """Standardizes description series such as rank and department

    Args:
        series (pd.Series):
            the series to process

    Returns:
        the updated series
    """
    return series.str.strip().str.lower().fillna("")


def standardize_desc_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardize description columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            descriptive columns such as rank_desc and department_desc

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = standardize_desc(df[col])
    return df


def float_to_int_str(df: pd.DataFrame, cols: list[str], cast_as_str: bool = False) -> pd.DataFrame:
    """Turns float values in column into strings without trailing ".0"

    Data loaded with pd.read_csv tend to turn integer columns into
    float columns if there are even just one value missing. This
    reverse that effect by converting everything to string and strip
    trailing ".0"s.

    Examples:
        [1973.0, np.nan, "abc"] => ["1973", "", "abc"]

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            columns to convert
        cast_as_str (bool):
            cast column to string even if no processing was needed.
            Defaults to False.

    Returns:
        the updated frame
    """
    cols_set = set(df.columns)
    for col in cols:
        if col not in cols_set:
            continue
        if df[col].dtype == np.float64:
            df.loc[:, col] = df[col].fillna(0).astype(
                "int64").astype(str).str.replace(r"^0$", "", regex=True)
        elif df[col].dtype == np.object:
            idx = df[col].map(lambda v: type(v) == float)
            df.loc[idx, col] = df.loc[idx, col].fillna(0).astype(
                "int64").astype(str).str.replace(r"^0$", "", regex=True)
            if cast_as_str:
                df.loc[~idx, col] = df.loc[~idx, col].astype(str)
        elif cast_as_str:
            df.loc[:, col] = df[col].astype(str)
    return df
