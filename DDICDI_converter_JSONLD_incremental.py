#!/usr/bin/env python
# coding: utf-8
import json
import numpy as np
import pandas as pd
import datetime
import time

# Helper functions for conditional references based on file format
def _get_dataset_reference(df_meta):
    """Get the appropriate dataset reference based on file format"""
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        return "#keyValueDataStore"
    else:
        return "#wideDataSet"

def _get_structure_reference(df_meta):
    """Get the appropriate structure reference based on file format"""
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        return "#keyValueStructure"
    else:
        return "#wideDataStructure"

def _get_dataset_type(df_meta):
    """Get the appropriate dataset type based on file format"""
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        return "KeyValueDataStore"
    else:
        return "WideDataSet"

def _get_structure_type(df_meta):
    """Get the appropriate structure type based on file format"""
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        return "KeyValueStructure"
    else:
        return "WideDataStructure"

# Core functions
def generate_PhysicalDataSetStructure(df_meta):
    json_ld_data = []
    elements = {
        "@id": "#physicalDataSetStructure",
        "@type": "PhysicalDataSetStructure",
        "correspondsTo_DataStructure": _get_structure_reference(df_meta),
        "structures": "#physicalDataSet"
    }
    json_ld_data.append(elements)
    return json_ld_data

def generate_PhysicalDataset(df_meta, spssfile):
    json_ld_data = []
    elements = {
        "@id": "#physicalDataSet",
        "@type": "PhysicalDataSet",
        "allowsDuplicates": False,
        "physicalFileName": spssfile,
        "correspondsTo_DataSet": _get_dataset_reference(df_meta),
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
    
    # Check if this is a CSV file
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'csv':
        elements["isDelimited"] = "true"
        elements["isFixedWidth"] = False
        
        # Get the delimiter from metadata if available, otherwise default to comma
        if hasattr(df_meta, 'delimiter'):
            elements["delimiter"] = df_meta.delimiter
        else:
            elements["delimiter"] = ","
    
    # Check if this is a JSON file with decomposed hierarchical keys
    elif hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        # Check for decomposed hierarchical keys pattern (key-1, key-2, ..., value)
        key_columns = [col for col in df_meta.column_names if col.startswith('key-') and col.split('-')[1].isdigit()]
        has_value_column = 'value' in df_meta.column_names
        
        if len(key_columns) > 0 and has_value_column:
            # This JSON file had hierarchical keys that were decomposed with "/" separator
            elements["isDelimited"] = True
            elements["isFixedWidth"] = False
            elements["delimiter"] = "/"
    
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
        "organizes": _get_dataset_reference(df_meta),
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
        "@id": _get_dataset_reference(df_meta),
        "@type": _get_dataset_type(df_meta),
        "isStructuredBy": _get_structure_reference(df_meta)
    }
    
    json_ld_data.append(elements)
    return json_ld_data

def generate_WideDataStructure(df_meta):
    json_ld_data = []
    elements = {
        "@id": _get_structure_reference(df_meta),
        "@type": _get_structure_type(df_meta),
        "has_DataStructureComponent": []
    }
    
    # Check if this is a JSON file to use different component logic
    is_json_file = hasattr(df_meta, 'file_format') and df_meta.file_format == 'json'
    
    # Set up for primary key if identifiers exist (non-JSON files only)
    if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars and not is_json_file:
        elements["has_PrimaryKey"] = "#primaryKey"
    
    # Process all variables for all possible roles
    for variable in df_meta.column_names:
        # Add as identifier component (common to both JSON and non-JSON)
        if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars and variable in df_meta.identifier_vars:
            elements["has_DataStructureComponent"].append(f"#identifierComponent-{variable}")
        
        # Add as attribute component (common to both JSON and non-JSON)
        if hasattr(df_meta, 'attribute_vars') and df_meta.attribute_vars and variable in df_meta.attribute_vars:
            elements["has_DataStructureComponent"].append(f"#attributeComponent-{variable}")
        
        # Add as dimension component (common to both JSON and non-JSON)
        if hasattr(df_meta, 'dimension_vars') and df_meta.dimension_vars and variable in df_meta.dimension_vars:
            elements["has_DataStructureComponent"].append(f"#dimensionComponent-{variable}")
        
        if is_json_file:
            # JSON-specific components
            # Add as contextual component
            if hasattr(df_meta, 'contextual_vars') and df_meta.contextual_vars and variable in df_meta.contextual_vars:
                elements["has_DataStructureComponent"].append(f"#contextualComponent-{variable}")
            
            # Add as synthetic ID component
            if hasattr(df_meta, 'synthetic_id_vars') and df_meta.synthetic_id_vars and variable in df_meta.synthetic_id_vars:
                elements["has_DataStructureComponent"].append(f"#syntheticIdComponent-{variable}")
            
            # Add as variable value component
            if hasattr(df_meta, 'variable_value_vars') and df_meta.variable_value_vars and variable in df_meta.variable_value_vars:
                elements["has_DataStructureComponent"].append(f"#variableValueComponent-{variable}")
                # Also add the corresponding VariableDescriptorComponent reference (required by SHACL)
                elements["has_DataStructureComponent"].append(f"#variableDescriptorComponent-{variable}")
        else:
            # Non-JSON files (SPSS, CSV, etc.) - use measure components
            # Add as measure component
            if hasattr(df_meta, 'measure_vars') and df_meta.measure_vars and variable in df_meta.measure_vars:
                elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")
            # If no roles are assigned, default to measure for non-JSON files
            elif (not hasattr(df_meta, 'identifier_vars') or variable not in df_meta.identifier_vars) and \
                 (not hasattr(df_meta, 'attribute_vars') or variable not in df_meta.attribute_vars) and \
                 (not hasattr(df_meta, 'measure_vars') or variable not in df_meta.measure_vars):
                elements["has_DataStructureComponent"].append(f"#measureComponent-{variable}")

    json_ld_data.append(elements)
    return json_ld_data

def generate_MeasureComponent(df_meta):
    json_ld_data = []
    # Process all variables that are assigned as measures
    if hasattr(df_meta, 'measure_vars') and df_meta.measure_vars:
        for variable in df_meta.measure_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements = {
                    "@id": f"#measureComponent-{variable}",
                    "@type": "MeasureComponent",
                    "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                }
                json_ld_data.append(elements)
    # Also handle any variables not explicitly assigned roles (default to measure)
    else:
        for variable in df_meta.column_names:
            if (not hasattr(df_meta, 'identifier_vars') or variable not in df_meta.identifier_vars) and \
               (not hasattr(df_meta, 'attribute_vars') or variable not in df_meta.attribute_vars):
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

def generate_DimensionComponent(df_meta):
    json_ld_data = []
    if hasattr(df_meta, 'dimension_vars') and df_meta.dimension_vars:
        for variable in df_meta.dimension_vars:
            if variable in df_meta.column_names:  # Verify variable exists in dataset
                elements = {
                    "@id": f"#dimensionComponent-{variable}",
                    "@type": "DimensionComponent",
                    "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                }
                json_ld_data.append(elements)
    return json_ld_data

def generate_ContextualComponent(df_meta):
    """Generate ContextualComponent entries for JSON files only"""
    json_ld_data = []
    # Only generate for JSON files (KeyValueDataStore)
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        if hasattr(df_meta, 'contextual_vars') and df_meta.contextual_vars:
            for variable in df_meta.contextual_vars:
                if variable in df_meta.column_names:  # Verify variable exists in dataset
                    elements = {
                        "@id": f"#contextualComponent-{variable}",
                        "@type": "ContextualComponent",
                        "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                    }
                    json_ld_data.append(elements)
    return json_ld_data

def generate_SyntheticIdComponent(df_meta):
    """Generate SyntheticIdComponent entries for JSON files only"""
    json_ld_data = []
    # Only generate for JSON files (KeyValueDataStore)
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        if hasattr(df_meta, 'synthetic_id_vars') and df_meta.synthetic_id_vars:
            for variable in df_meta.synthetic_id_vars:
                if variable in df_meta.column_names:  # Verify variable exists in dataset
                    elements = {
                        "@id": f"#syntheticIdComponent-{variable}",
                        "@type": "SyntheticIdComponent",
                        "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                    }
                    json_ld_data.append(elements)
    return json_ld_data

def generate_VariableValueComponent(df_meta):
    """Generate VariableValueComponent entries for JSON files only"""
    json_ld_data = []
    # Only generate for JSON files (KeyValueDataStore)
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        if hasattr(df_meta, 'variable_value_vars') and df_meta.variable_value_vars:
            for variable in df_meta.variable_value_vars:
                if variable in df_meta.column_names:  # Verify variable exists in dataset
                    elements = {
                        "@id": f"#variableValueComponent-{variable}",
                        "@type": "VariableValueComponent",
                        "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                    }
                    json_ld_data.append(elements)
    return json_ld_data

def generate_VariableDescriptorComponent(df_meta):
    """Generate VariableDescriptorComponent entries for JSON files only"""
    json_ld_data = []
    # Only generate for JSON files (KeyValueDataStore)
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        if hasattr(df_meta, 'variable_value_vars') and df_meta.variable_value_vars:
            for variable in df_meta.variable_value_vars:
                if variable in df_meta.column_names:  # Verify variable exists in dataset
                    elements = {
                        "@id": f"#variableDescriptorComponent-{variable}",
                        "@type": "VariableDescriptorComponent",
                        "refersTo": f"#variableValueComponent-{variable}",
                        "isDefinedBy_RepresentedVariable": f"#instanceVariable-{variable}"
                    }
                    json_ld_data.append(elements)
    return json_ld_data

def generate_MainKeyMember(df_meta):
    """Generate MainKeyMember entry for JSON files only"""
    json_ld_data = []
    # Only generate for JSON files (KeyValueDataStore)
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        # Collect all key-related component references
        based_on_components = []
        
        # Add identifier components
        if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
            for variable in df_meta.identifier_vars:
                if variable in df_meta.column_names:
                    based_on_components.append(f"#identifierComponent-{variable}")
        
        # Add contextual components
        if hasattr(df_meta, 'contextual_vars') and df_meta.contextual_vars:
            for variable in df_meta.contextual_vars:
                if variable in df_meta.column_names:
                    based_on_components.append(f"#contextualComponent-{variable}")
        
        # Add synthetic ID components
        if hasattr(df_meta, 'synthetic_id_vars') and df_meta.synthetic_id_vars:
            for variable in df_meta.synthetic_id_vars:
                if variable in df_meta.column_names:
                    based_on_components.append(f"#syntheticIdComponent-{variable}")
        
        # Only create MainKeyMember if there are key components to reference
        if based_on_components:
            # Use the first key variable's substantive value domain as reference
            first_key_var = None
            if hasattr(df_meta, 'identifier_vars') and df_meta.identifier_vars:
                first_key_var = df_meta.identifier_vars[0]
            elif hasattr(df_meta, 'contextual_vars') and df_meta.contextual_vars:
                first_key_var = df_meta.contextual_vars[0]
            elif hasattr(df_meta, 'synthetic_id_vars') and df_meta.synthetic_id_vars:
                first_key_var = df_meta.synthetic_id_vars[0]
            
            elements = {
                "@id": "#mainKeyMember",
                "@type": "MainKeyMember",
                "isBasedOn": based_on_components
            }
            
            # Add substantive value domain reference if we have a key variable
            if first_key_var:
                elements["hasValueFrom_ValueDomain"] = f"#substantiveValueDomain-{first_key_var}"
            
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

        # Add sentinel value domain reference if the variable has missing values
        if (variable in df_meta.missing_ranges) or (
                len(df_meta.missing_ranges) == 0 and variable in df_meta.missing_user_values):
            # changed from takesSentinelValuesFrom_SentinelValueDomain to takesSentinelValuesFrom   
            elements["takesSentinelValuesFrom"] = f"#sentinelValueDomain-{variable}"

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
                            range(int(float(dict_range['lo'])), int(float(dict_range['hi'])) + 1))
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

def generate_ValueMapping(df, df_meta, process_all_rows=False, chunk_size=5):
    """
    Generate ValueMapping objects for the dataset.
    Optimized for performance with large datasets.
    """
    # Determine how many rows to process
    if process_all_rows:
        max_rows = len(df)
    else:
        max_rows = min(len(df), chunk_size)
    
    # Only generate format lists if we have rows to process
    if len(df) == 0:
        # Shortcut for empty dataframes
        return [
            {
                "@id": f"#valueMapping-{variable}",
                "@type": "ValueMapping",
                "defaultValue": "",
                "formats": []
            }
            for variable in df_meta.column_names
        ]
    
    # For better performance with large datasets, we'll generate
    # the format lists separately for each variable
    result = []
    for variable in df_meta.column_names:
        # Create format list using range and format strings - much faster than list comprehension
        # for very large datasets
        datapoint_template = f"#dataPoint-{{0}}-{variable}"
        formats = [datapoint_template.format(i) for i in range(max_rows)]
        
        element = {
            "@id": f"#valueMapping-{variable}",
            "@type": "ValueMapping",
            "defaultValue": "",
            "formats": formats
        }
        result.append(element)
    
    return result

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

def generate_DataPoint(df, df_meta, process_all_rows=False, chunk_size=5):
    """
    Generate DataPoint objects for the dataset.
    Optimized for performance with large datasets.
    """
    # Determine how many rows to process
    if process_all_rows:
        max_rows = len(df)
    else:
        max_rows = min(len(df), chunk_size)
    
    # Using a list comprehension to generate all data points at once is more efficient
    # Pre-calculate the common values
    datapoint_type = "DataPoint"
    dataset_reference = _get_dataset_reference(df_meta)
    
    result = []
    # Generate data points in a single operation to avoid repeated function calls
    for variable in df_meta.column_names:
        variable_reference = f"#instanceVariable-{variable}"
        
        # Generate all data points for this variable in one go
        variable_datapoints = [
            {
                "@id": f"#dataPoint-{idx}-{variable}",
                "@type": datapoint_type,
                "isDescribedBy": variable_reference,
                "has_DataPoint_OF_DataSet": dataset_reference
            }
            for idx in range(max_rows)
        ]
        result.extend(variable_datapoints)
    
    return result

def generate_DataPointPosition(df, df_meta, process_all_rows=False, chunk_size=5):
    """
    Generate DataPointPosition objects for the dataset.
    Optimized for performance with large datasets.
    """
    # Determine how many rows to process
    if process_all_rows:
        max_rows = len(df)
    else:
        max_rows = min(len(df), chunk_size)
    
    # Pre-calculate constants to avoid repetitive string operations
    datapoint_position_type = "DataPointPosition"
    result = []
    
    # Generate all positions in batches by variable to improve memory locality
    for variable in df_meta.column_names:
        # Pre-calculate the datapoint prefix
        datapoint_prefix = f"#dataPoint-{{}}-{variable}"
        
        # Generate all positions for this variable in one operation
        variable_positions = [
            {
                "@id": f"#dataPointPosition-{idx}-{variable}", 
                "@type": datapoint_position_type,
                "value": idx,
                "indexes": datapoint_prefix.format(idx)
            }
            for idx in range(max_rows)
        ]
        result.extend(variable_positions)
    
    return result

def generate_InstanceValue(df, df_meta, process_all_rows=False, chunk_size=5):
    """
    Generate InstanceValue objects for the dataset.
    Optimized for performance with large datasets.
    """
    json_ld_data = []
    
    # Determine how many rows to process
    if process_all_rows:
        max_rows = len(df)
    else:
        max_rows = min(len(df), chunk_size)
    
    # If df has more than max_rows and we're not processing all rows, take a sample
    if len(df) > max_rows and not process_all_rows:
        df_sample = df.head(max_rows)
    else:
        df_sample = df.iloc[:max_rows]
    
    # Pre-compute value domain references for each variable (do this once)
    value_domain_refs = {}
    for variable in df_meta.column_names:
        if variable in df_meta.missing_ranges:
            value_domain_refs[variable] = {
                'has_missing': True,
                'ranges': df_meta.missing_ranges[variable],
                'numeric_ranges': [r for r in df_meta.missing_ranges[variable] if isinstance(r['lo'], float)]
            }
        else:
            value_domain_refs[variable] = {
                'has_missing': False
            }
    
    # Create a template element to avoid recreating common parts
    template_element = {
        "@type": "InstanceValue",
        "content": {
            "@type": "TypedString"
        }
    }
    
    # Process each variable once - this is much more efficient
    for variable in df_meta.column_names:
        # Get variable-specific information
        var_info = value_domain_refs[variable]
        has_missing_ranges = var_info['has_missing']
        
        # Convert column to strings in one operation if possible
        try:
            # Using pandas vectorized operations when possible
            content_values = df_sample[variable].astype(str).tolist()
        except:
            # Fallback for columns that can't be bulk converted
            content_values = [str(val) for val in df_sample[variable]]
        
        # Pre-calculate missing value domains to avoid repeated checks
        value_domains = []
        if has_missing_ranges and var_info.get('numeric_ranges'):
            numeric_ranges = var_info['numeric_ranges']
            
            # For numeric columns, try to use vectorized operations
            try:
                # Convert to numeric for comparison (will set non-numerics to NaN)
                numeric_values = pd.to_numeric(df_sample[variable], errors='coerce')
                
                # Initialize all as substantive domains
                is_missing = pd.Series([False] * len(df_sample), index=df_sample.index)
                
                # Check each range
                for range_dict in numeric_ranges:
                    # Combine conditions across all ranges
                    range_condition = (numeric_values >= range_dict['lo']) & (numeric_values <= range_dict['hi'])
                    is_missing = is_missing | range_condition
                
                # Create value domains list based on the result
                value_domains = [
                    f"#sentinelValueDomain-{variable}" if is_missing[i] 
                    else f"#substantiveValueDomain-{variable}"
                    for i in range(len(df_sample))
                ]
            except:
                # Fallback to non-vectorized approach for complex cases
                value_domains = []
                for value in df_sample[variable]:
                    in_missing_range = False
                    if value is not None:
                        for range_dict in numeric_ranges:
                            try:
                                value_float = float(value)
                                if range_dict['lo'] <= value_float <= range_dict['hi']:
                                    in_missing_range = True
                                    break
                            except (ValueError, TypeError):
                                pass
                    
                    if in_missing_range:
                        value_domains.append(f"#sentinelValueDomain-{variable}")
                    else:
                        value_domains.append(f"#substantiveValueDomain-{variable}")
        else:
            # If no missing ranges, all values use substantive domain
            value_domains = [f"#substantiveValueDomain-{variable}"] * len(df_sample)
        
        # Now build all elements for this variable at once
        variable_elements = []
        for idx in range(len(df_sample)):
            # Create element using the template to avoid recreation
            element = {
                "@id": f"#instanceValue-{idx}-{variable}",
                "@type": template_element["@type"],
                "content": {
                    "@type": template_element["content"]["@type"],
                    "content": content_values[idx]
                },
                "isStoredIn": f"#dataPoint-{idx}-{variable}",
                "hasValueFrom_ValueDomain": value_domains[idx]
            }
            variable_elements.append(element)
        
        # Add all elements for this variable at once
        json_ld_data.extend(variable_elements)
    
    return json_ld_data

def map_to_xsd_type(original_type):
    """Map original data types to XSD data types with full URLs"""
    # Convert original_type to lowercase string for comparison
    type_str = str(original_type).lower()
    
    type_mapping = {
        # Numeric types
        'int8': 'https://www.w3.org/TR/xmlschema-2/#byte',
        'int16': 'https://www.w3.org/TR/xmlschema-2/#short',
        'int32': 'https://www.w3.org/TR/xmlschema-2/#int',
        'int64': 'https://www.w3.org/TR/xmlschema-2/#long',
        'int': 'https://www.w3.org/TR/xmlschema-2/#int',
        'integer': 'https://www.w3.org/TR/xmlschema-2/#integer',
        'uint8': 'https://www.w3.org/TR/xmlschema-2/#unsignedByte',
        'uint16': 'https://www.w3.org/TR/xmlschema-2/#unsignedShort',
        'uint32': 'https://www.w3.org/TR/xmlschema-2/#unsignedInt',
        'uint64': 'https://www.w3.org/TR/xmlschema-2/#unsignedLong',
        'float': 'https://www.w3.org/TR/xmlschema-2/#float',
        'float32': 'https://www.w3.org/TR/xmlschema-2/#float',
        'float64': 'https://www.w3.org/TR/xmlschema-2/#double',
        'double': 'https://www.w3.org/TR/xmlschema-2/#double',
        'decimal': 'https://www.w3.org/TR/xmlschema-2/#decimal',
        'numeric': 'https://www.w3.org/TR/xmlschema-2/#decimal',
        'number': 'https://www.w3.org/TR/xmlschema-2/#decimal',
        'complex': 'https://www.w3.org/TR/xmlschema-2/#string',
        
        # String types
        'string': 'https://www.w3.org/TR/xmlschema-2/#string',
        'str': 'https://www.w3.org/TR/xmlschema-2/#string',
        'object': 'https://www.w3.org/TR/xmlschema-2/#string',
        'text': 'https://www.w3.org/TR/xmlschema-2/#string',
        'varchar': 'https://www.w3.org/TR/xmlschema-2/#string',
        'character': 'https://www.w3.org/TR/xmlschema-2/#string',
        'char': 'https://www.w3.org/TR/xmlschema-2/#string',
        
        # Date/Time types
        'datetime': 'https://www.w3.org/TR/xmlschema-2/#dateTime',
        'datetime64': 'https://www.w3.org/TR/xmlschema-2/#dateTime',
        'datetime64[ns]': 'https://www.w3.org/TR/xmlschema-2/#dateTime',
        'timestamp': 'https://www.w3.org/TR/xmlschema-2/#dateTime',
        'date': 'https://www.w3.org/TR/xmlschema-2/#date',
        'time': 'https://www.w3.org/TR/xmlschema-2/#time',
        'timedelta': 'https://www.w3.org/TR/xmlschema-2/#duration',
        'duration': 'https://www.w3.org/TR/xmlschema-2/#duration',
        
        # Boolean
        'bool': 'https://www.w3.org/TR/xmlschema-2/#boolean',
        'boolean': 'https://www.w3.org/TR/xmlschema-2/#boolean',
        
        # Other specialized types
        'category': 'https://www.w3.org/TR/xmlschema-2/#string',
        'factor': 'https://www.w3.org/TR/xmlschema-2/#string',
        'array': 'https://www.w3.org/TR/xmlschema-2/#string',
        'list': 'https://www.w3.org/TR/xmlschema-2/#string',
        
        # Default fallback
        'unknown': 'https://www.w3.org/TR/xmlschema-2/#string'
    }
    
    # Check for pandas-specific type strings
    if 'int' in type_str:
        return 'https://www.w3.org/TR/xmlschema-2/#int'
    elif 'float' in type_str:
        return 'https://www.w3.org/TR/xmlschema-2/#double'
    elif 'date' in type_str:
        return 'https://www.w3.org/TR/xmlschema-2/#dateTime'
    elif 'bool' in type_str:
        return 'https://www.w3.org/TR/xmlschema-2/#boolean'
    
    # Try direct mapping first
    return type_mapping.get(type_str, 'https://www.w3.org/TR/xmlschema-2/#string')

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
                "entryValue": mapped_type
            },
            "isDescribedBy": f"#substantiveValueAndConceptDescription-{variable}"
        }
        
        # Add reference to EnumerationDomain if variable has value labels
        if variable in df_meta.variable_value_labels:
            elements["takesValuesFrom"] = f"#substantiveEnumerationDomain-{variable}"
            
        json_ld_data.append(elements)
    return json_ld_data

def get_classification_level(variable_type):
    """Get the classification level based on the variable type."""
    if variable_type in ["continuous", "scale", "ordinal", "ratio"]:
        return "Interval"
    elif variable_type in ["nominal", "nominal/ordinal"]:
        return "Nominal"
    else:
        return "Nominal"  # Default

def generate_ValueAndConceptDescription(df_meta):
    json_ld_data = []
    relevant_variables = df_meta.missing_ranges if df_meta.missing_ranges else df_meta.missing_user_values

    class_level = {'nominal': 'Nominal', 'scale': 'Continuous', 'ordinal': 'Ordinal', 'unknown': 'Nominal'}
    
    # Generate substantive descriptions for all variables
    for variable in df_meta.column_names:
        elements = {
            "@id": f"#substantiveValueAndConceptDescription-{variable}",
            "@type": "ValueAndConceptDescription",
            "classificationLevel": class_level[df_meta.variable_measure[variable]]
        }
        json_ld_data.append(elements)

    # Generate sentinel descriptions for variables with missing values
    for variable in relevant_variables:
        values = relevant_variables[variable]
        if isinstance(values[0], dict):
            all_lo_values = [d['lo'] for d in values]
            all_hi_values = [d['hi'] for d in values]
            min_val = min(all_lo_values)
            max_val = max(all_hi_values)
        else:
            min_val, max_val = min(values), max(values)

        elements = {
            "@id": f"#sentinelValueAndConceptDescription-{variable}",
            "@type": "ValueAndConceptDescription",
            "description": {
                "@type": "InternationalString",
                "languageSpecificString": {  # Single object instead of array
                    "@type": "LanguageString",
                    "content": str(values)
                }
            },
            "maximumValueExclusive": str(max_val),
            "minimumValueExclusive": str(min_val)
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

def generate_SubstantiveEnumerationDomain(df_meta):
    json_ld_data = []
    for variable in df_meta.column_names:
        if variable in df_meta.variable_value_labels:
            # Create a set to track excluded values
            excluded_values = set()
            
            # Check if there are missing values for this variable
            if variable in df_meta.missing_ranges:
                for dict_range in df_meta.missing_ranges[variable]:
                    if isinstance(dict_range['lo'], float) and isinstance(dict_range['hi'], float):
                        excluded_values.update(
                            range(int(float(dict_range['lo'])), int(float(dict_range['hi'])) + 1))
                    elif isinstance(dict_range['lo'], str):
                        excluded_values.add(dict_range['lo'])

            # Use list comprehension to generate the hasTopConcept list
            excluded_values_str = {str(i) for i in excluded_values}
            has_top_concept = [
                f"#{variable}-concept-{value}"
                for value in df_meta.variable_value_labels[variable].keys()
                if (not value in excluded_values) and (not str(value) in excluded_values_str)
            ]

            # Only add to json_ld_data if has_top_concept list is not empty
            if has_top_concept:
                elements = {
                    "@id": f"#substantiveEnumerationDomain-{variable}",
                    "@type": "EnumerationDomain",
                    "sameAs": f"#substantiveConceptScheme-{variable}"
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
            elements["takesValuesFrom"] = f"#sentinelEnumerationDomain-{variable}"
        json_ld_data.append(elements)
    return json_ld_data

def generate_SentinelEnumerationDomain(df_meta):
    """New function to generate EnumerationDomain objects"""
    json_ld_data = []
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values
    
    for variable in relevant_variables:
        if variable in df_meta.variable_value_labels:
            elements = {
                "@id": f"#sentinelEnumerationDomain-{variable}",
                "@type": "EnumerationDomain",
                "sameAs": f"#sentinelConceptScheme-{variable}"
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

def generate_complete_json_ld(df, df_meta, spssfile='name', chunk_size=5, process_all_rows=False, max_rows=5):
    """
    Generate complete JSON-LD representation of the dataset.
    
    Parameters:
    -----------
    df : pandas DataFrame
        The dataset to convert
    df_meta : object
        Metadata about the dataset
    spssfile : str
        Name of the source file
    chunk_size : int
        Size of chunks to process at once (default: 5)
    process_all_rows : bool
        Whether to process all rows (True) or limit to first chunk (False)
    max_rows : int
        Maximum number of rows to process when process_all_rows is False
    """
    start_time = time.time()
    
    # Check if we need to process all rows or just a sample
    if process_all_rows and len(df) > chunk_size:
        print(f"Processing complete dataset with {len(df)} rows in chunks of {chunk_size}...")
        
        # For large datasets, we'll process in chunks for InstanceValue which is intensive
        # First generate all DataPoints and DataPointPositions at once - this is fast
        print("Generating DataPoints and DataPointPositions...")
        dp_start = time.time()
        all_data_points = generate_DataPoint(df, df_meta, process_all_rows, chunk_size)
        dp_end = time.time()
        print(f"Generated {len(all_data_points)} DataPoints in {dp_end - dp_start:.2f} seconds")
        
        dp_pos_start = time.time()
        all_data_point_positions = generate_DataPointPosition(df, df_meta, process_all_rows, chunk_size)
        dp_pos_end = time.time()
        print(f"Generated {len(all_data_point_positions)} DataPointPositions in {dp_pos_end - dp_pos_start:.2f} seconds")
        
        vm_start = time.time()
        value_mappings = generate_ValueMapping(df, df_meta, process_all_rows, chunk_size)
        vm_end = time.time()
        print(f"Generated {len(value_mappings)} ValueMappings in {vm_end - vm_start:.2f} seconds")
        
        # Process InstanceValues in chunks to manage memory usage
        print("Processing InstanceValues in chunks...")
        all_instance_values = []
        
        # Calculate total chunks for progress reporting
        total_chunks = (len(df) + chunk_size - 1) // chunk_size
        total_cells = len(df) * len(df_meta.column_names)
        
        # Process each chunk with optimization for large datasets
        chunk_start = 0
        iv_total_start = time.time()
        
        for chunk_idx in range(total_chunks):
            chunk_start_time = time.time()
            
            # Define chunk boundaries
            chunk_start = chunk_idx * chunk_size
            chunk_end = min(chunk_start + chunk_size, len(df))
            rows_in_chunk = chunk_end - chunk_start
            
            # Progress reporting
            percent_complete = (chunk_idx / total_chunks) * 100
            print(f"Processing chunk {chunk_idx+1}/{total_chunks}: rows {chunk_start} to {chunk_end-1} ({percent_complete:.1f}% complete)")
            
            # Get the current chunk using iloc for better performance
            df_chunk = df.iloc[chunk_start:chunk_end].copy()
            
            # Generate instance values for this chunk with adjusted indices
            generate_start = time.time()
            
            # Optimize: Keep numeric columns as numeric where possible
            # Pre-process for better performance in the InstanceValue function
            for col in df_chunk.columns:
                # Try to convert object columns to numeric if possible for faster processing
                if df_chunk[col].dtype == 'object':
                    try:
                        df_chunk[col] = pd.to_numeric(df_chunk[col], errors='ignore')
                    except:
                        pass  # Keep as is if conversion fails
            
            chunk_instance_values = []
            
            # Process InstanceValues for this chunk
            for variable in df_meta.column_names:
                # Create a template for efficiency
                id_template = f"#instanceValue-{{0}}-{variable}"
                stored_in_template = f"#dataPoint-{{0}}-{variable}"
                
                # Check if this variable has missing ranges
                has_missing_ranges = variable in df_meta.missing_ranges
                missing_ranges = df_meta.missing_ranges.get(variable, [])
                numeric_ranges = [r for r in missing_ranges if isinstance(r['lo'], float)]
                
                # Process all rows for this variable
                col_values = df_chunk[variable]
                
                # Apply a batch approach based on data type
                try:
                    # Use vectorized operations for numeric data when possible
                    if numeric_ranges and pd.api.types.is_numeric_dtype(col_values):
                        # For numeric columns with missing ranges, use vectorized comparison
                        in_missing_range = pd.Series([False] * len(col_values))
                        for range_dict in numeric_ranges:
                            range_condition = (col_values >= range_dict['lo']) & (col_values <= range_dict['hi'])
                            in_missing_range = in_missing_range | range_condition
                        
                        # Generate values based on condition
                        for idx, (value, is_missing) in enumerate(zip(col_values, in_missing_range)):
                            global_idx = chunk_start + idx
                            value_str = str(value)
                            
                            element = {
                                "@id": id_template.format(global_idx),
                                "@type": "InstanceValue",
                                "content": {
                                    "@type": "TypedString",
                                    "content": value_str
                                },
                                "isStoredIn": stored_in_template.format(global_idx),
                                "hasValueFrom_ValueDomain": (f"#sentinelValueDomain-{variable}" 
                                                              if is_missing else 
                                                               f"#substantiveValueDomain-{variable}")
                            }
                            chunk_instance_values.append(element)
                    else:
                        # For non-numeric or complex cases, fall back to regular processing
                        for idx, value in enumerate(col_values):
                            global_idx = chunk_start + idx
                            value_str = str(value)
                            
                            if has_missing_ranges:
                                in_missing = False
                                for range_dict in numeric_ranges:
                                    try:
                                        value_float = float(value)
                                        if range_dict['lo'] <= value_float <= range_dict['hi']:
                                            in_missing = True
                                            break
                                    except (ValueError, TypeError):
                                        pass
                                
                                value_domain = (f"#sentinelValueDomain-{variable}" if in_missing
                                             else f"#substantiveValueDomain-{variable}")
                            else:
                                value_domain = f"#substantiveValueDomain-{variable}"
                            
                            element = {
                                "@id": id_template.format(global_idx),
                                "@type": "InstanceValue",
                                "content": {
                                    "@type": "TypedString",
                                    "content": value_str
                                },
                                "isStoredIn": stored_in_template.format(global_idx),
                                "hasValueFrom_ValueDomain": value_domain
                            }
                            chunk_instance_values.append(element)
                except Exception as e:
                    # If any optimized approach fails, fall back to the most reliable method
                    print(f"Warning: Falling back to standard processing for variable {variable}: {str(e)}")
                    for idx, value in enumerate(col_values):
                        global_idx = chunk_start + idx
                        
                        element = {
                            "@id": id_template.format(global_idx),
                            "@type": "InstanceValue",
                            "content": {
                                "@type": "TypedString",
                                "content": str(value)
                            },
                            "isStoredIn": stored_in_template.format(global_idx),
                            "hasValueFrom_ValueDomain": f"#substantiveValueDomain-{variable}"
                        }
                        
                        # Check for missing values if needed
                        if has_missing_ranges:
                            for range_dict in missing_ranges:
                                if isinstance(range_dict['lo'], float):
                                    try:
                                        value_float = float(value)
                                        if range_dict['lo'] <= value_float <= range_dict['hi']:
                                            element["hasValueFrom_ValueDomain"] = f"#sentinelValueDomain-{variable}"
                                            break
                                    except (ValueError, TypeError):
                                        pass
                        
                        chunk_instance_values.append(element)
            
            # Add this chunk's instance values to the complete list
            all_instance_values.extend(chunk_instance_values)
            
            generate_end = time.time()
            chunk_end_time = time.time()
            
            # Calculate and display performance metrics
            chunk_duration = chunk_end_time - chunk_start_time
            rows_per_sec = rows_in_chunk / chunk_duration
            cells_processed = rows_in_chunk * len(df_meta.column_names)
            cells_per_sec = cells_processed / chunk_duration
            
            print(f"  Chunk {chunk_idx+1} processed in {chunk_duration:.2f} seconds")
            print(f"  Performance: {rows_per_sec:.1f} rows/sec, {cells_per_sec:.1f} cells/sec")
            print(f"  Memory usage: {len(chunk_instance_values)} objects created")
            
            # Estimate remaining time
            elapsed_time = time.time() - iv_total_start
            estimated_total = elapsed_time / (chunk_idx + 1) * total_chunks
            remaining_time = max(0, estimated_total - elapsed_time)
            
            if remaining_time > 60:
                mins = int(remaining_time // 60)
                secs = int(remaining_time % 60)
                print(f"  Estimated time remaining: {mins}m {secs}s")
            else:
                print(f"  Estimated time remaining: {int(remaining_time)}s")
        
        iv_total_end = time.time()
        print(f"All InstanceValues processed in {iv_total_end - iv_total_start:.2f} seconds")
        
        # Use the complete dataset for the rest of the components
        df_limited = df
        
    else:
        # Use the standard approach with a limited number of rows
        if len(df) > max_rows and not process_all_rows:
            print(f"Warning: Dataset has {len(df)} rows. Limiting to {max_rows} rows for performance.")
            print(f"Set process_all_rows=True to process all rows (may be slow for large datasets).")
            df_limited = df.head(max_rows)
        else:
            df_limited = df
        
        # Generate components for the limited dataset
        print("Generating components for limited dataset...")
        component_start_time = time.time()
        all_instance_values = generate_InstanceValue(df_limited, df_meta, process_all_rows, max_rows)
        print(f"InstanceValues generated in {(time.time() - component_start_time):.2f} seconds")
        
        component_start_time = time.time()
        all_data_points = generate_DataPoint(df_limited, df_meta, process_all_rows, max_rows)
        print(f"DataPoints generated in {(time.time() - component_start_time):.2f} seconds")
        
        component_start_time = time.time()
        all_data_point_positions = generate_DataPointPosition(df_limited, df_meta, process_all_rows, max_rows)
        print(f"DataPointPositions generated in {(time.time() - component_start_time):.2f} seconds")
        
        component_start_time = time.time()
        value_mappings = generate_ValueMapping(df_limited, df_meta, process_all_rows, max_rows)
        print(f"ValueMappings generated in {(time.time() - component_start_time):.2f} seconds")
    
    # Generate base components that are always included
    components = [
        generate_PhysicalDataset(df_meta, spssfile),
        generate_PhysicalRecordSegment(df_meta, df_limited),
        generate_PhysicalSegmentLayout(df_meta),
        value_mappings,
        generate_ValueMappingPosition(df_meta),
        all_data_points,
        all_data_point_positions,
        all_instance_values,
        generate_DataStore(df_meta),
        generate_LogicalRecord(df_meta),
        generate_WideDataSet(df_meta),
        generate_WideDataStructure(df_meta),
        generate_MeasureComponent(df_meta),
        generate_InstanceVariable(df_meta),
        generate_SubstantiveValueDomain(df_meta),
        generate_SubstantiveEnumerationDomain(df_meta),
        generate_SentinelValueDomain(df_meta),
        generate_SentinelEnumerationDomain(df_meta),
        generate_ValueAndConceptDescription(df_meta),
        generate_SubstantiveConceptScheme(df_meta),
        generate_SentinelConceptScheme(df_meta),
        generate_Concept(df_meta)
    ]

    # Only add primary key related components for non-JSON files
    is_json_file = hasattr(df_meta, 'file_format') and df_meta.file_format == 'json'
    if df_meta.identifier_vars and not is_json_file:
        pk_components = [
            generate_IdentifierComponent(df_meta),
            generate_PrimaryKey(df_meta),
            generate_PrimaryKeyComponent(df_meta)
        ]
        components.extend(pk_components)
    elif df_meta.identifier_vars and is_json_file:
        # For JSON files, only generate IdentifierComponent (no PrimaryKey)
        components.append(generate_IdentifierComponent(df_meta))
    
    # Add attribute components if attribute_vars is not empty
    if df_meta.attribute_vars:
        components.append(generate_AttributeComponent(df_meta))
    
    # Add dimension components if dimension_vars is not empty
    if hasattr(df_meta, 'dimension_vars') and df_meta.dimension_vars:
        components.append(generate_DimensionComponent(df_meta))
    
    # Add contextual components if contextual_vars is not empty (JSON files only)
    if hasattr(df_meta, 'contextual_vars') and df_meta.contextual_vars:
        components.append(generate_ContextualComponent(df_meta))
    
    # Add synthetic ID components if synthetic_id_vars is not empty (JSON files only)
    if hasattr(df_meta, 'synthetic_id_vars') and df_meta.synthetic_id_vars:
        components.append(generate_SyntheticIdComponent(df_meta))
    
    # Add variable value components if variable_value_vars is not empty (JSON files only)
    if hasattr(df_meta, 'variable_value_vars') and df_meta.variable_value_vars:
        components.append(generate_VariableValueComponent(df_meta))
        # Add corresponding variable descriptor components (required by SHACL)
        components.append(generate_VariableDescriptorComponent(df_meta))
    
    # Add MainKeyMember for JSON files (represents all key components)
    if hasattr(df_meta, 'file_format') and df_meta.file_format == 'json':
        components.append(generate_MainKeyMember(df_meta))
    
    # Get the separated components
    components_dict = wrap_in_graph(*components)
    
    # Create the final JSON-LD document with the new structure
    json_ld_doc = {
        "@context": [
            "https://docs.ddialliance.org/DDI-CDI/1.0/model/encoding/json-ld/ddi-cdi.jsonld",
            {
                "skos": "http://www.w3.org/2004/02/skos/core#"
            }
        ],
        "DDICDIModels": components_dict["ddi_components"]
    }
    
    # Add @included only if there are SKOS components
    if components_dict["skos_components"]:
        json_ld_doc["@included"] = components_dict["skos_components"]
    
    # Report execution time and statistics
    end_time = time.time()
    total_seconds = end_time - start_time
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    
    # Print summary statistics
    if minutes > 0:
        print(f"Total processing time: {minutes} minutes and {seconds:.2f} seconds")
    else:
        print(f"Total processing time: {seconds:.2f} seconds")
        
    num_rows = len(df)
    num_variables = len(df_meta.column_names)
    data_points_count = len(all_data_points) if 'all_data_points' in locals() else 0
    
    print(f"Dataset: {num_rows} rows x {num_variables} variables")
    print(f"Generated: {data_points_count} DataPoints")
    
    if process_all_rows and num_rows > chunk_size:
        print(f"Processing strategy: Chunked processing with {(num_rows + chunk_size - 1) // chunk_size} chunks of size {chunk_size}")
    else:
        print(f"Processing strategy: Limited to {max_rows} rows" if not process_all_rows and num_rows > max_rows else "Full dataset")

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

class MemoryManager:
    """
    A utility class to help manage memory during processing of large datasets.
    Provides monitoring and optimization functions.
    """
    @staticmethod
    def estimate_memory_usage(df, df_meta, process_all_rows=False, chunk_size=5):
        """
        Estimate memory usage for processing the dataset.
        Returns estimated memory in MB.
        """
        if process_all_rows:
            rows_to_process = len(df)
        else:
            rows_to_process = min(len(df), chunk_size)
        
        # Estimate size of each JSON element (average from testing)
        element_size = 500  # bytes
        
        # Total elements = DataPoints + DataPointPositions + ValueMappings + InstanceValues
        total_elements = (
            rows_to_process * len(df_meta.column_names) * 3  # DataPoints, DataPointPositions, InstanceValues
            + len(df_meta.column_names)  # ValueMappings
        )
        
        # Calculate estimated memory usage in MB
        memory_mb = (total_elements * element_size) / (1024 * 1024)
        
        return memory_mb
    
    @staticmethod
    def optimize_chunk_size(df, df_meta, available_memory_mb=500):
        """
        Calculate an optimal chunk size based on available memory.
        Aims to use at most available_memory_mb RAM.
        """
        if len(df) == 0:
            return 100  # Default for empty dataframes
        
        # Test with a small chunk to estimate memory usage per row
        test_chunk = 100
        memory_for_test = MemoryManager.estimate_memory_usage(df.head(test_chunk), df_meta, True, test_chunk)
        
        # Calculate memory per row
        memory_per_row = memory_for_test / test_chunk
        
        # Calculate optimal chunk size - use 80% of available memory to be safe
        safe_memory = available_memory_mb * 0.8
        optimal_chunk = int(safe_memory / memory_per_row)
        
        # Ensure chunk size is at least 50 rows but not more than the dataset
        optimal_chunk = max(50, min(len(df), optimal_chunk))
        
        # Round to a nice number
        if optimal_chunk > 1000:
            return int(optimal_chunk / 1000) * 1000
        elif optimal_chunk > 500:
            return int(optimal_chunk / 500) * 500
        elif optimal_chunk > 100:
            return int(optimal_chunk / 100) * 100
        else:
            return optimal_chunk

