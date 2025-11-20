# DDI-CDI Converter API Documentation

## Overview

The DDI-CDI Converter API provides programmatic access to convert statistical data files (SPSS, Stata, CSV, JSON) into DDI-CDI JSON-LD format. The API runs alongside the web interface on the same server.

**Base URLs:**
- **Production (Azure):** `https://ddi-cdi-converter-app.azurewebsites.net/api`
- **Local Development:** `http://localhost:8000/api`

## Authentication

The API supports optional API key authentication via the `X-API-Key` header.

### Setting Up Authentication

Set the `DDI_API_KEY` environment variable:

```bash
# Local development
export DDI_API_KEY="your-secret-key-here"

# Azure Web App (via Azure Portal)
# Go to: Configuration > Application settings > New application setting
# Name: DDI_API_KEY
# Value: your-secret-key-here
```

### Making Authenticated Requests

Include the API key in the `X-API-Key` header:

**Azure:**
```bash
curl -H "X-API-Key: your-secret-key-here" https://ddi-cdi-converter-app.azurewebsites.net/api/info
```

**Local:**
```bash
curl -H "X-API-Key: your-secret-key-here" http://localhost:8000/api/info
```

**Note**: If `DDI_API_KEY` is not set, the API runs in development mode without authentication.

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint**: `GET /api/health`

**Authentication**: Not required

**Example (Azure):**
```bash
curl https://ddi-cdi-converter-app.azurewebsites.net/api/health
```

**Example (Local):**
```bash
curl http://localhost:8000/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0",
  "service": "DDI-CDI Converter API"
}
```

---

### 2. API Information

Get information about available endpoints and parameters.

**Endpoint**: `GET /api/info`

**Authentication**: Not required

**Example (Azure):**
```bash
curl https://ddi-cdi-converter-app.azurewebsites.net/api/info
```

**Example (Local):**
```bash
curl http://localhost:8000/api/info
```

**Response**:
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
    "POST /api/convert": "Convert file to DDI-CDI JSON-LD (requires auth if configured)"
  },
  "supported_formats": [".sav", ".dta", ".csv", ".json"],
  "parameters": {
    "max_rows": "Number of rows to process (default: 5)",
    "process_all_rows": "Process all rows: true/false (default: false)",
    "decompose_keys": "Decompose JSON hierarchical keys: true/false (default: false)",
    "variable_roles": "JSON object with variable role assignments"
  }
}
```

---

### 3. Convert File

Convert an uploaded file to DDI-CDI JSON-LD format.

**Endpoint**: `POST /api/convert`

**Authentication**: Required if `DDI_API_KEY` is set

**Content-Type**: `multipart/form-data`

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | file | Yes | - | The data file to convert (`.sav`, `.dta`, `.csv`, `.json`) |
| `max_rows` | integer | No | 5 | Number of data rows to include in output |
| `process_all_rows` | string | No | "false" | Set to "true" to process all rows (overrides max_rows) |
| `decompose_keys` | string | No | "false" | For JSON: decompose hierarchical keys (e.g., "a/b/c") |
| `variable_roles` | JSON string | No | - | Custom variable role assignments |

#### Variable Roles

The `variable_roles` parameter accepts a JSON object mapping variable names to roles:

**For non-JSON files** (SPSS, Stata, CSV):
- `measure`: Measure variables
- `identifier`: Identifier variables
- `attribute`: Attribute variables
- Roles can be combined: `"measure,identifier"`, `"measure,attribute"`, etc.

**For JSON files**:
- `identifier`: Identifier variables
- `synthetic`: Synthetic ID variables
- `contextual`: Contextual variables
- `variablevalue`: Variable value components
- Roles are **not** combinable for JSON files

**Default behavior**:
- Non-JSON files: All variables default to `measure`
- JSON files: All variables default to `identifier`

---

## Examples

### Basic Conversion

Convert an SPSS file with default settings (5 rows):

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@data.sav" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.sav" \
  -o output.jsonld
```

### Convert with More Rows

Process 100 rows instead of the default 5:

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@data.sav" \
  -F "max_rows=100" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.sav" \
  -F "max_rows=100" \
  -o output.jsonld
```

### Process All Rows

Process the entire dataset (may be slow for large files):

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@data.csv" \
  -F "process_all_rows=true" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.csv" \
  -F "process_all_rows=true" \
  -o output.jsonld
```

### Custom Variable Roles

Specify custom roles for variables:

**Azure (Real Example with ESS11 data):**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@/Users/beb/dev/DDICDI_generator/files/ESS11-subset.sav" \
  -F 'variable_roles={"idno":"identifier"}' \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.csv" \
  -F 'variable_roles={"id":"identifier","age":"measure","gender":"attribute"}' \
  -o output.jsonld
```

### JSON File with Key Decomposition

Decompose hierarchical keys in JSON files:

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@data.json" \
  -F "decompose_keys=true" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@data.json" \
  -F "decompose_keys=true" \
  -o output.jsonld
```

### With Authentication

Include API key when authentication is enabled:

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@data.sav" \
  -F "max_rows=50" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@data.sav" \
  -F "max_rows=50" \
  -o output.jsonld
```

### Complete Example with All Parameters

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@survey.sav" \
  -F "max_rows=1000" \
  -F "process_all_rows=false" \
  -F 'variable_roles={"respondent_id":"identifier","age":"measure","income":"measure","country":"attribute"}' \
  -o survey_output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-secret-key-here" \
  -F "file=@survey.sav" \
  -F "max_rows=1000" \
  -F "process_all_rows=false" \
  -F 'variable_roles={"respondent_id":"identifier","age":"measure","income":"measure","country":"attribute"}' \
  -o survey_output.jsonld
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

Successful conversions return a DDI-CDI JSON-LD document with `Content-Type: application/json`.

The response structure follows the [DDI-CDI 1.0 specification](https://ddialliance.org/Specification/DDI-CDI/1.0/) and includes:

- `@context`: JSON-LD context definitions
- `DDICDIModels`: Array of DDI-CDI model objects including:
  - PhysicalDataSet and PhysicalRecordSegment
  - DataSet and LogicalRecord
  - WideDataStructure or KeyValueStructure
  - Component definitions (Measure, Identifier, Attribute, etc.)
  - InstanceVariables and DataPoints
  - Value domains (Substantive and Sentinel)
  - SKOS concepts for value labels

---

## Deployment

### Local Testing

The API runs alongside the Dash web interface:

```bash
python app.py
# API available at: http://localhost:8000/api
```

### Azure Web App Deployment

The API deploys automatically with the web application. No additional configuration needed.

To enable authentication on Azure:

1. Go to Azure Portal → Your App Service → Configuration
2. Add Application Setting:
   - Name: `DDI_API_KEY`
   - Value: Your secret key
3. Save and restart the app

The API will be available at: `https://ddi-cdi-converter-app.azurewebsites.net/api`

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting in production environments to prevent abuse.

Recommended approach:
- Use Azure API Management for enterprise deployments
- Implement Flask-Limiter for custom rate limiting

---

## Support and Issues

For questions or issues:
- Check the main application documentation in `CLAUDE.md`
- Review the web interface at `/` for interactive usage
- Report bugs via your project's issue tracker

---

## Version History

### v1.0 (Current)
- Initial API implementation
- Support for SPSS, Stata, CSV, and JSON files
- Optional API key authentication
- Configurable row processing
- Custom variable role assignment
