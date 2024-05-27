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
    with xf.element(etree.QName(nsmap['cdi'], 'Identifier')):
        with xf.element(etree.QName(nsmap['cdi'], 'DDIIdentifier')):
            add_cdi_element_incremental(xf, 'DataIdentifier', id_value)
            add_cdi_element_incremental(xf, 'Agency', agency)
            add_cdi_element_incremental(xf, 'Version', "1")

def add_ddiref_incremental(xf, ref_id, agency, object_type):
    with xf.element(etree.QName(nsmap['cdi'], 'DDIReference')):
        add_cdi_element_incremental(xf, 'DataIdentifier', ref_id)
        add_cdi_element_incremental(xf, 'Agency', agency)
        add_cdi_element_incremental(xf, 'Version', "1")
        add_cdi_element_incremental(xf, 'TypeOfObject', object_type)


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

def generate_DataStore(df_meta):
    element = add_cdi_element(root, 'DataStore')
    add_cdi_element(element, 'allowsDuplicates', "false")
    add_identifier(element, f"#dataStore")
    add_cdi_element(element, 'recordCount', df_meta.number_rows)
    LogicalRecord = add_cdi_element(element, 'DataStore_has_LogicalRecord')
    add_ddiref(LogicalRecord, f"#logicalRecord", agency, "LogicalRecord")
    return root

def generate_LogicalRecord_incremental(xf, df_meta, agency):
    with xf.element('LogicalRecord'):
        add_identifier_incremental(xf, f"#logicalRecord")
        with xf.element('LogicalRecord_organizes_DataSet'):
            add_ddiref_incremental(xf, f"#wideDataSet", agency, "WideDataSet")
        for idx, variable in enumerate(df_meta.column_names):
            with xf.element('LogicalRecord_has_InstanceVariable'):
                add_ddiref_incremental(xf, f"#instanceVariable-{variable}", agency, "InstanceVariable")

def generate_WideDataSet_incremental(xf, df_meta, agency):
    with xf.element(etree.QName(nsmap['cdi'], 'WideDataSet')):
        add_identifier_incremental(xf, f"#wideDataSet", agency)
        with xf.element(etree.QName(nsmap['cdi'], 'DataSetIsStructuredByDataStructure')):
            add_ddiref_incremental(xf, f"#wideDataStructure", agency, "WideDataStructure")

# Function to generate the complete XML incrementally
def generate_complete_xml_incremental(df, df_meta, spssfile='name', output_file='output.xml'):
    with etree.xmlfile(output_file, encoding='UTF-8') as xf:
        xf.write_declaration(standalone=True)
        with xf.element(etree.QName(nsmap['cdi'], 'DDICDIModels'), nsmap=nsmap):
            generate_DataStore_incremental(xf, df_meta, agency)
            generate_LogicalRecord_incremental(xf, df_meta, agency)
            generate_WideDataSet_incremental(xf, df_meta, agency)
            # ... call other refactored functions similarly

# Call the function to generate the XML and write to a file
generate_complete_xml_incremental(df, df_meta, spssfile='name', output_file='output.xml')