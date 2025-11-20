# DDI-CDI Converter API - Quick Start

## Quick Test Commands

### 1. Check API is Running
```bash
curl http://localhost:8000/api/health
```

### 2. Get API Info
```bash
curl http://localhost:8000/api/info
```

### 3. Basic Conversion
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@yourfile.sav" \
  -o output.jsonld
```

### 4. With Authentication (if DDI_API_KEY is set)
```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-api-key" \
  -F "file=@yourfile.sav" \
  -o output.jsonld
```

### 5. Process More Rows
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@yourfile.csv" \
  -F "max_rows=100" \
  -o output.jsonld
```

### 6. Custom Variable Roles
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@yourfile.csv" \
  -F 'variable_roles={"id":"identifier","age":"measure"}' \
  -o output.jsonld
```

## Setting Up API Key (Optional)

### Local Development
```bash
export DDI_API_KEY="your-secret-key"
python app.py
```

### Azure Web App
1. Go to Azure Portal
2. Navigate to: App Service → Configuration → Application settings
3. Add new setting:
   - Name: `DDI_API_KEY`
   - Value: `your-secret-key`
4. Save and restart

## Testing Locally Before Azure Deployment

The API works locally on http://localhost:8000/api and will work exactly the same on Azure without any code changes. Test all your curl commands locally first!

## Supported File Formats

- `.sav` - SPSS files
- `.dta` - Stata files
- `.csv` - CSV files
- `.json` - JSON files

## Common Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `max_rows` | number | Number of rows (default: 5) |
| `process_all_rows` | true/false | Process entire file |
| `decompose_keys` | true/false | Split hierarchical JSON keys |
| `variable_roles` | JSON object | Custom role assignments |

See `API_DOCUMENTATION.md` for complete documentation.
