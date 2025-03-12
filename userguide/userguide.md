# A Tour of the DDI-CDI Converter Tool - Practical Guidelines

## Upload a Data File

The DDI-CDI Converter tool allows you to easily convert your STATA or SPSS data files into DDI-CDI format. Here's how to get started by uploading your data file:

### Supported File Formats 
The tool accepts two common statistical data formats:
- STATA data files (`.dta`)
- SPSS data files (`.sav`)

### Upload Your File
In the main interface, you'll see a dashed box with the text "Drag and Drop or Select a File". You have two options for uploading:

- **Drag and drop method**: Simply drag your `.dta` or `.sav` file from your file explorer and drop it into the dashed box.
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

The DDI-CDI Converter has been designed to handle typical statistical datasets, but users should be aware of certain technical constraints when working with larger datasets:

### Memory Processing Limitations

1. **In-Memory Processing Model**: The current implementation processes data files entirely in memory, which places limitations on the size of files that can be efficiently processed.

2. **Default Row Limitation**: To ensure reliable performance across various hardware configurations, the tool is configured to process only the first 5 rows of data by default when including data values in the output.

3. **Chunked Processing**: For larger datasets, the tool implements a chunking mechanism that processes data in segments of 500 rows at a time to manage memory usage, but this approach still has limitations with very large datasets.

4. **Dynamic Memory Management**: The tool includes a `MemoryManager` component that attempts to optimize chunk sizes based on available system memory, but cannot overcome fundamental limitations of the in-memory processing model.

### DDI-CDI Data Model Complexity

The DDI-CDI specification requires a high level of descriptive detail for each data point, which results in significant output size expansion:

1. **Triple Element Representation**: In the DDI-CDI model, each cell in your data matrix requires three distinct elements to be fully represented:
   - **InstanceValue**: Describes the actual value
   - **DataPoint**: Defines the data point's properties and relationships 
   - **DataPointPosition**: Specifies the position within the data structure

2. **Output Size Expansion**: This triple representation means that a dataset with relatively modest dimensions will generate a much larger DDI-CDI representation. For example:
   - A dataset with 9,950 rows and just 22 columns would require 656,700 elements (9,950 × 22 × 3) to represent all data cells
   - The resulting JSON-LD file could contain over 5 million lines of code when including all structural metadata

3. **Visualization Limitations**: The preview functionality in the tool is designed to handle up to approximately 100,000 characters, beyond which the display is truncated (though the full content remains available for download).

4. **Memory Consumption**: Processing very large datasets can require significant memory resources, particularly when generating the complete DDI-CDI representation. The tool implements safeguards to prevent browser crashes, but these also limit the size of datasets that can be fully processed.

### Browser-Based Constraints

1. **Client-Side Processing**: As a web application, the tool relies on client-side (browser) resources for data processing, which imposes additional constraints compared to dedicated desktop applications.

2. **Download Size Limitations**: While the tool supports downloading files of any size that can be generated, browser memory limitations may impact the ability to process extremely large output files.

3. **Processing Time**: Large datasets may require significant processing time, during which the interface will display a progress indicator but may appear less responsive.

## Ideas for Next Steps

The current implementation of the DDI-CDI Converter demonstrates the potential for transforming statistical data into standardized DDI-CDI format. However, several enhancements could significantly improve its capabilities and applications:

### Backend Architecture Improvements

1. **Server-Side Processing**: Transitioning to a server-side processing model would overcome many of the current memory limitations:
   - Implementing a streaming architecture that processes data in manageable chunks
   - Using database intermediaries to handle large datasets without loading everything into memory
   - Leveraging background processing to allow users to submit conversion jobs and receive results when complete

2. **Distributed Processing**: For very large datasets, implementing a distributed processing system could divide conversion tasks across multiple computing resources.

3. **File Size Optimization**: Developing compression and optimization techniques specific to DDI-CDI representation could significantly reduce output file sizes while maintaining full compliance with the specification.

### API Development

1. **RESTful API**: Creating a comprehensive API would enable:
   - Programmatic access to conversion functionality
   - Integration with other data management systems
   - Batch processing of multiple files
   - Remote conversion without browser constraints

2. **Language-Specific Libraries**: Developing libraries in languages commonly used for data analysis (Python, R, etc.) would allow researchers to incorporate DDI-CDI conversion directly into their workflows.

3. **Webhook Notifications**: Implementing webhook notifications for completion of long-running conversion tasks would improve integration with other systems.

### Local Processing Tools

1. **Standalone Application**: Developing a desktop version of the converter would overcome browser limitations and provide:
   - Direct access to local system resources
   - Improved performance for large datasets
   - Offline conversion capabilities

2. **Command-Line Interface**: Creating a CLI tool would facilitate:
   - Batch processing through scripts
   - Integration with data pipelines
   - Server automation

3. **Integration with Statistical Software**: Developing plugins for SPSS, STATA, and other statistical packages would allow users to export directly to DDI-CDI format from their primary analytical tools.

### Additional Features

1. **Support for Additional Formats**: Expanding beyond SPSS and STATA to support:
   - R data files
   - Excel spreadsheets
   - CSV with metadata
   - Other statistical packages (SAS, etc.)

2. **Advanced Validation**: Implementing comprehensive validation tools to:
   - Verify DDI-CDI compliance
   - Identify potential issues in the output
   - Suggest optimizations for complex datasets

3. **Visualization Components**: Adding visualizations of the DDI-CDI structure to help users understand the relationships between elements in their data.

By implementing these enhancements, the DDI-CDI Converter could evolve into a more robust, scalable solution capable of handling datasets of any size while providing greater flexibility for integration with existing research workflows and data management systems.