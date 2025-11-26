# DDI-CDI Converter API Documentation

## Overview

The DDI-CDI Converter API provides programmatic access to convert statistical data files (SPSS, Stata, CSV, JSON) into DDI-CDI format with support for multiple RDF serialization formats: JSON-LD, Turtle, and N-Triples.

**Base URLs:**
- **Production (Azure):** `https://ddi-cdi-converter-app.azurewebsites.net/api`
- **Local Development:** `http://localhost:8000/api` (default port: 8000 or 8050)

---

## Quick Start

### Check API is Running
```bash
curl http://localhost:8000/api/health
```

### Basic Conversion (JSON-LD)
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/NES1948.sav" \
  -o output.jsonld
```

### Turtle Format (Human-Readable)
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/NES1948.sav" \
  -F "output_format=turtle" \
  -o output.ttl
```

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/health`

**Authentication:** Not required

**Example:**
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0",
  "service": "DDI-CDI Converter API"
}
```

---

### 2. API Information

Get information about available endpoints, parameters, and supported formats.

**Endpoint:** `GET /api/info`

**Authentication:** Not required

**Example:**
```bash
curl http://localhost:8000/api/info
```

**Response:**
```json
{
  "version": "1.0",
  "service": "DDI-CDI Converter API",
  "authentication": {
    "required": false,
    "method": "X-API-Key header",
    "env_var": "DDI_API_KEY"
  },
  "endpoints": {
    "GET /api/health": "Health check (no auth)",
    "GET /api/info": "API information (no auth)",
    "POST /api/convert": "Convert file to DDI-CDI (requires auth if configured)"
  },
  "supported_formats": [".sav", ".dta", ".csv", ".json"],
  "supported_output_formats": {
    "jsonld": {
      "name": "JSON-LD",
      "mimetype": "application/ld+json",
      "extension": ".jsonld",
      "description": "W3C JSON-LD RDF serialization"
    },
    "turtle": {
      "name": "Turtle",
      "mimetype": "text/turtle",
      "extension": ".ttl",
      "description": "W3C Turtle RDF serialization (human-readable)"
    },
    "ntriples": {
      "name": "N-Triples",
      "mimetype": "application/n-triples",
      "extension": ".nt",
      "description": "W3C N-Triples RDF serialization (simple line-based)"
    }
  },
  "parameters": {
    "file": "File to convert (required)",
    "output_format": "Output format: jsonld, turtle, ntriples (default: jsonld)",
    "base_uri": "Base URI for RDF output (default: http://example.org/ddi/)",
    "max_rows": "Number of rows to process (default: 5)",
    "process_all_rows": "Process all rows: true/false (default: false)",
    "decompose_keys": "Decompose JSON hierarchical keys: true/false (default: false)",
    "variable_roles": "JSON object with variable role assignments"
  }
}
```

---

### 3. Convert File

Convert an uploaded file to DDI-CDI format in JSON-LD, Turtle, or N-Triples.

**Endpoint:** `POST /api/convert`

**Authentication:** Required if `DDI_API_KEY` is set

**Content-Type:** `multipart/form-data`

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | file | Yes | - | The data file to convert (`.sav`, `.dta`, `.csv`, `.json`) |
| `output_format` | string | No | "jsonld" | Output format: "jsonld", "turtle", or "ntriples" |
| `base_uri` | string | No | "http://example.org/ddi/" | Base URI for instance data in RDF output |
| `max_rows` | integer | No | 5 | Number of data rows to include in output |
| `process_all_rows` | string | No | "false" | Set to "true" to process all rows (overrides max_rows) |
| `decompose_keys` | string | No | "false" | For JSON: decompose hierarchical keys (e.g., "a/b/c") |
| `variable_roles` | JSON string | No | - | Custom variable role assignments |

#### Output Formats

The API supports three RDF serialization formats:

1. **JSON-LD** (`jsonld`) - Default format
   - File extension: `.jsonld`
   - MIME type: `application/ld+json`
   - W3C standard JSON-LD format
   - Best for: Machine processing, web APIs

2. **Turtle** (`turtle`) - Human-readable format
   - File extension: `.ttl`
   - MIME type: `text/turtle`
   - Human-readable with namespace prefixes
   - Best for: Human inspection, documentation

3. **N-Triples** (`ntriples`) - Simple line-based format
   - File extension: `.nt`
   - MIME type: `application/n-triples`
   - Simple line-based format, one triple per line
   - Best for: Streaming, simple parsing

#### Variable Roles

The `variable_roles` parameter accepts a JSON object mapping variable names to roles:

**For non-JSON files** (SPSS, Stata, CSV):
- `measure`: Measure variables (numeric data)
- `identifier`: Identifier variables (IDs, keys)
- `attribute`: Attribute variables (categorical descriptors)
- Roles can be combined: `"measure,identifier"`, `"measure,attribute"`, etc.

**For JSON files:**
- `identifier`: Identifier variables
- `synthetic`: Synthetic ID variables
- `contextual`: Contextual variables
- `variablevalue`: Variable value components
- Roles are **not** combinable for JSON files

**Default behavior:**
- Non-JSON files: All variables default to `measure`
- JSON files: All variables default to `identifier`

---

## Examples

### JSON-LD Format (Default)

Convert to JSON-LD format (default):

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/NES1948.sav" \
  -F "max_rows=5" \
  -o output.jsonld
```

### Turtle Format (Human-Readable)

Convert to Turtle format for human-readable output:

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/NES1948.sav" \
  -F "max_rows=5" \
  -F "output_format=turtle" \
  -o output.ttl
```

### Turtle with Custom Base URI

Create portable RDF files with custom base URI:

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/NES1948.sav" \
  -F "max_rows=5" \
  -F "output_format=turtle" \
  -F "base_uri=http://myorg.edu/data/" \
  -o output.ttl
```

### N-Triples Format

Convert to N-Triples (simple line-based format):

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/NES1948.sav" \
  -F "output_format=ntriples" \
  -o output.nt
```

### CSV File with More Rows

Process 100 rows from a CSV file:

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.csv" \
  -F "max_rows=100" \
  -F "output_format=turtle" \
  -o output.ttl
```

### Process All Rows

Process the entire dataset (may be slow for large files):

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.csv" \
  -F "process_all_rows=true" \
  -F "output_format=jsonld" \
  -o output.jsonld
```

### Custom Variable Roles

Specify custom roles for variables:

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@files/ESS11-subset.sav" \
  -F 'variable_roles={"idno":"identifier","agea":"measure","gndr":"attribute"}' \
  -F "output_format=turtle" \
  -o output.ttl
```

### JSON File with Key Decomposition

Decompose hierarchical keys in JSON files:

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.json" \
  -F "decompose_keys=true" \
  -F "output_format=turtle" \
  -o output.ttl
```

### With Authentication

Include API key when authentication is enabled:

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@files/NES1948.sav" \
  -F "output_format=turtle" \
  -F "max_rows=50" \
  -o output.ttl
```

### Complete Example - All Parameters

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@survey.sav" \
  -F "output_format=turtle" \
  -F "base_uri=http://myorg.edu/surveys/" \
  -F "max_rows=1000" \
  -F "process_all_rows=false" \
  -F 'variable_roles={"respondent_id":"identifier","age":"measure","income":"measure","country":"attribute"}' \
  -o survey_output.ttl
```

---

## Authentication

The API supports optional API key authentication via the `X-API-Key` header.

### Setting Up Authentication

Set the `DDI_API_KEY` environment variable:

**Local development:**
```bash
export DDI_API_KEY="your-secret-key-here"
python app.py
```

**Azure Web App (via Azure Portal):**
1. Go to: Configuration > Application settings > New application setting
2. Name: `DDI_API_KEY`
3. Value: `your-secret-key-here`
4. Save and restart the app

### Making Authenticated Requests

Include the API key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@data.sav" \
  -o output.jsonld
```

**Note:** If `DDI_API_KEY` is not set, the API runs in development mode without authentication.

---

## URI Configuration

When converting to Turtle or N-Triples formats, you can configure the base URI for instance data:

### Default Base URI

By default, the API uses: `http://example.org/ddi/`

Example URIs in output:
```turtle
<http://example.org/ddi/#dataSet1>
<http://example.org/ddi/#v480004-concept-1.0>
<http://example.org/ddi/#instanceValue-0-age>
```

### Custom Base URI via Parameter

Use the `base_uri` parameter to create portable, institution-specific files:

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.sav" \
  -F "output_format=turtle" \
  -F "base_uri=http://myorg.edu/data/" \
  -o output.ttl
```

Example URIs in output:
```turtle
<http://myorg.edu/data/#dataSet1>
<http://myorg.edu/data/#v480004-concept-1.0>
<http://myorg.edu/data/#instanceValue-0-age>
```

### Environment Variable

Set a default base URI for all conversions:

```bash
export DDI_BASE_URI="http://myorg.edu/data/"
python app.py
```

---

## Error Responses

The API returns JSON error messages with appropriate HTTP status codes:

### 400 Bad Request

Missing or invalid parameters:

```json
{
  "error": "No file provided",
  "message": "Include a file in the request with key \"file\""
}
```

```json
{
  "error": "Unsupported file format",
  "message": "Supported formats: .sav, .dta, .csv, .json"
}
```

```json
{
  "error": "Invalid output format",
  "message": "Supported formats: jsonld, turtle, ntriples"
}
```

### 401 Unauthorized

Missing API key:

```json
{
  "error": "Missing API key",
  "message": "Include X-API-Key header in your request"
}
```

### 403 Forbidden

Invalid API key:

```json
{
  "error": "Invalid API key",
  "message": "The provided API key is not valid"
}
```

### 500 Internal Server Error

Processing failure:

```json
{
  "error": "Conversion failed",
  "message": "Detailed error message here"
}
```

---

## Response Format

Successful conversions return a DDI-CDI document in the requested format:

| Format | Content-Type | File Extension |
|--------|--------------|----------------|
| JSON-LD | `application/ld+json` | `.jsonld` |
| Turtle | `text/turtle` | `.ttl` |
| N-Triples | `application/n-triples` | `.nt` |

The response structure follows the [DDI-CDI 1.0 specification](https://ddialliance.org/Specification/DDI-CDI/1.0/) and includes:

- **JSON-LD format:**
  - `@context`: JSON-LD context definitions
  - `DDICDIModels`: Array of DDI-CDI model objects

- **All formats include:**
  - PhysicalDataSet and PhysicalRecordSegment
  - DataSet and LogicalRecord
  - WideDataStructure or KeyValueStructure
  - Component definitions (Measure, Identifier, Attribute, etc.)
  - InstanceVariables and DataPoints
  - Value domains (Substantive and Sentinel)
  - SKOS concepts for value labels

### Turtle Format Features

Turtle output includes standard RDF namespace prefixes for readability:

```turtle
@prefix ex: <http://example.org/ddi/> .
@prefix ddi: <http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

---

## Deployment

### Local Testing

The API runs alongside the Dash web interface:

```bash
python app.py
# API available at: http://localhost:8000/api
# Web UI available at: http://localhost:8000/
```

### Azure Web App Deployment

The API deploys automatically with the web application. No additional configuration needed.

**Azure URL:** `https://ddi-cdi-converter-app.azurewebsites.net/api`

To enable authentication on Azure:
1. Go to Azure Portal → Your App Service → Configuration
2. Add Application Setting:
   - Name: `DDI_API_KEY`
   - Value: Your secret key
3. Save and restart the app

---

## Supported File Formats

- **SPSS** (.sav) - Statistical Package for the Social Sciences
- **Stata** (.dta) - Stata data files
- **CSV** (.csv) - Comma-separated values with automatic delimiter detection
- **JSON** (.json) - Multiple JSON formats supported:
  - Flat key-value pairs
  - Hierarchical keys with "/" separator
  - Nested objects
  - Array-based data

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting in production environments to prevent abuse.

Recommended approaches:
- Use Azure API Management for enterprise deployments
- Implement Flask-Limiter for custom rate limiting

---

## Support and Issues

For questions or issues:
- Check the web interface at `/` for interactive usage
- Review the main application documentation in `CLAUDE.md`
- Report bugs via: https://github.com/anthropics/claude-code/issues

---

## Version History

### v1.0 (Current)
- Initial API implementation
- Support for SPSS, Stata, CSV, and JSON files
- Multiple RDF output formats (JSON-LD, Turtle, N-Triples)
- Configurable base URI for universal/portable files
- Optional API key authentication
- Configurable row processing
- Custom variable role assignment
- Metadata-only mode support
