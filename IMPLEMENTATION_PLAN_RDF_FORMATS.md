# Implementation Plan: RDF Output Format Support

**Date:** 2025-11-26
**Status:** Ready for User Review
**Scope:** Add Turtle and N-Triples output formats to API and UI

---

## Executive Summary

This plan addresses user feedback requesting more readable RDF output formats (Turtle and N-Triples) as alternatives to JSON-LD. The implementation will:

1. Add `format` parameter to REST API with options: jsonld, turtle, ntriples (default: jsonld)
2. Create reusable conversion utilities by extracting existing RDF logic
3. Address URI universality concerns (SIKT-specific addresses)
4. Update UI to expose existing N-Triples functionality and add Turtle option
5. Maintain backward compatibility with existing API behavior

---

## Current State Analysis

### Existing RDF Conversion Implementations

The codebase has **3 separate implementations** of RDF conversion logic:

1. **app.py (lines 1436-1499)**: Web UI N-Triples download (functional but hidden)
2. **files/convert-jsonld-rdf.py**: Standalone CLI for N-Triples conversion
3. **files/convert-jsonld-turtle.py**: Standalone CLI for Turtle conversion

All three follow identical patterns:
```python
# 1. Parse JSON-LD into RDF graph
g = Graph()
g.parse(input_file, format="json-ld")

# 2. Transform URIs: file:/// → https://sikt.no/cdi/RDF/
new_g = Graph()
for s, p, o in g:
    if str(s).startswith('file:///'):
        s = URIRef('https://sikt.no/cdi/RDF/' + str(s).split('/')[-1])
    # ... same for object
    new_g.add((s, p, o))

# 3. Serialize to target format
output = new_g.serialize(format=target_format)
```

### Key Findings

**Code Duplication:**
- Same URI transformation logic repeated 3 times
- Opportunity to create shared utility module

**URI Strategy:**
- Currently transforms `file:///` URIs to `https://sikt.no/cdi/RDF/`
- User wants "universal files, maybe remove the SIKT address"
- Need to decide on base URI strategy

**Hidden Functionality:**
- N-Triples button exists in UI DOM but is always hidden (style: display:none)
- Backend callback is fully functional
- Suggests incomplete feature rollout

**API Limitations:**
- No format parameter currently accepted
- Only returns JSON-LD (mimetype: application/ld+json)

---

## Design Decisions Required

### Decision 1: Base URI Strategy

**Current Behavior:**
```
file:///some/path/physicalDataSet
  → https://sikt.no/cdi/RDF/physicalDataSet
```

**Options:**

**Option A: Configurable Base URI (Recommended)**
```python
# Environment variable or config
BASE_URI = os.getenv('DDI_BASE_URI', 'https://sikt.no/cdi/RDF/')

# Allows:
# - Deployment-specific URIs (SIKT, other institutions)
# - Generic URIs for universal files (e.g., example.org)
# - Local URIs for testing (file://)
```

**Option B: Remove Base Transformation**
```python
# Keep fragment URIs as-is from JSON-LD
# file:///#physicalDataSet → #physicalDataSet (relative)
# Pros: Universal, portable
# Cons: Less semantic web friendly (no absolute URIs)
```

**Option C: DDI Standard Namespace**
```python
# Use DDI-CDI specification namespace
BASE_URI = 'http://ddialliance.org/Specification/DDI-CDI/1.0/instance/'
# Pros: Standards-compliant, universal
# Cons: Might conflict with DDI Alliance namespace policies
```

**Recommendation:** Option A (Configurable)
- Default to current SIKT URI for backward compatibility
- Allow override via environment variable `DDI_BASE_URI`
- Document how to set for universal/portable files
- Consider adding API parameter `base_uri` for per-request control

### Decision 2: Namespace Bindings

**Current Turtle Namespaces:**
```python
new_g.bind('sikt', 'https://sikt.no/cdi/RDF/')
new_g.bind('ddi', 'http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/')
new_g.bind('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
new_g.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
new_g.bind('skos', 'http://www.w3.org/2004/02/skos/core#')
new_g.bind('xsd', 'http://www.w3.org/2001/XMLSchema#')
```

**Questions:**
- Keep `sikt` prefix if base URI is configurable?
- Use generic prefix (e.g., `inst` for "instance")?

**Recommendation:**
- Use prefix that matches base URI domain
- For SIKT: `sikt` prefix
- For generic: `inst` or `ex` prefix
- Make prefix configurable alongside base URI

---

## Implementation Plan

### Phase 1: Create Reusable Conversion Utilities

**New File: `format_converter.py`**

```python
"""
RDF Format Conversion Utilities for DDI-CDI Converter
Provides conversion between JSON-LD and other RDF serializations
"""

from rdflib import Graph, URIRef
import json
import tempfile
import os

class FormatConverter:
    """Convert DDI-CDI JSON-LD to various RDF formats"""

    # Format configuration
    FORMATS = {
        'jsonld': {
            'name': 'JSON-LD',
            'mimetype': 'application/ld+json',
            'extension': '.jsonld',
            'requires_conversion': False
        },
        'turtle': {
            'name': 'Turtle',
            'mimetype': 'text/turtle',
            'extension': '.ttl',
            'rdflib_format': 'turtle',
            'requires_conversion': True
        },
        'ntriples': {
            'name': 'N-Triples',
            'mimetype': 'application/n-triples',
            'extension': '.nt',
            'rdflib_format': 'nt',
            'requires_conversion': True
        }
    }

    DEFAULT_BASE_URI = 'https://sikt.no/cdi/RDF/'
    DEFAULT_NAMESPACE_BINDINGS = {
        'ddi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#'
    }

    @classmethod
    def convert(cls, jsonld_string, target_format, base_uri=None):
        """
        Convert JSON-LD to target RDF format

        Args:
            jsonld_string: DDI-CDI JSON-LD document as string
            target_format: Target format ('jsonld', 'turtle', 'ntriples')
            base_uri: Optional base URI for instance data (defaults to SIKT URI)

        Returns:
            Converted content as bytes

        Raises:
            ValueError: If format is unsupported or conversion fails
        """
        # Validate format
        if target_format not in cls.FORMATS:
            raise ValueError(
                f"Unsupported format '{target_format}'. "
                f"Supported: {', '.join(cls.FORMATS.keys())}"
            )

        format_config = cls.FORMATS[target_format]

        # JSON-LD needs no conversion
        if not format_config['requires_conversion']:
            return jsonld_string.encode('utf-8')

        # Convert via RDFlib
        base_uri = base_uri or cls.DEFAULT_BASE_URI
        return cls._convert_via_rdflib(
            jsonld_string,
            target_format,
            base_uri
        )

    @classmethod
    def _convert_via_rdflib(cls, jsonld_string, target_format, base_uri):
        """
        Convert JSON-LD to RDF format using rdflib

        Args:
            jsonld_string: JSON-LD document as string
            target_format: Target format key
            base_uri: Base URI for instance data

        Returns:
            Serialized RDF as bytes
        """
        temp_file = None
        try:
            # Write JSON-LD to temporary file
            with tempfile.NamedTemporaryFile(
                suffix='.jsonld',
                delete=False,
                mode='w',
                encoding='utf-8'
            ) as f:
                f.write(jsonld_string)
                temp_file = f.name

            # Parse JSON-LD into RDF graph
            source_graph = Graph()
            source_graph.parse(temp_file, format='json-ld')

            # Transform URIs and create new graph
            target_graph = Graph()

            # Add namespace bindings
            # Determine prefix for base URI
            base_prefix = cls._get_prefix_for_uri(base_uri)
            target_graph.bind(base_prefix, base_uri)

            for prefix, namespace in cls.DEFAULT_NAMESPACE_BINDINGS.items():
                target_graph.bind(prefix, namespace)

            # Transform URIs
            for s, p, o in source_graph:
                s = cls._transform_uri(s, base_uri)
                o = cls._transform_uri(o, base_uri)
                target_graph.add((s, p, o))

            # Serialize to target format
            format_config = cls.FORMATS[target_format]
            rdflib_format = format_config['rdflib_format']

            output = target_graph.serialize(
                format=rdflib_format,
                encoding='utf-8'
            )

            # Handle different rdflib return types
            if isinstance(output, bytes):
                return output
            elif isinstance(output, str):
                return output.encode('utf-8')
            else:
                # BytesIO or similar
                return output.getvalue()

        except Exception as e:
            raise ValueError(
                f"Failed to convert to {target_format}: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

    @staticmethod
    def _transform_uri(uri_ref, base_uri):
        """
        Transform file:/// URIs to specified base URI

        Args:
            uri_ref: rdflib URIRef or Literal
            base_uri: Target base URI

        Returns:
            Transformed URIRef or original value
        """
        uri_str = str(uri_ref)

        # Only transform file:/// URIs
        if uri_str.startswith('file:///'):
            # Extract fragment/last segment
            fragment = uri_str.split('/')[-1]
            return URIRef(base_uri + fragment)

        return uri_ref

    @staticmethod
    def _get_prefix_for_uri(uri):
        """
        Determine appropriate namespace prefix for URI

        Args:
            uri: Base URI string

        Returns:
            Suggested prefix string
        """
        # Extract domain or path component
        if 'sikt.no' in uri:
            return 'sikt'
        elif 'example.org' in uri:
            return 'ex'
        else:
            return 'inst'  # Generic "instance" prefix

    @classmethod
    def get_format_info(cls, format_key=None):
        """
        Get information about supported formats

        Args:
            format_key: Specific format, or None for all

        Returns:
            Format config dict or dict of all formats
        """
        if format_key:
            return cls.FORMATS.get(format_key, {})
        return cls.FORMATS
```

**Key Features:**
- Single source of truth for format configuration
- Reusable across API, UI, and CLI scripts
- Configurable base URI support
- Automatic namespace prefix selection
- Comprehensive error handling
- Temporary file cleanup

---

### Phase 2: Update REST API

**File: `api.py`**

**Changes:**

1. Import FormatConverter:
```python
from format_converter import FormatConverter
```

2. Modify `/api/convert` endpoint (around line 66):
```python
@server.route('/api/convert', methods=['POST'])
@require_api_key
def convert_file():
    """
    Convert uploaded file to DDI-CDI format

    Request:
        - Multipart form data with 'file' field
        - Optional form fields:
            - format: Output format ('jsonld', 'turtle', 'ntriples') [default: 'jsonld']
            - base_uri: Base URI for instance data [default: SIKT URI]
            - max_rows: Number of rows to process [default: 5]
            - process_all_rows: 'true'/'false' [default: 'false']
            - decompose_keys: 'true'/'false' [default: 'false']
            - variable_roles: JSON string with role assignments

    Response:
        - RDF document in requested format with appropriate mimetype
    """

    # [Existing validation code...]

    # Get format parameter
    output_format = request.form.get('format', 'jsonld').lower()

    # Validate format
    try:
        format_info = FormatConverter.get_format_info(output_format)
        if not format_info:
            raise ValueError(f"Unsupported format: {output_format}")
    except ValueError as e:
        return jsonify({
            'error': 'Invalid format parameter',
            'message': str(e),
            'supported_formats': list(FormatConverter.FORMATS.keys())
        }), 400

    # Get optional base URI
    base_uri = request.form.get('base_uri', None)

    # [Existing file processing code...]

    # Generate DDI-CDI JSON-LD
    json_ld_output = generate_complete_json_ld(
        df=df,
        df_meta=df_meta,
        spssfile=file.filename,
        max_rows=max_rows,
        process_all_rows=process_all_rows
    )

    # Convert to requested format
    try:
        output_content = FormatConverter.convert(
            json_ld_output,
            output_format,
            base_uri=base_uri
        )
    except ValueError as e:
        return jsonify({
            'error': 'Format conversion failed',
            'message': str(e)
        }), 500

    # Return with appropriate mimetype
    response = Response(
        output_content,
        mimetype=format_info['mimetype']
    )

    # Add filename for download
    base_filename = os.path.splitext(file.filename)[0]
    download_filename = f"{base_filename}_DDICDI{format_info['extension']}"
    response.headers['Content-Disposition'] = (
        f'attachment; filename="{download_filename}"'
    )

    return response, 200
```

3. Update `/api/info` endpoint (around line 231):
```python
@server.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and available endpoints"""
    api_key_required = bool(os.environ.get(API_KEY_ENV_VAR))

    # Get format information
    formats_info = {}
    for fmt_key, fmt_config in FormatConverter.FORMATS.items():
        formats_info[fmt_key] = {
            'name': fmt_config['name'],
            'mimetype': fmt_config['mimetype'],
            'extension': fmt_config['extension']
        }

    return jsonify({
        'version': '1.0',
        'service': 'DDI-CDI Converter API',
        'authentication': {
            'required': api_key_required,
            'method': 'X-API-Key header',
            'env_var': API_KEY_ENV_VAR if not api_key_required else 'configured'
        },
        'endpoints': {
            'GET /api/health': 'Health check (no auth)',
            'GET /api/info': 'API information (no auth)',
            'POST /api/convert': 'Convert file to DDI-CDI (requires auth if configured)'
        },
        'supported_input_formats': ['.sav', '.dta', '.csv', '.json'],
        'supported_output_formats': formats_info,
        'parameters': {
            'format': f'Output format (default: "jsonld")',
            'base_uri': 'Base URI for instance data (optional, defaults to SIKT URI)',
            'max_rows': 'Number of rows to process (default: 5)',
            'process_all_rows': 'Process all rows: true/false (default: false)',
            'decompose_keys': 'Decompose JSON keys: true/false (default: false)',
            'variable_roles': 'JSON object with variable role assignments'
        }
    }), 200
```

---

### Phase 3: Update Web UI

**File: `app.py`**

**Changes:**

1. Import FormatConverter (around line 18):
```python
from format_converter import FormatConverter
```

2. Unhide N-Triples button and add Turtle button (around line 379):
```python
# Replace existing hidden N-Triples button with visible button group
html.Div([
    html.H3("Download RDF Formats", style={'marginTop': '20px'}),
    html.Div([
        html.Button(
            "Download JSON-LD",
            id='btn-download-jsonld',
            n_clicks=0,
            style={
                'marginRight': '10px',
                'backgroundColor': colors['accent'],
                'color': 'white'
            }
        ),
        html.Button(
            "Download Turtle (.ttl)",
            id='btn-download-turtle',
            n_clicks=0,
            style={
                'marginRight': '10px',
                'backgroundColor': colors['accent'],
                'color': 'white'
            }
        ),
        html.Button(
            "Download N-Triples (.nt)",
            id='btn-download-nt',
            n_clicks=0,
            style={
                'backgroundColor': colors['accent'],
                'color': 'white'
            }
        )
    ], style={'display': 'flex', 'gap': '10px'})
], id='download-buttons', style={'display': 'none'})
```

3. Add download components (around line 431):
```python
dcc.Download(id='download-jsonld'),
dcc.Download(id='download-turtle'),
dcc.Download(id='download-nt'),
```

4. Refactor existing N-Triples callback to use FormatConverter (around line 1436):
```python
@app.callback(
    Output('download-nt', 'data'),
    [Input('btn-download-nt', 'n_clicks')],
    [State('full-json-store', 'data'),
     State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_nt(n_clicks, full_json, displayed_json, filename):
    """Download N-Triples format"""
    if n_clicks is None or n_clicks == 0:
        return None

    try:
        # Get JSON-LD data
        if full_json:
            json_data = full_json
        elif displayed_json:
            json_data = displayed_json
        else:
            return None

        # Remove truncation message if present
        if isinstance(json_data, str) and "... Output truncated" in json_data:
            truncation_pos = json_data.find("\n\n... Output truncated")
            if truncation_pos > 0:
                json_data = json_data[:truncation_pos]

        # Convert using FormatConverter
        nt_content = FormatConverter.convert(
            json_data,
            target_format='ntriples'
        )

        # Generate filename
        base_filename = os.path.splitext(filename)[0] if filename else 'output'
        output_filename = f"{base_filename}_DDICDI.nt"

        return dict(
            content=nt_content.decode('utf-8'),
            filename=output_filename
        )

    except Exception as e:
        print(f"Error converting to N-Triples: {str(e)}")
        return None
```

5. Add new Turtle callback:
```python
@app.callback(
    Output('download-turtle', 'data'),
    [Input('btn-download-turtle', 'n_clicks')],
    [State('full-json-store', 'data'),
     State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_turtle(n_clicks, full_json, displayed_json, filename):
    """Download Turtle format"""
    if n_clicks is None or n_clicks == 0:
        return None

    try:
        # Get JSON-LD data
        if full_json:
            json_data = full_json
        elif displayed_json:
            json_data = displayed_json
        else:
            return None

        # Remove truncation message if present
        if isinstance(json_data, str) and "... Output truncated" in json_data:
            truncation_pos = json_data.find("\n\n... Output truncated")
            if truncation_pos > 0:
                json_data = json_data[:truncation_pos]

        # Convert using FormatConverter
        turtle_content = FormatConverter.convert(
            json_data,
            target_format='turtle'
        )

        # Generate filename
        base_filename = os.path.splitext(filename)[0] if filename else 'output'
        output_filename = f"{base_filename}_DDICDI.ttl"

        return dict(
            content=turtle_content.decode('utf-8'),
            filename=output_filename
        )

    except Exception as e:
        print(f"Error converting to Turtle: {str(e)}")
        return None
```

6. Add JSON-LD download callback (for consistency):
```python
@app.callback(
    Output('download-jsonld', 'data'),
    [Input('btn-download-jsonld', 'n_clicks')],
    [State('full-json-store', 'data'),
     State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_jsonld(n_clicks, full_json, displayed_json, filename):
    """Download JSON-LD format"""
    if n_clicks is None or n_clicks == 0:
        return None

    try:
        # Get JSON-LD data
        if full_json:
            json_data = full_json
        elif displayed_json:
            json_data = displayed_json
        else:
            return None

        # Remove truncation message if present
        if isinstance(json_data, str) and "... Output truncated" in json_data:
            truncation_pos = json_data.find("\n\n... Output truncated")
            if truncation_pos > 0:
                json_data = json_data[:truncation_pos]

        # Generate filename
        base_filename = os.path.splitext(filename)[0] if filename else 'output'
        output_filename = f"{base_filename}_DDICDI.jsonld"

        return dict(
            content=json_data,
            filename=output_filename
        )

    except Exception as e:
        print(f"Error downloading JSON-LD: {str(e)}")
        return None
```

---

### Phase 4: Update Standalone Scripts (Optional)

**Option A: Deprecate standalone scripts**
- Add deprecation notice to existing scripts
- Direct users to use API or web UI instead
- Keep scripts for backward compatibility

**Option B: Refactor to use FormatConverter**
- Modify `files/convert-jsonld-rdf.py` and `files/convert-jsonld-turtle.py`
- Import FormatConverter module
- Reduce scripts to CLI wrappers

**Recommendation:** Option A
- Standalone scripts are legacy/test tools
- API and UI provide better user experience
- Keep for backward compatibility but don't invest in refactoring

---

## Configuration

### Environment Variables

Add support for base URI configuration:

```bash
# .env or environment
DDI_BASE_URI=https://sikt.no/cdi/RDF/  # Default (current behavior)
# OR
DDI_BASE_URI=http://example.org/ddi/instances/  # Universal/portable
```

### Documentation Updates

**README.md additions:**

```markdown
## Output Formats

The converter supports multiple RDF output formats:

### JSON-LD (default)
- Most verbose, includes full context
- Best for programmatic processing
- File extension: `.jsonld`

### Turtle
- Human-readable RDF format
- Uses namespace prefixes for brevity
- Best for manual inspection and editing
- File extension: `.ttl`

### N-Triples
- Simple line-based RDF format
- Easy to parse and process
- Best for large-scale data exchange
- File extension: `.nt`

## API Usage

### Convert with specific output format

```bash
curl -X POST http://localhost:8050/api/convert \
  -F "file=@data.csv" \
  -F "format=turtle" \
  -o output.ttl
```

### Using custom base URI for universal files

```bash
curl -X POST http://localhost:8050/api/convert \
  -F "file=@data.csv" \
  -F "format=turtle" \
  -F "base_uri=http://example.org/ddi/instances/" \
  -o output.ttl
```

## Configuration

Set base URI via environment variable:

```bash
export DDI_BASE_URI=http://example.org/ddi/instances/
python app.py
```
```

---

## Testing Plan

### Unit Tests

Create `test_format_converter.py`:

```python
import unittest
from format_converter import FormatConverter

class TestFormatConverter(unittest.TestCase):

    def setUp(self):
        # Sample JSON-LD document
        self.sample_jsonld = '''
        {
            "@context": "https://docs.ddialliance.org/DDI-CDI/1.0/model/encoding/json-ld/ddi-cdi.jsonld",
            "@graph": [
                {
                    "@id": "file:///#dataSet1",
                    "@type": "DataSet",
                    "name": "Test Dataset"
                }
            ]
        }
        '''

    def test_jsonld_format_no_conversion(self):
        """JSON-LD format should return input unchanged"""
        result = FormatConverter.convert(self.sample_jsonld, 'jsonld')
        self.assertEqual(result.decode('utf-8'), self.sample_jsonld)

    def test_turtle_conversion(self):
        """Turtle conversion should succeed"""
        result = FormatConverter.convert(self.sample_jsonld, 'turtle')
        self.assertIsInstance(result, bytes)
        self.assertIn(b'@prefix', result)

    def test_ntriples_conversion(self):
        """N-Triples conversion should succeed"""
        result = FormatConverter.convert(self.sample_jsonld, 'ntriples')
        self.assertIsInstance(result, bytes)
        # N-Triples uses <URI> format
        self.assertIn(b'<http', result)

    def test_invalid_format(self):
        """Invalid format should raise ValueError"""
        with self.assertRaises(ValueError):
            FormatConverter.convert(self.sample_jsonld, 'invalid_format')

    def test_custom_base_uri(self):
        """Custom base URI should be applied"""
        custom_uri = 'http://example.org/test/'
        result = FormatConverter.convert(
            self.sample_jsonld,
            'turtle',
            base_uri=custom_uri
        )
        result_str = result.decode('utf-8')
        self.assertIn('example.org', result_str)

if __name__ == '__main__':
    unittest.main()
```

### API Tests

```bash
# Test format parameter validation
curl -X POST http://localhost:8050/api/convert \
  -F "file=@test.csv" \
  -F "format=invalid"
# Expected: 400 with error message

# Test JSON-LD (default)
curl -X POST http://localhost:8050/api/convert \
  -F "file=@test.csv" \
  -o test.jsonld

# Test Turtle
curl -X POST http://localhost:8050/api/convert \
  -F "file=@test.csv" \
  -F "format=turtle" \
  -o test.ttl

# Test N-Triples
curl -X POST http://localhost:8050/api/convert \
  -F "file=@test.csv" \
  -F "format=ntriples" \
  -o test.nt

# Test custom base URI
curl -X POST http://localhost:8050/api/convert \
  -F "file=@test.csv" \
  -F "format=turtle" \
  -F "base_uri=http://example.org/ddi/" \
  -o test.ttl

# Verify API info endpoint
curl http://localhost:8050/api/info | jq '.supported_output_formats'
```

### UI Tests

1. Upload a CSV file
2. Verify "Download RDF Formats" section appears
3. Click "Download Turtle" button
4. Verify `.ttl` file downloads
5. Open in text editor and verify Turtle syntax
6. Click "Download N-Triples" button
7. Verify `.nt` file downloads
8. Open and verify N-Triples syntax

---

## Migration Path

### Backward Compatibility

**Guaranteed:**
- Existing API calls without `format` parameter continue to work (default: jsonld)
- Existing JSON-LD generation unchanged
- All existing functionality preserved

**Changes:**
- N-Triples button becomes visible in UI (previously hidden)
- New Turtle download option added
- API accepts new optional parameters (`format`, `base_uri`)

### Deprecation Notices

Add to standalone scripts:

```python
# convert-jsonld-rdf.py and convert-jsonld-turtle.py
print("NOTE: This standalone script is deprecated.")
print("Consider using the API or web UI for better functionality.")
print("See documentation for details.\n")
```

---

## Security Considerations

### Input Validation

- Format parameter: validate against whitelist
- Base URI parameter: validate URI format, prevent injection
- File uploads: existing validation unchanged

### Error Handling

- Never expose internal paths in error messages
- Sanitize error messages from rdflib
- Log detailed errors server-side only

### Resource Limits

- Temporary file cleanup in all code paths (try/finally)
- Consider memory limits for large file conversions
- Timeout for rdflib parsing operations

---

## Performance Considerations

### Memory Usage

**Current N-Triples conversion pattern:**
```
JSON-LD string (in memory)
  → Temp file (disk)
  → RDFlib Graph (in memory)
  → Transformed Graph (in memory)
  → Serialized output (in memory)
```

**Memory multiplier:** ~3-4x input size

**Optimization opportunities (future):**
- Stream large datasets instead of in-memory graphs
- Incremental RDF serialization for chunked data processing
- Consider alternative parsers for very large files

### Conversion Speed

**Benchmark estimates (based on typical file sizes):**
- Small files (<1MB): <1 second
- Medium files (1-10MB): 1-5 seconds
- Large files (10-100MB): 5-30 seconds

**Bottlenecks:**
- RDFlib parsing is the slowest step
- Triple iteration for URI transformation
- Serialization to Turtle (slower than N-Triples)

---

## Open Questions for User

1. **Base URI Strategy:**
   - Should default remain `https://sikt.no/cdi/RDF/` or use generic URI?
   - Do you want environment variable configuration?
   - Do you want per-request base URI control via API?

2. **Namespace Prefix:**
   - Keep `sikt` prefix or use generic (e.g., `inst`, `ex`)?
   - Should prefix change based on base URI domain?

3. **UI Design:**
   - Show all three download buttons (JSON-LD, Turtle, N-Triples)?
   - Or use dropdown selector for format?
   - Add base URI input field in UI?

4. **Standalone Scripts:**
   - Deprecate and keep as-is?
   - Refactor to use FormatConverter?
   - Remove entirely?

5. **Additional Formats:**
   - Want RDF/XML support?
   - Want TriG format (for named graphs)?
   - Any other serializations needed?

---

## Implementation Checklist

- [ ] Create `format_converter.py` module
- [ ] Add unit tests for FormatConverter
- [ ] Update `api.py` to accept format parameter
- [ ] Update `/api/convert` endpoint
- [ ] Update `/api/info` endpoint
- [ ] Update `app.py` to import FormatConverter
- [ ] Refactor N-Triples callback to use FormatConverter
- [ ] Add Turtle download callback
- [ ] Add JSON-LD download callback (for consistency)
- [ ] Update UI to show download buttons
- [ ] Add deprecation notices to standalone scripts
- [ ] Update README.md with format documentation
- [ ] Update API documentation
- [ ] Add environment variable configuration
- [ ] Test API with all formats
- [ ] Test UI downloads
- [ ] Test custom base URI functionality
- [ ] Verify backward compatibility
- [ ] Performance testing with large files
- [ ] Update deployment configuration (if needed)

---

## Estimated Effort

- **Phase 1 (FormatConverter):** 2-3 hours
- **Phase 2 (API updates):** 1-2 hours
- **Phase 3 (UI updates):** 2-3 hours
- **Phase 4 (Documentation):** 1 hour
- **Testing:** 2 hours
- **Total:** 8-11 hours

---

## Next Steps

1. **Review this plan** with user to confirm approach
2. **Get decisions** on open questions above
3. **Implement Phase 1** (FormatConverter module)
4. **Test thoroughly** before deploying
5. **Deploy incrementally** (API first, then UI)

---

## Success Criteria

- [ ] API accepts `format` parameter (jsonld, turtle, ntriples)
- [ ] API returns correct mimetype for each format
- [ ] UI has visible download buttons for all formats
- [ ] Turtle output is human-readable with namespace prefixes
- [ ] N-Triples output is valid and parseable
- [ ] Base URI is configurable (environment variable or API parameter)
- [ ] Backward compatibility maintained (existing API calls work)
- [ ] Documentation updated with examples
- [ ] All tests pass
- [ ] User feedback: "Turtle is much easier to read than JSON-LD"
