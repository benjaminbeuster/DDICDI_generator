from datetime import datetime

prefix = "https://docs.ddialliance.org/DDI-CDI/1.0/model/FieldLevelDocumentation/DDICDILibrary/Classes"

markdown_text = r"""
## DDI-CDI Subset

This profile utilizes 29 classes from the DDI-CDI model (v1.0) and 333 SKOS classes.

|  DDI-CDI Classes  |  DDI-CDI Classes  | SKOS Classes |
|------------------|------------------|------------------|
| [AttributeComponent]({0}/DataDescription/Components/AttributeComponent.html) | [PhysicalDataSet]({0}/FormatDescription/PhysicalDataSet.html#super-class-hierarchy-generalization) | [`skos:ConceptScheme`](https://www.w3.org/2009/08/skos-reference/skos.html#ConceptScheme) |
| [ComponentPosition]({0}/DataDescription/Components/ComponentPosition.html) | [PhysicalRecordSegment]({0}/FormatDescription/PhysicalRecordSegment.html) | [`skos:Concept`](https://www.w3.org/2009/08/skos-reference/skos.html#Concept) |
| [ContextualComponent]({0}/DataDescription/KeyValue/ContextualComponent.html) | [PhysicalSegmentLayout]({0}/FormatDescription/PhysicalSegmentLayout.html) | |
| [DataPoint]({0}/DataDescription/DataPoint.html) | [PrimaryKey]({0}/DataDescription/Components/PrimaryKey.html) | |
| [DataPointPosition]({0}/FormatDescription/DataPointPosition.html) | [PrimaryKeyComponent]({0}/DataDescription/Components/PrimaryKeyComponent.html) | |
| [DataStore]({0}/FormatDescription/DataStore.html) | [SentinelValueDomain]({0}/Representations/SentinelValueDomain.html#super-class-hierarchy-generalization) | |
| [EnumerationDomain]({0}/Representations/EnumerationDomain.html) | [SubstantiveValueDomain]({0}/Representations/SubstantiveValueDomain.html) | |
| [IdentifierComponent]({0}/DataDescription/Components/IdentifierComponent.html) | [SyntheticIdComponent]({0}/DataDescription/KeyValue/SyntheticIdComponent.html#super-class-hierarchy-generalization) | |
| [InstanceValue]({0}/DataDescription/InstanceValue.html) | [ValueAndConceptDescription]({0}/Representations/ValueAndConceptDescription.html) | |
| [InstanceVariable]({0}/Conceptual/InstanceVariable.html) | [ValueMapping]({0}/FormatDescription/ValueMapping.html) | |
| [KeyValueDataStore]({0}/DataDescription/KeyValue/KeyValueDataStore.html) | [ValueMappingPosition]({0}/FormatDescription/ValueMappingPosition.html) | |
| [KeyValueStructure]({0}/DataDescription/KeyValue/KeyValueStructure.html) | [VariableDescriptorComponent]({0}/DataDescription/Components/VariableDescriptorComponent.html) | |
| [LogicalRecord]({0}/FormatDescription/LogicalRecord.html) | [VariableValueComponent]({0}/DataDescription/Components/VariableValueComponent.html) | |
| [MeasureComponent]({0}/DataDescription/Components/MeasureComponent.html) | [WideDataSet]({0}/DataDescription/Wide/WideDataSet.html) | |
|  | [WideDataStructure]({0}/DataDescription/Wide/WideDataStructure.html) | |
""".format(prefix)

# Get current date and format it
current_date = datetime.now().strftime('%d.%m.%Y')

about_text = f'''
This prototype was initially developed by Sikt as part of the [WorldFAIR Project](https://worldfair-project.eu/) and further developed under [FAIR Impact](https://www.fair-impact.eu/). It is designed to facilitate the implementation of [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) and to support training activities within the DDI community. For further information, please contact [Benjamin Beuster](mailto:benjamin.beuster@sikt.no). Last updated on: {current_date}
'''

app_title = 'DDI-CDI Converter for STATA, SPSS, CSV and JSON (Prototype)'
app_description = ''

# Modern bright color scheme
colors = {
    'background': '#ffffff',    # Pure white
    'surface': '#f8f9fa',      # Light gray for cards/sections
    'text': '#2c3e50',         # Dark blue-gray for text
    'primary': '#2196f3',      # Standard link blue (matching the class links)
    'secondary': '#6c757d',    # Medium gray
    'border': '#e9ecef',       # Light gray for borders
    'hover': '#f1f3f5'         # Slightly darker than surface for hover states
}

style_dict = {
    'backgroundColor': colors['background'],
    'textAlign': 'left',
    'color': colors['text'],
    'fontSize': '13px',
    'padding': '8px 12px',
    'fontFamily': "'Inter', sans-serif",
    'borderBottom': f'1px solid {colors["border"]}',
    'height': '32px'
}

header_dict = {
    'backgroundColor': colors['surface'],
    'textAlign': 'left',
    'color': colors['text'],
    'fontSize': '13px',
    'padding': '10px 12px',
    'fontFamily': "'Inter', sans-serif",
    'fontWeight': '600',
    'height': '36px',
    'position': 'sticky',
    'top': '0',
    'zIndex': '1'
}

table_style = {
    'overflowX': 'auto', 
    'overflowY': 'auto', 
    'maxHeight': '350px',
    'maxWidth': 'auto', 
    'marginTop': '20px',
    'borderRadius': '8px',
    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
    'border': f'1px solid {colors["border"]}',
    'fontSize': '13px'
}
