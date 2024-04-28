import datetime

# Modified html_text to use markdown
markdown_text = """
## DDI-CDI Subset

This profile utilizes 25 classes from the DDI-CDI model (2024-03-12).

|         |         |
|------------------|------------------|
| PhysicalDataStructure | DataStore |
| PhysicalDataset | LogicalRecord |
| PhysicalRecordSegment | WideDataSet |
| PhysicalSegmentLayout | WideDataStructure |
| ValueMapping | IdentifierComponent |
| ValueMappingPosition | MeasureComponent |
| DataPoint | PrimaryKey |
| DataPointPosition | PrimaryKeyComponent |
| InstanceValue | InstanceVariable |
| SubstantiveValueDomain | SentinelValueDomain |
| ValueAndConceptDescription | Codelist |
| Code | Category |
| Notation |  |
"""

from datetime import datetime

about_text = '''
This is a prototype developed for the DDI-CDI group, intended for model and implementation testing,
as well as for CDI training activities at Sikt. For contact, please reach out to benjamin.beuster@sikt.no.

Last update: 25.04.2024
'''

app_title = 'DDI-CDI Converter: Wide Table Generation for STATA & SPSS'
app_description = ''

colors = {'background': '#111111', 'text': '#7FDBFF'}

style_dict = {
    'backgroundColor': colors['background'],
    'textAlign': 'center',
    'color': 'white',
    'fontSize': 14
}

header_dict = {
    'backgroundColor': colors['background'],
    'textAlign': 'center',
    'color': colors['text'],
    'fontSize': 14
}


table_style = {'overflowX': 'auto', 'overflowY': 'auto', 'maxHeight': '350px',
               'maxWidth': 'auto', 'marginTop': '10px'}
