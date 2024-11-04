#!/usr/bin/env python
# coding: utf-8
import json
import numpy as np
import pandas as pd
import datetime

# Core functions
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

def generate_PhysicalDataset(df_meta, spssfile):
    json_ld_data = []
    elements = {
        "@id": f"#physicalDataSet",
        "@type": "PhysicalDataSet",
        "allowsDuplicates": False,
        "physicalFileName": spssfile,
        "correspondsTo_DataSet": "#wideDataSet",
        "formats": "#dataStore",
        "has_PhysicalRecordSegment": ["#physicalRecordSegment"]
    }
    json_ld_data.append(elements)
    return json_ld_data

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

def generate_WideDataSet(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#wideDataSet",
        "@type": "WideDataSet",
        "isStructuredBy": "#wideDataStructure"
    }

    json_ld_data.append(elements)
    return json_ld_data

def generate_WideDataStructure(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#wideDataStructure",
        "@type": "WideDataStructure",
        "has_DataStructureComponent": []
    }
    
    # Add primary key if we have identifier variables
    if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
        elements["has_PrimaryKey"] = "#primaryKey"
        # Add identifier components first
        for variable in df_meta.identifier_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements["has_DataStructureComponent"].append(f"#identifierComponent-{variable}")
    
    # Add attribute components second
    if hasattr(df_meta, 'attribute_vars') and df_meta.attribute_vars:
        for variable in df_meta.attribute_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements["has_DataStructureComponent"].append(f"#attributeComponent-{variable}")
    
    # Add measure components last
    if hasattr(df_meta, 'measure_vars') and df_meta.measure_vars:
        for variable in df_meta.measure_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")
    else:
        # Fallback: if no measure_vars defined, use all remaining variables as measures
        used_vars = set((getattr(df_meta, 'identifier_vars', []) + 
                        getattr(df_meta, 'attribute_vars', [])))
        for variable in df_meta.column_names:
            if variable not in used_vars:
                elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")

    json_ld_data.append(elements)
    return json_ld_data

def generate_MeasureComponent(df_meta):
    json_ld_data = []
    # First check if measure_vars exists and has content
    if hasattr(df_meta, 'measure_vars') and df_meta.measure_vars:
        for variable in df_meta.measure_vars:
            elements = {
                "@id": f"#measureComponent-{variable}",
                "@type": "MeasureComponent",
                "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
            }
            json_ld_data.append(elements)
    else:
        # If no measure_vars defined, use all variables that aren't identifiers or attributes
        used_vars = set()
        if hasattr(df_meta, 'identifier_vars'):
            used_vars.update(df_meta.identifier_vars)
        if hasattr(df_meta, 'attribute_vars'):
            used_vars.update(df_meta.attribute_vars)
        
        for variable in df_meta.column_names:
            if variable not in used_vars:
                elements = {
                    "@id": f"#measureComponent-{variable}",
                    "@type": "MeasureComponent",
                    "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                }
                json_ld_data.append(elements)
    
    return json_ld_data

def generate_IdentifierComponent(df_meta):
    json_ld_data = []
    for variable in df_meta.identifier_vars:
        elements = {
            "@id": f"#identifierComponent-{variable}",
            "@type": "IdentifierComponent",
            "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_AttributeComponent(df_meta):
    json_ld_data = []
    for variable in df_meta.attribute_vars:
        elements = {
            "@id": f"#attributeComponent-{variable}",
            "@type": "AttributeComponent",
            "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_PrimaryKey(df_meta):
    json_ld_data = []
    if df_meta.identifier_vars:
        elements = {
            "@id": "#primaryKey",
            "@type": "PrimaryKey",
            "isComposedOf": [f"#primaryKeyComponent-{var}" for var in df_meta.identifier_vars]
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_PrimaryKeyComponent(df_meta):
    json_ld_data = []
    for variable in df_meta.identifier_vars:
        elements = {
            "@id": f"#primaryKeyComponent-{variable}",
            "@type": "PrimaryKeyComponent",
            "correspondsTo_DataStructureComponent": f"#identifierComponent-{variable}"
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

def generate_ValueMapping(df, df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#valueMapping-{variable}",
            "@type": "ValueMapping",
            "defaultValue": "",
            "formats": []
        }
        # Add DataPoint references for each value in the variable
        for i in range(len(df[variable])):
            elements["formats"].append(f"#dataPoint-{i}-{variable}")
        
        json_ld_data.append(elements)
    return json_ld_data

def generate_ValueMappingPosition(df_meta):
    json_ld_data = []
    for idx, variable in enumerate(df_meta.column_names):
        elements = {
            "@id": f"#valueMappingPosition-{variable}",
            "@type": "ValueMappingPosition",
            "value": idx,
            "indexes": f"#valueMapping-{variable}"
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_DataPoint(df, df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        for idx in range(len(df[variable])):
            elements = {
                "@id": f"#dataPoint-{idx}-{variable}",
                "@type": "DataPoint",
                "isDescribedBy": f"#instanceVariable-{variable}"
            }
            json_ld_data.append(elements)
    return json_ld_data

def generate_DataPointPosition(df, df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        for idx in range(len(df[variable])):
            elements = {
                "@id": f"#dataPointPosition-{idx}-{variable}",
                "@type": "DataPointPosition",
                "value": idx,
                "indexes": f"#dataPoint-{idx}-{variable}"
            }
            json_ld_data.append(elements)
    return json_ld_data

def generate_InstanceValue(df, df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        for idx, value in enumerate(df[variable]):
            elements = {
                "@id": f"#instanceValue-{idx}-{variable}",
                "@type": "InstanceValue",
                "content": value,
                "isStoredIn": f"#dataPoint-{idx}-{variable}"
            }
            
            # Add value domain references based on missing values
            if variable in df_meta.missing_ranges:
                for range_dict in df_meta.missing_ranges[variable]:
                    if value is not None and isinstance(range_dict['lo'], float):
                        value = float(value)
                    if value is not None and range_dict['lo'] <= value <= range_dict['hi']:
                        elements["hasValueFrom_ValueDomain"] = f"#sentinelValueDomain-{variable}"
                        break
                else:
                    elements["hasValueFrom_ValueDomain"] = f"#substantiveValueDomain-{variable}"
            else:
                elements["hasValueFrom_ValueDomain"] = f"#substantiveValueDomain-{variable}"
            
            json_ld_data.append(elements)
    return json_ld_data

def generate_SubstantiveConceptualDomain(df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#substantiveConceptualDomain-{variable}",
            "@type": "SubstantiveConceptualDomain",
            "isDescribedBy": f"#substantiveValueAndConceptDescription-{variable}"
        }
        if variable in df_meta.variable_value_labels:
            elements["takesConceptsFrom"] = f"#substantiveConceptScheme-{variable}"
        json_ld_data.append(elements)
    return json_ld_data

def generate_SentinelConceptualDomain(df_meta):
    json_ld_data = []
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values
    
    for variable in relevant_variables:
        elements = {
            "@id": f"#sentinelConceptualDomain-{variable}",
            "@type": "SentinelConceptualDomain",
            "isDescribedBy": f"#sentinelValueAndConceptDescription-{variable}"
        }
        if variable in df_meta.variable_value_labels:
            elements["takesConceptsFrom"] = f"#sentinelConceptScheme-{variable}"
        json_ld_data.append(elements)
    return json_ld_data

def generate_ValueAndConceptDescription(df_meta):
    json_ld_data = []
    class_level = {'nominal': 'Nominal', 'scale': 'Continuous', 'ordinal': 'Ordinal', 'unknown': 'Nominal'}
    
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#substantiveValueAndConceptDescription-{variable}",
            "@type": "ValueAndConceptDescription",
            "classificationLevel": class_level[df_meta.variable_measure[variable]]
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_SentinelConceptScheme(df_meta):
    json_ld_data = []
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values
    
    for variable_name in relevant_variables:
        if variable_name in df_meta.variable_value_labels:
            elements = {
                "@id": f"#sentinelConceptScheme-{variable_name}",
                "@type": "skos:ConceptScheme",
                "skos:hasTopConcept": []
            }
            
            values = relevant_variables[variable_name]
            if isinstance(values[0], dict):
                for value in df_meta.variable_value_labels[variable_name].keys():
                    for range_dict in values:
                        if range_dict['lo'] <= value <= range_dict['hi']:
                            elements["skos:hasTopConcept"].append(f"#{variable_name}-concept-{value}")
            else:
                for value in values:
                    if value in df_meta.variable_value_labels[variable_name]:
                        elements["skos:hasTopConcept"].append(f"#{variable_name}-concept-{value}")
            
            if elements["skos:hasTopConcept"]:
                json_ld_data.append(elements)
    
    return json_ld_data

def generate_Concept(df_meta):
    json_ld_data = []
    for variable_name, values_dict in df_meta.variable_value_labels.items():
        for value, label in values_dict.items():
            elements = {
                "@id": f"#{variable_name}-concept-{value}",
                "@type": "skos:Concept",
                "skos:prefLabel": label
            }
            json_ld_data.append(elements)
    return json_ld_data

def wrap_in_graph(*args):
    """Helper function to flatten list of components into a single list"""
    return [item for sublist in args for item in sublist]

def generate_complete_json_ld(df, df_meta, spssfile='name'):
    # Generate base components that are always included
    components = [
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
        generate_InstanceVariable(df_meta),
        generate_SubstantiveConceptualDomain(df_meta),
        generate_SentinelConceptualDomain(df_meta),
        generate_ValueAndConceptDescription(df_meta),
        generate_SubstantiveConceptScheme(df_meta),
        generate_SentinelConceptScheme(df_meta),
        generate_Concept(df_meta)
    ]

    # Only add primary key related components if identifier_vars is provided AND not empty
    if df_meta.identifier_vars:
        pk_components = [
            generate_IdentifierComponent(df_meta),
            generate_PrimaryKey(df_meta),
            generate_PrimaryKeyComponent(df_meta)
        ]
        components.extend(pk_components)
    
    # Add attribute components if attribute_vars is not empty
    if df_meta.attribute_vars:
        components.append(generate_AttributeComponent(df_meta))
    
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
        "@type": "DDICDIModels",
        "DDICDIModels": {
            "@graph": all_objects
        }
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

