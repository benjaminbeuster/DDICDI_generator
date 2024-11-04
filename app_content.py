import datetime

prefix = "https://ddi-cdi.github.io/ddi-cdi_v1.0-post/field-level-documentation/DDICDILibrary/Classes"

markdown_text = r"""
## DDI-CDI Subset

This profile utilizes 24 classes from the DDI-CDI model (29.10.2024).

|         |         |
|------------------|------------------|
| [PhysicalDataSet]({0}/FormatDescription/PhysicalDataSet.html#super-class-hierarchy-generalization) | [DataStore]({0}/FormatDescription/DataStore.html) |
| [PhysicalRecordSegment]({0}/FormatDescription/PhysicalRecordSegment.html) | [LogicalRecord]({0}/FormatDescription/LogicalRecord.html) |
| [PhysicalSegmentLayout]({0}/FormatDescription/PhysicalSegmentLayout.html) | [WideDataSet]({0}/DataDescription/Wide/WideDataSet.html) |
| [ValueMapping]({0}/DataDescription/ValueMapping.html) | [WideDataStructure]({0}/DataDescription/Wide/WideDataStructure.html) |
| [ValueMappingPosition]({0}/DataDescription/ValueMappingPosition.html) | [InstanceVariable]({0}/Conceptual/InstanceVariable.html) |
| [DataPoint]({0}/DataDescription/DataPoint.html) | [PrimaryKey]({0}/DataDescription/Components/PrimaryKey.html) |
| [DataPointPosition]({0}/FormatDescription/DataPointPosition.html) | [PrimaryKeyComponent]({0}/DataDescription/Components/PrimaryKeyComponent.html) |
| [InstanceValue]({0}/DataDescription/InstanceValue.html) | [IdentifierComponent]({0}/DataDescription/Components/IdentifierComponent.html) |
| | [MeasureComponent]({0}/DataDescription/Components/MeasureComponent.html) |
| | [AttributeComponent]({0}/DataDescription/Components/AttributeComponent.html) |
| | [SubstantiveValueDomain]({0}/Representations/SubstantiveValueDomain.html) |
| | [SentinelValueDomain]({0}/Representations/SentinelValueDomain.html#super-class-hierarchy-generalization) |
| | [ValueAndConceptDescription]({0}/Representations/ValueAndConceptDescription.html) |
| | [Codelist]({0}/Representations/CodeList.html#super-class-hierarchy-generalization) |
| | [Code]({0}/Representations/Code.html) |
| | [Category]({0}/Representations/Category.html) |
| | [Notation]({0}/Representations/Notation.html) |
""".format(prefix)

from datetime import datetime

# Get current date and format it
current_date = datetime.now().strftime('%d.%m.%Y')

about_text = f'''
This prototype was developed by Sikt as part of the [Worldfair Project](https://worldfair-project.eu/). It is designed to facilitate the implementation of [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) and to support training activities within the DDI community. For further information, please contact [Benjamin Beuster](mailto:benjamin.beuster@sikt.no). Last updated on: {current_date}
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
