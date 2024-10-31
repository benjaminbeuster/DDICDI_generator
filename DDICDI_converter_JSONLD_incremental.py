#!/usr/bin/env python
# coding: utf-8
import json
import numpy as np
import pandas as pd
import datetime

# Create functions
def generate_InstanceVariable(df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        elements = {
            "@id": f"#{variable}",
            "@type": "InstanceVariable",
            "name": variable,
            "displayLabel": df_meta.column_labels[idx],
            "hasIntendedDataType": df_meta.original_variable_types[variable],
            'takesSubstantiveConceptsFrom' : f"#substantiveConceptualDomain-{variable}"
        }
        # Check if variable has sentinel concepts
        if variable in df_meta.missing_ranges or (len(df_meta.missing_ranges) == 0 and variable in df_meta.missing_user_values):
            elements['takesSentinelConceptsFrom'] = f"#sentinelConceptualDomain-{variable}"

        json_ld_data.append(elements)

    return json_ld_data

# In[ ]:


# MeasureComponent
def generate_MeasureComponent(df_meta):
    json_ld_data = []
    for x, variable in enumerate(df_meta.column_names[1:]):
        elements = {
            "@id": f"#measureComponent-{variable}",
            "@type": "MeasureComponent",
            "isDefinedBy": f"#{variable}"
        }
        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# IdentifierComponent
def generate_IdentifierComponent(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#identifierComponent-{df_meta.column_names[0]}",
        "@type": "IdentifierComponent",
        "isDefinedBy": f"#{df_meta.column_names[0]}"
    }
    json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# logicalRecord
def generate_LogicalRecord(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#logicalRecord",
        "@type": "LogicalRecord",
        "organizes": f"#wideDataSet"
    }
    has = []
    for x, variable in enumerate(df_meta.column_names):
        has.append(f"#{variable}")
    elements['has'] = has
    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# PhysicalDataset
def generate_PhysicalDataset(df_meta, spssfile):
    json_ld_data = []
    elements = {
        "@id": f"#physicalDataset",
        "@type": "PhysicalDataset",
        "formats": "#dataStore",
        "physicalFileName": spssfile
    }
    has = ["#physicalRecordSegment"]
    elements['has'] = has
    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# DataStore
def generate_DataStore(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#dataStore",
        "@type": "DataStore",
        "allowsDuplicates": "false",
        "recordCount": df_meta.number_rows
    }
    has = ["#logicalRecord"]
    elements['has'] = has

    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# WideDataSet
def generate_WideDataSet(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#wideDataSet",
        "@type": "WideDataSet",
        "isStructuredBy": "#wideDataStructure"
    }

    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# WideDataStructure
def generate_WideDataStructure(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#wideDataStructure",
        "@type": "WideDataStructure",
    }
    has = ["#primaryKey", f"#identifierComponent-{df_meta.column_names[0]}"]

    for x, variable in enumerate(df_meta.column_names[1:]):
        has.append(f"#measureComponent-{variable}")
    elements['has'] = has

    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# PrimaryKey
def generate_PrimaryKey(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#primaryKey",
        "@type": "PrimaryKey",
        "isComposedOf": "#primaryKeyComponent"
    }

    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# PrimaryKeyComponent
def generate_PrimaryKeyComponent(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#primaryKeyComponent",
        "@type": "PrimaryKeyComponent",
        "correspondsTo": f"#identifierComponent-{df_meta.column_names[0]}"
    }

    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# PhysicalRecordSegment
def generate_PhysicalRecordSegment(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#physicalRecordSegment",
        "@type": "PhysicalRecordSegment",
        "mapsTo": "#logicalRecord",
    }
    has = ["#physicalSegmentLayout"]
    elements['has'] = has

    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# PhysicalSegmentLayout
def generate_PhysicalSegmentLayout(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#physicalSegmentLayout",
        "@type": "PhysicalSegmentLayout",
        "formats": "#logicalRecord",
        "isDelimited": "false",
        "delimiter": "",
    }
    has = []
    for x, variable in enumerate(df_meta.column_names):
        has.append(f"#valueMapping-{variable}")
        has.append(f"#valueMappingPosition-{variable}")
    elements['has'] = has
    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# ValueMapping
def generate_ValueMapping(df, df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        elements = {
            "@id": f"#valueMapping-{variable}",
            "@type": "ValueMapping",
        }
        datapoints = []
        for i, x in enumerate(df[variable]):
            datapoints.append(f"#{variable}-dataPoint-{i}")
        elements['formats'] = datapoints

        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# ValueMappingPosition
def generate_ValueMappingPosition(df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        elements = {
            "@id": f"#valueMappingPosition-{variable}",
            "@type": "ValueMappingPosition",
            "value": idx,
            "indexes": f"#valueMapping-{variable}"
        }
        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# DataPoint
def generate_DataPoint(df, df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for variable in (df_meta.column_names):
        for idx, value in enumerate(df[variable]):
            elements = {
                "@id": f"#{variable}-dataPoint-{idx}",
                "@type": "DataPoint",
                "isDescribedBy": f"#{variable}-instanceValue-{idx}"
            }

            json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# DataPointPosition
def generate_DataPointPosition(df, df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for variable in (df_meta.column_names):
        for idx, value in enumerate(df[variable]):
            elements = {
                "@id": f"#{variable}-dataPointPosition-{idx}",
                "@type": "DataPointPosition",
                "value": idx,
                "indexes": f"#{variable}-dataPoint-{idx}"
            }

            json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# SubstantiveValueDomain
def generate_SubstantiveValueDomain(df_meta):
    json_ld_data = []
    for x, variable in enumerate(df_meta.variable_value_labels):
        elements = {
            "@id": f"#substantiveValueDomain-{variable}",
            "@type": "SubstantiveValueDomain",
            "takesValuesFrom": f"#codelist.{variable}"
        }
        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# InstanceValue
def generate_InstanceValue(df, df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for variable in (df_meta.column_names):
        for idx, value in enumerate(df[variable]):
            elements = {
                "@id": f"#{variable}-instanceValue-{idx}",
                "@type": "InstanceValue",
                "content": value,
                "isStoredIn": f"#{variable}-dataPoint-{idx}"
            }

            json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# Codelist
def generate_Codelist(df_meta):
    json_ld_data = []
    for x, variable in enumerate(df_meta.variable_value_labels.items()):
        elements = {
            "@id": f"#codelist-{variable[x]}",
            "@type": "Codelist",
        }
        has = []
        your_dict = variable[1]
        # Loop through the dictionary and extract the keys
        for key in your_dict.keys():
            codes = {
                "@id": f"#code-{key}-{variable[x]}"
            }
            has.append(codes)
        elements['has'] = has

        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# Code
def generate_Code(df_meta):
    json_ld_data = []
    for x, variable in enumerate(df_meta.variable_value_labels.items()):
        your_dict = variable[1]
        # Loop through the dictionary and extract the keys
        for key, value in your_dict.items():
            elements = {
                "@id": f"#code-{key}-{variable[x]}",
                "@type": "Code",
            }
            has = []
            codes = {
                "@id": f"#{key}"
            }
            has.append(codes)
            elements['denotes'] = has

            has = []
            codes = {
                "@id": f"#{value}"
            }
            has.append(codes)
            elements['uses'] = has

            json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# SubstantiveConceptualDomain
def generate_SubstantiveConceptualDomain(df_meta):
    json_ld_data = []

    for var in df_meta.column_names:
        elements = {
            "@id": f"#substantiveConceptualDomain-{var}",
            "@type": "SubstantiveConceptualDomain",
            "isDescribedBy": f"#substantiveValueAndConceptDescription-{var}"
        }

        if var in df_meta.variable_value_labels:
            elements["takesConceptsFrom"] = f"#substantiveConceptScheme-{var}"

        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# SubstantiveConceptScheme
def generate_SubstantiveConceptScheme(df_meta):
    json_ld_data = []

    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    for variable_name, values_dict in df_meta.variable_value_labels.items():
        elements = {
            "@id": f"#substantiveConceptScheme-{variable_name}",
            "@type": "skos:ConceptScheme",
        }

        excluded_values = set()

        # Check if variable_name is in relevant_variables
        if variable_name in relevant_variables:

            # If the relevant variable data is based on ranges and contains dictionaries
            if isinstance(relevant_variables[variable_name], list) and all(
                    isinstance(item, dict) for item in relevant_variables[variable_name]):
                for dict_range in relevant_variables[variable_name]:
                    lo_is_numeric = isinstance(dict_range['lo'], (int, float)) or (
                            isinstance(dict_range['lo'], str) and dict_range['lo'].isnumeric()
                    )
                    hi_is_numeric = isinstance(dict_range['hi'], (int, float)) or (
                            isinstance(dict_range['hi'], str) and dict_range['hi'].isnumeric()
                    )

                    if lo_is_numeric and hi_is_numeric:
                        excluded_values.update(
                            range(int(float(dict_range['lo'])), int(float(dict_range['hi'])) + 1)
                        )
                    elif isinstance(dict_range['lo'], str):
                        excluded_values.add(dict_range['lo'])
                    else:
                        print(f"Warning: Unsupported 'lo' value: {dict_range['lo']}")

            # If the relevant variable data contains strings (user-defined missing values)
            elif isinstance(relevant_variables[variable_name], list):
                excluded_values.update(set(map(str, relevant_variables[variable_name])))

        # Use list comprehension to generate the hasTopConcept list
        excluded_values_str = {str(i) for i in excluded_values}
        has_top_concept = [
            f"#{variable_name}-concept-{value}"
            for value in values_dict.keys()
            if (not value in excluded_values) and (not str(value) in excluded_values_str)
        ]

        # Only add to json_ld_data if has_top_concept list is not empty
        if has_top_concept:
            elements['skos:hasTopConcept'] = has_top_concept
            json_ld_data.append(elements)

    return json_ld_data


# ValueAndConceptDescription
def generate_ValueAndConceptDescription(df_meta):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = {}
    if df_meta.missing_ranges:
        relevant_variables = df_meta.missing_ranges
    elif df_meta.missing_user_values:
        relevant_variables = df_meta.missing_user_values

    json_ld_data = []

    for variable in df_meta.column_names:
        # Add substantiveValueAndConceptDescription for every variable
        json_ld_data.append({
            "@id": f"#substantiveValueAndConceptDescription-{variable}",
            "@type": "ValueAndConceptDescription",
            "classificationLevel": f"{df_meta.variable_measure[variable]}"
        })

        # Add sentinelValueAndConceptDescription only if the condition is met
        if variable in relevant_variables:
            values = relevant_variables[variable]
            if isinstance(values[0], dict):  # Check if the values are dictionaries
                all_lo_values = [d['lo'] for d in values]
                all_hi_values = [d['hi'] for d in values]
                min_val = min(all_lo_values)
                max_val = max(all_hi_values)
            else:
                min_val, max_val = min(values), max(values)

            json_ld_data.append({
                "@id": f"#sentinelValueAndConceptDescription-{variable}",
                "@type": "ValueAndConceptDescription",
                "description": str(values),
                "minimumValueExclusive": str(min_val),
                "maximumValueExclusive": str(max_val),
            })

    return json_ld_data
# In[ ]:

# SentinelConceptualDomain
def generate_SentinelConceptualDomain(df_meta):
    json_ld_data = []

    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    for variable in relevant_variables:
        elements = {
            "@id": f"#sentinelConceptualDomain-{variable}",
            "@type": "SentinelConceptualDomain",
            "isDescribedBy": f"#sentinelValueAndConceptDescription-{variable}",
        }
        if variable in df_meta.variable_value_labels.keys():
            elements["takesConceptsFrom"] = f"#sentinelConceptScheme-{variable}"

        json_ld_data.append(elements)

    return json_ld_data

# SentinelConceptScheme
def generate_SentinelConceptScheme(df_meta):
    json_ld_data = []

    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    def is_value_in_range(value, ranges):
        """Check if a value is in any of the given ranges."""
        for range_dict in ranges:
            if range_dict['lo'] <= value <= range_dict['hi']:
                return True
        return False

    for variable_name, values_dict in df_meta.variable_value_labels.items():
        elements = {
            "@id": f"#sentinelConceptScheme-{variable_name}",
            "@type": "skos:ConceptScheme",
        }

        has_top_concept = []

        if variable_name in relevant_variables:
            if variable_name in df_meta.missing_ranges:
                # Use list comprehension to generate the hasTopConcept list
                has_top_concept = [
                    f"#{variable_name}-concept-{value}"
                    for value in values_dict.keys()
                    if is_value_in_range(value, df_meta.missing_ranges[variable_name])
                ]
            else:
                excluded_values = set(df_meta.missing_user_values[variable_name])
                has_top_concept = [
                    f"#{variable_name}-concept-{value}"
                    for value in values_dict.keys()
                    if value in excluded_values
                ]

        # Add the hasTopConcept list to elements
        elements['skos:hasTopConcept'] = has_top_concept

        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:

# Concept
def generate_Concept(df_meta):
    def is_value_in_excluded_ranges(value, excluded_ranges):
        # Ensure value is of the correct type
        if all(isinstance(i, float) for i in excluded_ranges):
            try:
                value = float(value)
            except ValueError:
                return False
        return value in excluded_ranges

    json_ld_data = []

    # Convert user-defined missing values to the desired format
    missing = df_meta.missing_ranges
    if len(missing) == 0:
        missing = {}
        for key, vals in df_meta.missing_user_values.items():
            missing[key] = [{"lo": val, "hi": val} for val in vals]

    for variable_name, values_dict in df_meta.variable_value_labels.items():
        # Check if variable_name is in missing and, if so, generate the excluded_ranges
        excluded_ranges = set()
        if variable_name in missing:
            for dict_range in missing[variable_name]:
                excluded_ranges.add(dict_range['lo'])
                if dict_range['lo'] != dict_range['hi']:
                    excluded_ranges.add(dict_range['hi'])

        # Iterate through values_dict and create elements, taking into account excluded_keys
        for key, value in values_dict.items():
            elements = {
                "@id": f"#{variable_name}-concept-{key}",
                "@type": "skos:Concept",
                "notation": key,
                "prefLabel": f"{value}",
            }

            # Add the inScheme key to elements based on whether the key is in excluded_ranges
            if is_value_in_excluded_ranges(key, excluded_ranges):
                elements['inScheme'] = f"#sentinelConceptScheme-{variable_name}"
            else:
                elements['inScheme'] = f"#substantiveConceptScheme-{variable_name}"

            # Append elements to json_ld_data inside the loop
            json_ld_data.append(elements)

    return json_ld_data


# create functions for updated key

# MeasureComponent2
def generate_MeasureComponent2(df_meta, varlist=None):
    json_ld_data = []
    for x, variable in enumerate(df_meta.column_names):
        if variable not in varlist:
            elements = {
                "@id": f"#measureComponent-{variable}",
                "@type": "MeasureComponent",
                "isDefinedBy": f"#{variable}"
            }
            json_ld_data.append(elements)

    return json_ld_data

# IdentifierComponent2
def generate_IdentifierComponent2(df_meta, varlist=None):
    json_ld_data = []
    for x, variable in enumerate(df_meta.column_names):
        if variable in varlist:
            elements = {
                "@id": f"#identifierComponent-{variable}",
                "@type": "IdentifierComponent",
                "isDefinedBy": f"#{variable}"
            }
            json_ld_data.append(elements)

    return json_ld_data


# WideDataStructure2
def generate_WideDataStructure2(df_meta, varlist=None):
    json_ld_data = []
    elements = {
        "@id": f"#wideDataStructure",
        "@type": "WideDataStructure",
    }
    has = ["#primaryKey"]

    for x, variable in enumerate(df_meta.column_names):
        if variable in varlist:
            has.append(f"#identifierComponent-{variable}")
        else:
            has.append(f"#measureComponent-{variable}")
    elements['has'] = has

    json_ld_data.append(elements)
    return json_ld_data


# PrimaryKeyComponent2
def generate_PrimaryKeyComponent2(df_meta, varlist=None):
    json_ld_data = []
    elements = {
        "@id": "#primaryKeyComponent",
        "@type": "PrimaryKeyComponent",
    }
    has = []
    for variable in varlist:
        has.append(f"#identifierComponent-{variable}")

    elements['correspondsTo'] = has
    json_ld_data.append(elements)
    return json_ld_data

# PrimaryKey2
def generate_PrimaryKey2(df_meta, varlist=None):
    json_ld_data = []
    elements = {
        "@id": "#primaryKey",
        "@type": "PrimaryKey",
    }
    
    has = []
    for variable in varlist:
        has.append(f"#identifierComponent-{variable}")
    
    elements['isComposedOf'] = has
    json_ld_data.append(elements)
    return json_ld_data


################################################################################

def generate_complete_json_ld(df, df_meta, spssfile='name'):
    # ... [all your function definitions here]

    # Generate JSON-LD
    InstanceVariable = generate_InstanceVariable(df_meta)
    SubstantiveConceptualDomain = generate_SubstantiveConceptualDomain(df_meta)
    SentinelConceptualDomain = generate_SentinelConceptualDomain(df_meta)
    ValueAndConceptDescription = generate_ValueAndConceptDescription(df_meta)
    SubstantiveConceptScheme = generate_SubstantiveConceptScheme(df_meta)
    SentinelConceptScheme = generate_SentinelConceptScheme(df_meta)
    Concept = generate_Concept(df_meta)
    LogicalRecord = generate_LogicalRecord(df_meta)
    PhysicalDataset = generate_PhysicalDataset(df_meta, spssfile)
    PhysicalRecordSegment = generate_PhysicalRecordSegment(df_meta)
    PhysicalSegmentLayout = generate_PhysicalSegmentLayout(df_meta)
    ValueMapping = generate_ValueMapping(df, df_meta)
    ValueMappingPosition = generate_ValueMappingPosition(df_meta)
    InstanceValue = generate_InstanceValue(df, df_meta)
    DataPoint = generate_DataPoint(df, df_meta)
    DataPointPosition = generate_DataPointPosition(df, df_meta)
    DataStore = generate_DataStore(df_meta)
    WideDataSet = generate_WideDataSet(df_meta)
    WideDataStructure = generate_WideDataStructure(df_meta)
    PrimaryKey = generate_PrimaryKey(df_meta)
    PrimaryKeyComponent = generate_PrimaryKeyComponent(df_meta)
    MeasureComponent = generate_MeasureComponent(df_meta)
    IdentifierComponent = generate_IdentifierComponent(df_meta)

    json_ld_graph = DataStore + LogicalRecord + WideDataSet + \
                    WideDataStructure + IdentifierComponent + MeasureComponent + PrimaryKey + PrimaryKeyComponent + InstanceVariable + \
                    SubstantiveConceptualDomain + SubstantiveConceptScheme + SentinelConceptualDomain + ValueAndConceptDescription + \
                    SentinelConceptScheme + Concept + PhysicalDataset + PhysicalRecordSegment + PhysicalSegmentLayout + ValueMapping + \
                    ValueMappingPosition + DataPoint + DataPointPosition + InstanceValue
    # Create a dictionary with the specified "@context" and "@graph" keys
    json_ld_dict = {
        "@context": [
            "https://ddi-alliance.bitbucket.io/DDI-CDI/DDI-CDI_v1.0-rc1/encoding/json-ld/ddi-cdi.jsonld",
            {
                "skos": "http://www.w3.org/2004/02/skos/core#"
            }
        ],
        "@graph": json_ld_graph
    }
    def default_encode(obj):
        if isinstance(obj, np.int64):
            return int(obj)
        elif pd.isna(obj):  # Checks for pd.NA
            return None
        elif isinstance(obj, pd.Timestamp):  # Checks for Timestamp
            return obj.isoformat()
        # Add handling for datetime objects
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # Convert the Python dictionary to a JSON string with pretty formatting
    json_ld_string = json.dumps(json_ld_dict, indent=4, default=default_encode)

    return json_ld_string


###################################################################################################

def generate_complete_json_ld2(df, df_meta, vars=None, spssfile='name'):
    # ... [all your function definitions here]

    # Generate JSON-LD
    InstanceVariable = generate_InstanceVariable(df_meta)
    SubstantiveConceptualDomain = generate_SubstantiveConceptualDomain(df_meta)
    SentinelConceptualDomain = generate_SentinelConceptualDomain(df_meta)
    ValueAndConceptDescription = generate_ValueAndConceptDescription(df_meta)
    SubstantiveConceptScheme = generate_SubstantiveConceptScheme(df_meta)
    SentinelConceptScheme = generate_SentinelConceptScheme(df_meta)
    Concept = generate_Concept(df_meta)
    LogicalRecord = generate_LogicalRecord(df_meta)
    PhysicalDataset = generate_PhysicalDataset(df_meta, spssfile)
    PhysicalRecordSegment = generate_PhysicalRecordSegment(df_meta)
    PhysicalSegmentLayout = generate_PhysicalSegmentLayout(df_meta)
    ValueMapping = generate_ValueMapping(df, df_meta)
    ValueMappingPosition = generate_ValueMappingPosition(df_meta)
    InstanceValue = generate_InstanceValue(df, df_meta)
    DataPoint = generate_DataPoint(df, df_meta)
    DataPointPosition = generate_DataPointPosition(df, df_meta)
    DataStore = generate_DataStore(df_meta)
    WideDataSet = generate_WideDataSet(df_meta)
    WideDataStructure = generate_WideDataStructure2(df_meta, vars)
    PrimaryKey = generate_PrimaryKey2(df_meta, vars)
    PrimaryKeyComponent = generate_PrimaryKeyComponent2(df_meta, vars)
    MeasureComponent = generate_MeasureComponent2(df_meta, vars)
    IdentifierComponent = generate_IdentifierComponent2(df_meta, vars)

    json_ld_graph = DataStore + LogicalRecord + WideDataSet + \
                    WideDataStructure + IdentifierComponent + MeasureComponent + PrimaryKey + PrimaryKeyComponent + InstanceVariable + \
                    SubstantiveConceptualDomain + SubstantiveConceptScheme + SentinelConceptualDomain + ValueAndConceptDescription + \
                    SentinelConceptScheme + Concept + PhysicalDataset + PhysicalRecordSegment + PhysicalSegmentLayout + ValueMapping + \
                    ValueMappingPosition + DataPoint + DataPointPosition + InstanceValue
    # Create a dictionary with the specified "@context" and "@graph" keys
    json_ld_dict = {
        "@context": [
            "https://ddi-alliance.bitbucket.io/DDI-CDI/DDI-CDI_v1.0-rc1/encoding/json-ld/ddi-cdi.jsonld",
            {
                "skos": "http://www.w3.org/2004/02/skos/core#"
            }
        ],
        "@graph": json_ld_graph
    }
    def default_encode(obj):
        if isinstance(obj, np.int64):
            return int(obj)
        elif pd.isna(obj):  # Checks for pd.NA
            return None
        elif isinstance(obj, pd.Timestamp):  # Checks for Timestamp
            return obj.isoformat()
        # Add handling for datetime objects
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # Convert the Python dictionary to a JSON string with pretty formatting
    json_ld_string = json.dumps(json_ld_dict, indent=4, default=default_encode)

    return json_ld_string