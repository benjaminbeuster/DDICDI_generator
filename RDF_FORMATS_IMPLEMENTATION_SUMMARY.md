# RDF Output Formats Implementation Summary

**Date:** 2025-11-26
**Status:** ✅ COMPLETE

## Overview

Successfully implemented support for multiple RDF output formats (JSON-LD, Turtle, N-Triples) in both the REST API and web UI, addressing user feedback that "JSON-LD is hard to read."

## What Was Implemented

### 1. New Module: `format_converter.py`

Created a reusable format conversion utility with the `FormatConverter` class:

- **Supported Formats:**
  - JSON-LD (.jsonld) - W3C JSON-LD RDF serialization [default]
  - Turtle (.ttl) - Human-readable RDF format with namespace prefixes
  - N-Triples (.nt) - Simple line-based RDF format

- **Key Features:**
  - Configurable base URI (default: `http://example.org/ddi/`)
  - Standard namespace bindings for Turtle output
  - Automatic URI transformation from `file:///` to configured base
  - Comprehensive error handling
  - Format metadata (mimetype, extension, description)

### 2. REST API Updates (`api.py`)

#### New Parameters:

**`output_format`** (optional, default: 'jsonld')
- Options: jsonld, turtle, ntriples
- Controls the RDF serialization format

**`base_uri`** (optional)
- Custom base URI for instance data
- Defaults to environment variable `DDI_BASE_URI` or `http://example.org/ddi/`

#### Updated Endpoints:

**`POST /api/convert`**
- Now returns different mimetypes based on format:
  - `application/ld+json` for JSON-LD
  - `text/turtle` for Turtle
  - `application/n-triples` for N-Triples
- Adds Content-Disposition header with appropriate file extension
- Validates format parameter against supported formats

**`GET /api/info`**
- Now lists all supported output formats with descriptions
- Documents new parameters

### 3. Web UI Updates (`app.py`)

#### New UI Components:

- **Format Dropdown Selector:**
  - Replaces separate JSON-LD and N-Triples buttons
  - Compact design with clear format descriptions
  - Options:
    - JSON-LD (.jsonld)
    - Turtle (.ttl) - Human-readable
    - N-Triples (.nt) - Simple line-based

- **Unified Download Button:**
  - Single "Download" button works with selected format
  - Generates appropriate filename with correct extension

#### New Callback:

**`download_format()`**
- Unified download handler for all formats
- Reads base URI from environment variable `DDI_BASE_URI`
- Uses FormatConverter for conversion
- Handles errors gracefully

### 4. Deprecation Notices

Added clear deprecation warnings to standalone scripts:
- `files/convert-jsonld-rdf.py`
- `files/convert-jsonld-turtle.py`

Scripts still work but direct users to API/UI for better functionality.

## Configuration

### Environment Variable

Set custom base URI for universal/portable files:

```bash
export DDI_BASE_URI=http://example.org/ddi/
python app.py
```

Default if not set: `http://example.org/ddi/`

## API Usage Examples

### Convert to JSON-LD (default)

```bash
curl -X POST http://localhost:8050/api/convert \
  -F "file=@data.csv" \
  -o output.jsonld
```

### Convert to Turtle

```bash
curl -X POST http://localhost:8050/api/convert \
  -F "file=@data.csv" \
  -F "output_format=turtle" \
  -o output.ttl
```

### Convert to N-Triples

```bash
curl -X POST http://localhost:8050/api/convert \
  -F "file=@data.csv" \
  -F "output_format=ntriples" \
  -o output.nt
```

### Custom Base URI

```bash
curl -X POST http://localhost:8050/api/convert \
  -F "file=@data.csv" \
  -F "output_format=turtle" \
  -F "base_uri=http://myorg.edu/data/" \
  -o output.ttl
```

### Check Available Formats

```bash
curl http://localhost:8050/api/info | jq '.supported_output_formats'
```

## Test Results

All tests passed successfully:

### ✅ JSON-LD Format
- Status: 200
- Content-Type: `application/ld+json`
- File extension: `.jsonld`
- Output: Valid JSON-LD with DDI-CDI context

### ✅ Turtle Format
- Status: 200
- Content-Type: `text/turtle`
- File extension: `.ttl`
- Output: Valid Turtle with namespace prefixes (ddi, xsd, skos, etc.)

### ✅ N-Triples Format
- Status: 200
- Content-Type: `application/n-triples`
- File extension: `.nt`
- Output: Valid N-Triples (simple line-based format)

### ✅ Custom Base URI
- Successfully applies custom base URI
- Tested with `http://myorg.edu/data/`
- URIs in output correctly use custom base

## URI Transformation

The system transforms URIs during RDF conversion:

**Before (JSON-LD):**
```
file:///#physicalDataSet
```

**After (Turtle/N-Triples):**
```
<http://example.org/ddi/#physicalDataSet>
```

**With custom base URI:**
```
<http://myorg.edu/data/#physicalDataSet>
```

## Namespace Bindings (Turtle Format)

Turtle output includes standard RDF namespace prefixes for readability:

```turtle
@prefix ex: <http://example.org/ddi/> .
@prefix ddi: <http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

## Files Changed

### New Files:
1. `format_converter.py` - Format conversion utility module

### Modified Files:
1. `api.py` - Added output_format and base_uri parameters
2. `app.py` - Updated UI with dropdown selector and unified callback
3. `files/convert-jsonld-rdf.py` - Added deprecation notice
4. `files/convert-jsonld-turtle.py` - Added deprecation notice

### Documentation:
1. `IMPLEMENTATION_PLAN_RDF_FORMATS.md` - Detailed implementation plan
2. `RDF_FORMATS_IMPLEMENTATION_SUMMARY.md` - This file

## Backward Compatibility

✅ **Fully backward compatible:**
- Existing API calls without `output_format` parameter work unchanged
- Default format is JSON-LD (same as before)
- All existing functionality preserved
- Standalone scripts still work (with deprecation notice)

## Benefits

1. **Improved Readability:** Turtle format is much more human-readable than JSON-LD
2. **Universal Files:** Configurable base URI allows creating portable, institution-agnostic files
3. **Format Flexibility:** Users can choose format based on their use case
4. **Standards Compliance:** All formats follow W3C RDF specifications
5. **Better Integration:** N-Triples format easier to parse for many RDF tools

## Next Steps (Optional Enhancements)

Potential future improvements not included in this implementation:

1. Add RDF/XML format support
2. Add format auto-detection based on Accept header
3. Implement streaming for very large files
4. Add format validation endpoint
5. Support for additional serialization options (e.g., Turtle pretty-print settings)

## User Feedback Addressed

✅ **Original Request:** "Is there an option for producing a Turtle output (JSON-LD is hard to read...:-))?"

✅ **Solution Implemented:**
- Turtle format now available via API and UI
- Simple dropdown selector in web interface
- Clear format descriptions help users choose
- Configurable base URI for universal files

## Conclusion

The implementation successfully addresses all user requirements:
- ✅ Turtle output for human readability
- ✅ Universal/portable files with configurable base URI
- ✅ API parameter for format selection
- ✅ Compact dropdown UI design
- ✅ All tests passing
- ✅ Backward compatible
- ✅ Well-documented

The DDI-CDI Converter now provides flexible RDF output options suitable for both human inspection and machine processing.
