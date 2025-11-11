# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DDI-CDI Converter is a Python-based web application that converts statistical files (Stata .dta, SPSS .sav, CSV, and JSON) into DDI-CDI JSON-LD format. The tool is optimized for WideDataStructure and KeyValueStructure patterns from the DDI-CDI model.

- **Prototype Status**: This is a prototype tool developed for DDI-CDI implementation training, not production-ready
- **Target Model**: DDI-CDI v1.0 - uses 29 DDI-CDI classes and 2 SKOS classes
- **Deployment**: Azure Web App (see azure.yaml for configuration)

## Development Commands

### Running the Application

```bash
# Using pip
python app.py

# Using Poetry
poetry run python app.py
```

The web interface will be available at http://localhost:8050 by default (or port defined in PORT environment variable).

### Installing Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Using Poetry
poetry install
```

### Testing File Import

The application supports multiple file formats for testing:
- SPSS files (.sav) via pyreadstat
- Stata files (.dta) via pyreadstat
- CSV files (.csv) with automatic delimiter detection
- JSON files (.json) in various formats (flat key-value, nested, array-based, hierarchical with "/" separators)

## Code Architecture

### Application Structure

The codebase follows a modular Dash/Flask architecture:

**Core Application (app.py)**
- Main Dash application with Flask server
- File upload handling with drag-and-drop UI
- Interactive data preview tables with role assignment dropdowns
- Different role options for JSON vs non-JSON files
- Configuration parameters at top of file control processing limits

**File Import Layer (spss_import.py)**
- Unified interface for reading different file formats
- Key functions:
  - `read_sav()`: Handles both .sav and .dta files
  - `read_csv()`: CSV import with delimiter auto-detection and date parsing
  - `read_json()`: Multi-format JSON handling (flat, nested, array, hierarchical)
- Creates standardized metadata objects compatible across all formats
- Handles missing values, data type inference, and encoding detection

**DDI-CDI Generation (DDICDI_converter_JSONLD_incremental.py)**
- Converts tabular data to DDI-CDI JSON-LD
- Two primary data structure patterns:
  - **WideDataStructure**: For traditional tabular data (SPSS, Stata, CSV)
  - **KeyValueStructure**: For JSON key-value data
- Component role types vary by format:
  - Non-JSON: MeasureComponent, IdentifierComponent, AttributeComponent, PrimaryKey
  - JSON: VariableValueComponent, VariableDescriptorComponent, ContextualComponent, SyntheticIdComponent, IdentifierComponent
- Chunked processing for large datasets with memory optimization via MemoryManager class
- Incremental generation functions for each DDI-CDI class

**UI Content (app_content.py)**
- Markdown documentation of DDI-CDI classes used
- Color scheme and styling definitions
- About text and project metadata

### Key Design Patterns

**Metadata Object Pattern**: All file readers create a metadata object with these attributes:
- `column_names`: List of variable names
- `column_labels`: Variable labels/descriptions
- `original_variable_types`: Data types per variable
- `variable_value_labels`: Value label mappings
- `missing_ranges`/`missing_user_values`: Missing value definitions
- `variable_measure`: Measurement level (nominal, scale, ordinal)
- Role classifications: `measure_vars`, `identifier_vars`, `attribute_vars`, `contextual_vars`, `synthetic_id_vars`, `variable_value_vars`
- `file_format`: Identifies format ('csv', 'json', or from pyreadstat)

**Conditional Structure Generation**: The converter adapts output based on file format:
- Checks `df_meta.file_format` to determine structure type
- Uses helper functions `_get_dataset_reference()`, `_get_structure_reference()` to return appropriate references
- Non-JSON files generate PrimaryKey components when identifiers present
- JSON files skip PrimaryKey generation (use IdentifierComponent only)

**Role Assignment System**: Variables can have multiple roles (comma-separated):
- UI provides different dropdown options based on file format
- Non-JSON: measure, identifier, attribute (combinable)
- JSON: identifier, synthetic, contextual, variablevalue (single selection)
- Default role assignment logic in `get_default_roles_for_variables()` based on file analysis

**Chunked Processing**: For large datasets with `process_all_rows=True`:
- Processes data in chunks (default 500 rows via CHUNK_SIZE constant)
- Optimizes chunk size dynamically based on available memory
- Shows progress reporting during processing
- Pre-processes DataPoints/positions, processes InstanceValues in chunks

### Configuration Parameters

Located at top of app.py:
```python
MAX_ROWS_TO_PROCESS = 5  # Default row limit for output
PREVIEW_ROWS = 5         # Rows shown in preview table
CHUNK_SIZE = 500         # Chunk size for large dataset processing
```

In spss_import.py:
```python
ROW_LIMIT = 10000000     # Max rows to read from file
```

### JSON File Handling

The application intelligently detects and handles multiple JSON formats:

1. **Flat key-value**: `{"key1": value1, "key2": value2}`
2. **Hierarchical keys**: `{"a/b/c": value}` - decomposed into separate key-1, key-2, key-3 columns when enabled
3. **Nested objects**: `{"record1": {"prop1": val1, "prop2": val2}}`
4. **Deep nested**: Objects containing other objects - flattened with dot notation
5. **Array format**: `{"array": [{"obj1": val}, {"obj2": val}]}`
6. **Structured format**: Explicit variable definitions with types and value labels

Decomposition of hierarchical keys is controlled by the `decompose_keys` switch in the UI (shown only for JSON files).

### Missing Value Handling

The system handles missing values through SentinelValueDomain:
- SPSS: Uses `missing_ranges` from metadata
- Stata: Uses `missing_user_values` from metadata
- CSV: No native missing value support
- JSON: No native missing value support
- InstanceValue generation checks if values fall in missing ranges and references appropriate domain

### Memory Management

The `MemoryManager` class in DDICDI_converter_JSONLD_incremental.py provides:
- `estimate_memory_usage()`: Estimates RAM needed for processing
- `optimize_chunk_size()`: Calculates optimal chunk size based on available memory (default 500MB target)
- Used when processing large datasets with `process_all_rows=True`

## DDI-CDI Model Implementation

This converter implements a subset focused on:
- **Wide Data Pattern**: Traditional rectangular datasets with measures, identifiers, attributes
- **Key-Value Pattern**: JSON key-value stores with contextual/synthetic IDs and variable values
- **Physical Description**: Data storage format, record segments, value mappings
- **Value Domains**: Substantive (valid values) and Sentinel (missing values) domains with SKOS concepts

The application generates references between:
- DataPoints ↔ InstanceVariables ↔ ValueDomains
- PhysicalRecordSegment ↔ LogicalRecord ↔ DataSet
- DataStructure ↔ Components (Measure/Identifier/Attribute or VariableValue/Descriptor/Contextual/Synthetic)

## Common Development Tasks

### Modifying Row Limits

Edit constants at top of `app.py`:
- `MAX_ROWS_TO_PROCESS`: Rows included in JSON-LD when metadata toggle is on
- `PREVIEW_ROWS`: Rows displayed in preview table
- `CHUNK_SIZE`: Processing batch size for large datasets

### Adding New File Format Support

1. Add import function in `spss_import.py` following the pattern of `read_csv()` or `read_json()`
2. Create metadata object with required attributes (see Metadata Object Pattern above)
3. Set `file_format` attribute on metadata
4. Add file extension to upload component accept list in `app.py`
5. Add conditional logic in `combined_callback()` to call new import function
6. Update `get_default_roles_for_variables()` if format needs special role defaults

### Modifying DDI-CDI Output Structure

The generation functions in `DDICDI_converter_JSONLD_incremental.py` map 1:1 to DDI-CDI classes. To modify:
1. Locate the `generate_[ClassName]()` function
2. Modify the element dictionary structure
3. Update references in parent/child generation functions as needed
4. Consider file format conditionals using helper functions like `_get_dataset_reference()`

### Testing with Azure AI Search

Note in user's CLAUDE.md indicates the app is configured with Azure AI Search integration (see README_Sikt_notes.md which doesn't exist in current scan).

## Dependencies

Key dependencies with version constraints:
- pandas 1.5.3 (specific version for stability)
- pyreadstat 1.2.7 (SPSS/Stata file reading)
- dash 2.13.0 (web framework)
- rdflib 7.1.3 (RDF/JSON-LD conversion for N-Triples export)
- flask 2.1.2 (underlying web server)

See `requirements.txt` or `pyproject.toml` for complete list.

## Important Notes

- The tool defaults to 5 rows for performance across different hardware
- N-Triples output button exists in DOM but is hidden in UI (style: display:none)
- XML output format was removed - only JSON-LD is generated now
- File uploads are processed in temporary files then deleted after processing
- Git operations require explicit user consent - never commit automatically
- The `lists.txt` file tracks current variable role assignments during session
