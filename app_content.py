from datetime import datetime

prefix = "https://docs.ddialliance.org/DDI-CDI/1.0/model/FieldLevelDocumentation/DDICDILibrary/Classes"

markdown_text = r"""
## DDI-CDI Subset

This profile utilizes 29 classes from the DDI-CDI model (v1.0) and 2 SKOS classes.

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

# API Documentation Content
api_documentation = """
## REST API Documentation

The DDI-CDI Converter provides a REST API for programmatic file conversion with support for multiple RDF output formats.

### Base URL

**Production (Azure):**
```
https://ddi-cdi-converter-app.azurewebsites.net/api
```

**Local Development:**
```
http://localhost:8000/api
```

### Endpoints

#### 1. Health Check
```bash
GET /api/health
```
Check if the API is running. No authentication required.

**Example:**
```bash
curl https://ddi-cdi-converter-app.azurewebsites.net/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0",
  "service": "DDI-CDI Converter API"
}
```

#### 2. Convert File
```bash
POST /api/convert
```
Convert a file to DDI-CDI format in JSON-LD, Turtle, or N-Triples.

**Parameters:**
- `file` (required): The file to convert (.sav, .dta, .csv, .json)
- `output_format` (optional): Output format - "jsonld", "turtle", or "ntriples" (default: "jsonld")
- `base_uri` (optional): Base URI for RDF output (default: "http://example.org/ddi/")
- `max_rows` (optional): Number of rows to include (default: 5)
- `process_all_rows` (optional): "true" to process all rows (default: "false")
- `decompose_keys` (optional): "true" to decompose hierarchical JSON keys (default: "false")
- `variable_roles` (optional): JSON string with role assignments

**Example 1: JSON-LD (default):**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \\
  -F "file=@yourfile.sav" \\
  -F "max_rows=5" \\
  -o output.jsonld
```

**Example 2: Turtle format (human-readable):**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \\
  -F "file=@yourfile.sav" \\
  -F "max_rows=5" \\
  -F "output_format=turtle" \\
  -o output.ttl
```

**Example 3: Turtle with custom base URI:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \\
  -F "file=@yourfile.sav" \\
  -F "max_rows=5" \\
  -F "output_format=turtle" \\
  -F "base_uri=http://myorg.edu/data/" \\
  -o output.ttl
```

**Example 4: N-Triples format (simple line-based):**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \\
  -F "file=@yourfile.sav" \\
  -F "output_format=ntriples" \\
  -o output.nt
```

**Example 5: With variable roles:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \\
  -F "file=@yourfile.sav" \\
  -F 'variable_roles={"idno":"identifier"}' \\
  -F "output_format=turtle" \\
  -o output.ttl
```

**Response:**
Returns the DDI-CDI document in the requested format:
- JSON-LD: `application/ld+json`
- Turtle: `text/turtle`
- N-Triples: `application/n-triples`

#### 3. API Information
```bash
GET /api/info
```
Get information about available endpoints, parameters, and supported formats.

**Example:**
```bash
curl https://ddi-cdi-converter-app.azurewebsites.net/api/info
```

### Output Formats

The API supports three RDF serialization formats:

1. **JSON-LD** (.jsonld) - Default format, W3C standard JSON-LD
2. **Turtle** (.ttl) - Human-readable with namespace prefixes
3. **N-Triples** (.nt) - Simple line-based format

Use the `output_format` parameter to select the format and optionally provide a `base_uri` for universal/portable files.

### Supported File Formats
- SPSS (.sav)
- Stata (.dta)
- CSV (.csv)
- JSON (.json)

### Authentication
By default, no authentication is required. To enable API key authentication, set the `DDI_API_KEY` environment variable:

**Azure:**
1. Go to Azure Portal → App Service → Configuration → Application settings
2. Add: `DDI_API_KEY` = `your-secret-key`
3. Save and restart

**Local:**
```bash
export DDI_API_KEY="your-secret-key"
python app.py
```

Then include the API key in requests:
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \\
  -H "X-API-Key: your-secret-key" \\
  -F "file=@yourfile.sav" \\
  -F "output_format=turtle" \\
  -o output.ttl
```

**Full documentation:** See `API_DOCUMENTATION.md` for complete details.
"""

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
