# DDI-CDI Converter (Prototype): Wide Table Generation for STATA & SPSS

The DDI-CDI Converter Prototype is a Python-based web application developed to convert proprietary statistical files from Stata and SPSS into [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) XML files. This prototype meets the growing demand for interoperability and data sharing by transforming proprietary data formats into an open, standardized, and machine-readable format.

## Example Application

An [example application](https://ddi-cdi-converter-app.azurewebsites.net/) is available to demonstrate the capabilities of this prototype. This prototype was developed by Sikt as part of the [Worldfair Project](https://worldfair-project.eu/) and supported by the DDI-CDI-Working Group.

## Disclaimer

The DDI-CDI Converter is designed to facilitate the implementation of [DDI-CDI](https://ddialliance.org/Specification/DDI-CDI/) and to support training activities within the DDI community. For further information, please contact [Benjamin Beuster](mailto:benjamin.beuster@sikt.no).

Given that only limited time and resources were available for its creation, the tool is not intended for use as a production tool in its current form. Instead, it serves as an example for developers interested in these types of applications.

The current tool is optimized for display on a PC screen and does not account for mobile design or other scenarios that might be required in a production tool. It does not cover all possible fields in the DDI-CDI model for data files but focuses on a selection of fields, particularly those related to the WideDataStructure from the DataDescription.