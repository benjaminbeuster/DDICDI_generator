import datetime

prefix = "https://docs.ddialliance.org/DDI-CDI/1.0/model/FieldLevelDocumentation/DDICDILibrary/Classes"

markdown_text = r"""
## DDI-CDI Subset

This profile utilizes 26 classes from the DDI-CDI model (29.10.2024).

|  DDI-CDI Classes  |  DDI-CDI Classes  | SKOS Mapping in JSON-LD |
|------------------|------------------|------------------|
| [PhysicalDataSet]({0}/FormatDescription/PhysicalDataSet.html#super-class-hierarchy-generalization) | [PrimaryKey]({0}/DataDescription/Components/PrimaryKey.html) | |
| [PhysicalRecordSegment]({0}/FormatDescription/PhysicalRecordSegment.html) | [PrimaryKeyComponent]({0}/DataDescription/Components/PrimaryKeyComponent.html) | |
| [PhysicalSegmentLayout]({0}/FormatDescription/PhysicalSegmentLayout.html) | [IdentifierComponent]({0}/DataDescription/Components/IdentifierComponent.html) | |
| [ValueMapping]({0}/DataDescription/ValueMapping.html) | [MeasureComponent]({0}/DataDescription/Components/MeasureComponent.html) | |
| [ValueMappingPosition]({0}/DataDescription/ValueMappingPosition.html) | [AttributeComponent]({0}/DataDescription/Components/AttributeComponent.html) | |
| [DataPoint]({0}/DataDescription/DataPoint.html) | [SubstantiveValueDomain]({0}/Representations/SubstantiveValueDomain.html) | |
| [DataPointPosition]({0}/FormatDescription/DataPointPosition.html) | [SentinelValueDomain]({0}/Representations/SentinelValueDomain.html#super-class-hierarchy-generalization) | |
| [InstanceValue]({0}/DataDescription/InstanceValue.html) | [ValueAndConceptDescription]({0}/Representations/ValueAndConceptDescription.html) | |
| [DataStore]({0}/FormatDescription/DataStore.html) | [EnumerationDomain]({0}/Representations/EnumerationDomain.html) | |
| [LogicalRecord]({0}/FormatDescription/LogicalRecord.html) | [Codelist]({0}/Representations/CodeList.html#super-class-hierarchy-generalization) | [`skos:ConceptScheme`](https://www.w3.org/2009/08/skos-reference/skos.html#ConceptScheme) |
| [WideDataSet]({0}/DataDescription/Wide/WideDataSet.html) | [Code]({0}/Representations/Code.html) | [`skos:Concept`](https://www.w3.org/2009/08/skos-reference/skos.html#Concept) |
| [WideDataStructure]({0}/DataDescription/Wide/WideDataStructure.html) | [Category]({0}/Representations/Category.html) | [`skos:Concept`](https://www.w3.org/2009/08/skos-reference/skos.html#Concept) |
| [InstanceVariable]({0}/Conceptual/InstanceVariable.html) | [Notation]({0}/Representations/Notation.html) | [`skos:Concept`](https://www.w3.org/2009/08/skos-reference/skos.html#Concept) |
""".format(prefix)

from datetime import datetime

# Get current date and format it
current_date = datetime.now().strftime('%d.%m.%Y')

about_text = f'''
This prototype was initially developed by Sikt as part of the [WorldFAIR Project](https://worldfair-project.eu/) and further developed under [FAIR Impact](https://www.fair-impact.eu/). It is designed to facilitate the implementation of [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) and to support training activities within the DDI community. For further information, please contact [Benjamin Beuster](mailto:benjamin.beuster@sikt.no). Last updated on: {current_date}
'''

app_title = 'DDI-CDI Converter (Prototype): Wide Table Generation for STATA & SPSS'
app_description = ''

# Modern bright color scheme
colors = {
    'background': '#ffffff',    # Pure white
    'surface': '#f8f9fa',      # Light gray for cards/sections
    'text': '#2c3e50',         # Dark blue-gray for text
    'primary': '#3498db',      # Bright blue
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
    'height': '36px'
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
