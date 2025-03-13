from __future__ import annotations
import typing as t
from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat as pyr
from collections import namedtuple

# Set pandas options
pd.set_option('display.max_rows', 2500)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# Define constants
ROW_LIMIT = 10000000
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
        raise ValueError(f"Unsupported file type for read_sav! Expected .sav or .dta, got: {extension}")

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

    # Store filename in meta
    meta.datafile = filename
    
    # Return all expected values
    return df, meta, str(filename), meta.number_rows


def read_csv(filename: Path, delimiter=',', header=0, encoding=None, infer_types=True, date_format=None, dayfirst=False, **kwargs):
    """
    Read CSV file and create a metadata structure compatible with what pyreadstat returns
    
    Parameters:
    -----------
    filename : Path
        Path to the CSV file
    delimiter : str, default ','
        Character or regex pattern to separate fields
    header : int, default 0
        Row number to use as column names
    encoding : str, default None
        File encoding (will try multiple encodings if None)
    infer_types : bool, default True
        Attempt to infer data types from the data
    date_format : str, default None
        Format string for parsing dates (e.g., '%d/%m/%Y'). If None, tries to infer.
    dayfirst : bool, default False
        When parsing dates without a specified format, interpret the first value as day (European style)
    **kwargs : dict
        Additional arguments passed to pandas read_csv function
        
    Returns:
    --------
    tuple : (DataFrame, metadata, filename, number_rows)
    """
    filename = Path(filename)  # Ensure filename is a Path object
    
    # Try reading the file with different encodings if not specified
    if encoding:
        encodings = [encoding]
    else:
        encodings = ENCODINGS
    
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(filename, delimiter=delimiter, header=header, encoding=enc, 
                            low_memory=False, **kwargs)
            break
        except Exception as e:
            print(f"Failed to read file with encoding {enc}: {e}")
            continue
    
    if df is None:
        raise ValueError("Could not read file with any encoding!")
    
    # Create a custom mutable metadata class instead of a namedtuple
    class CSVMetadata:
        """Mutable metadata class for CSV files, compatible with pyreadstat's metadata structure"""
        def __init__(self, column_names, column_names_to_labels, original_variable_types,
                    variable_value_labels, missing_ranges, variable_measure, number_rows,
                    datafile, missing_user_values, measure_vars, identifier_vars, attribute_vars):
            self.column_names = column_names
            self.column_names_to_labels = column_names_to_labels
            self.column_labels = column_names_to_labels  # Add this alias for compatibility
            self.original_variable_types = original_variable_types
            self.readstat_variable_types = original_variable_types  # Add this alias for compatibility
            self.variable_value_labels = variable_value_labels
            self.missing_ranges = missing_ranges
            self.variable_measure = variable_measure
            self.number_rows = number_rows
            self.datafile = datafile
            self.missing_user_values = missing_user_values
            self.measure_vars = measure_vars
            self.identifier_vars = identifier_vars
            self.attribute_vars = attribute_vars
    
    # Infer data types if requested
    if infer_types:
        df = df.convert_dtypes()
    
    # Create column labels (same as column names in CSV)
    column_names = list(df.columns)
    column_labels = {col: col for col in column_names}
    
    # Determine variable types
    variable_types = {}
    measure_types = {}
    
    for col in column_names:
        dtype = df[col].dtype
        
        # Determine format type
        if pd.api.types.is_numeric_dtype(dtype):
            if pd.api.types.is_integer_dtype(dtype):
                variable_types[col] = 'numeric'
                measure_types[col] = 'scale'
            elif pd.api.types.is_float_dtype(dtype):
                variable_types[col] = 'numeric'
                measure_types[col] = 'scale'
        elif pd.api.types.is_datetime64_dtype(dtype):
            variable_types[col] = 'datetime'
            measure_types[col] = 'scale'
        else:
            variable_types[col] = 'string'
            measure_types[col] = 'nominal'
            
    # Process data
    for col in df.columns:
        if df[col].dtype.kind in 'biufc':
            df[col].fillna(pd.NA, inplace=True)
            # Only convert to Int64 if all values are integers
            if all(df[col].dropna().astype(float).map(float.is_integer)):
                df[col] = df[col].astype('Int64')
        else:
            df[col].fillna(np.nan, inplace=True)
    
    # Improved date column detection and parsing
    date_columns = []
    
    # Function to safely check if a column sample contains date-like strings
    def has_date_strings(series):
        # Check a sample of non-null values (up to 10)
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
            
        # Simple patterns that often indicate dates
        date_patterns = [
            r'\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}',  # DD/MM/YYYY, MM/DD/YYYY, etc.
            r'\d{4}[/.-]\d{1,2}[/.-]\d{1,2}',    # YYYY/MM/DD, etc.
            r'\d{1,2}[-]\w{3}[-]\d{2,4}',        # DD-MMM-YYYY, etc.
            r'\w{3}[-]\d{1,2}[-]\d{2,4}'         # MMM-DD-YYYY, etc.
        ]
        
        import re
        for val in sample:
            if val is None or pd.isna(val):
                continue
            val_str = str(val)
            for pattern in date_patterns:
                if re.search(pattern, val_str):
                    return True
        return False
    
    # First, identify date columns by name and content
    for col in df.columns:
        is_date_by_name = any(keyword in col.lower() for keyword in ['date', 'time', 'day', 'month', 'year', 'dt'])
        
        # If column name suggests date and content is string, check content
        if is_date_by_name and df[col].dtype.kind in ['O', 'S', 'U']:
            if has_date_strings(df[col]):
                try:
                    # Try parsing with explicit format if provided
                    if date_format:
                        df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
                    else:
                        # Otherwise use pandas inference with dayfirst parameter
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=dayfirst)
                    
                    if not df[col].isna().all():  # If we successfully parsed some dates
                        date_columns.append(col)
                        variable_types[col] = 'datetime'
                        measure_types[col] = 'scale'
                        print(f"Successfully converted column '{col}' to datetime")
                except Exception as e:
                    print(f"Could not convert column '{col}' to datetime: {e}")
        
        # Also check columns that don't have date-like names but might contain dates
        elif df[col].dtype.kind in ['O', 'S', 'U'] and has_date_strings(df[col]):
            try:
                # Try parsing with explicit format if provided
                if date_format:
                    df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
                else:
                    # Otherwise use pandas inference with dayfirst parameter
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=dayfirst)
                
                if not df[col].isna().all():  # If we successfully parsed some dates
                    date_columns.append(col)
                    variable_types[col] = 'datetime'
                    measure_types[col] = 'scale'
                    print(f"Successfully converted column '{col}' to datetime based on content")
            except Exception as e:
                print(f"Could not convert column '{col}' to datetime: {e}")
    
    # Recode string variables
    for var in df.columns:
        if df[var].dtype == 'string' or df[var].dtype == 'object':
            df[[var]].replace({'': pd.NA}, inplace=True)
    
    # No value labels for CSV, create empty dict
    value_labels = {}
    missing_ranges = {}
    missing_user_values = {}
    
    # Replace NaN with None
    df.replace({np.nan: None, pd.NA: None}, inplace=True)
    
    # Create metadata
    meta = CSVMetadata(
        column_names=column_names,
        column_names_to_labels=column_labels,
        original_variable_types=variable_types,
        variable_value_labels=value_labels,
        missing_ranges=missing_ranges,
        variable_measure=measure_types,
        number_rows=len(df),
        datafile=filename,
        missing_user_values=missing_user_values,
        measure_vars=column_names,  # By default, treat all columns as measure variables
        identifier_vars=[],         # Start with empty list of identifiers
        attribute_vars=[]           # Start with empty list of attributes
    )
    
    return df, meta, str(filename), meta.number_rows


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

    # Handle missing values for Stata files
    missing = {}
    if hasattr(df_meta, 'missing_user_values') and df_meta.missing_user_values:
        for key, vals in df_meta.missing_user_values.items():
            missing[key] = [{"lo": val, "hi": val} for val in vals]

    # For values and missing, handle them differently due to dictionaries/lists inside
    df_values = create_dataframe_from_dict(df_meta.variable_value_labels, ['name', 'values'])
    df_missing = create_dataframe_from_dict(missing, ['name', 'missing'])

    # Debug print
    print("Stata missing values found:", df_meta.missing_user_values if hasattr(df_meta, 'missing_user_values') else None)
    print("Converted missing values:", missing)
    print("Missing values DataFrame:", df_missing)

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