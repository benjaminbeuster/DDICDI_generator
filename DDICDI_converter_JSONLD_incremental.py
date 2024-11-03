#!/usr/bin/env python
# coding: utf-8
import json
import numpy as np
import pandas as pd
import datetime

# PhysicalDataSetStructure
def generate_PhysicalDataSetStructure(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#physicalDataSetStructure",
        "@type": "PhysicalDataSetStructure",
        "correspondsTo_DataStructure": "#wideDataStructure",
        "structures": "#physicalDataSet"
    }
    json_ld_data.append(elements)
    return json_ld_data

# PhysicalDataset
def generate_PhysicalDataset(df_meta, spssfile):
    json_ld_data = []
    elements = {
        "@id": f"#physicalDataSet",
        "@type": "PhysicalDataset",
        "allowsDuplicates": False,
        "physicalFileName": spssfile,
        "correspondsTo_DataSet": "#wideDataSet",
        "formats": "#dataStore",
        "has_PhysicalRecordSegment": ["#physicalRecordSegment"]
    }
    json_ld_data.append(elements)
    return json_ld_data


# PhysicalRecordSegment
def generate_PhysicalRecordSegment(df_meta, df):
    json_ld_data = []
    elements = {
        "@id": f"#physicalRecordSegment",
        "@type": "PhysicalRecordSegment",
        "allowsDuplicates": False,
        "mapsTo": "#logicalRecord",
        "has_PhysicalSegmentLayout": "#physicalSegmentLayout",
        "has_DataPointPosition": []
    }

    # Iterate through column names and their values to add DataPointPosition references
    for variable in df_meta.column_names:
        for i in range(len(df[variable])):
            elements["has_DataPointPosition"].append(f"#dataPointPosition-{i}-{variable}")

    json_ld_data.append(elements)
    return json_ld_data



# PhysicalSegmentLayout
def generate_PhysicalSegmentLayout(df_meta):
    json_ld_data = []
    elements = {
        "@id": f"#physicalSegmentLayout",
        "@type": "PhysicalSegmentLayout",
        "allowsDuplicates": False,
        "formats": "#logicalRecord",
        "isDelimited": False,
        "isFixedWidth": False,
        "delimiter": "",
        "has_ValueMapping": [],
        "has_ValueMappingPosition": []
    }
    
    # Add both ValueMapping and ValueMappingPosition references for each variable
    for variable in df_meta.column_names:
        elements["has_ValueMapping"].append(f"#valueMapping-{variable}")
        elements["has_ValueMappingPosition"].append(f"#valueMappingPosition-{variable}")
        
    json_ld_data.append(elements)
    return json_ld_data

# ValueMapping
def generate_ValueMapping(df, df_meta):
    json_ld_data = []

    # Iterate through column names
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#valueMapping-{variable}",
            "@type": "ValueMapping",
            "defaultValue": "",
            "formats": []  # Will store DataPoint references
        }
        
        # Add DataPoint references for each value in the variable
        for i in range(len(df[variable])):
            elements["formats"].append(f"#dataPoint-{i}-{variable}")

        json_ld_data.append(elements)

    return json_ld_data



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


# DataPoint
def generate_DataPoint(df, df_meta):
    json_ld_data = []

    # Iterate through column names
    for variable in df_meta.column_names:
        # For each value in the variable
        for idx in range(len(df[variable])):
            elements = {
                "@id": f"#dataPoint-{idx}-{variable}",
                "@type": "DataPoint",
                "isDescribedBy": f"#instanceVariable-{variable}"
            }
            json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# DataPointPosition
def generate_DataPointPosition(df, df_meta):
    json_ld_data = []

    # Iterate through column names
    for variable in df_meta.column_names:
        # For each value in the variable
        for idx in range(len(df[variable])):
            elements = {
                "@id": f"#dataPointPosition-{idx}-{variable}",
                "@type": "DataPointPosition",
                "value": idx,
                "indexes": f"#dataPoint-{idx}-{variable}"
            }
            json_ld_data.append(elements)

    return json_ld_data

# InstanceValue
def generate_InstanceValue(df, df_meta):
    json_ld_data = []

    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    # Iterate through column names and associated index
    for variable in df_meta.column_names:
        for idx, value in enumerate(df[variable]):
            elements = {
                "@id": f"#instanceValue-{idx}-{variable}",
                "@type": "InstanceValue",
                "content": value,
                "isStoredIn": f"#dataPoint-{idx}-{variable}"
            }

            # Check if variable has missing ranges and value is within those ranges
            if variable in df_meta.missing_ranges:
                is_sentinel = False
                for range_dict in df_meta.missing_ranges[variable]:
                    if value is not None and isinstance(range_dict['lo'], float):
                        # Convert value to float for comparison
                        try:
                            value_float = float(value)
                            if range_dict['lo'] <= value_float <= range_dict['hi']:
                                elements["hasValueFrom_ValueDomain"] = f"#sentinelValueDomain-{variable}"
                                is_sentinel = True
                                break
                        except (ValueError, TypeError):
                            pass
                
                if not is_sentinel:
                    elements["hasValueFrom_ValueDomain"] = f"#substantiveValueDomain-{variable}"
            else:
                elements["hasValueFrom_ValueDomain"] = f"#substantiveValueDomain-{variable}"

            json_ld_data.append(elements)

    return json_ld_data


# DataStore
def generate_DataStore(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#dataStore",
        "@type": "DataStore",
        "allowsDuplicates": False,
        "recordCount": df_meta.number_rows,
        "has_LogicalRecord": ["#logicalRecord"]
    }
    json_ld_data.append(elements)
    return json_ld_data


# logicalRecord
def generate_LogicalRecord(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#logicalRecord",
        "@type": "LogicalRecord",
        "organizes": "#wideDataSet",
        "has_InstanceVariable": []
    }
    
    # Add InstanceVariable references with consistent ID naming
    for variable in df_meta.column_names:
        elements["has_InstanceVariable"].append(f"#instanceVariable-{variable}")
    
    json_ld_data.append(elements)
    return json_ld_data


# WideDataSet
def generate_WideDataSet(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#wideDataSet",
        "@type": "WideDataSet",
        "isStructuredBy": "#wideDataStructure"
    }

    json_ld_data.append(elements)
    return json_ld_data


# WideDataStructure
def generate_WideDataStructure(df_meta, vars=None):
    json_ld_data = []
    elements = {
        "@id": "#wideDataStructure",
        "@type": "WideDataStructure",
        "has_PrimaryKey": "#primaryKey",
        "has_DataStructureComponent": []
    }
    
    # If vars is None, treat all columns as measure components
    if vars is None:
        for variable in df_meta.column_names:
            elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")
    else:
        # Add identifier components for variables in vars
        for variable in vars:
            elements["has_DataStructureComponent"].append(f"#identifierComponent-{variable}")
        
        # Add measure components for variables not in vars
        for variable in df_meta.column_names:
            if variable not in vars:
                elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")

    json_ld_data.append(elements)
    return json_ld_data

# MeasureComponent
def generate_MeasureComponent(df_meta):
    json_ld_data = []
    # Process all columns, not just those after the first
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#measureComponent-{variable}",
            "@type": "MeasureComponent",
            # Point to instanceVariable instead of just variable
            "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
        }
        json_ld_data.append(elements)

    return json_ld_data


# In[ ]:


# IdentifierComponent
def generate_IdentifierComponent(df_meta, vars=None):
    json_ld_data = []
    
    # Only generate IdentifierComponents if vars is provided
    if vars is not None:
        for var in vars:
            elements = {
                "@id": f"#identifierComponent-{var}",
                "@type": "IdentifierComponent",
                "isDefinedBy_RepresentedVariable": f"#instanceVariable-{var}"
            }
            json_ld_data.append(elements)

    return json_ld_data




# In[ ]:


# PrimaryKey
def generate_PrimaryKey(df_meta, vars=None):
    json_ld_data = []
    elements = {
        "@id": "#primaryKey",
        "@type": "PrimaryKey",
        "isComposedOf": []
    }
    
    # Add primary key components if vars is provided
    if vars is not None:
        for var in vars:
            elements["isComposedOf"].append(f"#primaryKeyComponent-{var}")
    
    json_ld_data.append(elements)
    return json_ld_data


# In[ ]:


# PrimaryKeyComponent
def generate_PrimaryKeyComponent(df_meta, vars=None):
    json_ld_data = []
    
    if vars is not None:
        for var in vars:
            elements = {
                "@id": f"#primaryKeyComponent-{var}",
                "@type": "PrimaryKeyComponent",
                "correspondsTo_DataStructureComponent": f"#identifierComponent-{var}"
            }
            json_ld_data.append(elements)

    return json_ld_data

def generate_InstanceVariable(df_meta):
    json_ld_data = []

    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        elements = {
            "@id": f"#instanceVariable-{variable}",
            "@type": "InstanceVariable",
            "name": variable,
            "displayLabel": df_meta.column_labels[idx],
            "hasIntendedDataType": df_meta.original_variable_types[variable],
            "has_PhysicalSegmentLayout": "#physicalSegmentLayout",
            "has_ValueMapping": f"#valueMapping-{variable}",
            'takesSubstantiveConceptsFrom': f"#substantiveConceptualDomain-{variable}"
        }
        
        # Check if variable has sentinel concepts
        if variable in df_meta.missing_ranges or (len(df_meta.missing_ranges) == 0 and variable in df_meta.missing_user_values):
            elements['takesSentinelConceptsFrom'] = f"#sentinelConceptualDomain-{variable}"

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

    # Recode classification level
    class_level = {
        'nominal': 'Nominal',
        'scale': 'Continuous', 
        'ordinal': 'Ordinal',
        'unknown': 'Nominal'
    }

    json_ld_data = []

    for variable in df_meta.column_names:
        # Add substantiveValueAndConceptDescription for every variable
        json_ld_data.append({
            "@id": f"#substantiveValueAndConceptDescription-{variable}",
            "@type": "ValueAndConceptDescription",
            "classificationLevel": class_level.get(df_meta.variable_measure[variable].lower(), 'Nominal')
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
                "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
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
                "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
            }
            json_ld_data.append(elements)

    return json_ld_data


# WideDataStructure2
def generate_WideDataStructure2(df_meta, varlist=None):
    json_ld_data = []
    elements = {
        "@id": f"#wideDataStructure",
        "@type": "WideDataStructure",
        "has_PrimaryKey": "#primaryKey",
        "has_DataStructureComponent": []
    }

    for variable in df_meta.column_names:
        if variable in varlist:
            elements["has_DataStructureComponent"].append(f"#identifierComponent-{variable}")
        else:
            elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")

    json_ld_data.append(elements)
    return json_ld_data


# PrimaryKeyComponent2
def generate_PrimaryKeyComponent2(df_meta, varlist=None):
    json_ld_data = []
    if varlist:
        for var in varlist:
            elements = {
                "@id": f"#primaryKeyComponent-{var}",
                "@type": "PrimaryKeyComponent",
                "correspondsTo_DataStructureComponent": f"#identifierComponent-{var}"
            }
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

def wrap_in_graph(*components):
    """Helper function to wrap components in a valid PhysicalDataSetStructure"""
    # Flatten all components into a single list
    all_components = [item for sublist in components for item in sublist]
    
    # Create the root structure
    root_structure = {
        "@context": [
            "https://ddi-cdi.github.io/ddi-cdi_v1.0-post/encoding/json-ld/ddi-cdi.jsonld",
            {
                "skos": "http://www.w3.org/2004/02/skos/core#"
            }
        ],
        "@id": "#physicalDataSetStructure",
        "@type": "PhysicalDataSetStructure",
        "correspondsTo_DataStructure": "#wideDataStructure",
        "structures": "#physicalDataSet"
    }
    
    # Add all other components as separate objects at the root level
    return [root_structure] + all_components

def generate_complete_json_ld(df, df_meta, spssfile='name'):
    # Generate all components
    components = [
        generate_PhysicalDataSetStructure(df_meta),
        generate_PhysicalDataset(df_meta, spssfile),
        generate_PhysicalRecordSegment(df_meta, df),
        generate_PhysicalSegmentLayout(df_meta),
        generate_ValueMapping(df, df_meta),
        generate_ValueMappingPosition(df_meta),
        generate_DataPoint(df, df_meta),
        generate_DataPointPosition(df, df_meta),
        generate_InstanceValue(df, df_meta),
        generate_DataStore(df_meta),
        generate_LogicalRecord(df_meta),
        generate_WideDataSet(df_meta),
        generate_WideDataStructure(df_meta),
        generate_MeasureComponent(df_meta),
        generate_IdentifierComponent(df_meta),
        generate_PrimaryKey(df_meta),
        generate_PrimaryKeyComponent(df_meta),
        generate_InstanceVariable(df_meta),
        generate_SubstantiveConceptualDomain(df_meta),
        generate_SentinelConceptualDomain(df_meta),
        generate_ValueAndConceptDescription(df_meta),
        generate_SubstantiveConceptScheme(df_meta),
        generate_SentinelConceptScheme(df_meta),
        generate_Concept(df_meta)
    ]
    
    # Get the flattened list of all components
    all_objects = wrap_in_graph(*components)
    
    # Create the final JSON-LD document
    json_ld_doc = {
        "@context": [
            "https://ddi-cdi.github.io/ddi-cdi_v1.0-post/encoding/json-ld/ddi-cdi.jsonld",
            {
                "skos": "http://www.w3.org/2004/02/skos/core#"
            }
        ],
        "@graph": all_objects
    }

    def default_encode(obj):
        if isinstance(obj, np.int64):
            return int(obj)
        elif pd.isna(obj):
            return None
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # Convert to JSON string
    return json.dumps(json_ld_doc, indent=4, default=default_encode)


###################################################################################################

def generate_complete_json_ld2(df, df_meta, vars=None, spssfile='name'):
    # Generate all components
    components = [
        generate_PhysicalDataSetStructure(df_meta),
        generate_DataStore(df_meta),
        generate_LogicalRecord(df_meta),
        generate_WideDataSet(df_meta),
        generate_WideDataStructure2(df_meta, vars),
        generate_IdentifierComponent2(df_meta, vars),
        generate_MeasureComponent2(df_meta, vars),
        generate_PrimaryKey2(df_meta, vars),
        generate_PrimaryKeyComponent(df_meta, vars),
        generate_InstanceVariable(df_meta),
        generate_SubstantiveConceptualDomain(df_meta),
        generate_SubstantiveConceptScheme(df_meta),
        generate_SentinelConceptualDomain(df_meta),
        generate_SentinelConceptScheme(df_meta),
        generate_ValueAndConceptDescription(df_meta),
        generate_Concept(df_meta),
        generate_PhysicalDataset(df_meta, spssfile),
        generate_PhysicalRecordSegment(df_meta, df),
        generate_PhysicalSegmentLayout(df_meta),
        generate_ValueMapping(df, df_meta),
        generate_ValueMappingPosition(df_meta),
        generate_DataPoint(df, df_meta),
        generate_DataPointPosition(df, df_meta),
        generate_InstanceValue(df, df_meta)
    ]
    
    # Wrap in graph structure
    json_ld_graph = wrap_in_graph(*components)

    def default_encode(obj):
        if isinstance(obj, np.int64):
            return int(obj)
        elif pd.isna(obj):  # Checks for pd.NA
            return None
        elif isinstance(obj, pd.Timestamp):  # Checks for Timestamp
            return obj.isoformat()
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # Convert to JSON string
    return json.dumps(json_ld_graph, indent=4, default=default_encode)

