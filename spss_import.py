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
ROW_LIMIT = 11
#, row_limit=ROW_LIMIT,

ENCODINGS = ["utf-8", "LATIN1", "cp1252", "iso-8859-1"]
MISSING_DATE = "1582-10-14"
REPLACEMENT_DATE = "1678-01-01"


# import of spss and stata files
def read_sav(filename: Path, missings=True, disable_datetime_conversion=True):
    print("Starting read_sav")
    try:
        # Read the SPSS file
        print("About to read file with pyreadstat")
        df, meta = pyr.read_sav(
            filename,
            apply_value_formats=False,
            row_limit=5
        )
        print("File read successful")
        
        # Store the filename
        meta.datafile = filename
        
        print("Returning values")
        return df, meta, filename, meta.number_rows
        
    except Exception as e:
        print(f"Error in read_sav: {str(e)}")
        raise


def read_dta(filename: Path, missings=True, disable_datetime_conversion=True):
    print("Starting read_dta")
    try:
        # Read the Stata file
        print("About to read file with pyreadstat")
        df, meta = pyr.read_dta(
            filename,
            apply_value_formats=False,
            row_limit=5
        )
        print("File read successful")
        
        # Store the filename
        meta.datafile = filename
        
        print("Returning values")
        return df, meta, filename, meta.number_rows
        
    except Exception as e:
        print(f"Error in read_dta: {str(e)}")
        raise


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