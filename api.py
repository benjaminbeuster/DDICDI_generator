#!/usr/bin/env python
# coding: utf-8

"""
REST API for DDI-CDI Converter
Provides endpoints for programmatic file conversion
"""

from flask import request, jsonify, send_file, Response
from functools import wraps
import tempfile
import os
import base64
from DDICDI_converter_JSONLD_incremental import generate_complete_json_ld, MemoryManager
from spss_import import read_sav, read_csv, read_json
import io
import json

# API Configuration
API_KEY_ENV_VAR = 'DDI_API_KEY'
DEFAULT_MAX_ROWS = 5

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        # Get expected API key from environment variable
        expected_key = os.environ.get(API_KEY_ENV_VAR)

        if not expected_key:
            # If no API key is configured, allow access (development mode)
            return f(*args, **kwargs)

        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'message': 'Include X-API-Key header in your request'
            }), 401

        if api_key != expected_key:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def register_api_routes(server):
    """Register all API routes to the Flask server"""

    @server.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint - no authentication required"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0',
            'service': 'DDI-CDI Converter API'
        }), 200


    @server.route('/api/convert', methods=['POST'])
    @require_api_key
    def convert_file():
        """
        Convert uploaded file to DDI-CDI JSON-LD format

        Request:
            - Multipart form data with 'file' field
            - Optional form fields:
                - max_rows: Number of rows to process (default: 5)
                - process_all_rows: 'true' to process all rows (default: 'false')
                - decompose_keys: 'true' to decompose hierarchical JSON keys (default: 'false')
                - variable_roles: JSON string with role assignments

        Response:
            - JSON-LD document as application/json
        """

        # Validate file upload
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Include a file in the request with key "file"'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'error': 'Empty filename',
                'message': 'The uploaded file has no filename'
            }), 400

        # Get optional parameters
        try:
            max_rows = int(request.form.get('max_rows', DEFAULT_MAX_ROWS))
        except ValueError:
            return jsonify({
                'error': 'Invalid max_rows parameter',
                'message': 'max_rows must be an integer'
            }), 400

        process_all_rows = request.form.get('process_all_rows', 'false').lower() == 'true'
        decompose_keys = request.form.get('decompose_keys', 'false').lower() == 'true'

        # Parse variable roles if provided
        variable_roles = {}
        if 'variable_roles' in request.form:
            try:
                variable_roles = json.loads(request.form.get('variable_roles'))
            except json.JSONDecodeError:
                return jsonify({
                    'error': 'Invalid variable_roles parameter',
                    'message': 'variable_roles must be valid JSON'
                }), 400

        # Save uploaded file to temporary location
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name

            # Determine file type and read file
            filename_lower = file.filename.lower()

            if filename_lower.endswith('.sav') or filename_lower.endswith('.dta'):
                df, df_meta, _, _ = read_sav(temp_path)
            elif filename_lower.endswith('.csv'):
                df, df_meta, _, _ = read_csv(temp_path)
            elif filename_lower.endswith('.json'):
                df, df_meta, _, _ = read_json(temp_path, decompose_keys=decompose_keys)
            else:
                return jsonify({
                    'error': 'Unsupported file format',
                    'message': 'Supported formats: .sav, .dta, .csv, .json'
                }), 400

            # Initialize role classifications if they don't exist
            if not hasattr(df_meta, 'measure_vars') or df_meta.measure_vars is None:
                df_meta.measure_vars = []
            if not hasattr(df_meta, 'identifier_vars') or df_meta.identifier_vars is None:
                df_meta.identifier_vars = []
            if not hasattr(df_meta, 'attribute_vars') or df_meta.attribute_vars is None:
                df_meta.attribute_vars = []
            if not hasattr(df_meta, 'contextual_vars') or df_meta.contextual_vars is None:
                df_meta.contextual_vars = []
            if not hasattr(df_meta, 'synthetic_id_vars') or df_meta.synthetic_id_vars is None:
                df_meta.synthetic_id_vars = []
            if not hasattr(df_meta, 'variable_value_vars') or df_meta.variable_value_vars is None:
                df_meta.variable_value_vars = []

            # Set default roles if none provided
            if not variable_roles:
                # Default: all variables are measures for non-JSON files
                is_json = filename_lower.endswith('.json')
                if not is_json:
                    # Non-JSON: default all to measure
                    df_meta.measure_vars = list(df_meta.column_names)
                else:
                    # JSON: default all to identifier (more conservative)
                    df_meta.identifier_vars = list(df_meta.column_names)

            # Apply variable roles if provided
            if variable_roles:
                # Reset all role lists
                df_meta.measure_vars = []
                df_meta.identifier_vars = []
                df_meta.attribute_vars = []
                df_meta.contextual_vars = []
                df_meta.synthetic_id_vars = []
                df_meta.variable_value_vars = []
                df_meta.variable_descriptor_vars = []

                # Apply roles from the provided mapping
                for var_name, roles in variable_roles.items():
                    if var_name not in df_meta.column_names:
                        continue

                    # Handle comma-separated roles
                    role_list = [r.strip() for r in roles.split(',')]

                    for role in role_list:
                        if role == 'measure':
                            df_meta.measure_vars.append(var_name)
                        elif role == 'identifier':
                            df_meta.identifier_vars.append(var_name)
                        elif role == 'attribute':
                            df_meta.attribute_vars.append(var_name)
                        elif role == 'contextual':
                            df_meta.contextual_vars.append(var_name)
                        elif role == 'synthetic':
                            df_meta.synthetic_id_vars.append(var_name)
                        elif role == 'variablevalue':
                            df_meta.variable_value_vars.append(var_name)
                        elif role == 'variabledescriptor':
                            df_meta.variable_descriptor_vars.append(var_name)

            # Generate DDI-CDI JSON-LD
            json_ld_output = generate_complete_json_ld(
                df=df,
                df_meta=df_meta,
                spssfile=file.filename,
                max_rows=max_rows,
                process_all_rows=process_all_rows
            )

            # Return JSON-LD directly (already a JSON string, don't double-encode)
            return Response(json_ld_output, mimetype='application/ld+json'), 200

        except Exception as e:
            return jsonify({
                'error': 'Conversion failed',
                'message': str(e)
            }), 500

        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass


    @server.route('/api/info', methods=['GET'])
    def api_info():
        """Get API information and available endpoints"""
        api_key_required = bool(os.environ.get(API_KEY_ENV_VAR))

        return jsonify({
            'version': '1.0',
            'service': 'DDI-CDI Converter API',
            'authentication': {
                'required': api_key_required,
                'method': 'X-API-Key header',
                'env_var': API_KEY_ENV_VAR if not api_key_required else 'configured'
            },
            'endpoints': {
                'GET /api/health': 'Health check (no auth)',
                'GET /api/info': 'API information (no auth)',
                'POST /api/convert': 'Convert file to DDI-CDI JSON-LD (requires auth if configured)'
            },
            'supported_formats': ['.sav', '.dta', '.csv', '.json'],
            'parameters': {
                'max_rows': 'Number of rows to process (default: 5)',
                'process_all_rows': 'Process all rows: true/false (default: false)',
                'decompose_keys': 'Decompose JSON hierarchical keys: true/false (default: false)',
                'variable_roles': 'JSON object with variable role assignments'
            }
        }), 200
