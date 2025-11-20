# DDI-CDI Converter API - Quick Start

## Base URLs

**Production (Azure):** `https://ddi-cdi-converter-app.azurewebsites.net/api`
**Local Development:** `http://localhost:8000/api`

---

## Quick Test Commands

### 1. Check API is Running

**Azure:**
```bash
curl https://ddi-cdi-converter-app.azurewebsites.net/api/health
```

**Local:**
```bash
curl http://localhost:8000/api/health
```

### 2. Get API Info

**Azure:**
```bash
curl https://ddi-cdi-converter-app.azurewebsites.net/api/info
```

**Local:**
```bash
curl http://localhost:8000/api/info
```

### 3. Basic Conversion

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@yourfile.sav" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@yourfile.sav" \
  -o output.jsonld
```

### 4. With Authentication (if DDI_API_KEY is set)

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -H "X-API-Key: your-api-key" \
  -F "file=@yourfile.sav" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -H "X-API-Key: your-api-key" \
  -F "file=@yourfile.sav" \
  -o output.jsonld
```

### 5. Process More Rows

**Azure:**
```bash
curl -X POST https://ddi-cdi-converter-app.azurewebsites.net/api/convert \
  -F "file=@yourfile.csv" \
  -F "max_rows=100" \
  -o output.jsonld
```

**Local:**
```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@yourfile.csv" \
  -F "max_rows=100" \
  -o output.jsonld
```

### 6. Custom Variable Roles

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

## Testing Strategy

**Recommendation:** Test commands locally first, then use the same commands on Azure by just replacing the URL.

Example workflow:
1. Test locally: `curl http://localhost:8000/api/health`
2. Deploy to Azure
3. Test on Azure: `curl https://ddi-cdi-converter-app.azurewebsites.net/api/health`

The API works identically in both environments!

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
