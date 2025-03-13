# DDI-CDI Converter (Prototype): Wide Table Generation for STATA, SPSS & CSV

The DDI-CDI Converter Prototype is a Python-based web application developed to convert statistical files from Stata, SPSS, and CSV formats into [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) JSON-LD files. This prototype meets the growing demand for interoperability and data sharing by transforming various data formats into an open, standardized, and machine-readable format.

## Example Application

An [example application](https://ddi-cdi-converter-app.azurewebsites.net/) is available to demonstrate the capabilities of this prototype. This prototype was developed by Sikt as part of the [Worldfair Project](https://worldfair-project.eu/) and supported by the DDI-CDI-Working Group.

## Output Format

As of the latest update, the application now exclusively supports JSON-LD output format. XML output has been removed to simplify the codebase and focus on modern, web-friendly data formats.

## Supported File Formats

The application supports the following input file formats:

- **SPSS files** (.sav): Full support with metadata and variable properties
- **Stata files** (.dta): Full support with metadata and variable properties
- **CSV files** (.csv): Support with basic metadata inference
  - CSV files have limited built-in metadata compared to SPSS/Stata files
  - The application attempts to infer variable types and measure types from the data
  - Date columns are detected based on column names containing "date" or "time" and converted appropriately

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- For SPSS file support: pyreadstat dependencies (may require C compiler on some systems)

### Option 1: Installation with pip

1. Clone the repository:
   ```
   git clone https://github.com/benjaminbeuster/DDICDI_generator.git
   cd DDICDI_generator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```
   
   The web interface will be available at http://localhost:8050 by default.

### Option 2: Installation with Poetry

1. Clone the repository:
   ```
   git clone https://github.com/benjaminbeuster/DDICDI_generator.git
   cd DDICDI_generator
   ```

2. Install Poetry if you don't have it already:
   ```
   pip install poetry
   ```

3. Install dependencies using Poetry:
   ```
   poetry install
   ```

4. Run the application using Poetry:
   ```
   poetry run python app.py
   ```

### Customizing Row Limits

By default, the application processes only 5 rows of data to ensure performance across different hardware configurations. To increase this limit for local installations:

1. Open `app.py` in a text editor
2. Look for the following configuration parameters near the top of the file:
   ```python
   # Configuration parameters
   MAX_ROWS_TO_PROCESS = 5  # Maximum number of rows to process by default
   PREVIEW_ROWS = 5  # Number of rows to show in the data preview table
   CHUNK_SIZE = 500  # Size of chunks to process when handling larger datasets
   ```
3. Modify the `MAX_ROWS_TO_PROCESS` value to increase the number of rows processed
4. You can also adjust `CHUNK_SIZE` for better performance with larger datasets
5. Save the file and restart the application

Additionally, in `spss_import.py`, there's a more generous limit (`ROW_LIMIT = 10000000`) for the maximum number of rows to read from SPSS/STATA files initially.

Note that processing large datasets will require more memory and processing power. The optimal row limit depends on your specific hardware configuration.

### Using the Startup Script

For Linux/macOS users, you can use the provided startup script:

```
chmod +x startup.sh
./startup.sh
```

## Disclaimer

The DDI-CDI Converter is designed to facilitate the implementation of [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) and to support training activities within the DDI community. For further information, please contact [Benjamin Beuster](mailto:benjamin.beuster@sikt.no).

Given that only limited time and resources were available for its creation, the tool is not intended for use as a production tool in its current form. Instead, it serves as an example for developers interested in these types of applications.

The current tool is optimized for display on a PC screen and does not account for mobile design or other scenarios that might be required in a production tool. It does not cover all possible fields in the DDI-CDI model for data files but focuses on a selection of fields, particularly those related to the WideDataStructure from the DataDescription.