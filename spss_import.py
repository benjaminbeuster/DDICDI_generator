from __future__ import annotations
import typing as t
from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat as pyr

# Set pandas options
pd.set_option('display.max_rows', 2500)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# Define constants
<<<<<<< HEAD
ROW_LIMIT = 66
=======
ROW_LIMIT = 3
>>>>>>> c81e3f5b6128176fdfcef807f68a1d0b5b1d5f22
ENCODINGS = ["utf-8", "LATIN1", "cp1252", "iso-8859-1"]
MISSING_DATE = "1582-10-14"
REPLACEMENT_DATE = "1678-01-01"


# import of spss and stata files
def read_sav(filename: Path, missings=True, disable_datetime_conversion=True):
    kwargs = dict(
        user_missing=missings,
        dates_as_pandas_datetime=False,  # Do not interpret dates initially
    )
    filename = Path(filename)  # Ensure filename is a Path object
    extension = filename.suffix.lower()

    if extension not in ['.sav', '.dta']:
        raise ValueError("Unsupported file type!")

    # Try reading the file with different encodings
    for encoding in ENCODINGS:
        try:
            if extension == '.sav':
                df, meta = pyr.read_sav(filename, encoding=encoding, row_limit=ROW_LIMIT, **kwargs)
            elif extension == '.dta':
                df, meta = pyr.read_dta(filename, encoding=encoding, row_limit=ROW_LIMIT, **kwargs)
            # Fill NA values based on the data type of each column
            for col in df.columns:
                if df[col].dtype.kind in 'biufc':
                    df[col].fillna(pd.NA, inplace=True)
                    # Only convert to Int64 if all values are integers
                    if all(df[col].dropna().astype(float).map(float.is_integer)):
                        df[col] = df[col].astype('Int64')
                else:
                    df[col].fillna(np.nan, inplace=True)
            break
        except Exception as e:
            print(f"Failed to read file with encoding {encoding}: {e}")
            continue
    else:
        raise ValueError("Could not read file with any encoding!")

    # Manually handle the problematic date columns
    for col in df.columns:
        if "datetime" in str(df[col].dtype) or "date" in str(df[col].dtype):
            df[col] = df[col].apply(lambda x: REPLACEMENT_DATE if str(x) == MISSING_DATE else x)
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Recode string variables
    for var in df.columns:
        if df[var].dtype == 'string' or df[var].dtype == 'object':
            df[[var]].replace({'': pd.NA}, inplace=True)

    # Recode dtype for non-object columns and convert object columns to string type
    for col in df.columns:
        if df[col].dtype != 'string' and df[col].dtype != 'object':
            df[col] = df[col].convert_dtypes()

    df.replace({np.nan: None, pd.NA: None}, inplace=True)

    df.attrs["datafile"] = "file"
    return df, meta


###################################################################
def create_dataframe_from_dict(d: dict, column_names: list):
    if d:
        df_list = [{'name': k, column_names[1]: str(v)} for k, v in d.items()]  # Convert values to string
        return pd.DataFrame(df_list)
    else:
        return pd.DataFrame(columns=column_names)


def create_variable_view_common(df_meta):
    # Extract the attributes from df_meta
    label = df_meta.column_names_to_labels
    format = df_meta.original_variable_types
    measure = df_meta.variable_measure

    # Convert dictionaries into individual dataframes
    df_label = pd.DataFrame(list(label.items()), columns=['name', 'label'])
    df_format = pd.DataFrame(list(format.items()), columns=['name', 'format'])
    df_measure = pd.DataFrame(list(measure.items()), columns=['name', 'measure'])

    # Merge dataframes on the 'name' column
    variable_view = df_label \
        .merge(df_format, on='name', how='outer') \
        .merge(df_measure, on='name', how='outer')

    return variable_view


def create_variable_view(df_meta):
    if df_meta is None:
        raise ValueError("df_meta cannot be None")

    variable_view = create_variable_view_common(df_meta)

    # For values and missing, handle them differently due to dictionaries/lists inside
    df_values = create_dataframe_from_dict(df_meta.variable_value_labels, ['name', 'values'])
    df_missing = create_dataframe_from_dict(df_meta.missing_ranges, ['name', 'missing'])

    # Merge dataframes on the 'name' column
    if not df_values.empty:
        variable_view = variable_view.merge(df_values, on='name', how='outer')
    else:
        variable_view['values'] = pd.NA

    if not df_missing.empty:
        variable_view = variable_view.merge(df_missing, on='name', how='outer')
    else:
        variable_view['missing'] = pd.NA

    variable_view.replace({np.nan: None, pd.NA: None}, inplace=True)

    return variable_view[['name', 'format', 'label', 'values', 'missing', 'measure']]


def create_variable_view2(df_meta):
    if df_meta is None:
        raise ValueError("df_meta cannot be None")

    variable_view = create_variable_view_common(df_meta)

    # Convert user-defined missing values to the desired format
    missing = {}
    for key, vals in df_meta.missing_user_values.items():
        missing[key] = [{"lo": val, "hi": val} for val in vals]

    # For values and missing, handle them differently due to dictionaries/lists inside
    df_values = create_dataframe_from_dict(df_meta.variable_value_labels, ['name', 'values'])
    df_missing = create_dataframe_from_dict(missing, ['name', 'missing'])

    # Merge dataframes on the 'name' column
    if not df_values.empty:
        variable_view = variable_view.merge(df_values, on='name', how='outer')
    else:
        variable_view['values'] = pd.NA

    if not df_missing.empty:
        variable_view = variable_view.merge(df_missing, on='name', how='outer')
    else:
        variable_view['missing'] = pd.NA

    variable_view.replace({np.nan: None, pd.NA: None}, inplace=True)

    return variable_view[['name', 'format', 'label', 'values', 'missing', 'measure']]