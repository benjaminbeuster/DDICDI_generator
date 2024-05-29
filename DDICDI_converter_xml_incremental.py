from lxml import etree
import xml.etree.ElementTree as ET
from spss_import import read_sav

# Load your dataframe and metadata here
df, df_meta, file_name, n_rows = read_sav("files/ESS10-subset.sav")

# Define the namespaces
nsmap = {
    'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/',
    'r': 'ddi:reusable:3_3'  # Replace with the actual URI for the 'r' namespace
}
agency = 'int.esseric'

# Helper functions for incremental writing
def add_cdi_element_incremental(xf, tag, text=None):
    with xf.element(etree.QName(nsmap['cdi'], tag)):
        if text is not None:
            xf.write(str(text))

def add_identifier_incremental(xf, id_value, agency='int.esseric'):
    with xf.element(etree.QName(nsmap['cdi'], 'identifier')):
        with xf.element(etree.QName(nsmap['cdi'], 'ddiIdentifier')):
            add_cdi_element_incremental(xf, 'dataIdentifier', id_value)
            add_cdi_element_incremental(xf, 'registrationAuthorityIdentifier', agency)
            add_cdi_element_incremental(xf, 'versionIdentifier', "1")

def add_ddiref_incremental(xf, ref_id, agency, validType):
    with xf.element(etree.QName(nsmap['cdi'], 'ddiReference')):
        add_cdi_element_incremental(xf, 'dataIdentifier', ref_id)
        add_cdi_element_incremental(xf, 'registrationAuthorityIdentifier', agency)
        add_cdi_element_incremental(xf, 'versionIdentifier', "1")
    # Note that 'validType' is added to the parent of 'DDIReference', not as a child of 'DDIReference'
    add_cdi_element_incremental(xf, 'validType', validType)


###########################################################################
###########################################################################
###########################################################################      

def generate_DataStore_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'DataStore')):
        add_cdi_element_incremental(xf, 'allowsDuplicates', "false")
        add_identifier_incremental(xf, f"#dataStore", agency)
        add_cdi_element_incremental(xf, 'recordCount', str(df_meta.number_rows))
        with xf.element(etree.QName(nsmap['cdi'], 'DataStore_has_LogicalRecord')):
            add_ddiref_incremental(xf, f"#logicalRecord", agency, "LogicalRecord")

def generate_LogicalRecord_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'LogicalRecord')):
        add_identifier_incremental(xf, f"#logicalRecord", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'LogicalRecord_organizes_DataSet')):
            add_ddiref_incremental(xf, f"#wideDataSet", agency, "WideDataSet")
        for idx, variable in enumerate(df_meta.column_names):
            with xf.element(etree.QName(nsmap['cdi'], 'LogicalRecord_has_InstanceVariable')):
                add_ddiref_incremental(xf, f"#instanceVariable-{variable}", agency, "InstanceVariable")

def generate_WideDataSet_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'WideDataSet')):
        add_identifier_incremental(xf, f"#wideDataSet", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'DataSet_isStructuredBy_DataStructure')):
            add_ddiref_incremental(xf, f"#wideDataStructure", agency, "WideDataStructure")

def generate_WideDataStructure_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'WideDataStructure')):
        add_identifier_incremental(xf, f"#wideDataStructure", agency)
        
        # IdentifierComponent for the first column
        with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_DataStructureComponent')):
            add_ddiref_incremental(xf, f"#identifierComponent-{df_meta.column_names[0]}", agency, "IdentifierComponent")
        
        # MeasureComponent for the remaining columns
        for variable in df_meta.column_names[1:]:
            with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_DataStructureComponent')):
                add_ddiref_incremental(xf, f"#measureComponent-{variable}", agency, "MeasureComponent")
        
        # PrimaryKey
        with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_PrimaryKey')):
            add_ddiref_incremental(xf, f"#primaryKey", agency, "PrimaryKey")

def generate_IdentifierComponent_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'IdentifierComponent')):
        add_identifier_incremental(xf, f"#identifierComponent-{df_meta.column_names[0]}", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'DataStructureComponent_isDefinedBy_RepresentedVariable')):
            add_ddiref_incremental(xf, f"#instanceVariable-{df_meta.column_names[0]}", agency, "InstanceVariable")

def generate_MeasureComponent_incremental(xf, df_meta, agency):
    for variable in df_meta.column_names[1:]:
        with xf.element(etree.QName(nsmap['cdi'], 'MeasureComponent')):
            add_identifier_incremental(xf, f"#measureComponent-{variable}", agency)
            with xf.element(etree.QName(nsmap['cdi'], 'DataStructureComponent_isDefinedBy_RepresentedVariable')):
                add_ddiref_incremental(xf, f"#instanceVariable-{variable}", agency, "InstanceVariable")


def generate_PrimaryKey_incremental(xf, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKey')):
        add_identifier_incremental(xf, f"#primaryKey", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKey_isComposedOf_PrimaryKeyComponent')):
            add_ddiref_incremental(xf, f"#primaryKeyComponent", agency, "PrimaryKeyComponent")

def generate_PrimaryKeyComponent_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKeyComponent')):
        add_identifier_incremental(xf, f"#primaryKeyComponent", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKeyComponent_correspondsTo_DataStructureComponent')):
            add_ddiref_incremental(xf, f"#identifierComponent-{df_meta.column_names[0]}", agency, "IdentifierComponent")


def generate_InstanceVariable_incremental(xf, df_meta, agency):
    for idx, variable in enumerate(df_meta.column_names):
        with xf.element(etree.QName(nsmap['cdi'], 'InstanceVariable')):
            with xf.element(etree.QName(nsmap['cdi'], 'displayLabel')):
                with xf.element(etree.QName(nsmap['cdi'], 'languageSpecificString')):
                    add_cdi_element_incremental(xf, 'content', df_meta.column_labels[idx])
            add_identifier_incremental(xf, f"#instanceVariable-{variable}", agency)
            with xf.element(etree.QName(nsmap['cdi'], 'name')):
                add_cdi_element_incremental(xf, 'name', variable)
            with xf.element(etree.QName(nsmap['cdi'], 'hasIntendedDataType')):
                add_cdi_element_incremental(xf, 'name', df_meta.original_variable_types[variable])

            # Check if variable has sentinel concepts
            if variable in df_meta.missing_ranges or (
                    len(df_meta.missing_ranges) == 0 and variable in df_meta.missing_user_values):
                with xf.element(etree.QName(nsmap['cdi'], 'RepresentedVariable_takesSentinelValuesFrom_SentinelValueDomain')):
                    add_ddiref_incremental(xf, f"#sentinelValueDomain-{variable}", agency, "SentinelValueDomain")
            with xf.element(etree.QName(nsmap['cdi'], 'RepresentedVariable_takesSubstantiveValuesFrom_SubstantiveValueDomain')):
                add_ddiref_incremental(xf, f"#substantiveValueDomain-{variable}", agency, 'SubstantiveValueDomain')
            with xf.element(etree.QName(nsmap['cdi'], 'InstanceVariable_has_PhysicalSegmentLayout')):
                add_ddiref_incremental(xf, f"#physicalSegmentLayout", agency, "PhysicalSegmentLayout")
            with xf.element(etree.QName(nsmap['cdi'], 'InstanceVariable_has_ValueMapping')):
                add_ddiref_incremental(xf, f"#valueMapping-{variable}", agency, "ValueMapping")

def generate_SubstantiveValueDomain_incremental(xf, df_meta, agency):
    for var in df_meta.column_names:
        with xf.element(etree.QName(nsmap['cdi'], 'SubstantiveValueDomain')):
            add_identifier_incremental(xf, f"#substantiveValueDomain-{var}", agency)
            
            if var in df_meta.variable_value_labels:
                with xf.element(etree.QName(nsmap['cdi'], 'SubstantiveValueDomain_takesValuesFrom_EnumerationDomain')):
                    add_ddiref_incremental(xf, f"#substantiveCodelist-{var}", agency, 'CodeList')
            
            with xf.element(etree.QName(nsmap['cdi'], 'SubstantiveValueDomain_isDescribedBy_ValueAndConceptDescription')):
                add_ddiref_incremental(xf, f"#substantiveValueAndConceptDescription-{var}", agency, "ValueAndConceptDescription")

def generate_SentinelValueDomain_incremental(xf, df_meta, agency):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    for variable in relevant_variables:
        with xf.element(etree.QName(nsmap['cdi'], 'SentinelValueDomain')):
            add_identifier_incremental(xf, f"#sentinelValueDomain-{variable}", agency)

            if variable in df_meta.variable_value_labels:
                with xf.element(etree.QName(nsmap['cdi'], 'SentinelValueDomain_takesValuesFrom_EnumerationDomain')):
                    add_ddiref_incremental(xf, f"#sentinelCodelist-{variable}", agency, 'CodeList')

            with xf.element(etree.QName(nsmap['cdi'], 'SentinelValueDomain_isDescribedBy_ValueAndConceptDescription')):
                add_ddiref_incremental(xf, f"#sentinelValueAndConceptDescription-{variable}", agency, "ValueAndConceptDescription")

def generate_ValueAndConceptDescription_incremental(xf, df_meta, agency):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if df_meta.missing_ranges else df_meta.missing_user_values

    # Recode classification level
    class_level = {'nominal': 'Nominal', 'scale': 'Continuous', 'ordinal': 'Ordinal', 'unknown': 'Nominal'}
    for variable in df_meta.column_names:
        with xf.element(etree.QName(nsmap['cdi'], 'ValueAndConceptDescription')):
            add_cdi_element_incremental(xf, 'classificationLevel', class_level[df_meta.variable_measure[variable]])
            add_identifier_incremental(xf, f"#substantiveValueAndConceptDescription-{variable}", agency)

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

            with xf.element(etree.QName(nsmap['cdi'], 'ValueAndConceptDescription')):
                with xf.element(etree.QName(nsmap['cdi'], 'description')):
                    with xf.element(etree.QName(nsmap['cdi'], 'languageSpecificString')):
                        add_cdi_element_incremental(xf, 'content', str(values))
                add_identifier_incremental(xf, f"#sentinelValueAndConceptDescription-{variable}", agency)
                add_cdi_element_incremental(xf, "maximumValueExclusive", str(max_val))
                add_cdi_element_incremental(xf, "minimumValueExclusive", str(min_val))

def generate_CodeList_incremental(xf, df_meta, agency):
    # Determine the relevant variables based on the presence of missing values
    relevant_variables = df_meta.missing_ranges if len(df_meta.missing_ranges) > 0 else df_meta.missing_user_values

    for variable_name, values_dict in df_meta.variable_value_labels.items():
        with xf.element(etree.QName(nsmap['cdi'], 'CodeList')):
            add_identifier_incremental(xf, f"#substantiveCodelist-{variable_name}", agency)
            with xf.element(etree.QName(nsmap['cdi'], 'name')):
                add_cdi_element_incremental(xf, 'name', f"#substantiveCodelist-{variable_name}")
            add_cdi_element_incremental(xf, 'allowsDuplicates', "false")

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
                    with xf.element(etree.QName(nsmap['cdi'], 'CodeList_has_Code')):
                        add_ddiref_incremental(xf, f"#code-{value}-{variable_name}", agency, "Code")


def is_value_in_range(value, ranges):
    """Check if a value is in any of the given ranges."""
    for range_dict in ranges:
        if range_dict['lo'] <= value <= range_dict['hi']:
            return True
    return False

def generate_SentinelCodelist_incremental(xf, df_meta, agency):
    # Check if there are any missing ranges or user-defined missing values for any variable
    has_missing_values = any(len(df_meta.missing_ranges.get(var, [])) > 0 or
                             len(df_meta.missing_user_values.get(var, [])) > 0
                             for var in df_meta.column_names)

    # If there are no missing values for any variable, return early without generating XML
    if not has_missing_values:
        return

    for variable_name, values_dict in df_meta.variable_value_labels.items():
        # Determine if the current variable has missing values defined
        variable_has_missing = variable_name in df_meta.missing_ranges or \
                               variable_name in df_meta.missing_user_values

        # Only generate XML elements for variables with missing values
        if variable_has_missing:
            with xf.element(etree.QName(nsmap['cdi'], 'CodeList')):
                add_identifier_incremental(xf, f"#sentinelCodelist-{variable_name}", agency)
                with xf.element(etree.QName(nsmap['cdi'], 'name')):
                    add_cdi_element_incremental(xf, 'name', f"#sentinelCodelist-{variable_name}")
                add_cdi_element_incremental(xf, 'allowsDuplicates', "false")

                if variable_name in df_meta.missing_ranges:
                    # Use a for loop to generate the hasTopConcept list
                    for value in values_dict.keys():
                        if is_value_in_range(value, df_meta.missing_ranges[variable_name]):
                            with xf.element(etree.QName(nsmap['cdi'], 'CodeList_has_Code')):
                                add_ddiref_incremental(xf, f"#code-{value}-{variable_name}", agency, "Code")
                elif variable_name in df_meta.missing_user_values:
                    excluded_values = set(df_meta.missing_user_values[variable_name])
                    for value in values_dict.keys():
                        if value in excluded_values:
                            with xf.element(etree.QName(nsmap['cdi'], 'CodeList_has_Code')):
                                add_ddiref_incremental(xf, f"#code-{value}-{variable_name}", agency, "Code")


def generate_Code_incremental(xf, df_meta, agency):
    for variable_name, values_dict in df_meta.variable_value_labels.items():
        for key, value in values_dict.items():
            with xf.element(etree.QName(nsmap['cdi'], 'Code')):
                add_identifier_incremental(xf, f"#code-{key}-{variable_name}", agency)
                with xf.element(etree.QName(nsmap['cdi'], 'Code_denotes_Category')):
                    add_ddiref_incremental(xf, f"#category-{value}", agency, "Category")
                with xf.element(etree.QName(nsmap['cdi'], 'Code_uses_Notation')):
                    add_ddiref_incremental(xf, f"#notation-{key}", agency, "Notation")

def generate_Category_incremental(xf, df_meta, agency):
    cats = list(set(value for values_dict in df_meta.variable_value_labels.values() for value in values_dict.values()))
    for cat in cats:
        with xf.element(etree.QName(nsmap['cdi'], 'Category')):
            with xf.element(etree.QName(nsmap['cdi'], 'displayLabel')):
                with xf.element(etree.QName(nsmap['cdi'], 'languageSpecificString')):
                    add_cdi_element_incremental(xf, 'content', f"{cat}")
            add_identifier_incremental(xf, f"#category-{cat}", agency)
            with xf.element(etree.QName(nsmap['cdi'], 'name')):
                add_cdi_element_incremental(xf, 'name', f"{cat}")

def generate_Notation_incremental(xf, df_meta, agency):
    notations = list(set(key for values_dict in df_meta.variable_value_labels.values() for key in values_dict.keys()))
    for note in notations:
        with xf.element(etree.QName(nsmap['cdi'], 'Notation')):
            with xf.element(etree.QName(nsmap['cdi'], 'content')):
                add_cdi_element_incremental(xf, 'content', f"{note}")
            add_identifier_incremental(xf, f"#notation-{note}", agency)

def generate_PhysicalDataSetStructure_incremental(xf, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSetStructure')):
        add_identifier_incremental(xf, f"#physicalDataSetStructure", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSetStructure_correspondsTo_DataStructure')):
            add_ddiref_incremental(xf, f"#wideDataStructure", agency, "WideDataStructure")
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSetStructure_structures_PhysicalDataSet')):
            add_ddiref_incremental(xf, f"#physicalDataSet", agency, "PhysicalDataSet")

def generate_PhysicalDataset_incremental(xf, df_meta, spssfile, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSet')):
        add_cdi_element_incremental(xf, 'allowsDuplicates', "false")
        add_identifier_incremental(xf, f"#physicalDataset", agency)
        add_cdi_element_incremental(xf, 'physicalFileName', spssfile)
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSet_correspondsTo_DataSet')):
            add_ddiref_incremental(xf, f"#wideDataset", agency, "WideDataSet")
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSet_formats_DataStore')):
            add_ddiref_incremental(xf, f"#dataStore", agency, "DataStore")
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalDataSet_has_PhysicalRecordSegment')):
            add_ddiref_incremental(xf, f"#physicalRecordSegment", agency, "PhysicalRecordSegment")

def generate_PhysicalRecordSegment_incremental(xf, df, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PhysicalRecordSegment')):
        add_cdi_element_incremental(xf, 'allowsDuplicates', "false")
        add_identifier_incremental(xf, f"#physicalRecordSegment", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalRecordSegment_has_PhysicalSegmentLayout')):
            add_ddiref_incremental(xf, f"#physicalSegmentLayout", agency, "PhysicalSegmentLayout")
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalRecordSegment_mapsTo_LogicalRecord')):
            add_ddiref_incremental(xf, f"#logicalRecord", agency, "LogicalRecord")

        # Iterate through column names and associated index
        for idx, variable in enumerate(df_meta.column_names):
            # Assuming there are multiple DataPointPositions per variable, and the index (i) is relevant
            for i in range(len(df[variable])):
                with xf.element(etree.QName(nsmap['cdi'], 'PhysicalRecordSegment_has_DataPointPosition')):
                    add_ddiref_incremental(xf, f"#dataPointPosition-{i}-{variable}", agency, "DataPointPosition")


def generate_PhysicalSegmentLayout_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PhysicalSegmentLayout')):
        add_cdi_element_incremental(xf, 'allowsDuplicates', "false")
        add_identifier_incremental(xf, f"#physicalSegmentLayout", agency)
        add_cdi_element_incremental(xf, 'isDelimited', "false")
        add_cdi_element_incremental(xf, 'isFixedWidth', "false")
        with xf.element(etree.QName(nsmap['cdi'], 'PhysicalSegmentLayout_formats_LogicalRecord')):
            add_ddiref_incremental(xf, f"#logicalRecord", agency, "LogicalRecord")

        for variable in df_meta.column_names:
            with xf.element(etree.QName(nsmap['cdi'], 'PhysicalSegmentLayout_has_ValueMapping')):
                add_ddiref_incremental(xf, f"#valueMapping-{variable}", agency, "ValueMapping")

        for variable in df_meta.column_names:
            with xf.element(etree.QName(nsmap['cdi'], 'PhysicalSegmentLayout_has_ValueMappingPosition')):
                add_ddiref_incremental(xf, f"#valueMappingPosition-{variable}", agency, "ValueMappingPosition")

def generate_ValueMapping_incremental(xf, df, df_meta, agency):
    for variable in df_meta.column_names:
        with xf.element(etree.QName(nsmap['cdi'], 'ValueMapping')):
            add_cdi_element_incremental(xf, 'defaultValue', "")
            add_identifier_incremental(xf, f"#valueMapping-{variable}", agency)

            # Assuming there are multiple DataPoints per variable, and the index (i) is relevant
            for i in range(len(df[variable])):
                with xf.element(etree.QName(nsmap['cdi'], 'ValueMapping_formats_DataPoint')):
                    add_ddiref_incremental(xf, f"#dataPoint-{i}-{variable}", agency, "DataPoint")

def generate_ValueMappingPosition_incremental(xf, df_meta, agency):
    for idx, variable in enumerate(df_meta.column_names):
        with xf.element(etree.QName(nsmap['cdi'], 'ValueMappingPosition')):
            add_identifier_incremental(xf, f"#valueMappingPosition-{variable}", agency)
            add_cdi_element_incremental(xf, 'value', idx)
            with xf.element(etree.QName(nsmap['cdi'], 'ValueMappingPosition_indexes_ValueMapping')):
                add_ddiref_incremental(xf, f"#valueMapping-{variable}", agency, "ValueMapping")

def generate_DataPoint_incremental(xf, df, df_meta, agency):
    for variable in df_meta.column_names:
        # Assuming there are multiple DataPoints per variable, and the index (idx) is relevant
        for idx in range(len(df[variable])):
            with xf.element(etree.QName(nsmap['cdi'], 'DataPoint')):
                add_identifier_incremental(xf, f"#dataPoint-{idx}-{variable}", agency)
                with xf.element(etree.QName(nsmap['cdi'], 'DataPoint_isDescribedBy_InstanceVariable')):
                    add_ddiref_incremental(xf, f"#instanceVariable-{variable}", agency, "InstanceVariable")


def generate_DataPointPosition_incremental(xf, df, df_meta, agency):
    for variable in df_meta.column_names:
        # Assuming there are multiple DataPointPositions per variable, and the index (idx) is relevant
        for idx in range(len(df[variable])):
            with xf.element(etree.QName(nsmap['cdi'], 'DataPointPosition')):
                add_identifier_incremental(xf, f"#dataPointPosition-{idx}-{variable}", agency)
                add_cdi_element_incremental(xf, 'value', idx)
                with xf.element(etree.QName(nsmap['cdi'], 'DataPointPosition_indexes_DataPoint')):
                    add_ddiref_incremental(xf, f"#dataPoint-{idx}-{variable}", agency, "DataPoint")

def generate_InstanceValue_incremental(xf, df, df_meta, agency):
    for variable in df_meta.column_names:
        for idx, value in enumerate(df[variable]):
            with xf.element(etree.QName(nsmap['cdi'], 'InstanceValue')):
                with xf.element(etree.QName(nsmap['cdi'], 'content')):
                    add_cdi_element_incremental(xf, 'content', value)
                add_identifier_incremental(xf, f"#instanceValue-{idx}-{variable}", agency)

                if variable in df_meta.missing_ranges:
                    for range_dict in df_meta.missing_ranges[variable]:
                        if value is not None and isinstance(range_dict['lo'], float):
                            # convert value to float for comparison
                            value = float(value)
                        if value is not None and range_dict['lo'] <= value <= range_dict['hi'] and isinstance(value, (str, int, float)):
                            with xf.element(etree.QName(nsmap['cdi'], 'InstanceValue_hasValueFrom_ValueDomain')):
                                add_ddiref_incremental(xf, f"#sentinelValueDomain-{variable}", agency, "SentinelValueDomain")
                            break
                    else:
                        with xf.element(etree.QName(nsmap['cdi'], 'InstanceValue_hasValueFrom_ValueDomain')):
                            add_ddiref_incremental(xf, f"#substantiveValueDomain-{variable}", agency, "SubstantiveValueDomain")
                else:
                    with xf.element(etree.QName(nsmap['cdi'], 'InstanceValue_hasValueFrom_ValueDomain')):
                        add_ddiref_incremental(xf, f"#substantiveValueDomain-{variable}", agency, "SubstantiveValueDomain")

                with xf.element(etree.QName(nsmap['cdi'], 'InstanceValue_isStoredIn_DataPoint')):
                    add_ddiref_incremental(xf, f"#dataPoint-{idx}-{variable}", agency, "DataPoint")


###########################################################################


from lxml import etree

def pretty_print_xml(input_file, output_file):
    parser = etree.XMLParser(remove_blank_text=True)
    document = etree.parse(input_file, parser)
    document.write(output_file, pretty_print=True, encoding='UTF-8', xml_declaration=True)

def generate_complete_xml_incremental(df, df_meta, spssfile='name', output_file='output.xml'):
    temp_file = 'temp_output.xml'
    schema_location = ('http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/ '
                       'https://ddi-cdi-resources.bitbucket.io/2024-03-12/encoding/xml-schema/ddi-cdi.xsd')
    with etree.xmlfile(temp_file, encoding='UTF-8') as xf:
        xf.write_declaration(standalone=True)
        # Define the root element with the schemaLocation attribute
        with xf.element(etree.QName(nsmap['cdi'], 'DDICDIModels'), nsmap=nsmap, 
                        attrib={"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": schema_location}):  
            generate_PhysicalDataSetStructure_incremental(xf, agency)
            generate_PhysicalDataset_incremental(xf, df_meta, spssfile, agency)
            generate_PhysicalRecordSegment_incremental(xf, df, df_meta, agency)
            generate_PhysicalSegmentLayout_incremental(xf, df_meta, agency)
            generate_ValueMappingPosition_incremental(xf, df_meta, agency)
            generate_ValueMapping_incremental(xf, df, df_meta, agency)
            generate_DataPoint_incremental(xf, df, df_meta, agency)
            generate_DataPointPosition_incremental(xf, df, df_meta, agency)
            generate_InstanceValue_incremental(xf, df, df_meta, agency)
            generate_DataStore_incremental(xf, df_meta, agency)
            generate_LogicalRecord_incremental(xf, df_meta, agency)
            generate_WideDataSet_incremental(xf, df_meta, agency)
            generate_WideDataStructure_incremental(xf, df_meta, agency)
            generate_IdentifierComponent_incremental(xf, df_meta, agency)
            generate_MeasureComponent_incremental(xf, df_meta, agency)
            generate_PrimaryKey_incremental(xf, agency)
            generate_PrimaryKeyComponent_incremental(xf, df_meta, agency)
            generate_InstanceVariable_incremental(xf, df_meta, agency)
            generate_SubstantiveValueDomain_incremental(xf, df_meta, agency)
            generate_SentinelValueDomain_incremental(xf, df_meta, agency)
            generate_ValueAndConceptDescription_incremental(xf, df_meta, agency)
            generate_CodeList_incremental(xf, df_meta, agency)
            generate_SentinelCodelist_incremental(xf, df_meta, agency)
            generate_Code_incremental(xf, df_meta, agency)
            generate_Category_incremental(xf, df_meta, agency)
            generate_Notation_incremental(xf, df_meta, agency)





                
            # ... other elements would be generated here incrementally

    # After the file has been written incrementally, pretty-print it to the final output file
    pretty_print_xml(temp_file, output_file)

    # Optionally, remove the temporary file
    import os
    os.remove(temp_file)

# Call the function to generate the XML and write to a file
#generate_complete_xml_incremental(df, df_meta, spssfile=file_name, output_file='output.xml')


###########################################################################

def generate_WideDataStructure2_incremental(xf, df_meta, vars, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'WideDataStructure')):
        add_identifier_incremental(xf, "#wideDataStructure", agency)

        # If vars is None, iterate through all column names in df_meta
        if vars is None:
            for variable in df_meta.column_names:
                with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_DataStructureComponent')):
                    add_ddiref_incremental(xf, f"#measureComponent-{variable}", agency, "MeasureComponent")

        # If vars is not None
        else:
            # Iterate through all variables in vars
            for var in vars:
                with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_DataStructureComponent')):
                    add_ddiref_incremental(xf, f"#identifierComponent-{var}", agency, "IdentifierComponent")

            # Iterate through all column names in df_meta
            for variable in df_meta.column_names:
                # If the variable is not in vars
                if variable not in vars:
                    with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_DataStructureComponent')):
                        add_ddiref_incremental(xf, f"#measureComponent-{variable}", agency, "MeasureComponent")

        with xf.element(etree.QName(nsmap['cdi'], 'DataStructure_has_PrimaryKey')):
            add_ddiref_incremental(xf, f"#primaryKey", agency, "PrimaryKey")

def generate_IdentifierComponent2_incremental(xf, df_meta, vars, agency):
    if vars is not None:
        for var in vars:
            with xf.element(etree.QName(nsmap['cdi'], 'IdentifierComponent')):
                add_identifier_incremental(xf, f"#identifierComponent-{var}", agency)
                with xf.element(etree.QName(nsmap['cdi'], 'DataStructureComponent_isDefinedBy_RepresentedVariable')):
                    add_ddiref_incremental(xf, f"#instanceVariable-{var}", agency, "InstanceVariable")

def generate_MeasureComponent2_incremental(xf, df_meta, vars, agency):
    if vars is None:
        for variable in df_meta.column_names:
            with xf.element(etree.QName(nsmap['cdi'], 'MeasureComponent')):
                add_identifier_incremental(xf, f"#measureComponent-{variable}", agency)
                with xf.element(etree.QName(nsmap['cdi'], 'DataStructureComponent_isDefinedBy_RepresentedVariable')):
                    add_ddiref_incremental(xf, f"#instanceVariable-{variable}", agency, "InstanceVariable")
    else:
        for variable in df_meta.column_names:
            if variable not in vars:
                with xf.element(etree.QName(nsmap['cdi'], 'MeasureComponent')):
                    add_identifier_incremental(xf, f"#measureComponent-{variable}", agency)
                    with xf.element(etree.QName(nsmap['cdi'], 'DataStructureComponent_isDefinedBy_RepresentedVariable')):
                        add_ddiref_incremental(xf, f"#instanceVariable-{variable}", agency, "InstanceVariable")

def generate_PrimaryKey2_incremental(xf, df_meta, vars, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKey')):
        add_identifier_incremental(xf, f"#primaryKey", agency)
        if vars is not None:
            for var in vars:
                with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKey_isComposedOf_PrimaryKeyComponent')):
                    add_ddiref_incremental(xf, f"#primaryKeyComponent-{var}", agency, "PrimaryKeyComponent")

def generate_PrimaryKeyComponent2_incremental(xf, df_meta, vars, agency):
    if vars is not None:
        for var in vars:
            with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKeyComponent')):
                add_identifier_incremental(xf, f"#primaryKeyComponent-{var}", agency)
                with xf.element(etree.QName(nsmap['cdi'], 'PrimaryKeyComponent_correspondsTo_DataStructureComponent')):
                    add_ddiref_incremental(xf, f"#identifierComponent-{var}", agency, "IdentifierComponent")

#################################################################################################################################

from lxml import etree

def update_xml(original_xml, new_xml):
    # Parse the XMLs into lxml Element objects
    original_tree = etree.fromstring(original_xml.encode('utf-8'))
    new_tree = etree.fromstring(new_xml.encode('utf-8'))

    # Get the root elements
    original_root = original_tree
    new_root = new_tree

    # Get the tags of the elements directly under the new root
    new_tags = {etree.QName(child).localname for child in new_root}

    # Remove all children of the original root that have the same tag as any of the new elements
    original_root[:] = [child for child in original_root if etree.QName(child).localname not in new_tags]

    # Add all children from the new root to the original root
    for child in new_root:
        original_root.append(child)

    # Convert the updated original tree back into a pretty-printed string
    updated_xml = etree.tostring(original_root, pretty_print=True, encoding='utf-8').decode()

    return updated_xml