#!/usr/bin/env python
# coding: utf-8

import sys
import xml.etree.ElementTree as ET

sys.path.append("..")
import os
import pandas as pd
import pyreadstat as pyr
import json
import numpy as np
import datetime
from spss_import import read_sav
from lxml import etree
from xml_functions import remove_empty_elements, add_cdi_element, add_identifier, add_ddiref


# In[ ]:

# DataStore
def generate_DataStore(df_meta):
    element = add_cdi_element(root, 'DataStore')
    add_cdi_element(element, 'allowsDuplicates', "false")
    add_identifier(element, f"#dataStore")
    add_cdi_element(element, 'recordCount', df_meta.number_rows)
    LogicalRecord = add_cdi_element(element, 'DataStore_has_LogicalRecord')
    add_ddiref(LogicalRecord, f"#logicalRecord", agency, "LogicalRecord")
    return root


# In[ ]:


# logicalRecord
def generate_LogicalRecord(df_meta):
    element = add_cdi_element(root, 'LogicalRecord')
    add_identifier(element, f"#logicalRecord")
    LogicalRecord_organizes_DataSet = add_cdi_element(element, 'LogicalRecord_organizes_DataSet')
    add_ddiref(LogicalRecord_organizes_DataSet, f"#wideDataSet", agency, "WideDataSet")
    for idx, variable in enumerate(df_meta.column_names):
        LogicalRecord_has_InstanceVariable = add_cdi_element(element, 'LogicalRecord_has_InstanceVariable')
        add_ddiref(LogicalRecord_has_InstanceVariable, f"#instanceVariable-{variable}", agency, "InstanceVariable")
    return root


# In[ ]:


# WideDataSet
def generate_WideDataSet(df_meta):
    element = add_cdi_element(root, 'WideDataSet')
    add_identifier(element, f"#wideDataSet")
    DataSet_isStructuredBy_DataStructure = add_cdi_element(element, 'DataSet_isStructuredBy_DataStructure')
    add_ddiref(DataSet_isStructuredBy_DataStructure, f"#wideDataStructure", agency, "WideDataStructure")
    return root


# In[ ]:


# WideDataStructure
def generate_WideDataStructure(df_meta):
    element = add_cdi_element(root, 'WideDataStructure')
    add_identifier(element, f"#wideDataStructure")

    DataStructure_has_DataStructureComponent = add_cdi_element(element, 'DataStructure_has_DataStructureComponent')
    add_ddiref(DataStructure_has_DataStructureComponent, f"#identifierComponent-{df_meta.column_names[0]}", agency,
               "IdentifierComponent")

    for x, variable in enumerate(df_meta.column_names[1:]):
        DataStructure_has_DataStructureComponent = add_cdi_element(element, 'DataStructure_has_DataStructureComponent')
        add_ddiref(DataStructure_has_DataStructureComponent, f"#measureComponent-{variable}", agency,
                   "MeasureComponent")

    DataStructure_has_PrimaryKey = add_cdi_element(element, 'DataStructure_has_PrimaryKey')
    add_ddiref(DataStructure_has_PrimaryKey, f"#primaryKey", agency, "PrimaryKey")
    return root


# In[ ]:


# IdentifierComponent
def generate_IdentifierComponent(df_meta):
    element = add_cdi_element(root, 'IdentifierComponent')
    add_identifier(element, f"#identifierComponent-{df_meta.column_names[0]}")
    DataStructureComponent_isDefinedBy_RepresentedVariable = add_cdi_element(element,
                                                                             'DataStructureComponent_isDefinedBy_RepresentedVariable')
    add_ddiref(DataStructureComponent_isDefinedBy_RepresentedVariable, f"#instanceVariable-{df_meta.column_names[0]}",
               agency, "InstanceVariable")
    return root


# In[ ]:


# MeasureComponent
def generate_MeasureComponent(df_meta):
    for x, variable in enumerate(df_meta.column_names[1:]):
        MeasureComponent = add_cdi_element(root, 'MeasureComponent')
        add_identifier(MeasureComponent, f"#measureComponent-{variable}")
        DataStructureComponent_isDefinedBy_RepresentedVariable = add_cdi_element(MeasureComponent,
                                                                                 'DataStructureComponent_isDefinedBy_RepresentedVariable')
        add_ddiref(DataStructureComponent_isDefinedBy_RepresentedVariable, f"#instanceVariable-{variable}", agency,
                   "InstanceVariable")
    return root


# In[ ]:


# PrimaryKey
def generate_PrimaryKey(df_meta):
    element = add_cdi_element(root, 'PrimaryKey')
    add_identifier(element, f"#primaryKey")
    PrimaryKey_isComposedOf_PrimaryKeyComponent = add_cdi_element(element,
                                                                  'PrimaryKey_isComposedOf_PrimaryKeyComponent')
    add_ddiref(PrimaryKey_isComposedOf_PrimaryKeyComponent, f"#primaryKeyComponent", agency, "PrimaryKeyComponent")
    return root


# In[ ]:


# PrimaryKeyComponent
def generate_PrimaryKeyComponent(df_meta):
    element = add_cdi_element(root, 'PrimaryKeyComponent')
    add_identifier(element, f"#primaryKeyComponent")
    PrimaryKeyComponent_correspondsTo_DataStructureComponent = add_cdi_element(element,
                                                                               'PrimaryKeyComponent_correspondsTo_DataStructureComponent')
    add_ddiref(PrimaryKeyComponent_correspondsTo_DataStructureComponent,
               f"#identifierComponent-{df_meta.column_names[0]}", agency, "IdentifierComponent")
    return root


# In[ ]:


def generate_InstanceVariable(df_meta):
    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        element = add_cdi_element(root, 'InstanceVariable')
        displayLabel = add_cdi_element(element, 'displayLabel')
        languageSpecificString = add_cdi_element(displayLabel, 'languageSpecificString')
        add_cdi_element(languageSpecificString, 'content', f"{df_meta.column_labels[idx]}")
        add_identifier(element, f"#instanceVariable-{variable}")
        name = add_cdi_element(element, 'name')
        add_cdi_element(name, 'name', f"{variable}")
        hasIntendedDataType = add_cdi_element(element, 'hasIntendedDataType')
        add_cdi_element(hasIntendedDataType, 'name', f"{df_meta.original_variable_types[variable]}")

        # Check if variable has sentinel concepts
        if variable in df_meta.missing_ranges or (
                len(df_meta.missing_ranges) == 0 and variable in df_meta.missing_user_values):
            RepresentedVariable_takesSentinelValuesFrom_SentinelValueDomain = add_cdi_element(element,
                                                                                              'RepresentedVariable_takesSentinelValuesFrom_SentinelValueDomain')
            add_ddiref(RepresentedVariable_takesSentinelValuesFrom_SentinelValueDomain,
                       f"#sentinelValueDomain-{variable}", agency, "SentinelValueDomain")
        RepresentedVariable_takesSubstantiveValuesFrom_SubstantiveValueDomain = add_cdi_element(element,
                                                                                                'RepresentedVariable_takesSubstantiveValuesFrom_SubstantiveValueDomain')
        add_ddiref(RepresentedVariable_takesSubstantiveValuesFrom_SubstantiveValueDomain,
                   f"#substantiveValueDomain-{variable}", agency, 'SubstantiveValueDomain')
        InstanceVariable_has_PhysicalSegmentLayout = add_cdi_element(element,
                                                                     'InstanceVariable_has_PhysicalSegmentLayout')
        add_ddiref(InstanceVariable_has_PhysicalSegmentLayout, f"#physicalSegmentLayout", agency,
                   "PhysicalSegmentLayout")
        InstanceVariable_has_ValueMapping = add_cdi_element(element, 'InstanceVariable_has_ValueMapping')
        add_ddiref(InstanceVariable_has_ValueMapping, f"#valueMapping-{variable}", agency, "ValueMapping")
    return root


# In[ ]:


# SubstantiveValueDomain
def generate_SubstantiveValueDomain(df_meta):
    for var in df_meta.column_names:
        element = add_cdi_element(root, 'SubstantiveValueDomain')
        add_identifier(element, f"#substantiveValueDomain-{var}")
        if var in df_meta.variable_value_labels:
            SubstantiveValueDomain_takesValuesFrom_EnumerationDomain = add_cdi_element(element,
                                                                                       'SubstantiveValueDomain_takesValuesFrom_EnumerationDomain')
            add_ddiref(SubstantiveValueDomain_takesValuesFrom_EnumerationDomain, f"#substantiveCodelist-{var}", agency,
                       'CodeList')
        SubstantiveValueDomain_isDescribedBy_ValueAndConceptDescription = add_cdi_element(element,
                                                                                          'SubstantiveValueDomain_isDescribedBy_ValueAndConceptDescription')
        add_ddiref(SubstantiveValueDomain_isDescribedBy_ValueAndConceptDescription,
                   f"#substantiveValueAndConceptDescription-{var}", agency, "ValueAndConceptDescription")
    return root


# In[ ]:


# SentinelConceptualDomain
def generate_SentinelValueDomain(df_meta):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    for variable in relevant_variables:
        element = add_cdi_element(root, 'SentinelValueDomain')
        add_identifier(element, f"#sentinelValueDomain-{variable}")

        if variable in df_meta.variable_value_labels:
            SentinelValueDomain_takesValuesFrom_EnumerationDomain = add_cdi_element(element,
                                                                                    'SentinelValueDomain_takesValuesFrom_EnumerationDomain')
            add_ddiref(SentinelValueDomain_takesValuesFrom_EnumerationDomain, f"#sentinelCodelist-{variable}", agency,
                       'CodeList')
        SentinelValueDomain_isDescribedBy_ValueAndConceptDescription = add_cdi_element(element,
                                                                                       'SentinelValueDomain_isDescribedBy_ValueAndConceptDescription')
        add_ddiref(SentinelValueDomain_isDescribedBy_ValueAndConceptDescription,
                   f"#sentinelValueAndConceptDescription-{variable}", agency, "ValueAndConceptDescription")
    return root


# In[ ]:


# ValueAndConceptDescription
def generate_ValueAndConceptDescription(df_meta):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = {}
    if df_meta.missing_ranges:
        relevant_variables = df_meta.missing_ranges
    elif df_meta.missing_user_values:
        relevant_variables = df_meta.missing_user_values

    json_ld_data = []

    # recode classification level
    class_level = {'nominal': 'Nominal', 'scale': 'Continuous', 'ordinal': 'Ordinal', 'unknown': 'Nominal'}
    for variable in df_meta.column_names:
        element = add_cdi_element(root, 'ValueAndConceptDescription')
        add_cdi_element(element, 'classificationLevel', f"{class_level[df_meta.variable_measure[variable]]}")
        add_identifier(element, f"#substantiveValueAndConceptDescription-{variable}")

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

            element = add_cdi_element(root, 'ValueAndConceptDescription')
            description = add_cdi_element(element, 'description')
            languageSpecificString = add_cdi_element(description, 'languageSpecificString')
            add_cdi_element(languageSpecificString, 'content', str(values))
            add_identifier(element, f"#sentinelValueAndConceptDescription-{variable}")
            add_cdi_element(element, "maximumValueExclusive", str(max_val))
            add_cdi_element(element, "minimumValueExclusive", str(min_val))

            json_ld_data.append({
                "@id": f"#sentinelValueAndConceptDescription-{variable}",
                "@type": "ValueAndConceptDescription",
                "description": str(values),
                "minimumValueExclusive": str(min_val),
                "maximumValueExclusive": str(max_val),
            })
    return root


# In[ ]:


# SubstantiveCodeList
def generate_CodeList(df_meta):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    for variable_name, values_dict in df_meta.variable_value_labels.items():
        element = add_cdi_element(root, 'CodeList')
        add_identifier(element, f"#substantiveCodelist-{variable_name}")

        name = add_cdi_element(element, 'name')
        add_cdi_element(name, 'name', f"#substantiveCodelist-{variable_name}")

        add_cdi_element(element, 'allowsDuplicates', "false")

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

        for value in values_dict.keys():
            excluded_values_str = {str(i) for i in excluded_values}
            if (not value in excluded_values) and (not str(value) in excluded_values_str):
                CodeList_has_Code = add_cdi_element(element, 'CodeList_has_Code')
                add_ddiref(CodeList_has_Code, f"#code-{value}-{variable_name}", agency, "Code")
    return root


# In[ ]:


# SentinelCodelist
def generate_SentinelCodelist(df_meta):
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
        element = add_cdi_element(root, 'CodeList')
        add_identifier(element, f"#sentinelCodelist-{variable_name}")

        name = add_cdi_element(element, 'name')
        add_cdi_element(name, 'name', f"#sentinelCodelist-{variable_name}")

        add_cdi_element(element, 'allowsDuplicates', "false")

        if variable_name in relevant_variables:
            if variable_name in df_meta.missing_ranges:
                # Use a for loop to generate the hasTopConcept list
                for value in values_dict.keys():
                    if is_value_in_range(value, df_meta.missing_ranges[variable_name]):
                        CodeList_has_Code = add_cdi_element(element, 'CodeList_has_Code')
                        add_ddiref(CodeList_has_Code, f"#code-{value}-{variable_name}", agency, "Code")
            else:
                excluded_values = set(df_meta.missing_user_values[variable_name])
                for value in values_dict.keys():
                    if value in excluded_values:
                        CodeList_has_Code = add_cdi_element(element, 'CodeList_has_Code')
                        add_ddiref(CodeList_has_Code, f"#code-{value}-{variable_name}", agency, "Code")
    return root


# In[ ]:


# Code
def generate_Code(df_meta):
    for variable_name, values_dict in df_meta.variable_value_labels.items():
        for key, value in values_dict.items():
            element = add_cdi_element(root, 'Code')
            add_identifier(element, f"#code-{key}-{variable_name}")
            Code_denotes_Category = add_cdi_element(element, 'Code_denotes_Category')
            add_ddiref(Code_denotes_Category, f"#category-{value}", agency, "Category")
            Code_uses_Notation = add_cdi_element(element, 'Code_uses_Notation')
            add_ddiref(Code_uses_Notation, f"#notation-{key}", agency, "Notation")
    return root


# In[ ]:


# Category and Notation
def generate_Category_Notation(df_meta):
    notations = list(set(key for values_dict in df_meta.variable_value_labels.values() for key in values_dict.keys()))
    cats = list(set(value for values_dict in df_meta.variable_value_labels.values() for value in values_dict.values()))

    for cat in cats:
        element = add_cdi_element(root, 'Category')
        displayLabel = add_cdi_element(element, 'displayLabel')
        languageSpecificString = add_cdi_element(displayLabel, 'languageSpecificString')
        add_cdi_element(languageSpecificString, 'content', f"{cat}")
        add_identifier(element, f"#category-{cat}")
        name = add_cdi_element(element, 'name')
        add_cdi_element(name, 'name', f"{cat}")

    for note in notations:
        element = add_cdi_element(root, 'Notation')
        content = add_cdi_element(element, 'content')
        add_cdi_element(content, 'content', f"{note}")
        add_identifier(element, f"#notation-{note}")
    return root


# In[ ]:
# PhysicalDataSetStructure
def generate_PhysicalDataSetStructure(df_meta):
    element = add_cdi_element(root, 'PhysicalDataSetStructure')
    add_identifier(element, f"#physicalDataSetStructure")
    PhysicalDataSetStructure_correspondsTo_DataStructure = add_cdi_element(element,
                                                                           'PhysicalDataSetStructure_correspondsTo_DataStructure')
    add_ddiref(PhysicalDataSetStructure_correspondsTo_DataStructure, f"#wideDataStructure", agency, "WideDataStructure")
    PhysicalDataSetStructure_structures_PhysicalDataSet = add_cdi_element(element,
                                                                          'PhysicalDataSetStructure_structures_PhysicalDataSet')
    add_ddiref(PhysicalDataSetStructure_structures_PhysicalDataSet, f"#physicalDataSet", agency, "PhysicalDataSet")
    return root


# PhysicalDataset
def generate_PhysicalDataset(df_meta, spssfile):
    element = add_cdi_element(root, 'PhysicalDataSet')
    add_cdi_element(element, 'allowsDuplicates', "false")
    add_identifier(element, f"#physicalDataset")
    add_cdi_element(element, 'physicalFileName', spssfile)
    PhysicalDataSet_correspondsTo_DataSet = add_cdi_element(element, f"PhysicalDataSet_correspondsTo_DataSet")
    add_ddiref(PhysicalDataSet_correspondsTo_DataSet, f"#wideDataset", agency, "WideDataSet")
    PhysicalDataSet_formats_DataStore = add_cdi_element(element, f"PhysicalDataSet_formats_DataStore")
    add_ddiref(PhysicalDataSet_formats_DataStore, f"#dataStore", agency, "DataStore")
    PhysicalDataSet_has_PhysicalRecordSegment = add_cdi_element(element, 'PhysicalDataSet_has_PhysicalRecordSegment')
    add_ddiref(PhysicalDataSet_has_PhysicalRecordSegment, f"#physicalRecordSegment", agency, "PhysicalRecordSegment")
    return root


# In[ ]:


# PhysicalRecordSegment
def generate_PhysicalRecordSegment(df, df_meta):
    element = add_cdi_element(root, 'PhysicalRecordSegment')
    add_cdi_element(element, 'allowsDuplicates', "false")
    add_identifier(element, f"#physicalRecordSegment")

    PhysicalRecordSegment_has_PhysicalSegmentLayout = add_cdi_element(element,
                                                                      f"PhysicalRecordSegment_has_PhysicalSegmentLayout")
    add_ddiref(PhysicalRecordSegment_has_PhysicalSegmentLayout, f"#physicalSegmentLayout", agency,
               "PhysicalSegmentLayout")
    PhysicalRecordSegment_mapsTo_LogicalRecord = add_cdi_element(element, f"PhysicalRecordSegment_mapsTo_LogicalRecord")
    add_ddiref(PhysicalRecordSegment_mapsTo_LogicalRecord, f"#logicalRecord", agency, "LogicalRecord")

    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):

        for i, x in enumerate(df[variable]):
            PhysicalRecordSegment_has_DataPointPosition = add_cdi_element(element,
                                                                          f"PhysicalRecordSegment_has_DataPointPosition")
            add_ddiref(PhysicalRecordSegment_has_DataPointPosition, f"#dataPointPosition-{i}-{variable}", agency,
                       "DataPointPosition")
    return root


# In[ ]:


# PhysicalSegmentLayout
def generate_PhysicalSegmentLayout(df_meta):
    element = add_cdi_element(root, 'PhysicalSegmentLayout')
    add_cdi_element(element, 'allowsDuplicates', "false")
    add_identifier(element, f"#physicalSegmentLayout")
    add_cdi_element(element, 'isDelimited', "false")
    add_cdi_element(element, 'isFixedWidth', "false")
    PhysicalSegmentLayout_formats_LogicalRecord = add_cdi_element(element,
                                                                  'PhysicalSegmentLayout_formats_LogicalRecord')
    add_ddiref(PhysicalSegmentLayout_formats_LogicalRecord, f"#logicalRecord", agency, "LogicalRecord")

    for x, variable in enumerate(df_meta.column_names):
        PhysicalSegmentLayout_has_ValueMapping = add_cdi_element(element, f"PhysicalSegmentLayout_has_ValueMapping")
        add_ddiref(PhysicalSegmentLayout_has_ValueMapping, f"#valueMapping-{variable}", agency, "ValueMapping")

    for x, variable in enumerate(df_meta.column_names):
        PhysicalSegmentLayout_has_ValueMappingPosition = add_cdi_element(element,
                                                                         f"PhysicalSegmentLayout_has_ValueMappingPosition")
        add_ddiref(PhysicalSegmentLayout_has_ValueMappingPosition, f"#valueMappingPosition-{variable}", agency,
                   "ValueMappingPosition")
    return root


# In[ ]:


# ValueMapping
def generate_ValueMapping(df, df_meta):
    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        element = add_cdi_element(root, 'ValueMapping')
        add_cdi_element(element, 'defaultValue', "")
        add_identifier(element, f"#valueMapping-{variable}")

        for i, x in enumerate(df[variable]):
            ValueMapping_formats_DataPoint = add_cdi_element(element, f"ValueMapping_formats_DataPoint")
            add_ddiref(ValueMapping_formats_DataPoint, f"#dataPoint-{i}-{variable}", agency, "DataPoint")
    return root


# In[ ]:


# ValueMappingPosition
def generate_ValueMappingPosition(df_meta):
    # Iterate through column names and associated index
    for idx, variable in enumerate(df_meta.column_names):
        element = add_cdi_element(root, 'ValueMappingPosition')
        add_identifier(element, f"#valueMappingPosition-{variable}")
        add_cdi_element(element, 'value', idx)
        ValueMappingPosition_indexes_ValueMapping = add_cdi_element(element,
                                                                    'ValueMappingPosition_indexes_ValueMapping')
        add_ddiref(ValueMappingPosition_indexes_ValueMapping, f"#valueMapping-{variable}", agency, "ValueMapping")
    return root


# In[ ]:


# DataPoint
def generate_DataPoint(df, df_meta):
    # Iterate through column names and associated index
    for variable in (df_meta.column_names):
        for idx, value in enumerate(df[variable]):
            element = add_cdi_element(root, 'DataPoint')
            add_identifier(element, f"#dataPoint-{idx}-{variable}")
            DataPoint_isDescribedBy_InstanceVariable = add_cdi_element(element,
                                                                       'DataPoint_isDescribedBy_InstanceVariable')
            add_ddiref(DataPoint_isDescribedBy_InstanceVariable, f"#instanceVariable-{variable}", agency,
                       "InstanceVariable")
    return root


# In[ ]:


# DataPointPosition
def generate_DataPointPosition(df, df_meta):
    # Iterate through column names and associated index
    for variable in (df_meta.column_names):
        for idx, value in enumerate(df[variable]):
            element = add_cdi_element(root, 'DataPointPosition')
            add_identifier(element, f"#dataPointPosition-{idx}-{variable}")
            add_cdi_element(element, 'value', idx)
            DataPointPosition_indexes_DataPoint = add_cdi_element(element, 'DataPointPosition_indexes_DataPoint')
            add_ddiref(DataPointPosition_indexes_DataPoint, f"#dataPoint-{idx}-{variable}", agency, "DataPoint")
    return root


# In[ ]:

def generate_InstanceValue(df, df_meta):
    # Iterate through column names and associated index
    for variable in (df_meta.column_names):
        for idx, value in enumerate(df[variable]):
            element = add_cdi_element(root, 'InstanceValue')
            content = add_cdi_element(element, "content")
            add_cdi_element(content, "content", value)
            add_identifier(element, f"#instanceValue-{idx}-{variable}")

            if variable in df_meta.missing_ranges:
                for range_dict in df_meta.missing_ranges[variable]:
                    if value is not None and isinstance(range_dict['lo'], float):
                        # convert value to float for comparison
                        value = float(value)
                    if value is not None and range_dict['lo'] <= value <= range_dict['hi'] and isinstance(value, (
                    str, int, float)):
                        InstanceValue_hasValueFrom_ValueDomain = add_cdi_element(element,
                                                                                 'InstanceValue_hasValueFrom_ValueDomain')
                        add_ddiref(InstanceValue_hasValueFrom_ValueDomain, f"#sentinelValueDomain-{variable}", agency,
                                   "SentinelValueDomain")
                        break
                else:
                    InstanceValue_hasValueFrom_ValueDomain = add_cdi_element(element,
                                                                             'InstanceValue_hasValueFrom_ValueDomain')
                    add_ddiref(InstanceValue_hasValueFrom_ValueDomain, f"#substantiveValueDomain-{variable}", agency,
                               "SubstantiveValueDomain")

            else:
                InstanceValue_hasValueFrom_ValueDomain = add_cdi_element(element,
                                                                         'InstanceValue_hasValueFrom_ValueDomain')
                add_ddiref(InstanceValue_hasValueFrom_ValueDomain, f"#substantiveValueDomain-{variable}", agency,
                           "SubstantiveValueDomain")

            InstanceValue_isStoredIn_DataPoint = add_cdi_element(element, 'InstanceValue_isStoredIn_DataPoint')
            add_ddiref(InstanceValue_isStoredIn_DataPoint, f"#dataPoint-{idx}-{variable}", agency, "DataPoint")
    return root


# In[ ]:


def generate_complete_xml(df, df_meta, spssfile='name'):
    # Define the namespace
    nsmap = {'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/'}
    # Create the root element
    global root
    root = etree.Element(etree.QName(nsmap['cdi'], 'DDICDIModels'), nsmap=nsmap)
    root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
             'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/ https://ddi-cdi-resources.bitbucket.io/2024-03-12/encoding/xml-schema/ddi-cdi.xsd')
    global agency
    agency = 'int.esseric'

    generate_PhysicalDataSetStructure(df_meta)
    generate_PhysicalDataset(df_meta, spssfile)
    generate_PhysicalRecordSegment(df, df_meta)
    generate_PhysicalSegmentLayout(df_meta)
    generate_ValueMapping(df, df_meta)
    generate_ValueMappingPosition(df_meta)
    generate_DataPoint(df, df_meta)
    generate_DataPointPosition(df, df_meta)
    generate_InstanceValue(df, df_meta)
    generate_DataStore(df_meta)
    generate_LogicalRecord(df_meta)
    generate_WideDataSet(df_meta)
    generate_WideDataStructure(df_meta)
    generate_IdentifierComponent(df_meta)
    generate_MeasureComponent(df_meta)
    generate_PrimaryKey(df_meta)
    generate_PrimaryKeyComponent(df_meta)
    generate_InstanceVariable(df_meta)
    generate_SubstantiveValueDomain(df_meta)
    generate_SentinelValueDomain(df_meta)
    generate_ValueAndConceptDescription(df_meta)
    generate_CodeList(df_meta)
    generate_SentinelCodelist(df_meta)
    generate_Code(df_meta)
    generate_Category_Notation(df_meta)

    # Add XML declaration and write XML file
    xml_string = etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=True)

    # Add the comment as the second line
    # add current time to xml_string
    current_time = datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")

    # Create the comment string and encode it to bytes
    comment = f'<!-- CDI version 1, generated: {current_time} -->'.encode('utf-8')

    # Replace the XML declaration with the declaration followed by the comment
    xml_string_with_comment = xml_string.replace(b'?>', b'?>\n' + comment, 1)

    # with open(r'files/CDI.xml', 'wb') as f:
    #     f.write(xml_string_with_comment)

    return xml_string_with_comment


# # Repeat function for using multiple PrimaryKeyComponents

# In[ ]:


# WideDataStructure2
def generate_WideDataStructure2(df_meta, vars=None):
    # Add a CDI element to the root
    element = add_cdi_element(root, 'WideDataStructure')

    # Add an identifier to the element
    add_identifier(element, "#wideDataStructure")

    # If vars is None, iterate through all column names in df_meta
    if vars is None:
        for x, variable in enumerate(df_meta.column_names):
            # Add a CDI element to the element
            DataStructureComponent = add_cdi_element(element, 'DataStructure_has_DataStructureComponent')

            # Add a DDI reference to the DataStructureComponent
            add_ddiref(DataStructureComponent, f"#measureComponent-{variable}", agency, "MeasureComponent")

    # If vars is not None
    else:
        # Iterate through all variables in vars
        for var in vars:
            # Add a CDI element to the element
            DataStructureComponent = add_cdi_element(element, 'DataStructure_has_DataStructureComponent')

            # Add a DDI reference to the DataStructureComponent
            add_ddiref(DataStructureComponent, f"#identifierComponent-{var}", agency, "IdentifierComponent")

        # Iterate through all column names in df_meta
        for x, variable in enumerate(df_meta.column_names):
            # If the variable is not in vars
            if variable not in vars:
                # Add a CDI element to the element
                DataStructureComponent = add_cdi_element(element, 'DataStructure_has_DataStructureComponent')

                # Add a DDI reference to the DataStructureComponent
                add_ddiref(DataStructureComponent, f"#measureComponent-{variable}", agency, "MeasureComponent")

    # Add a CDI element to the element
    DataStructure_has_PrimaryKey = add_cdi_element(element, 'DataStructure_has_PrimaryKey')

    # Add a DDI reference to the DataStructure_has_PrimaryKey
    add_ddiref(DataStructure_has_PrimaryKey, f"#primaryKey", agency, "PrimaryKey")

    return root


# In[ ]:


# IdentifierComponent2
def generate_IdentifierComponent2(df_meta, vars=None):
    if vars is not None:
        for var in vars:
            element = add_cdi_element(root, 'IdentifierComponent')
            add_identifier(element, f"#identifierComponent-{var}")
            DataStructureComponent_isDefinedBy_RepresentedVariable = add_cdi_element(element,
                                                                                     'DataStructureComponent_isDefinedBy_RepresentedVariable')
            add_ddiref(DataStructureComponent_isDefinedBy_RepresentedVariable, f"#instanceVariable-{var}", agency,
                       "InstanceVariable")
    return root


# In[ ]:


# MeasureComponent2
def generate_MeasureComponent2(df_meta, vars=None):
    if vars is None:
        for variable in df_meta.column_names:
            MeasureComponent = add_cdi_element(root, 'MeasureComponent')
            add_identifier(MeasureComponent, f"#measureComponent-{variable}")
            DataStructureComponent_isDefinedBy_RepresentedVariable = add_cdi_element(MeasureComponent,
                                                                                     'DataStructureComponent_isDefinedBy_RepresentedVariable')
            add_ddiref(DataStructureComponent_isDefinedBy_RepresentedVariable, f"#instanceVariable-{variable}", agency,
                       "InstanceVariable")
    else:
        for variable in (df_meta.column_names):
            if variable not in vars:
                MeasureComponent = add_cdi_element(root, 'MeasureComponent')
                add_identifier(MeasureComponent, f"#measureComponent-{variable}")
                DataStructureComponent_isDefinedBy_RepresentedVariable = add_cdi_element(MeasureComponent,
                                                                                         'DataStructureComponent_isDefinedBy_RepresentedVariable')
                add_ddiref(DataStructureComponent_isDefinedBy_RepresentedVariable, f"#instanceVariable-{variable}",
                           agency, "InstanceVariable")
    return root


# In[ ]:


# PrimaryKey2
def generate_PrimaryKey2(df_meta, vars=None):
    element = add_cdi_element(root, 'PrimaryKey')
    add_identifier(element, f"#primaryKey")
    if vars is not None:
        for var in vars:
            PrimaryKey_isComposedOf_PrimaryKeyComponent = add_cdi_element(element,
                                                                          'PrimaryKey_isComposedOf_PrimaryKeyComponent')
            add_ddiref(PrimaryKey_isComposedOf_PrimaryKeyComponent, f"#primaryKeyComponent-{var}", agency,
                       f"PrimaryKeyComponent")
    return root


# In[ ]:


# PrimaryKeyComponent2
def generate_PrimaryKeyComponent2(df_meta, vars=None):
    if vars is not None:
        for var in vars:
            element = add_cdi_element(root, 'PrimaryKeyComponent')
            add_identifier(element, f"#primaryKeyComponent-{var}")
            PrimaryKeyComponent_correspondsTo_DataStructureComponent = add_cdi_element(element,
                                                                                       'PrimaryKeyComponent_correspondsTo_DataStructureComponent')
            add_ddiref(PrimaryKeyComponent_correspondsTo_DataStructureComponent, f"#identifierComponent-{var}", agency,
                       "IdentifierComponent")
    return root


# In[ ]:|


def generate_complete_xml2(df, df_meta, vars=None, spssfile='name'):
    # Define the namespace
    nsmap = {'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/'}
    # Create the root element
    global root
    root = etree.Element(etree.QName(nsmap['cdi'], 'DDICDIModels'), nsmap=nsmap)
    root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
             'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/ https://ddi-cdi-resources.bitbucket.io/2024-03-12/encoding/xml-schema/ddi-cdi.xsd')
    global agency
    agency = 'int.esseric'

    generate_WideDataStructure2(df_meta, vars)
    generate_IdentifierComponent2(df_meta, vars)
    generate_MeasureComponent2(df_meta, vars)
    generate_PrimaryKey2(df_meta, vars)
    generate_PrimaryKeyComponent2(df_meta, vars)

    # Add XML declaration and write XML file
    xml_string = etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=True)

    # Add the comment as the second line
    # add current time to xml_string
    current_time = datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")

    # Create the comment string and encode it to bytes
    comment = f'<!-- CDI version 1, generated: {current_time} -->'.encode('utf-8')

    # Replace the XML declaration with the declaration followed by the comment
    xml_string_with_comment = xml_string.replace(b'?>', b'?>\n' + comment, 1)

    # with open(r'files/CDI2.xml', 'wb') as f:
    #     f.write(xml_string_with_comment)

    return xml_string_with_comment

# Function to update XML
def update_xml(original_xml, new_xml):
    # Parse the XMLs into ElementTree objects
    original_tree = ET.ElementTree(ET.fromstring(original_xml))
    new_tree = ET.ElementTree(ET.fromstring(new_xml))

    # Get the root elements
    original_root = original_tree.getroot()
    new_root = new_tree.getroot()

    # Get the tags of the elements directly under the new root
    new_tags = {child.tag for child in new_root}

    # Remove all children of the original root that have the same tag as any of the new elements
    original_root[:] = [child for child in original_root if child.tag not in new_tags]

    # Add all children from the new root to the original root
    for child in new_root:
        original_root.append(child)

    # Convert the updated original tree back into a string
    updated_xml = ET.tostring(original_root, encoding='utf-8').decode()

    return updated_xml
