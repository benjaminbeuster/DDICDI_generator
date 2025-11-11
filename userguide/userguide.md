# A Tour of the DDI-CDI Converter Tool - Practical Guidelines

## Upload a Data File

The DDI-CDI Converter tool allows you to easily convert your STATA, SPSS, or CSV data files into DDI-CDI format. Here's how to get started by uploading your data file:

### Supported File Formats 
The tool accepts three common statistical data formats:
- STATA data files (`.dta`)
- SPSS data files (`.sav`)
- CSV files (`.csv`) - Note that CSV files have limited built-in metadata compared to SPSS/Stata files

### Upload Your File
In the main interface, you'll see a dashed box with the text "Drag and Drop or Select a File". You have two options for uploading:

- **Drag and drop method**: Simply drag your `.dta`, `.sav`, or `.csv` file from your file explorer and drop it into the dashed box.
- **File selection method**: Click on the "Select a File" link, which will open your computer's file browser. Navigate to your data file, select it, and click "Open".

### Processing
After uploading, the tool will automatically:
- Read and process your file
- Display a preview of your data in a table format
- Prepare the interface for further data exploration and conversion tasks

### Important Notes
- Only one file can be uploaded at a time
- For optimal performance, the tool is configured to process a limited number of rows by default (5 rows)
- Large files may take several minutes to process
- After successful upload, you'll see your data displayed and can proceed with the conversion tasks

## Explore the Data File

After uploading your data file, the DDI-CDI Converter tool provides comprehensive ways to explore and understand your data. The tool offers two complementary views to help you examine your dataset:

### Data View

The Data View presents your actual data in a tabular format, similar to what you would see in statistical software like STATA or SPSS:

1. **Data Preview**: The tool displays a preview of your dataset, showing the actual data values in a structured table.
   
2. **Data Exploration**: You can scroll through the data to get a feel for the content and structure of your dataset.
   
3. **Column Headers**: Each column represents a variable from your dataset, with the variable name displayed as the header.

4. **Row Preview**: By default, the tool shows a limited number of rows (5) for performance reasons, but this gives you a good representation of your data.

### Variable View

The Variable View provides detailed metadata about each variable in your dataset:

1. **Switch to Variable View**: Click the "Switch View" button to toggle between the Data View and Variable View.

2. **Variable Metadata**: The Variable View displays comprehensive information about each variable, including:
   - **Name**: The variable name as defined in your dataset
   - **Format**: The data type (e.g., F4.0, F1.0, F2.0) indicating numeric precision and display format
   - **Label**: The descriptive label that provides context about what the variable represents
   - **Measure**: The measurement type (scale, nominal, ordinal)

3. **Variable Role Selection**: In the Variable View, you can classify each variable according to its role in your data:
   - **Measure**: Variables containing the actual measurements or observations
   - **Identifier**: Variables that uniquely identify records (used as the primary key)
   - **Attribute**: Variables that provide additional information about the measures
   - You can also assign multiple roles to a variable by selecting combined options like "Measure, Identifier"

4. **Role Selection Process**:
   - Click on the dropdown in the "Roles" column for each variable
   - Select the appropriate role (Measure, Attribute, Identifier, or a combination)
   - Variables classified as Identifiers will be used to uniquely identify records in the converted output

5. **Guidance Text**: The interface provides helpful instructions: "Please select variable role. Identifiers are used for the PrimaryKey to uniquely identify the records."

## Select Granularity of Output and Download Results

After exploring your data and assigning variable roles, you can generate and download the DDI-CDI representation of your dataset. The tool provides options to customize the output according to your needs:

### Configure Output Granularity

The DDI-CDI Converter allows you to control how much of your data is included in the output:

1. **Include data rows option**:
   - Toggle the switch labeled "Include data rows (limited to 5 rows by default)" to determine whether actual data values should be included in the output.
   - When turned **OFF**: Only the metadata (variable definitions, labels, etc.) will be included in the output.
   - When turned **ON**: Both metadata and actual data values will be included in the output (limited to 5 rows for large datasets).

2. **Performance warnings**:
   - The tool will display contextual warnings based on your dataset size and selected options.
   - Example: "Warning: For performance reasons, only the first 5 rows will be included in the JSON-LD output."
   - These warnings help you make informed decisions about output granularity, especially for large datasets.

3. **Processing status**:
   - When processing large datasets, the tool will display status messages and a progress indicator.
   - Once processing is complete, you'll see a confirmation message with processing time information.

### Download the JSON-LD Output

The DDI-CDI Converter generates output in JSON-LD format:

1. **Preview the output**:
   - After assigning variable roles and setting granularity options, the tool will display a preview of the generated JSON-LD representation.
   - For large outputs, the preview may be truncated, but the full content will be available for download.
   - The preview shows the structured output with proper formatting, allowing you to verify the content before downloading.

2. **Download the output**:
   - Click the "JSON-LD" button with the download icon to save the complete JSON-LD output to your computer.
   - The file will be automatically named based on your original data file, with the `.jsonld` extension.

3. **Output content**:
   - The generated output includes:
     - DDI-CDI structural metadata (dataset information, variable definitions)
     - Value labels and coding information
     - Missing value specifications
     - Actual data values (if "Include data rows" is enabled)
     - Proper namespaces and context references

## Best Practices for Working with the Tool

1. **Start with metadata only**: For initial testing, keep "Include data rows" turned off to quickly generate and validate the structural metadata.

2. **Identify key variables**: Pay special attention to identifying which variables should serve as identifiers (primary keys).

3. **Check variable roles**: Ensure that each variable is assigned the appropriate role based on its function in your dataset.

4. **Handle large datasets carefully**: For very large datasets, be aware that including data rows may significantly increase processing time and output file size.

5. **Verify the preview**: Always examine the JSON-LD preview to ensure it contains the expected content before downloading.

6. **Follow performance recommendations**: Pay attention to warning messages about dataset size and processing limitations.

By following these guidelines, you can effectively use the DDI-CDI Converter to transform your statistical data files into standardized DDI-CDI format for improved data documentation, sharing, and interoperability.

## Technical Specifications and Limitations of the Tool

The DDI-CDI Converter has been designed to handle typical statistical datasets, but users should be aware of certain technical constraints when working with larger datasets. This section explains these limitations and provides solutions for overcoming them through local customization.

### Understanding Performance Constraints

#### Row Limitations and Why They Exist

- **Default 5-Row Processing**: By default, the tool is configured to process only the first 5 rows of data when including actual values in the output. This limit exists to:
  - Ensure consistent performance across different browser environments
  - Prevent browser crashes due to memory exhaustion
  - Provide quick previews of how your data will be represented in DDI-CDI format

- **The Triple Representation Challenge**: In the DDI-CDI model, each cell in your data requires three distinct elements:
  - *InstanceValue*: Describes the actual value
  - *DataPoint*: Defines the data point's properties and relationships
  - *DataPointPosition*: Specifies the position within the data structure
  
  This means that for each row and column in your data, three separate JSON-LD elements must be generated, causing significant output expansion.

#### Output Size Considerations

- A dataset with 9,950 rows and 22 columns requires 656,700 elements (9,950 × 22 × 3)
- The resulting JSON-LD can contain millions of lines of code with structural metadata

#### Memory Management Approaches

- **In-Memory Processing Model**: The current implementation processes data files entirely in memory
- **Chunked Processing**: For larger datasets, the tool uses a chunking mechanism (default 500 rows per chunk)
- **Dynamic Memory Management**: The MemoryManager component attempts to optimize chunk sizes based on available system memory

#### Interface Limitations

- **Visualization Limitations**: 
  - Preview functionality handles up to ~100,000 characters
  - Larger outputs are truncated in the display but remain fully available for download

- **Browser Constraints**: 
  - Client-side processing depends on your browser's available memory
  - Large file downloads may be affected by browser memory limitations
  - Processing time increases significantly with dataset size

### Customizing the Tool Through GitHub

The DDI-CDI Converter is [open source on GitHub](https://github.com/benjaminbeuster/DDICDI_generator), allowing extensive customization for your specific needs:

#### Current Deployment

The tool is currently deployed as an Azure Web App, which provides several advantages:
- **Scalability**: The Azure platform allows for scaling the application based on demand
- **Accessibility**: Available globally without requiring local installation
- **Maintenance**: Centrally maintained and updated version
- **Consistency**: Provides a consistent experience across different devices

You can access the deployed version at [https://ddi-cdi-converter-app.azurewebsites.net/](https://ddi-cdi-converter-app.azurewebsites.net/).

#### Setting Up a Local Installation

1. Clone the repository: `git clone https://github.com/benjaminbeuster/DDICDI_generator.git`
2. Follow the installation instructions in the [repository's README](https://github.com/benjaminbeuster/DDICDI_generator#installation-instructions)

#### Modifying Row Limitations

To increase the default row limit for processing larger datasets:

1. Open `app.py` in a text editor
2. Locate these configuration parameters near the top of the file:
   ```python
   # Configuration parameters
   MAX_ROWS_TO_PROCESS = 5  # Maximum number of rows to process by default
   PREVIEW_ROWS = 5  # Number of rows to show in the data preview table
   CHUNK_SIZE = 500  # Size of chunks to process when handling larger datasets
   ```
3. Modify `MAX_ROWS_TO_PROCESS` to your desired value
4. Adjust `CHUNK_SIZE` to optimize performance based on your system's capabilities
5. For maximum file reading capacity, you can also modify `ROW_LIMIT` in `spss_import.py`

#### Benefits of Local Installation

- **Hardware Optimization**: Utilize your full system resources instead of browser limitations
- **Privacy and Security**: Process sensitive data entirely on your own machine
- **Customization**: Modify the code to meet specific project requirements
- **Larger Datasets**: Process significantly more data than possible in the web version

### Recommended Approaches for Large Datasets

1. **Start With Metadata Only**: Initially generate only metadata (no data rows) to validate structure
2. **Incremental Testing**: Test with a small number of rows before processing entire datasets
3. **Local Processing**: For very large datasets, use a local installation with customized parameters
4. **Monitor System Resources**: Watch memory usage during processing of large files
5. **Split Large Files**: Consider pre-processing very large files into smaller chunks when possible

### When to Consider Alternative Solutions

The current tool may not be suitable for datasets that:
- Exceed 100,000+ rows (without local customization)
- Require real-time processing
- Need extensive custom mapping beyond the supported statistical formats
- Require integration with other systems through APIs

For these cases, consider exploring the [Ideas for Next Steps](#ideas-for-next-steps) section or contributing to the GitHub repository to enhance the tool's capabilities.

## Ideas for Next Steps

The current implementation of the DDI-CDI Converter demonstrates the potential for transforming statistical data into standardized DDI-CDI format. Several enhancements could extend its capabilities while maintaining its lightweight, accessible nature:

### Performance Enhancements

- **Streaming Processing**: Implement data streaming to process files incrementally without loading entire datasets into memory
- **Optimized Memory Management**: Refine the chunking mechanism to better handle varying hardware capabilities
- **File Size Optimization**: Develop compression techniques for DDI-CDI representation while maintaining specification compliance

### API Development

- **RESTful API Wrapper**: Create a lightweight API layer around the core functionality:
  - File upload endpoints
  - Configuration endpoints to control processing parameters
  - Asynchronous processing with status notifications
  - Secure download links for completed conversions

- **Integration Examples**: Provide code samples for common integration scenarios:
  - Data repository integrations
  - Statistical software plugins
  - Research workflow tools

### Community Engagement

- **Contributor Guidelines**: Create clear documentation for developers interested in extending the tool
- **Use Case Repository**: Collect and showcase different applications of the converter
- **Extension Mechanism**: Design a plugin system to allow community-developed extensions without modifying core code

By implementing these enhancements, the DDI-CDI Converter can evolve into a more versatile tool that remains true to its lightweight design principles while offering increased functionality through API access.

## Acknowledgments

Parts of this user guide, particularly the technical specifications and customization sections, were created with the assistance of AI technology. The AI analyzed the codebase to extract accurate information about configuration parameters, memory management approaches, and customization options. Additionally, AI was used for language improvements throughout the document and for verifying the accuracy and completeness of the user guide.

The core functionality descriptions, workflow guidance, and best practices sections were developed based on extensive testing and user experience design principles to provide practical, actionable guidance for users of all technical levels.
