#!/usr/bin/env python
# coding: utf-8

from flask import Flask
import os
import base64
import tempfile
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from DDICDI_converter_xml_incremental import (
    generate_complete_xml_with_keys
)
from DDICDI_converter_JSONLD_incremental import (
    generate_complete_json_ld
)
from spss_import import read_sav, create_variable_view, create_variable_view2
from app_content import markdown_text, colors, style_dict, table_style, header_dict, app_title, app_description, about_text


# Define the namespaces, DDI
nsmap = {
    'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/',
    'r': 'ddi:reusable:3_3'  # Replace with the actual URI for the 'r' namespace
}
agency = 'int.esseric'

# Define the Flask server
server = Flask(__name__)

# Define the Dash app and associate it with the Flask server
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.LITERA])

# add title
app.title = app_title

brand_section = html.Div([
    dbc.NavLink(app_title, href="#", style={'verticalAlign': 'middle'}, className='ml-0')  # Add className='ml-0' and remove marginRight
])

logo_section = html.Div(
    children=[
        html.Img(
            src=app.get_asset_url('sikt.jpg'),
            style={
                'height': '40px',
                'maxWidth': '100%',
                'objectFit': 'contain',
                'marginRight': '10px'
            }
        ),
        html.Img(
            src=app.get_asset_url('petals_logos.2.0-01.webp'),
            style={
                'height': '50px',  # Increased from 40px to 50px
                'width': 'auto',
                'marginRight': '10px',
                'opacity': '0.8'
            }
        )
    ],
    style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center'
    }
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(app_description, href="#", className="nav-link-custom")),
        logo_section
    ],
    brand=brand_section,
    brand_href="#",
    color=colors['background'],
    light=True,
    className="custom-navbar shadow-sm",
    style={
        'borderBottom': f'1px solid {colors["border"]}',
        'marginBottom': '30px',
        'padding': '15px 0'
    }
)

about_section = dbc.Card(
    dbc.CardBody(
        dcc.Markdown(about_text, className="card-text")
    ),
    className="mt-4",  # Adding some margin at the top for spacing
    style={
        'fontFamily': "'Inter', sans-serif",
        'fontSize': '15px',
        'letterSpacing': '-0.01em'
    }
)

app.layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col([
            html.Br(),
            # REMOVE THIS SECTION
            # dcc.Upload(
            #     id='upload-data',
            #     children=dbc.Button('Import Data', color="primary", className="mr-1"),
            #     multiple=False,
            #     accept=".sav,.dta"  # Accept both .sav and .dta files
            # ),

            # ADD THIS NEW DRAG-AND-DROP SECTION INSTEAD
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select a File', 
                        style={
                            'color': colors['primary'], 
                            'cursor': 'pointer',
                            'fontWeight': '500',
                            'letterSpacing': '-0.01em'
                        })
                ], style={
                    'width': '100%',
                    'height': '80px',
                    'lineHeight': '80px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '12px',
                    'textAlign': 'center',
                    'margin': '20px 0',
                    'backgroundColor': colors['surface'],
                    'transition': 'all 0.3s ease-in-out',
                    'cursor': 'pointer',
                    'borderColor': colors['border'],
                    'color': colors['secondary'],
                    'fontFamily': "'Inter', sans-serif",
                    'fontWeight': '500',
                    'letterSpacing': '-0.01em',
                    'fontSize': '16px'  # Increased from default
                }),
                style={
                    'width': '100%',
                    'height': '100%',
                },
                multiple=False,
                accept=".sav,.dta"
            ),
            html.Br(),

            # Add style and id to the Switch View button
            dbc.Button(
                "Switch View", 
                id="table-switch-button", 
                color="primary", 
                className="mr-1",
                style={'display': 'none'}  # Hidden by default
            ),

            html.Br(),

            # Create two separate columns for the tables and wrap them in a Row
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-table1",
                        type="default",
                        children=[
                            # Insert the refined instruction text here with an id and hidden style
                            html.Div(
                                "This table displays the first 5 rows of the data file. Note: The XML output is also limited to these 5 rows.",
                                id="table1-instruction",
                                style={
                                    'color': colors['secondary'],
                                    'fontSize': '13px',
                                    'marginBottom': '10px',
                                    'fontFamily': "'Inter', sans-serif",
                                    'display': 'none'
                                }
                            ),

                            dash_table.DataTable(
                                id='table1',
                                columns=[],
                                data=[],
                                style_table=table_style,
                                style_header=header_dict,
                                style_cell=style_dict
                            )
                        ]
                    ),
                ], id="table1-col"),

                dbc.Col([
                    dcc.Loading(
                        id="loading-table2",
                        type="default",
                        children=[
                            # Insert the instruction text here
                            html.Div("Please select the Identifier Variables from the first column to be used as the Primary Key.",
                                     style={
                                         'color': colors['secondary'],
                                         'fontSize': '15px',  # Increased from 14px
                                         'marginBottom': '10px',
                                         'fontFamily': "'Inter', sans-serif"
                                     }
                                    ),

                            dash_table.DataTable(
                                id='table2',
                                editable=True,
                                persistence=True,
                                persistence_type='session',
                                row_selectable=False,  # Remove multi-selection
                                style_table=table_style,
                                style_header=header_dict,
                                style_cell=style_dict,
                                columns=[
                                    {
                                        "name": "Type",
                                        "id": "var_type",
                                        "presentation": "dropdown",
                                        "editable": True
                                    },
                                    # ... other columns ...
                                ],
                                dropdown={
                                    'var_type': {
                                        'options': [
                                            {'label': 'Measure', 'value': 'measure'},
                                            {'label': 'Attribute', 'value': 'attribute'},
                                            {'label': 'Identifier', 'value': 'identifier'}
                                        ],
                                        'clearable': False
                                    }
                                },
                                # Add these properties to ensure dropdown is clickable and visible
                                css=[{
                                    'selector': '.Select-menu-outer',
                                    'rule': 'display: block !important'
                                }],
                                style_cell_conditional=[{
                                    'if': {'column_id': 'var_type'},
                                    'textAlign': 'left',
                                    'minWidth': '150px',
                                    'width': '150px',
                                    'maxWidth': '150px',
                                }],
                                style_data_conditional=[{
                                    'if': {'column_id': 'var_type'},
                                    'cursor': 'pointer'
                                }]
                            ),
                        ]
                    ),
                ], id="table2-col", style={'display': 'none'}),  # Initially, hide the second table
            ]),

            html.Br(),
            # Group the buttons together in a ButtonGroup
            dbc.ButtonGroup(
                [
                    dbc.Button('XML', id='btn-download', color="primary", className="mr-1"),
                    dbc.Button('JSON-LD', id='btn-download-json', color="primary", className="mr-1"),
                    dbc.Button('Download', id='btn-download-active', color="success"),
                ],
                style={'display': 'none', 'gap': '10px'},
                id='button-group',
                className="shadow-sm"
            ),
            # Add switch using dbc.Switch
            dbc.Switch(
                id="include-metadata",
                label="Include cell metadata",
                value=False,
                style={
                    'display': 'inline-block',
                    'marginLeft': '15px',
                    'color': colors['secondary']
                }
            ),
            dcc.Download(id='download-active'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    # Wrap both outputs in a single Pre element
                    html.Pre(
                        children=[
                            html.Div(id='xml-ld-output',
                                style={
                                    'whiteSpace': 'pre',
                                    'wordBreak': 'break-all',
                                    'color': colors['text'],
                                    'backgroundColor': colors['surface'],
                                    'marginTop': '20px',
                                    'maxHeight': '400px',
                                    'overflowY': 'scroll',
                                    'fontSize': '14px',
                                    'padding': '20px',
                                    'borderRadius': '8px',
                                    'border': f'1px solid {colors["border"]}',
                                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
                                    'display': 'block',
                                    'fontFamily': "'JetBrains Mono', 'Fira Code', 'IBM Plex Mono', monospace",
                                    'lineHeight': '1.5'
                                }
                            ),
                            html.Div(id='json-ld-output',
                                style={
                                    'whiteSpace': 'pre',
                                    'wordBreak': 'break-all',
                                    'color': colors['text'],
                                    'backgroundColor': colors['surface'],
                                    'marginTop': '10px',
                                    'maxHeight': '300px',
                                    'overflowY': 'scroll',
                                    'fontSize': '14px',
                                    'padding': '20px',
                                    'borderRadius': '8px',
                                    'border': f'1px solid {colors["border"]}',
                                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
                                    'display': 'none',
                                    'fontFamily': "'JetBrains Mono', 'Fira Code', 'IBM Plex Mono', monospace",
                                    'lineHeight': '1.5'
                                }
                            ),
                        ]
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Markdown(markdown_text, 
                                dangerously_allow_html=True,
                                className="card-text"
                            ),
                            style={
                                'overflowY': 'scroll',
                                'height': '400px',
                                'padding': '20px',
                                'fontSize': '15px',
                                'fontFamily': "'Inter', sans-serif",
                                'letterSpacing': '-0.01em'
                            }
                        )
                    ])
                ], width=6)

            ]),
        ])
    ]),
    about_section  # <-- add this line to include the about_section
], fluid=True)

def style_data_conditional(df):
    style_data_conditional = []
    for col in df.columns:
        if df[col].dtype == "object":
            style_data_conditional.append({
                'if': {'column_id': col},
                'textAlign': 'left',
                'maxWidth': '150px',
                'whiteSpace': 'normal',
                'height': 'auto',
            })
    return style_data_conditional

# Define callbacks
@app.callback(
    Output('table1-instruction', 'style'),
    [Input('table1', 'data')]
)
def update_instruction_text_style(data):
    if data:
        return {'color': '#3498db', 'fontSize': '14px', 'marginBottom': '10px', 'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    [Output('table1', 'data'),
     Output('table1', 'columns'),
     Output('table1', 'style_data_conditional'),
     Output('table2', 'data'),
     Output('table2', 'columns'),
     Output('table2', 'style_data_conditional'),
     Output('xml-ld-output', 'children'),
     Output('button-group', 'style'),
     Output('table1-instruction', 'children'),
     Output('json-ld-output', 'children'),
     Output('table-switch-button', 'style'),
     Output('include-metadata', 'style'),
     Output('upload-data', 'contents')],
    [Input('upload-data', 'contents'),
     Input('table2', 'selected_rows'),
     Input('include-metadata', 'value'),
     Input('table2', 'data')],
    [State('upload-data', 'filename')]
)
def combined_callback(contents, selected_rows, include_metadata, table2_data, filename):
    global df, df_meta
    
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Handle metadata toggle separately
    if trigger == 'include-metadata' and 'df' in globals():
        try:
            # Debug logging
            print("=== Debug Information ===")
            print(f"Include metadata: {include_metadata}")
            
            # Get and log identifiers
            identifiers = [row['name'] for row in table2_data if row.get('var_type') == 'identifier'] if table2_data else []
            print(f"Identifiers: {identifiers}")
            
            # Get and log data subset
            data_subset = df.head(5) if include_metadata else df.head(0)
            print(f"Data subset shape: {data_subset.shape}")
            print(f"Data subset columns: {data_subset.columns.tolist()}")
            
            # Log df_meta attributes
            if hasattr(df_meta, 'identifier_vars'):
                print(f"df_meta.identifier_vars before: {df_meta.identifier_vars}")
                df_meta.identifier_vars = identifiers
                print(f"df_meta.identifier_vars after: {df_meta.identifier_vars}")
            
            # Generate XML with detailed error handling
            try:
                xml_data = generate_complete_xml_with_keys(
                    data_subset, 
                    df_meta, 
                    vars=identifiers,
                    spssfile=filename
                )
                print("XML generation successful")
            except Exception as e:
                print(f"XML generation error: {str(e)}")
                import traceback
                print(traceback.format_exc())
                xml_data = "Error generating XML"

            # Generate JSON-LD with detailed error handling
            try:
                json_ld_data = generate_complete_json_ld(
                    data_subset, 
                    df_meta,
                    spssfile=filename
                )
                print("JSON-LD generation successful")
            except Exception as e:
                print(f"JSON-LD generation error: {str(e)}")
                import traceback
                print(traceback.format_exc())
                json_ld_data = "Error generating JSON-LD"

            print("=== End Debug Information ===")

            instruction_text = f"The table below shows the first 5 rows from the dataset '{filename}'. The generated XML and JSON-LD output will {'include' if include_metadata else 'not include'} any data rows."
            
            return (
                dash.no_update,  # table1 data
                dash.no_update,  # table1 columns
                dash.no_update,  # table1 style
                dash.no_update,  # table2 data
                dash.no_update,  # table2 columns
                dash.no_update,  # table2 style
                xml_data,        # xml output
                dash.no_update,  # button group style
                instruction_text,# table1 instruction
                json_ld_data,    # json output
                dash.no_update,  # table switch button style
                dash.no_update,  # include metadata style
                dash.no_update   # upload contents
            )
            
        except Exception as e:
            print(f"Callback error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Return error state
            return [dash.no_update] * 13

    # Handle file upload (both initial and subsequent)
    if trigger == 'upload-data' and contents is not None:
        try:
            # Clear previous data
            if 'df_meta' in globals():
                df_meta.measure_vars = []
                df_meta.identifier_vars = []
                df_meta.attribute_vars = []
            
            # Reset lists.txt
            with open('lists.txt', 'w') as f:
                f.write("Measures: []\n")
                f.write("Identifiers: []\n")
                f.write("Attributes: []\n")

            # Process the uploaded file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_file:
                tmp_file.write(decoded)
                tmp_filename = tmp_file.name

            if '.dta' in tmp_filename or '.sav' in tmp_filename:
                df, df_meta, file_name, n_rows = read_sav(tmp_filename)
                df2 = create_variable_view2(df_meta) if '.dta' in tmp_filename else create_variable_view(df_meta)
                
                # Initialize with empty classifications
                df_meta.measure_vars = []
                df_meta.identifier_vars = []
                df_meta.attribute_vars = []

                # Prepare table data
                columns1 = [{"name": i, "id": i} for i in df.columns]
                columns2 = [
                    {
                        "name": "Type",
                        "id": "var_type",
                        "presentation": "dropdown"
                    }
                ] + [{"name": i, "id": i} for i in df2.columns]
                
                conditional_styles1 = style_data_conditional(df)
                conditional_styles2 = style_data_conditional(df2)

                # Add the var_type column to df2 with default value
                df2['var_type'] = 'measure'
                table2_data = df2.to_dict('records')

                # Generate initial XML and JSON-LD
                data_subset = df.head(5) if include_metadata else df.head(0)
                xml_data = generate_complete_xml_with_keys(
                    data_subset, 
                    df_meta, 
                    vars=[],
                    spssfile=filename
                )
                json_ld_data = generate_complete_json_ld(
                    data_subset, 
                    df_meta,
                    spssfile=filename
                )

                instruction_text = f"The table below shows the first 5 rows from the dataset '{filename}'."

                # Clean up temp file
                os.unlink(tmp_filename)

                return (
                    df.to_dict('records'),
                    columns1,
                    conditional_styles1,
                    table2_data,
                    columns2,
                    conditional_styles2,
                    xml_data,
                    {'display': 'block'},
                    instruction_text,
                    json_ld_data,
                    {'display': 'block'},
                    {'display': 'inline-block', 'marginLeft': '15px', 'color': colors['secondary']},
                    None  # Clear the upload contents
                )

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return [], [], [], [], [], [], f"Error: {str(e)}", {'display': 'none'}, "", "", {'display': 'none'}, {'display': 'none'}, None

    # When table2 data changes (dropdown selections change)
    if trigger == 'table2' and table2_data and 'df' in globals():  # Check if df exists
        # Update classifications based on dropdown selections
        measures = [row['name'] for row in table2_data if row.get('var_type') == 'measure']
        identifiers = [row['name'] for row in table2_data if row.get('var_type') == 'identifier']
        attributes = [row['name'] for row in table2_data if row.get('var_type') == 'attribute']
        
        if 'df_meta' in globals():
            df_meta.measure_vars = measures
            df_meta.identifier_vars = identifiers
            df_meta.attribute_vars = attributes
            
        # Update lists.txt with new classifications
        with open('lists.txt', 'w') as f:
            f.write(f"Measures: {measures}\n")
            f.write(f"Identifiers: {identifiers}\n")
            f.write(f"Attributes: {attributes}\n")
            
        # Generate new XML and JSON-LD with updated classifications
        data_subset = df.head(5) if include_metadata else df.head(0)
        xml_data = generate_complete_xml_with_keys(
            data_subset, 
            df_meta, 
            vars=identifiers,
            spssfile=filename
        )
        json_ld_data = generate_complete_json_ld(
            data_subset, 
            df_meta,
            spssfile=filename
        )
        
        # Return all outputs with updated XML and JSON
        return (
            dash.no_update,  # table1 data
            dash.no_update,  # table1 columns
            dash.no_update,  # table1 style
            table2_data,     # table2 data
            dash.no_update,  # table2 columns
            dash.no_update,  # table2 style
            xml_data,        # xml output
            dash.no_update,  # button group style
            dash.no_update,  # table1 instruction
            json_ld_data,    # json output
            dash.no_update,  # table switch button style
            dash.no_update,  # include metadata style
            dash.no_update   # upload contents
        )

    if not contents:
        return [], [], [], [], [], [], "", {'display': 'none'}, "", "", {'display': 'none'}, {'display': 'none'}, dash.no_update

    try:
        print("Step 1: Starting file processing")
        # Decode and save uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file_extension = os.path.splitext(filename)[1]

        print("Step 2: Creating temp file")
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp_file:
            tmp_file.write(decoded)
            tmp_filename = tmp_file.name

        print("Step 3: About to read file")
        # Read data based on file type
        if '.dta' in tmp_filename or '.sav' in tmp_filename:
            print("Step 4: Reading SAV/DTA file")
            df, df_meta, file_name, n_rows = read_sav(tmp_filename)
            print("Step 5: File read complete")
            print(f"df_meta exists: {df_meta is not None}")
            df2 = create_variable_view2(df_meta) if '.dta' in tmp_filename else create_variable_view(df_meta)
            
            # Initialize the classification attributes
            df_meta.measure_vars = df_meta.column_names  # Default all to measures
            df_meta.identifier_vars = []
            df_meta.attribute_vars = []
            
            # Try to load existing classifications from lists.txt if it exists
            try:
                with open('lists.txt', 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('Measures:'):
                            df_meta.measure_vars = eval(line.split(':', 1)[1].strip())
                        elif line.startswith('Identifiers:'):
                            df_meta.identifier_vars = eval(line.split(':', 1)[1].strip())
                        elif line.startswith('Attributes:'):
                            df_meta.attribute_vars = eval(line.split(':', 1)[1].strip())
            except FileNotFoundError:
                pass  # Use the defaults if file doesn't exist
        else:
            raise ValueError("Unsupported file type")

        # Prepare table data
        columns1 = [{"name": i, "id": i} for i in df.columns]
        columns2 = [
            {
                "name": "Type",
                "id": "var_type",
                "presentation": "dropdown"
            }
        ] + [{"name": i, "id": i} for i in df2.columns]
        conditional_styles1 = style_data_conditional(df)
        conditional_styles2 = style_data_conditional(df2)

        # Add the var_type column to df2 with default value
        df2['var_type'] = 'measure'
        
        # Convert df2 to records for the table
        table2_data = df2.to_dict('records')

        # Get selected variables
        vars = []
        if selected_rows and table2_data:
            vars = [table2_data[row_index]["name"] for row_index in selected_rows]

        # Modify this section to properly handle include_metadata
        if trigger == 'include-metadata' or trigger == 'upload-data':
            if include_metadata:
                data_subset = df.head(5)
                instruction_text = f"The table below shows the first 5 rows from the dataset '{filename}'. The generated XML and JSON-LD output will include these 5 rows."
            else:
                data_subset = df.head(0)
                instruction_text = f"The table below shows the first 5 rows from the dataset '{filename}'. The generated XML and JSON-LD output will not include any data rows."
        else:
            # For other triggers, maintain the current state
            data_subset = df.head(5) if include_metadata else df.head(0)
            instruction_text = f"The table below shows the first 5 rows from the dataset '{filename}'. The generated XML and JSON-LD output will {'include' if include_metadata else 'not include'} any data rows."

        # Generate outputs with the conditional data selection
        xml_data = generate_complete_xml_with_keys(
            data_subset, 
            df_meta, 
            vars=vars,
            spssfile=filename
        )

        json_ld_data = generate_complete_json_ld(
            data_subset, 
            df_meta,
            spssfile=filename
        )

        # Add debug logging for variable types
        if table2_data:
            measures = [row['name'] for row in table2_data if row.get('var_type') == 'measure']
            identifiers = [row['name'] for row in table2_data if row.get('var_type') == 'identifier']
            attributes = [row['name'] for row in table2_data if row.get('var_type') == 'attribute']
            
            # Save to lists.txt
            with open('lists.txt', 'w') as f:
                f.write(f"Measures: {measures}\n")
                f.write(f"Identifiers: {identifiers}\n")
                f.write(f"Attributes: {attributes}\n")

        return (df.to_dict('records'), columns1, conditional_styles1, 
                table2_data, columns2, conditional_styles2, 
                xml_data, {'display': 'block'}, 
                instruction_text, json_ld_data,
                {'display': 'block'},
                {'display': 'inline-block', 'marginLeft': '15px', 'color': colors['secondary']},
                None  # Clear the upload contents
            )

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], [], [], [], [], [], "An error occurred while processing the file.", {'display': 'none'}, "", "", {'display': 'none'}, {'display': 'none'}, None

    finally:
        if 'tmp_filename' in locals():
            os.remove(tmp_filename)

# reset selected rows in datatable
@app.callback(
    Output('table2', 'selected_rows'),
    [Input('upload-data', 'contents')]
)
def reset_selected_rows(contents):
    if contents is not None:
        return []  # Return an empty list to have no selection by default
    else:
        raise dash.exceptions.PreventUpdate

@app.callback(
    [Output("table1-col", "style"),
     Output("table2-col", "style")],
    [Input("table-switch-button", "n_clicks")],
    [State("table1-col", "style"),
     State("table2-col", "style")]
)
def switch_table(n_clicks, style1, style2):
    if n_clicks is None:
        return style1, style2

    if n_clicks % 2 == 0:
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}

@app.callback(
    Output('download-xml', 'data'),
    [Input('btn-download', 'n_clicks')],
    [State('xml-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_xml(n_clicks, xml_data, filename):
    if n_clicks is None or filename is None or xml_data is None:
        raise dash.exceptions.PreventUpdate

    download_filename = os.path.splitext(filename)[0] + '.xml'
    return dict(content=xml_data, filename=download_filename, type='text/xml')

@app.callback(
    Output('download-json', 'data'),
    [Input('btn-download-json', 'n_clicks')],
    [State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_json(n_clicks, json_data, filename):
    if n_clicks is None or filename is None or json_data is None:
        raise dash.exceptions.PreventUpdate

    download_filename = os.path.splitext(filename)[0] + '.jsonld'
    return dict(content=json_data, filename=download_filename, type='application/json')

@app.callback(
    [Output('xml-ld-output', 'style'),
     Output('json-ld-output', 'style')],
    [Input('btn-download', 'n_clicks'),
     Input('btn-download-json', 'n_clicks')],
    [State('xml-ld-output', 'style'),
     State('json-ld-output', 'style')]
)
def toggle_output_display(xml_clicks, json_clicks, xml_style, json_style):
    ctx = dash.callback_context
    
    base_style = {
        'whiteSpace': 'pre',
        'wordBreak': 'break-all',
        'color': colors['text'],
        'backgroundColor': colors['background'],
        'marginTop': '10px',
        'maxHeight': '300px',
        'overflowY': 'scroll',
        'fontSize': '14px',
    }
    
    if not ctx.triggered:
        # Default state: show XML, hide JSON
        return {**base_style, 'display': 'block'}, {**base_style, 'display': 'none'}
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-download':
        return {**base_style, 'display': 'block'}, {**base_style, 'display': 'none'}
    elif button_id == 'btn-download-json':
        return {**base_style, 'display': 'none'}, {**base_style, 'display': 'block'}
    
    # Fallback to default state
    return {**base_style, 'display': 'block'}, {**base_style, 'display': 'none'}

# Add new callback for the download button
@app.callback(
    Output('download-active', 'data'),
    [Input('btn-download-active', 'n_clicks')],
    [State('xml-ld-output', 'style'),
     State('xml-ld-output', 'children'),
     State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_active_content(n_clicks, xml_style, xml_content, json_content, filename):
    if n_clicks is None or filename is None:
        raise dash.exceptions.PreventUpdate
    
    # Check which content is currently visible by checking XML's display style
    # (since we know one is always visible and they're mutually exclusive)
    is_xml_visible = xml_style.get('display') == 'block'
    
    if is_xml_visible:
        download_filename = os.path.splitext(filename)[0] + '.xml'
        return dict(content=xml_content, filename=download_filename, type='text/xml')
    else:
        download_filename = os.path.splitext(filename)[0] + '.jsonld'
        return dict(content=json_content, filename=download_filename, type='application/json')

if __name__ == '__main__':
    # Get the PORT from environment variables and use 8000 as fallback
    port = int(os.getenv('PORT', 8000))
    # Run the server
    server.run(host='0.0.0.0', port=port)

    # test