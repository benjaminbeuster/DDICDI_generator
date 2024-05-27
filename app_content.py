import datetime

prefix = "https://ddi-cdi-resources.bitbucket.io/2024-03-12/field-level-documentation/DDICDILibrary/Classes"

markdown_text = r"""
## DDI-CDI Subset

This profile utilizes 25 classes from the DDI-CDI model (12.03.2024).

|         |         |
|------------------|------------------|
| [PhysicalDataSetStructure]({0}/FormatDescription/PhysicalDataSetStructure.html) | [DataStore]({0}/FormatDescription/DataStore.html) |
| [PhysicalDataSet]({0}/FormatDescription/PhysicalDataSet.html#super-class-hierarchy-generalization) | [LogicalRecord]({0}/FormatDescription/LogicalRecord.html) |
| [PhysicalRecordSegment]({0}/FormatDescription/PhysicalRecordSegment.html) | [WideDataSet]({0}/DataDescription/Wide/WideDataSet.html) |
| [PhysicalSegmentLayout]({0}/FormatDescription/PhysicalSegmentLayout.html) | [WideDataStructure]({0}/DataDescription/Wide/WideDataStructure.html) |
| [ValueMapping]({0}/FormatDescription/ValueMapping.html) | [IdentifierComponent]({0}/DataDescription/Components/IdentifierComponent.html) |
| [ValueMappingPosition]({0}/FormatDescription/ValueMappingPosition.html) | [MeasureComponent]({0}/DataDescription/Components/MeasureComponent.html) |
| [DataPoint]({0}/DataDescription/DataPoint.html) | [PrimaryKey]({0}/DataDescription/Components/PrimaryKey.html) |
| [DataPointPosition]({0}/FormatDescription/DataPointPosition.html) | [PrimaryKeyComponent]({0}/DataDescription/Components/PrimaryKeyComponent.html) |
| [InstanceValue]({0}/DataDescription/InstanceValue.html) | [InstanceVariable]({0}/Conceptual/InstanceVariable.html) |
| [SubstantiveValueDomain]({0}/Representations/SubstantiveValueDomain.html) | [SentinelValueDomain]({0}/Representations/SentinelValueDomain.html#super-class-hierarchy-generalization) |
| [ValueAndConceptDescription]({0}/Representations/ValueAndConceptDescription.html) | [Codelist]({0}/Representations/CodeList.html#super-class-hierarchy-generalization) |
| [Code]({0}/Representations/Code.html) | [Category]({0}/Conceptual/Category.html) |
| [Notation]({0}/DataDescription/Notation.html) |  |
""".format(prefix)

from datetime import datetime

# Get current date and format it
current_date = datetime.now().strftime('%d.%m.%Y')

about_text = f'''
This prototype was developed by Sikt as part of the [Worldfair Project](https://worldfair-project.eu/). It is designed to facilitate the implementation of [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) and to support training activities within the DDI community. For further information, please contact [Benjamin Beuster](mailto:benjamin.beuster@sikt.no). Last updated on: {current_date}
'''

app_title = 'DDI-CDI Converter (Prototype): Wide Table Generation for STATA & SPSS'
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
