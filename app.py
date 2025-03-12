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
from DDICDI_converter_JSONLD_incremental import (
    generate_complete_json_ld,
    MemoryManager
)
from spss_import import read_sav, create_variable_view, create_variable_view2
from app_content import markdown_text, colors, style_dict, table_style, header_dict, app_title, app_description, about_text
from dash.exceptions import PreventUpdate
import rdflib
from rdflib import Graph

# Configuration parameters
MAX_ROWS_TO_PROCESS = 5  # Maximum number of rows to process by default
PREVIEW_ROWS = 5  # Number of rows to show in the data preview table
CHUNK_SIZE = 500  # Size of chunks to process when handling larger datasets

# Define the namespaces, DDI
nsmap = {
    'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/',
    'r': 'ddi:reusable:3_3'  # Replace with the actual URI for the 'r' namespace
}
agency = 'int.example'

# Define the Flask server
server = Flask(__name__)

# Define the Dash app and associate it with the Flask server
app = dash.Dash(__name__, server=server, external_stylesheets=[
    dbc.themes.LITERA,
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
])

# Define a helper function to always hide the N-Triples button in the UI
def get_button_group_style(visible=False):
    """Helper function to get the button group style while ensuring N-Triples button is always hidden"""
    return {'display': 'block' if visible else 'none', 'gap': '10px', 'flexDirection': 'row'}

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

about_section = dbc.Card([
    dbc.CardBody([
        dcc.Markdown(about_text, 
            link_target="_blank",
            className="card-text"),
        html.Div([
            html.Img(
                src=app.get_asset_url('petals_logos.2.0-01.webp'),
                style={
                    'height': '50px',
                    'width': 'auto',
                    'marginRight': '20px',
                    'opacity': '0.8'
                }
            ),
            html.Img(
                src=app.get_asset_url('FAIR-IMPACT.png'),
                style={
                    'height': '40px',
                    'width': 'auto',
                    'opacity': '0.8'
                }
            )
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'marginTop': '20px',
            'borderTop': f'1px solid {colors["border"]}',
            'paddingTop': '20px'
        })
    ]),
], className="mt-4", style={
    'fontFamily': "'Inter', sans-serif",
    'fontSize': '15px',
    'letterSpacing': '-0.01em'
})

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
                            html.Div("Please select variable role. Identifiers are used for the PrimaryKey to uniquely identify the records.",
                                     id="table2-instruction",
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
                                        "name": "Select role",
                                        "id": "roles",
                                        "presentation": "dropdown",
                                        "editable": True
                                    },
                                    {
                                        "name": "name",
                                        "id": "name",
                                        "editable": False
                                    },
                                    {
                                        "name": "label",
                                        "id": "label",
                                        "editable": False
                                    },
                                    {
                                        "name": "format",
                                        "id": "format",
                                        "editable": False
                                    },
                                    {
                                        "name": "measure",
                                        "id": "measure",
                                        "editable": False
                                    }
                                ],
                                dropdown={
                                    'roles': {
                                        'options': [
                                            {'label': 'Measure', 'value': 'measure'},
                                            {'label': 'Identifier', 'value': 'identifier'},
                                            {'label': 'Attribute', 'value': 'attribute'},
                                            {'label': 'Measure, Identifier', 'value': 'measure,identifier'},
                                            {'label': 'Measure, Attribute', 'value': 'measure,attribute'},
                                            {'label': 'Identifier, Attribute', 'value': 'identifier,attribute'},
                                            {'label': 'Measure, Identifier, Attribute', 'value': 'measure,identifier,attribute'}
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
                                    'if': {'column_id': ['roles']},
                                    'textAlign': 'center',
                                    'minWidth': '100px',
                                    'backgroundColor': 'rgba(33, 150, 243, 0.15)',  # Same as #2196f3 but with 15% opacity
                                    'color': colors['primary'],
                                    'fontWeight': '500'
                                }],
                                style_data_conditional=[{
                                    'if': {'column_id': ['roles']},
                                    'cursor': 'pointer',
                                    'backgroundColor': 'white',
                                    'border': f'1px solid {colors["primary"]}',
                                    'color': colors['primary']
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
                    dbc.Button([html.I(className="fas fa-download mr-2"), 'JSON-LD'], 
                              id='btn-download-json', 
                              color="primary", 
                              className="mr-1"),
                    # N-Triples button hidden but still in the DOM for callback functionality
                    dbc.Button([html.I(className="fas fa-download mr-2"), 'N-Triples'], 
                              id='btn-download-nt', 
                              color="info", 
                              className="mr-1",
                              style={'display': 'none'}),
                ],
                style=get_button_group_style(visible=False),  # Use helper function
                id='button-group',
                className="shadow-sm"
            ),
            # Add switch using dbc.Switch
            dbc.Switch(
                id="include-metadata",
                label=f"Include data rows (limited to {MAX_ROWS_TO_PROCESS} rows by default)",
                value=False,
                style={
                    'display': 'inline-block',
                    'marginLeft': '15px',
                    'color': colors['secondary']
                }
            ),
            # Add a switch for processing all rows (permanently hidden but still functional)
            dbc.Switch(
                id="process-all-rows",
                label=f"Process ALL rows in chunks of {CHUNK_SIZE} (may be slow for large datasets)",
                value=False,
                style={
                    'display': 'none'  # Permanently hidden
                }
            ),
            # Add a warning message about large datasets
            html.Div(
                id="performance-warning",
                style={
                    'color': '#e74c3c',
                    'fontSize': '13px',
                    'marginTop': '5px',
                    'display': 'none'
                }
            ),
            dcc.Download(id='download-json'),
            dcc.Download(id='download-nt'),
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
                                link_target="_blank",
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
            # Add a div for progress information with loading spinner
            html.Div([
                html.Div(
                    id="progress-spinner",
                    className="spinner-border text-primary",
                    style={
                        'display': 'none',
                        'width': '2rem', 
                        'height': '2rem',
                        'marginRight': '10px'
                    }
                ),
                html.Div(
                    id="progress-info",
                    style={
                        'display': 'none',
                        'color': colors['primary'],
                        'fontFamily': "'Inter', sans-serif",
                        'fontSize': '14px',
                        'margin': '10px 0',
                        'fontWeight': '500',
                        'padding': '8px',
                        'borderRadius': '4px',
                        'backgroundColor': '#e8f4f8',
                        'textAlign': 'center',
                        'flex': '1'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'width': '100%'}),
            # Add hidden divs for storing intermediate data
            dcc.Store(id='processing-start-time'),
            dcc.Store(id='processing-data', data={'status': 'idle'}),
            dcc.Store(id='full-json-store'),
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
    [Output('table1-instruction', 'style'),
     Output('table2-instruction', 'style')],
    [Input('table1', 'data')]
)
def update_instruction_text_style(data):
    if data:
        instruction_style = {
            'color': colors['secondary'], 
            'fontSize': '14px', 
            'marginBottom': '10px', 
            'fontFamily': "'Inter', sans-serif",
            'display': 'block'
        }
        return instruction_style, instruction_style
    else:
        return {'display': 'none'}, {'display': 'none'}

# Modify the truncate_for_display function to ensure it doesn't affect the original JSON
def truncate_for_display(json_str, max_length=500000, include_metadata=False):
    """
    Truncates JSON string for display if it's too large and include_metadata is True.
    Returns the truncated string and a boolean indicating if truncation occurred.
    """
    # Only truncate if include_metadata is True
    if include_metadata and json_str and len(json_str) > max_length:
        # Find the last complete JSON object or array that fits
        truncated = json_str[:max_length]
        # Try to find the last complete object
        last_brace = max(truncated.rfind('}'), truncated.rfind(']'))
        if last_brace > 0:
            truncated = truncated[:last_brace+1]
        
        # Add indicator that content was truncated
        message = "\n\n... Output truncated for display. Full data available via download button."
        return truncated + message, True
    return json_str, False

# Modify the combined_callback to use truncation for display
@app.callback(
    [Output('table1', 'data'),
     Output('table1', 'columns'),
     Output('table1', 'style_data_conditional'),
     Output('table2', 'data'),
     Output('table2', 'columns'),
     Output('table2', 'style_data_conditional'),
     Output('button-group', 'style'),
     Output('table1-instruction', 'children'),
     Output('table2-instruction', 'children'),
     Output('json-ld-output', 'children'),
     Output('table-switch-button', 'style'),
     Output('include-metadata', 'style'),
     Output('upload-data', 'contents'),
     Output('full-json-store', 'data')],  # Add this new output
    [Input('upload-data', 'contents'),
     Input('table2', 'selected_rows'),
     Input('include-metadata', 'value'),
     Input('table2', 'data'),
     Input('process-all-rows', 'value')],
    [State('upload-data', 'filename')]
)
def combined_callback(contents, selected_rows, include_metadata, table2_data, process_all_rows, filename):
    global df, df_meta
    
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Handle metadata toggle separately
    if trigger in ['include-metadata', 'process-all-rows'] and 'df' in globals():
        try:
            # Debug logging
            print("=== Debug Information ===")
            print(f"Include metadata: {include_metadata}")
            print(f"Process all rows: {process_all_rows}")
            
            # Get and log identifiers
            measures = []
            identifiers = []
            attributes = []
            
            # Process the comma-separated roles for each variable
            for row in table2_data:
                roles = row.get('roles', '').split(',') if row.get('roles') else []
                if 'measure' in roles:
                    measures.append(row['name'])
                if 'identifier' in roles:
                    identifiers.append(row['name'])
                if 'attribute' in roles:
                    attributes.append(row['name'])
            print(f"Identifiers: {identifiers}")
            
            # Get and log data subset
            data_subset = df if include_metadata else df.head(0)
            print(f"Data subset shape: {data_subset.shape}")
            print(f"Data subset columns: {data_subset.columns.tolist()}")
            
            # Log df_meta attributes
            if hasattr(df_meta, 'identifier_vars'):
                print(f"df_meta.identifier_vars before: {df_meta.identifier_vars}")
                df_meta.identifier_vars = identifiers
                print(f"df_meta.identifier_vars after: {df_meta.identifier_vars}")
            
            # Generate JSON-LD with detailed error handling
            try:
                # Determine optimal chunk size for large datasets
                dynamic_chunk_size = CHUNK_SIZE
                if process_all_rows and len(df) > CHUNK_SIZE:
                    try:
                        # Try to optimize chunk size based on available memory
                        dynamic_chunk_size = MemoryManager.optimize_chunk_size(df, df_meta)
                        print(f"Optimized chunk size: {dynamic_chunk_size} rows (based on available memory)")
                    except Exception as e:
                        print(f"Warning: Could not optimize chunk size, using default: {e}")
                        dynamic_chunk_size = CHUNK_SIZE
                
                json_ld_data = generate_complete_json_ld(
                    data_subset, 
                    df_meta,
                    spssfile=filename,
                    chunk_size=dynamic_chunk_size,
                    process_all_rows=process_all_rows,
                    max_rows=MAX_ROWS_TO_PROCESS
                )
                print("JSON-LD generation successful")
            except Exception as e:
                print(f"JSON-LD generation error: {str(e)}")
                import traceback
                print(traceback.format_exc())
                json_ld_data = "Error generating JSON-LD"

            print("=== End Debug Information ===")

            # Modify this section to properly handle include_metadata
            if trigger == 'include-metadata' or trigger == 'upload-data':
                if include_metadata:
                    data_subset = df
                    if process_all_rows:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include ALL {len(df)} rows."
                    elif len(df) > MAX_ROWS_TO_PROCESS:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include up to {MAX_ROWS_TO_PROCESS} rows due to performance limitations."
                    else:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include all {len(df)} rows."
                else:
                    data_subset = df.head(0)
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will not include any data rows."
            else:
                # For other triggers, maintain the current state
                data_subset = df if include_metadata else df.head(0)
                if include_metadata:
                    if process_all_rows:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include ALL {len(df)} rows."
                    elif len(df) > MAX_ROWS_TO_PROCESS:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include up to {MAX_ROWS_TO_PROCESS} rows due to performance limitations."
                    else:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include all {len(df)} rows."
                else:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will not include any data rows."
            
            # Create instruction text for table2 (column view)
            instruction_text2 = f"The table below shows all {len(df.columns)} columns from the dataset '{filename}'. Please select the appropriate role for each variable (column)."
            
            # Before returning, store the full JSON and truncate for display
            if json_ld_data and json_ld_data != "Error generating JSON-LD":
                # Store the full JSON output for download BEFORE truncation
                full_json = json_ld_data
                # Truncate for display only if include_metadata is true
                truncated_json, was_truncated = truncate_for_display(json_ld_data, include_metadata=include_metadata)
                
                return (
                    dash.no_update,  # table1 data
                    dash.no_update,  # table1 columns
                    dash.no_update,  # table1 style
                    dash.no_update,  # table2 data
                    dash.no_update,  # table2 columns
                    dash.no_update,  # table2 style
                    get_button_group_style(visible=True),  # Use helper function
                    instruction_text1, # table1 instruction
                    instruction_text2, # table2 instruction
                    truncated_json,    # json output for display
                    {'display': 'block'},
                    {'display': 'inline-block', 'marginLeft': '15px', 'color': colors['secondary']},
                    None,  # Clear the upload contents
                    full_json  # full JSON for download
                )
            
        except Exception as e:
            print(f"Callback error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Return error state
            return [dash.no_update] * 14

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
                        "name": "Select role",
                        "id": "roles",
                        "presentation": "dropdown",
                        "editable": True
                    },
                    {
                        "name": "name",
                        "id": "name",
                        "editable": False
                    },
                    {
                        "name": "label",
                        "id": "label",
                        "editable": False
                    },
                    {
                        "name": "format",
                        "id": "format",
                        "editable": False
                    },
                    {
                        "name": "measure",
                        "id": "measure",
                        "editable": False
                    }
                ] + [{"name": i, "id": i} for i in df2.columns]
                
                conditional_styles1 = style_data_conditional(df)
                conditional_styles2 = style_data_conditional(df2)

                # Add the roles column to df2 with default values (measure)
                df2['roles'] = 'measure'
                table2_data = df2.to_dict('records')

                # Generate only JSON-LD initially
                # Determine optimal chunk size for large datasets
                dynamic_chunk_size = CHUNK_SIZE
                if process_all_rows and len(df) > CHUNK_SIZE:
                    try:
                        # Try to optimize chunk size based on available memory
                        dynamic_chunk_size = MemoryManager.optimize_chunk_size(df, df_meta)
                        print(f"Optimized chunk size: {dynamic_chunk_size} rows (based on available memory)")
                    except Exception as e:
                        print(f"Warning: Could not optimize chunk size, using default: {e}")
                        dynamic_chunk_size = CHUNK_SIZE
                        
                data_subset = df if include_metadata else df.head(0)
                json_ld_data = generate_complete_json_ld(
                    data_subset, 
                    df_meta,
                    spssfile=filename,
                    chunk_size=dynamic_chunk_size,
                    process_all_rows=process_all_rows,
                    max_rows=MAX_ROWS_TO_PROCESS
                )

                if include_metadata:
                    if process_all_rows:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include ALL {len(df)} rows."
                    elif len(df) > MAX_ROWS_TO_PROCESS:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include up to {MAX_ROWS_TO_PROCESS} rows due to performance limitations."
                    else:
                        instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include all {len(df)} rows."
                else:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will not include any data rows."

                # Create instruction text for table2 (column view)
                instruction_text2 = f"The table below shows all {len(df.columns)} columns from the dataset '{filename}'. Please select the appropriate role for each variable (column)."

                # Clean up temp file
                os.unlink(tmp_filename)

                # Before returning, store the full JSON and truncate for display
                if json_ld_data and json_ld_data != "Error generating JSON-LD":
                    # Store the full JSON output for download BEFORE truncation
                    full_json = json_ld_data
                    # Truncate for display only if include_metadata is true
                    truncated_json, was_truncated = truncate_for_display(json_ld_data, include_metadata=include_metadata)
                    
                    return (
                        df.head(PREVIEW_ROWS).to_dict('records'),  # Only show PREVIEW_ROWS in the table
                        columns1,
                        conditional_styles1,
                        table2_data,
                        columns2,
                        conditional_styles2,
                        get_button_group_style(visible=True),  # Use helper function
                        instruction_text1,
                        instruction_text2,
                        truncated_json,    # json output for display
                        {'display': 'block'},
                        {'display': 'inline-block', 'marginLeft': '15px', 'color': colors['secondary']},
                        None,  # Clear the upload contents
                        full_json  # full JSON for download
                    )

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return [], [], [], [], [], [], get_button_group_style(visible=False), "", "", "", {'display': 'none'}, {'display': 'none'}, None, None

    # When table2 data changes (dropdown selections change)
    if trigger == 'table2' and table2_data and 'df' in globals():  # Check if df exists
        # Update classifications based on multi-role selections
        measures = []
        identifiers = []
        attributes = []
        
        # Process the comma-separated roles for each variable
        for row in table2_data:
            roles = row.get('roles', '').split(',') if row.get('roles') else []
            if 'measure' in roles:
                measures.append(row['name'])
            if 'identifier' in roles:
                identifiers.append(row['name'])
            if 'attribute' in roles:
                attributes.append(row['name'])
        
        if 'df_meta' in globals():
            df_meta.measure_vars = measures
            df_meta.identifier_vars = identifiers
            df_meta.attribute_vars = attributes
            
        # Update lists.txt with new classifications
        with open('lists.txt', 'w') as f:
            f.write(f"Measures: {measures}\n")
            f.write(f"Identifiers: {identifiers}\n")
            f.write(f"Attributes: {attributes}\n")
        
        # Determine optimal chunk size for large datasets
        dynamic_chunk_size = CHUNK_SIZE
        if process_all_rows and len(df) > CHUNK_SIZE:
            try:
                # Try to optimize chunk size based on available memory
                dynamic_chunk_size = MemoryManager.optimize_chunk_size(df, df_meta)
                print(f"Optimized chunk size: {dynamic_chunk_size} rows (based on available memory)")
            except Exception as e:
                print(f"Warning: Could not optimize chunk size, using default: {e}")
                dynamic_chunk_size = CHUNK_SIZE
        
        # Generate only JSON-LD with updated classifications
        data_subset = df if include_metadata else df.head(0)
        json_ld_data = generate_complete_json_ld(
            data_subset, 
            df_meta,
            spssfile=filename,
            chunk_size=dynamic_chunk_size,
            process_all_rows=process_all_rows,
            max_rows=MAX_ROWS_TO_PROCESS
        )
        
        # Return all outputs with updated JSON
        return (
            dash.no_update,  # table1 data
            dash.no_update,  # table1 columns
            dash.no_update,  # table1 style
            table2_data,     # table2 data
            dash.no_update,  # table2 columns
            dash.no_update,  # table2 style
            get_button_group_style(visible=True),  # Use helper function
            dash.no_update,  # table1 instruction
            dash.no_update,  # table2 instruction
            json_ld_data,    # json output
            {'display': 'block'},  # table switch button style
            {'display': 'inline-block', 'marginLeft': '15px', 'color': colors['secondary']},  # include metadata style
            dash.no_update,  # upload contents
            None  # full JSON store
        )

    if not contents:
        return [], [], [], [], [], [], get_button_group_style(visible=False), "", "", "", {'display': 'none'}, {'display': 'none'}, dash.no_update, None

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
            print("Reading file using read_sav") 
            df, df_meta, file_name, n_rows = read_sav(tmp_filename)
        else:
            raise ValueError(f"Unsupported file type. File must be .sav or .dta, got: {tmp_filename}")

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

        # Prepare table data
        columns1 = [{"name": i, "id": i} for i in df.columns]
        columns2 = [
            {
                "name": "Select role",
                "id": "roles",
                "presentation": "dropdown",
                "editable": True
            },
            {
                "name": "name",
                "id": "name",
                "editable": False
            },
            {
                "name": "label",
                "id": "label",
                "editable": False
            },
            {
                "name": "format",
                "id": "format",
                "editable": False
            },
            {
                "name": "measure",
                "id": "measure",
                "editable": False
            }
        ] + [{"name": i, "id": i} for i in df2.columns]
        conditional_styles1 = style_data_conditional(df)
        conditional_styles2 = style_data_conditional(df2)

        # Add the roles column to df2 with default values (measure)
        df2['roles'] = 'measure'
        
        # Convert df2 to records for the table
        table2_data = df2.to_dict('records')

        # Get selected variables
        vars = []
        if selected_rows and table2_data:
            vars = [table2_data[row_index]["name"] for row_index in selected_rows]

        # Modify this section to properly handle include_metadata
        if trigger == 'include-metadata' or trigger == 'upload-data':
            if include_metadata:
                data_subset = df
                if process_all_rows:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include ALL {len(df)} rows."
                elif len(df) > MAX_ROWS_TO_PROCESS:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include up to {MAX_ROWS_TO_PROCESS} rows due to performance limitations."
                else:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include all {len(df)} rows."
            else:
                data_subset = df.head(0)
                instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will not include any data rows."
        else:
            # For other triggers, maintain the current state
            data_subset = df if include_metadata else df.head(0)
            if include_metadata:
                if process_all_rows:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include ALL {len(df)} rows."
                elif len(df) > MAX_ROWS_TO_PROCESS:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include up to {MAX_ROWS_TO_PROCESS} rows due to performance limitations."
                else:
                    instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will include all {len(df)} rows."
            else:
                instruction_text1 = f"The table below shows the first {PREVIEW_ROWS} of {len(df)} rows from the dataset '{filename}'. The generated JSON-LD output will not include any data rows."

        # Create instruction text for table2 (column view)
        instruction_text2 = f"The table below shows all {len(df.columns)} columns from the dataset '{filename}'. Please select the appropriate role for each variable (column)."

        # Generate only JSON-LD with the conditional data selection
        # Determine optimal chunk size for large datasets
        dynamic_chunk_size = CHUNK_SIZE
        if process_all_rows and len(df) > CHUNK_SIZE:
            try:
                # Try to optimize chunk size based on available memory
                dynamic_chunk_size = MemoryManager.optimize_chunk_size(df, df_meta)
                print(f"Optimized chunk size: {dynamic_chunk_size} rows (based on available memory)")
            except Exception as e:
                print(f"Warning: Could not optimize chunk size, using default: {e}")
                dynamic_chunk_size = CHUNK_SIZE
                
        json_ld_data = generate_complete_json_ld(
            data_subset, 
            df_meta,
            spssfile=filename,
            chunk_size=dynamic_chunk_size,
            process_all_rows=process_all_rows,
            max_rows=MAX_ROWS_TO_PROCESS
        )

        # Add debug logging for variable types
        if table2_data:
            measures = [row['name'] for row in table2_data if row.get('role_measure') == True]
            identifiers = [row['name'] for row in table2_data if row.get('role_identifier') == True]
            attributes = [row['name'] for row in table2_data if row.get('role_attribute') == True]
            
            # Save to lists.txt
            with open('lists.txt', 'w') as f:
                f.write(f"Measures: {measures}\n")
                f.write(f"Identifiers: {identifiers}\n")
                f.write(f"Attributes: {attributes}\n")

        # Before returning, store the full JSON and truncate for display
        if json_ld_data and json_ld_data != "Error generating JSON-LD":
            # Store the full JSON output for download BEFORE truncation
            full_json = json_ld_data
            # Truncate for display only if include_metadata is true
            truncated_json, was_truncated = truncate_for_display(json_ld_data, include_metadata=include_metadata)
            
            return (df.head(PREVIEW_ROWS).to_dict('records'), columns1, conditional_styles1, 
                    table2_data, columns2, conditional_styles2, 
                    get_button_group_style(visible=True),  # Use helper function
                    instruction_text1, instruction_text2, truncated_json,
                    {'display': 'block'},
                    {'display': 'inline-block', 'marginLeft': '15px', 'color': colors['secondary']},
                    None,  # Clear the upload contents
                    full_json  # full JSON for download
                )

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], [], [], [], [], [], get_button_group_style(visible=False), "", "", "", {'display': 'none'}, {'display': 'none'}, None, None

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
    Output('download-json', 'data'),
    [Input('btn-download-json', 'n_clicks')],
    [State('full-json-store', 'data'),
     State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_json(n_clicks, full_json, displayed_json, filename):
    if n_clicks is None:
        raise PreventUpdate
    
    if not n_clicks or (not full_json and not displayed_json):
        return None
    
    # Use the full JSON if available, otherwise use the displayed JSON
    # BUT - strip out any truncation message that might be present
    json_data = full_json if full_json else displayed_json
    
    # Remove the truncation message if it exists
    if isinstance(json_data, str) and "... Output truncated for display." in json_data:
        truncation_msg_pos = json_data.find("\n\n... Output truncated for display.")
        if truncation_msg_pos > 0:
            json_data = json_data[:truncation_msg_pos]
    
    if filename:
        download_filename = f"{os.path.splitext(filename)[0]}_DDICDI.jsonld"
    else:
        download_filename = "output_DDICDI.jsonld"
    
    return dict(content=json_data, filename=download_filename)

@app.callback(
    [Output('xml-ld-output', 'style'),
     Output('json-ld-output', 'style')],
    [Input('btn-download-json', 'n_clicks'),
     Input('btn-download-nt', 'n_clicks')],
    [State('xml-ld-output', 'style'),
     State('json-ld-output', 'style')]
)
def toggle_output_display(json_clicks, nt_clicks, xml_style, json_style):
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
    
    # Always hide XML, show JSON
    return {**base_style, 'display': 'none'}, {**base_style, 'display': 'block'}

@app.callback(
    Output('download-nt', 'data'),
    [Input('btn-download-nt', 'n_clicks')],
    [State('full-json-store', 'data'),
     State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_nt(n_clicks, full_json, displayed_json, filename):
    if n_clicks is None:
        raise PreventUpdate
    
    if not n_clicks or (not full_json and not displayed_json):
        return None
    
    # Use the full JSON if available, otherwise use the displayed JSON
    json_data = full_json if full_json else displayed_json
    
    # Remove the truncation message if it exists
    if isinstance(json_data, str) and "... Output truncated for display." in json_data:
        truncation_msg_pos = json_data.find("\n\n... Output truncated for display.")
        if truncation_msg_pos > 0:
            json_data = json_data[:truncation_msg_pos]
    
    try:
        # Create temporary files for the conversion process
        with tempfile.NamedTemporaryFile(suffix='.jsonld', delete=False, mode='w', encoding='utf-8') as temp_jsonld_file:
            temp_jsonld_file.write(json_data)
            temp_jsonld_path = temp_jsonld_file.name
        
        # Create a graph and parse the JSON-LD
        g = Graph()
        g.bind('sikt', 'https://sikt.no/cdi/RDF/')
        g.parse(temp_jsonld_path, format="json-ld")
        
        # Create new graph with transformed URIs
        new_g = Graph()
        for s, p, o in g:
            # Transform file:/// URIs to https://sikt.no/cdi/RDF/
            if str(s).startswith('file:///'):
                s = rdflib.URIRef('https://sikt.no/cdi/RDF/' + str(s).split('/')[-1])
            if str(o).startswith('file:///'):
                o = rdflib.URIRef('https://sikt.no/cdi/RDF/' + str(o).split('/')[-1])
            new_g.add((s, p, o))
        
        # Serialize to N-Triples format
        nt_data = new_g.serialize(format="nt", encoding="utf-8")
        
        # Create the download filename
        if filename:
            download_filename = f"{os.path.splitext(filename)[0]}_DDICDI.nt"
        else:
            download_filename = "output_DDICDI.nt"
        
        # Remove temporary files
        os.unlink(temp_jsonld_path)
        
        return dict(content=nt_data.decode('utf-8'), filename=download_filename)
    
    except Exception as e:
        print(f"Error converting to N-Triples: {str(e)}")
        # Ensure temporary files are removed in case of error
        if 'temp_jsonld_path' in locals():
            os.unlink(temp_jsonld_path)
        return None

# Add callback to show performance warning for large datasets
@app.callback(
    [Output('performance-warning', 'children'),
     Output('performance-warning', 'style')],
    [Input('table1', 'data'),
     Input('include-metadata', 'value'),
     Input('process-all-rows', 'value')]
)
def show_performance_warning(data, include_metadata, process_all_rows):
    # Only show warning if we have data and include_metadata is True
    if data and include_metadata and 'df' in globals():
        if len(df) > MAX_ROWS_TO_PROCESS:
            if process_all_rows:
                warning_text = f"Warning: Processing all {len(df)} rows in chunks of {CHUNK_SIZE}. This may take significantly longer. The generated JSON-LD will include all rows."
            else:
                warning_text = f"Warning: For performance reasons, only the first {MAX_ROWS_TO_PROCESS} rows will be included in the JSON-LD output."
            
            warning_style = {
                'display': 'block',
                'color': '#9B870C',
                'fontFamily': "'Inter', sans-serif",
                'fontSize': '14px',
                'margin': '10px 0',
                'fontWeight': '500',
                'padding': '8px',
                'borderRadius': '4px',
                'backgroundColor': '#fef9e7' if include_metadata and process_all_rows else '#fcf3cf'
            }
            return warning_text, warning_style
    
    # Default - no warning
    return "", {'display': 'none'}

# Add callback to show/hide the process-all-rows switch based on include-metadata
@app.callback(
    Output('process-all-rows', 'style'),
    [Input('include-metadata', 'value'),
     Input('table1', 'data')]
)
def toggle_process_all_rows(include_metadata, data):
    # Always keep the process-all-rows switch hidden
    return {'display': 'none'}

# Add callback to update the process-all-rows label with row count
@app.callback(
    Output('process-all-rows', 'label'),
    [Input('table1', 'data')]
)
def update_process_all_rows_label(data):
    if 'df' in globals() and len(df) > 0:
        return f"Process ALL {len(df)} rows in chunks of {CHUNK_SIZE} (may be slow for large datasets)"
    else:
        return f"Process ALL rows in chunks of {CHUNK_SIZE} (may be slow for large datasets)"

# Add callback for displaying processing status
@app.callback(
    [Output('progress-info', 'children'),
     Output('progress-info', 'style')],
    [Input('include-metadata', 'value'),
     Input('process-all-rows', 'value'),
     Input('table1', 'data'),
     Input('json-ld-output', 'children')],
    [State('processing-start-time', 'data')]
)
def update_progress_info(include_metadata, process_all_rows, data, json_output, start_time):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    base_style = {
        'display': 'block',
        'color': colors['primary'],
        'fontFamily': "'Inter', sans-serif",
        'fontSize': '14px',
        'margin': '10px 0',
        'fontWeight': '500',
        'padding': '8px',
        'borderRadius': '4px',
        'backgroundColor': '#e8f4f8',
        'textAlign': 'center'
    }
    
    # Only show progress message when metadata is being included
    if not include_metadata or not data or 'df' not in globals():
        return "", {'display': 'none'}
    
    # If JSON output is already generated, show completion message
    if json_output and json_output != "Error generating JSON-LD":
        base_style['backgroundColor'] = '#d4edda'  # Green background for success
        base_style['color'] = '#155724'  # Dark green text
        base_style['fontSize'] = '16px'  # Larger font
        base_style['fontWeight'] = '600'  # Bolder text
        base_style['boxShadow'] = '0 2px 5px rgba(0,0,0,0.1)'  # Add shadow for emphasis
        
        # Calculate processing time if we have a start time
        time_info = ""
        if start_time:
            import time
            end_time = time.time()
            processing_time = end_time - start_time
            if processing_time > 60:
                minutes = int(processing_time // 60)
                seconds = int(processing_time % 60)
                time_info = f" (completed in {minutes}m {seconds}s)"
            else:
                time_info = f" (completed in {processing_time:.1f}s)"
        
        # Add completion time to the message
        if 'df' in globals():
            row_count = len(df)
            if process_all_rows and row_count > MAX_ROWS_TO_PROCESS:
                return f"✅ COMPLETED: All {row_count} rows processed successfully!{time_info} JSON-LD is ready for download.", base_style
            elif include_metadata:
                rows_processed = min(row_count, MAX_ROWS_TO_PROCESS)
                return f"✅ COMPLETED: {rows_processed} rows processed successfully!{time_info} JSON-LD is ready for download.", base_style
        
        return f"✅ COMPLETED: Processing finished!{time_info} JSON-LD is ready for download.", base_style
    
    # If there was an error, show error message
    if json_output == "Error generating JSON-LD":
        base_style['backgroundColor'] = '#f8d7da'  # Red background for error
        base_style['color'] = '#721c24'  # Dark red text
        return "❌ Error: Processing failed. Please try again or check the logs.", base_style
    
    # If process_all_rows is True and we have a lot of data, show detailed message
    if process_all_rows and 'df' in globals() and len(df) > MAX_ROWS_TO_PROCESS:
        # Calculate actual chunk size (it might be dynamic)
        try:
            actual_chunk_size = MemoryManager.optimize_chunk_size(df, df_meta)
        except:
            actual_chunk_size = CHUNK_SIZE
            
        total_chunks = (len(df) + actual_chunk_size - 1) // actual_chunk_size
        return f"⏳ Processing {len(df)} rows in {total_chunks} chunks of ~{actual_chunk_size} rows. Please wait...", base_style
    
    # Default processing message
    return "⏳ Generating JSON-LD... Please wait...", base_style

# Add callback to control the loading spinner
@app.callback(
    Output('progress-spinner', 'style'),
    [Input('include-metadata', 'value'),
     Input('process-all-rows', 'value'),
     Input('json-ld-output', 'children')]
)
def update_spinner(include_metadata, process_all_rows, json_output):
    spinner_style = {
        'width': '2rem', 
        'height': '2rem',
        'marginRight': '10px'
    }
    
    # Only show spinner when metadata is being included and processing is not complete
    if include_metadata and (json_output is None or json_output == "" or json_output == "Error generating JSON-LD"):
        spinner_style['display'] = 'inline-block'
    else:
        spinner_style['display'] = 'none'
    
    return spinner_style

# Callback to update the processing start time
@app.callback(
    Output('processing-start-time', 'data'),
    [Input('include-metadata', 'value'),
     Input('process-all-rows', 'value')]
)
def update_processing_start_time(include_metadata, process_all_rows):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Only update timestamp when one of these toggles is activated
    if trigger in ['include-metadata', 'process-all-rows'] and include_metadata:
        import time
        return time.time()
    
    return dash.no_update

# Update the highlight_download_button callback to indicate when data is truncated
@app.callback(
    [Output('btn-download-json', 'style'),
     Output('btn-download-nt', 'style')],
    [Input('json-ld-output', 'children'),
     Input('full-json-store', 'data')]
)
def highlight_download_button(json_output, full_json):
    if json_output and json_output != "Error generating JSON-LD":
        # Check if output was truncated
        was_truncated = full_json and len(full_json) > len(json_output)
        
        # Make the download button stand out
        button_style = {
            'fontWeight': 'bold',
            'transition': 'all 0.3s ease'
        }
        
        # Style for N-Triples button - always keep it hidden
        nt_style = {
            'fontWeight': 'bold',
            'transition': 'all 0.3s ease',
            'display': 'none'  # Always keep N-Triples button hidden
        }
        
        return button_style, nt_style
    
    # Default style - always keep N-Triples button hidden
    return {}, {'display': 'none'}

if __name__ == '__main__':
    # Get the PORT from environment variables and use 8000 as fallback
    port = int(os.getenv('PORT', 8000))
    # Run the server
    server.run(host='0.0.0.0', port=port)

    # test