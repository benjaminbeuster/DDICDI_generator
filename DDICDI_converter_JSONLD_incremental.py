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
        "has_ValueMappingPosition": []
    }
    
    # Add both ValueMapping and ValueMappingPosition references for each variable
    for variable in df_meta.column_names:
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
    
    # Add identifier components first
    if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
        elements["has_PrimaryKey"] = "#primaryKey"
        for variable in df_meta.identifier_vars:
            if variable in df_meta.column_names:
                elements["has_DataStructureComponent"].append(f"#identifierComponent-{variable}")
    
    # Add attribute components second
    if hasattr(df_meta, 'attribute_vars') and df_meta.attribute_vars:
        for variable in df_meta.attribute_vars:
            if variable in df_meta.column_names:
                elements["has_DataStructureComponent"].append(f"#attributeComponent-{variable}")
    
    # Add measure components last
    if hasattr(df_meta, 'measure_vars') and df_meta.measure_vars:
        for variable in df_meta.measure_vars:
            if variable in df_meta.column_names:
                elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")

    json_ld_data.append(elements)
    return json_ld_data

def generate_MeasureComponent(df_meta):
    json_ld_data = []
    if hasattr(df_meta, 'measure_vars') and df_meta.measure_vars:
        for variable in df_meta.measure_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements = {
                    "@id": f"#measureComponent-{variable}",
                    "@type": "MeasureComponent",
                    "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                }
                json_ld_data.append(elements)
    return json_ld_data

def generate_IdentifierComponent(df_meta):
    json_ld_data = []
    if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
        for variable in df_meta.identifier_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements = {
                    "@id": f"#identifierComponent-{variable}",
                    "@type": "IdentifierComponent",
                    "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                }
                json_ld_data.append(elements)
    return json_ld_data

def generate_AttributeComponent(df_meta):
    json_ld_data = []
    if hasattr(df_meta, 'attribute_vars') and df_meta.attribute_vars:
        for variable in df_meta.attribute_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements = {
                    "@id": f"#attributeComponent-{variable}",
                    "@type": "AttributeComponent",
                    "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                }
                json_ld_data.append(elements)
    return json_ld_data

def generate_PrimaryKey(df_meta):
    json_ld_data = []
    if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
        elements = {
            "@id": "#primaryKey",
            "@type": "PrimaryKey",
            "isComposedOf": [f"#primaryKeyComponent-{var}" for var in df_meta.identifier_vars if var in df_meta.column_names]
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_PrimaryKeyComponent(df_meta):
    json_ld_data = []
    if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
        for variable in df_meta.identifier_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements = {
                    "@id": f"#primaryKeyComponent-{variable}",
                    "@type": "PrimaryKeyComponent",
                    "correspondsTo_DataStructureComponent": f"#identifierComponent-{variable}"
                }
                json_ld_data.append(elements)
    return json_ld_data

def generate_InstanceVariable(df_meta):
    json_ld_data = []
    for idx, variable in enumerate(df_meta.column_names):
        # Handle both list and dictionary cases for column_labels
        label = (df_meta.column_labels[idx] 
                if isinstance(df_meta.column_labels, list) 
                else df_meta.column_labels.get(variable, variable))
        
        # Handle both list and dictionary cases for original_variable_types
        data_type = (df_meta.original_variable_types[idx]
                    if isinstance(df_meta.original_variable_types, list)
                    else df_meta.original_variable_types.get(variable, "string"))

        elements = {
            "@id": f"#instanceVariable-{variable}",
            "@type": "InstanceVariable",
            "physicalDataType": {
                "@type": "ControlledVocabularyEntry",
                "entryValue": str(data_type)
            },
            "displayLabel": {
                "@type": "LabelForDisplay",
                "locationVariant": {
                    "@type": "ControlledVocabularyEntry",
                    "entryValue": label
                }
            },
            "name": {
                "@type": "ObjectName",
                "name": variable
            },
            "has_PhysicalSegmentLayout": "#physicalSegmentLayout",
            "has_ValueMapping": f"#valueMapping-{variable}",
            "takesSubstantiveValuesFrom_SubstantiveValueDomain": f"#substantiveValueDomain-{variable}"
        }
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
        
        # Add DataPoint references if the dataframe has rows
        if len(df) > 0:
            elements["formats"] = [f"#dataPoint-{i}-{variable}" for i in range(len(df[variable]))]
        
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
                # Nested TypedString structure
                "content": {
                    "@type": "TypedString",
                    "content": str(value)
                },
                "isStoredIn": f"#dataPoint-{idx}-{variable}"
            }
            
            # Add value domain references
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

def map_to_xsd_type(original_type):
    """Map original data types to XSD data types with full URLs"""
    type_mapping = {
        # Numeric types
        'int8': 'https://www.w3.org/TR/xmlschema-2/#byte',
        'int16': 'https://www.w3.org/TR/xmlschema-2/#short',
        'int32': 'https://www.w3.org/TR/xmlschema-2/#int',
        'int64': 'https://www.w3.org/TR/xmlschema-2/#long',
        'float': 'https://www.w3.org/TR/xmlschema-2/#float',
        'double': 'https://www.w3.org/TR/xmlschema-2/#double',
        'decimal': 'https://www.w3.org/TR/xmlschema-2/#decimal',
        
        # String types
        'string': 'https://www.w3.org/TR/xmlschema-2/#string',
        'str': 'https://www.w3.org/TR/xmlschema-2/#string',
        
        # Date/Time types
        'datetime': 'https://www.w3.org/TR/xmlschema-2/#dateTime',
        'date': 'https://www.w3.org/TR/xmlschema-2/#date',
        'time': 'https://www.w3.org/TR/xmlschema-2/#time',
        
        # Boolean
        'bool': 'https://www.w3.org/TR/xmlschema-2/#boolean',
        
        # Default fallback
        'unknown': 'https://www.w3.org/TR/xmlschema-2/#string'
    }
    return type_mapping.get(original_type.lower(), 'https://www.w3.org/TR/xmlschema-2/#string')

def generate_SubstantiveValueDomain(df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        # Get the original type and map it to XSD type
        original_type = df_meta.readstat_variable_types[variable]
        mapped_type = map_to_xsd_type(original_type)
        
        elements = {
            "@id": f"#substantiveValueDomain-{variable}",
            "@type": "SubstantiveValueDomain",
            "recommendedDataType": {
                "@type": "ControlledVocabularyEntry",
                "entryValue": mapped_type  # Use the mapped type instead of hardcoded string
            },
            "isDescribedBy": f"#substantiveValueAndConceptDescription-{variable}"
        }
        json_ld_data.append(elements)
    return json_ld_data

def generate_SentinelValueDomain(df_meta):
    json_ld_data = []
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values
    
    for variable in relevant_variables:
        original_type = df_meta.readstat_variable_types[variable]
        mapped_type = map_to_xsd_type(original_type)
        
        elements = {
            "@id": f"#sentinelValueDomain-{variable}",
            "@type": "SentinelValueDomain",
            "recommendedDataType": {
                "@type": "ControlledVocabularyEntry",
                "entryValue": mapped_type
            },
            "isDescribedBy": f"#sentinelValueAndConceptDescription-{variable}"
        }
        if variable in df_meta.variable_value_labels:
            elements["takesValuesFrom"] = f"#sentinelConceptScheme-{variable}"
        json_ld_data.append(elements)
    return json_ld_data

def get_classification_level(variable_type):
    """
    Determine the classification level based on the variable type
    Valid values are: "Continuous", "Interval", "Nominal", "Ordinal", "Ratio"
    """
    # This mapping should be adjusted based on your specific needs
    if variable_type in ['float', 'double', 'numeric']:
        return "Continuous"
    elif variable_type in ['integer', 'int']:
        return "Interval"
    elif variable_type in ['string', 'character']:
        return "Nominal"
    else:
        return "Nominal"  # Default case

def generate_ValueAndConceptDescription(df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#substantiveValueAndConceptDescription-{variable}",
            "@type": "ValueAndConceptDescription",
            "classificationLevel": "Nominal"
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
                # Nested TypedString for notation and prefLabel
                "skos:notation": {
                    "@type": "TypedString",
                    "content": str(value)
                },
                "skos:prefLabel": {
                    "@type": "TypedString",
                    "content": str(label)
                }
            }
            json_ld_data.append(elements)
    return json_ld_data

def wrap_in_graph(*args):
    """Helper function to separate DDI-CDI and SKOS components"""
    all_items = [item for sublist in args for item in sublist]
    
    # Separate SKOS and DDI-CDI components
    ddi_components = []
    skos_components = []
    
    for item in all_items:
        if item.get("@type", "").startswith("skos:"):
            skos_components.append(item)
        else:
            ddi_components.append(item)
    
    # Return components organized for the new structure
    return {
        "ddi_components": ddi_components,
        "skos_components": skos_components if skos_components else None
    }

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
        generate_SubstantiveValueDomain(df_meta),
        generate_SentinelValueDomain(df_meta),
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
    
    # Get the separated components
    components_dict = wrap_in_graph(*components)
    
    # Create the final JSON-LD document with the new structure
    json_ld_doc = {
        "@context": [
            "https://ddi-cdi.github.io/ddi-cdi_v1.0-post/encoding/json-ld/ddi-cdi.jsonld",
            {
                "skos": "http://www.w3.org/2004/02/skos/core#"
            }
        ],
        "DDICDIModels": components_dict["ddi_components"]
    }

    # Add @included only if there are SKOS components
    if components_dict["skos_components"]:
        json_ld_doc["@included"] = components_dict["skos_components"]

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

