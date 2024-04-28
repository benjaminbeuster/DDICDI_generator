from __future__ import annotations
import typing as t
from pathlib import Path
import pandas as pd
import pyreadstat as pyr
pd.set_option('display.max_rows', 2500)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None
import datetime

######################################################################

def read_sav(filename: Path, encoding="utf-8", missings=True, disable_datetime_conversion=True):
    kwargs = dict(
        user_missing=missings,
        dates_as_pandas_datetime=False,  # Do not interpret dates initially
    )
    filename = Path(filename)  # Ensure filename is a Path object
    extension = filename.suffix.lower()

    if extension not in ['.sav', '.dta']:
        raise ValueError("Unsupported file type!")

    if extension == '.sav':
        try:
            df, meta = pyr.read_sav(filename, encoding=encoding, row_limit=5, **kwargs)
        except Exception:
            df, meta = pyr.read_sav(filename, encoding="LATIN1", row_limit=5, **kwargs)

    elif extension == '.dta':
        try:
            df, meta = pyr.read_dta(filename, encoding=encoding, row_limit=5, **kwargs)
        except Exception:
            df, meta = pyr.read_dta(filename, encoding="LATIN1", row_limit=5, **kwargs)

    # Since you are already limiting the rows while reading,
    # the following line is redundant and can be removed.
    # df = df.head()

    # Manually handle the problematic date columns
    for col in df.columns:
        if "datetime" in str(df[col].dtype) or "date" in str(df[col].dtype):
            df[col] = df[col].apply(lambda x: "1678-01-01" if str(x) == "1582-10-14" else x)
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Recode dtype
    df = df.convert_dtypes()

    # Recode string variables
    for var in df.columns:
        if df[var].dtype == 'string':
            df[[var]].replace({'': pd.NA}, inplace=True)

    df.attrs["datafile"] = "file"
    return df, meta


###################################################################

def create_variable_view(df_meta):
    # Extract the attributes from df_meta
    label = df_meta.column_names_to_labels
    values = df_meta.variable_value_labels
    missing = df_meta.missing_ranges
    format = df_meta.original_variable_types
    measure = df_meta.variable_measure

    # Convert dictionaries into individual dataframes
    df_label = pd.DataFrame(list(label.items()), columns=['name', 'label'])
    df_format = pd.DataFrame(list(format.items()), columns=['name', 'format'])
    df_measure = pd.DataFrame(list(measure.items()), columns=['name', 'measure'])

    # For values and missing, handle them differently due to dictionaries/lists inside
    df_values_list = [{'name': k, 'values': str(v)} for k, v in values.items()]  # Convert values to string
    df_values = pd.DataFrame(df_values_list)

    df_missing_list = [{'name': k, 'missing': str(v)} for k, v in missing.items()]  # Convert missing values to string
    df_missing = pd.DataFrame(df_missing_list)

    # Merge dataframes on the 'name' column
    variable_view = df_label
    if not df_values.empty:
        variable_view = variable_view.merge(df_values, on='name', how='outer')

    if not df_missing.empty:
        variable_view = variable_view.merge(df_missing, on='name', how='outer')

    variable_view = variable_view \
        .merge(df_format, on='name', how='outer') \
        .merge(df_measure, on='name', how='outer')

    # Ensure 'values' and 'missing' columns are present
    if 'values' not in variable_view.columns:
        variable_view['values'] = pd.NA

    if 'missing' not in variable_view.columns:
        variable_view['missing'] = pd.NA

    return variable_view[['name', 'format', 'label', 'values', 'missing', 'measure']]


def create_variable_view2(df_meta):
    # Extract the attributes from df_meta
    label = df_meta.column_names_to_labels
    values = df_meta.variable_value_labels

    # Convert user-defined missing values to the desired format
    missing = {}
    for key, vals in df_meta.missing_user_values.items():
        missing[key] = [{"lo": val, "hi": val} for val in vals]

    format = df_meta.original_variable_types
    measure = df_meta.variable_measure

    # Convert dictionaries into individual dataframes
    df_label = pd.DataFrame(list(label.items()), columns=['name', 'label'])
    df_format = pd.DataFrame(list(format.items()), columns=['name', 'format'])
    df_measure = pd.DataFrame(list(measure.items()), columns=['name', 'measure'])

    # For values and missing, handle them differently due to dictionaries/lists inside
    df_values_list = [{'name': k, 'values': str(v)} for k, v in values.items()]  # Convert values to string
    df_values = pd.DataFrame(df_values_list)

    df_missing_list = [{'name': k, 'missing': str(v)} for k, v in missing.items()]  # Convert missing values to string
    df_missing = pd.DataFrame(df_missing_list)

    # Merge dataframes on the 'name' column
    variable_view = df_label
    if not df_values.empty:
        variable_view = variable_view.merge(df_values, on='name', how='outer')
    else:
        variable_view['values'] = pd.NA

    if not df_missing.empty:
        variable_view = variable_view.merge(df_missing, on='name', how='outer')
    else:
        variable_view['missing'] = pd.NA

    variable_view = variable_view \
        .merge(df_format, on='name', how='outer') \
        .merge(df_measure, on='name', how='outer')

    # Ensure 'values' and 'missing' columns are present
    if 'values' not in variable_view.columns:
        variable_view['values'] = pd.NA

    if 'missing' not in variable_view.columns:
        variable_view['missing'] = pd.NA

    return variable_view[['name', 'format', 'label', 'values', 'missing', 'measure']]
