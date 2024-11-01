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
import pyreadstat
import pandas as pd
from lxml import etree
from DDICDI_converter_xml_incremental import (
    generate_complete_xml_incremental,
    generate_WideDataStructure2_incremental,
    generate_IdentifierComponent2_incremental,
    generate_MeasureComponent2_incremental,
    generate_PrimaryKey2_incremental,
    generate_PrimaryKeyComponent2_incremental,
    update_xml
)
from DDICDI_converter_jsonld_incremental import (
    generate_complete_json_ld,
    generate_complete_json_ld2
)
from spss_import import read_sav, create_variable_view, create_variable_view2
from app_content import markdown_text, colors, style_dict, table_style, header_dict, app_title, app_description, about_text
from io import BytesIO


# Define the namespaces, DDI
nsmap = {
    'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/',
    'r': 'ddi:reusable:3_3'  # Replace with the actual URI for the 'r' namespace
}
agency = 'int.esseric'

# Define the Flask server
server = Flask(__name__)

# Define the Dash app and associate it with the Flask server
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.SUPERHERO])

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
                'height': '60px',  # Change the height to 60px to match the other logo
                'maxWidth': '100%',
                'objectFit': 'contain',
                'marginRight': '10px'
            }
        ),
        html.Img(
            src=app.get_asset_url('petals_logos.2.0-01.webp'),
            style={
                'height': '60px',
                'width': 'auto',
                'marginRight': '10px',
                'opacity': '0.8'  # Adjust the opacity value to make the image more or less transparent
            }
        )
    ],
    style={
        'display': 'flex',
        'alignItems': 'center',  # This will vertically align the images
        'justifyContent': 'center'  # This will horizontally align the images
    }
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(app_description, href="#")),
        html.Div(
            children=[
                dbc.Col([
                    html.Img(
                        src=app.get_asset_url('petals_logos.2.0-01.webp'),
                        style={
                            'height': '60px',
                            'width': 'auto',
                            'marginRight': '10px',
                            'opacity': '0.8'  # Adjust the opacity value to make the image more or less transparent
                        }
                    )
                ]),
                dbc.Col([
                    html.Img(
                        src=app.get_asset_url('sikt.jpg'),
                        style={
                            'height': '60px',  # Change the height to 60px to match the other logo
                            'maxWidth': '100%',
                            'objectFit': 'contain',
                            'marginRight': '10px'
                        }
                    )
                ])
            ],
            style={
                'display': 'flex',
                'alignItems': 'center',  # This will vertically align the images
                'justifyContent': 'center'  # This will horizontally align the images
            }
        )
    ],
    brand=brand_section,
    brand_href="#",
    color="dark",
    dark=True,
)

about_section = dbc.Card(
    dbc.CardBody(
        dcc.Markdown(about_text, className="card-text")
    ),
    className="mt-4",  # Adding some margin at the top for spacing
)

app.layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col([
            html.Br(),
            dcc.Upload(
                id='upload-data',
                children=dbc.Button('Import Data', color="primary", className="mr-1"),
                multiple=False,
                accept=".sav,.dta"  # Accept both .sav and .dta files
            ),

            html.Br(),

            # Add a button to switch between tables
            dbc.Button("Switch View", id="table-switch-button", color="primary", className="mr-1"),

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
                                style={'color': '#3498db', 'fontSize': '14px', 'marginBottom': '10px',
                                       'display': 'none'}),

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
                                     style={'color': '#3498db', 'fontSize': '14px', 'marginBottom': '10px'}),

                            dash_table.DataTable(
                                id='table2',
                                editable=False,  # Allow content to be editable
                                row_selectable="multi",  # Allow multiple rows to be selected
                                selected_rows=[],
                                style_table=table_style,
                                style_header=header_dict,
                                style_cell=style_dict
                            ),
                        ]
                    ),
                ], id="table2-col", style={'display': 'none'}),  # Initially, hide the second table
            ]),

            html.Br(),
            dbc.Button('Download XML', id='btn-download', color="success", className="mr-1",
                       style={'display': 'none'}),
            dbc.Button('Download JSON-LD', id='btn-download-json', color="success", className="mr-1",
                       style={'display': 'none'}),
            dcc.Download(id='download-xml'),
            dcc.Download(id='download-json'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Pre(
                        id='xml-ld-output',
                        style={
                            'whiteSpace': 'pre',
                            'wordBreak': 'break-all',
                            'color': colors['text'],
                            'backgroundColor': colors['background'],
                            'marginTop': '10px',
                            'maxHeight': '300px',
                            'overflowY': 'scroll',
                            'fontSize': '14px',
                        }
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Markdown(markdown_text, dangerously_allow_html=True),
                            style={
                                'overflowY': 'scroll',  # Add scroll if content is too long
                                'height': '400px',  # Adjust based on your requirement
                                'border': '1px solid #ccc',  # Optional: Add a border for better visibility
                                'padding': '10px',  # Add some padding
                                'fontSize': '14px',  # Adjust font size if needed
                            }
                        )
                    ])
                ], width=6)

            ]),
            html.Div(id='json-ld-output', style={'display': 'none'}),
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
     Output('btn-download', 'style'),
     Output('btn-download-json', 'style'),
     Output('table1-instruction', 'children'),
     Output('json-ld-output', 'children')],
    [Input('upload-data', 'contents'),
     Input('table2', 'selected_rows')],
    [State('upload-data', 'filename'),
     State('table2', 'data')]
)
def combined_callback(contents, selected_rows, filename, table2_data):
    if not contents:
        return [], [], [], [], [], [], "", {'display': 'none'}, {'display': 'none'}, "", ""

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    file_extension = os.path.splitext(filename)[1]

    try:
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp_file:
            tmp_file.write(decoded)
            tmp_filename = tmp_file.name

        if '.dta' in tmp_filename:
            df, df_meta, file_name, n_rows = read_sav(tmp_filename)
            df2 = create_variable_view2(df_meta)
        elif '.sav' in tmp_filename:
            df, df_meta, file_name, n_rows = read_sav(tmp_filename)
            df2 = create_variable_view(df_meta)
        else:
            raise ValueError("Unsupported file type")

        columns1 = [{"name": i, "id": i} for i in df.columns]
        columns2 = [{"name": i, "id": i} for i in df2.columns]
        conditional_styles1 = style_data_conditional(df)
        conditional_styles2 = style_data_conditional(df2)

        # Temporary files to store the XML and JSON-LD output
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_xml_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_json_file:
            temp_xml_filename = temp_xml_file.name
            temp_json_filename = temp_json_file.name

        # Initialize vars as empty list
        vars = []
        
        # If rows are selected, update both XML and JSON-LD
        if selected_rows and table2_data and df_meta:
            vars = [table2_data[row_index]["name"] for row_index in selected_rows]

            # Generate initial XML
            generate_complete_xml_incremental(
                df.head(1), 
                df_meta, 
                spssfile=filename, 
                output_file=temp_xml_filename
            )

            if vars:
                # Generate a new XML file with the primary key components
                temp_updated_xml = tempfile.NamedTemporaryFile(suffix='.xml', delete=False).name
                
                with etree.xmlfile(temp_updated_xml, encoding='UTF-8') as xf:
                    xf.write_declaration(standalone=True)
                    with xf.element(etree.QName(nsmap['cdi'], 'DDICDIModels'), nsmap=nsmap):
                        generate_WideDataStructure2_incremental(xf, df_meta, vars, agency)
                        generate_IdentifierComponent2_incremental(xf, df_meta, vars, agency)
                        generate_MeasureComponent2_incremental(xf, df_meta, vars, agency)
                        generate_PrimaryKey2_incremental(xf, df_meta, vars, agency)
                        generate_PrimaryKeyComponent2_incremental(xf, df_meta, vars, agency)

                # Read both XML files and parse them
                parser = etree.XMLParser(remove_blank_text=True)
                original_tree = etree.parse(temp_xml_filename, parser)
                updated_tree = etree.parse(temp_updated_xml, parser)

                # Merge the XML content
                merged_xml = update_xml(
                    etree.tostring(original_tree, encoding='utf-8', pretty_print=True).decode('utf-8'),
                    etree.tostring(updated_tree, encoding='utf-8', pretty_print=True).decode('utf-8')
                )

                # Parse the merged XML and pretty print it
                merged_tree = etree.fromstring(merged_xml.encode('utf-8'))
                xml_data_pretty = etree.tostring(
                    merged_tree, 
                    encoding='utf-8', 
                    pretty_print=True, 
                    xml_declaration=True
                ).decode('utf-8')
                
                # Clean up temporary file
                os.remove(temp_updated_xml)
            else:
                # Read and pretty print the original XML
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(temp_xml_filename, parser)
                xml_data_pretty = etree.tostring(
                    tree, 
                    encoding='utf-8', 
                    pretty_print=True, 
                    xml_declaration=True
                ).decode('utf-8')

        else:
            # Generate XML without primary keys
            generate_complete_xml_incremental(
                df.head(1), 
                df_meta, 
                spssfile=filename, 
                output_file=temp_xml_filename
            )
            # Read and pretty print the XML
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(temp_xml_filename, parser)
            xml_data_pretty = etree.tostring(
                tree, 
                encoding='utf-8', 
                pretty_print=True, 
                xml_declaration=True
            ).decode('utf-8')

        # Handle JSON-LD (keeping this part unchanged as it works)
        json_ld_data = generate_complete_json_ld2(
            df.head(), 
            df_meta, 
            vars=vars if 'vars' in locals() else [],
            spssfile=filename
        )

        # Update instruction text
        instruction_text = f"The table below shows the first 5 rows from the dataset '{filename}'. Please note that the generated XML and JSON-LD output will only include these 5 rows, even though the full dataset contains {n_rows} rows."
        
        return (df.to_dict('records'), columns1, conditional_styles1, 
                df2.to_dict('records'), columns2, conditional_styles2, 
                xml_data_pretty, {'display': 'block'}, {'display': 'block'}, 
                instruction_text, json_ld_data)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], [], [], [], [], [], "An error occurred while processing the file.", {'display': 'none'}, {'display': 'none'}, "", ""

    finally:
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

if __name__ == '__main__':
    # Get the PORT from environment variables and use 8000 as fallback
    port = int(os.getenv('PORT', 8000))
    # Run the server
    server.run(host='0.0.0.0', port=port)

    # test