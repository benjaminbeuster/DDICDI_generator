from lxml import etree
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

                with xf.element(etree.QName(nsmap['cdi'], 'description')):
                    with xf.element(etree.QName(nsmap['cdi'], 'languageSpecificString')):
                        add_cdi_element_incremental(xf, 'content', str(values))
                add_identifier_incremental(xf, f"#sentinelValueAndConceptDescription-{variable}", agency)
                add_cdi_element_incremental(xf, "maximumValueExclusive", str(max_val))
                add_cdi_element_incremental(xf, "minimumValueExclusive", str(min_val))

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
            # ... other elements would be generated here incrementally

    # After the file has been written incrementally, pretty-print it to the final output file
    pretty_print_xml(temp_file, output_file)

    # Optionally, remove the temporary file
    import os
    os.remove(temp_file)

# Call the function to generate the XML and write to a file
generate_complete_xml_incremental(df, df_meta, spssfile='name', output_file='output.xml')