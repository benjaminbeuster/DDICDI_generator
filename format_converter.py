#!/usr/bin/env python
# coding: utf-8

"""
RDF Format Conversion Utilities for DDI-CDI Converter
Provides conversion between JSON-LD and other RDF serializations
"""

from rdflib import Graph, URIRef
import tempfile
import os


class FormatConverter:
    """Convert DDI-CDI JSON-LD to various RDF formats"""

    # Format configuration
    FORMATS = {
        'jsonld': {
            'name': 'JSON-LD',
            'mimetype': 'application/ld+json',
            'extension': '.jsonld',
            'requires_conversion': False,
            'description': 'W3C JSON-LD RDF serialization'
        },
        'turtle': {
            'name': 'Turtle',
            'mimetype': 'text/turtle',
            'extension': '.ttl',
            'rdflib_format': 'turtle',
            'requires_conversion': True,
            'description': 'W3C Turtle RDF serialization (human-readable)'
        },
        'ntriples': {
            'name': 'N-Triples',
            'mimetype': 'application/n-triples',
            'extension': '.nt',
            'rdflib_format': 'nt',
            'requires_conversion': True,
            'description': 'W3C N-Triples RDF serialization (simple line-based)'
        }
    }

    DEFAULT_BASE_URI = 'http://example.org/ddi/'

    # Standard namespace bindings for Turtle output
    DEFAULT_NAMESPACE_BINDINGS = {
        'ddi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#'
    }

    @classmethod
    def convert(cls, jsonld_string, target_format, base_uri=None):
        """
        Convert JSON-LD to target RDF format

        Args:
            jsonld_string: DDI-CDI JSON-LD document as string
            target_format: Target format ('jsonld', 'turtle', 'ntriples')
            base_uri: Optional base URI for instance data (defaults to http://example.org/ddi/)

        Returns:
            Converted content as bytes

        Raises:
            ValueError: If format is unsupported or conversion fails
        """
        # Validate format
        if target_format not in cls.FORMATS:
            supported = ', '.join(cls.FORMATS.keys())
            raise ValueError(
                f"Unsupported format '{target_format}'. "
                f"Supported formats: {supported}"
            )

        format_config = cls.FORMATS[target_format]

        # JSON-LD needs no conversion
        if not format_config['requires_conversion']:
            return jsonld_string.encode('utf-8')

        # Convert via RDFlib
        base_uri = base_uri or cls.DEFAULT_BASE_URI
        return cls._convert_via_rdflib(
            jsonld_string,
            target_format,
            base_uri
        )

    @classmethod
    def _convert_via_rdflib(cls, jsonld_string, target_format, base_uri):
        """
        Convert JSON-LD to other RDF formats using rdflib

        Args:
            jsonld_string: JSON-LD document as string
            target_format: Target format ('turtle', 'ntriples')
            base_uri: Base URI for instance data

        Returns:
            Serialized RDF as bytes
        """
        temp_file = None
        try:
            # Write JSON-LD to temporary file for parsing
            with tempfile.NamedTemporaryFile(
                suffix='.jsonld',
                delete=False,
                mode='w',
                encoding='utf-8'
            ) as f:
                f.write(jsonld_string)
                temp_file = f.name

            # Parse JSON-LD into RDF graph
            source_graph = Graph()
            source_graph.parse(temp_file, format='json-ld')

            # Transform URIs and create new graph
            target_graph = Graph()

            # Add namespace bindings
            # Determine prefix for base URI
            base_prefix = cls._get_prefix_for_uri(base_uri)
            target_graph.bind(base_prefix, base_uri)

            for prefix, namespace in cls.DEFAULT_NAMESPACE_BINDINGS.items():
                target_graph.bind(prefix, namespace)

            # Transform URIs
            for s, p, o in source_graph:
                s = cls._transform_uri(s, base_uri)
                o = cls._transform_uri(o, base_uri)
                target_graph.add((s, p, o))

            # Serialize to target format
            format_config = cls.FORMATS[target_format]
            rdflib_format = format_config['rdflib_format']

            output = target_graph.serialize(
                format=rdflib_format,
                encoding='utf-8'
            )

            # Handle different return types from rdflib versions
            if isinstance(output, bytes):
                return output
            elif isinstance(output, str):
                return output.encode('utf-8')
            else:
                # BytesIO or similar
                return output.getvalue()

        except Exception as e:
            raise ValueError(
                f"Failed to convert to {target_format}: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

    @staticmethod
    def _transform_uri(uri_ref, base_uri):
        """
        Transform file:/// URIs to specified base URI

        Args:
            uri_ref: rdflib URIRef or Literal
            base_uri: Target base URI

        Returns:
            Transformed URIRef or original value
        """
        uri_str = str(uri_ref)

        # Only transform file:/// URIs
        if uri_str.startswith('file:///'):
            # Extract fragment/last segment
            fragment = uri_str.split('/')[-1]

            # Remove .jsonld extension from temporary filenames
            # e.g., tmpq7lxd77t.jsonld#v480004 -> #v480004
            if '.jsonld#' in fragment:
                # Extract just the fragment part after #
                fragment = '#' + fragment.split('#', 1)[1]

            return URIRef(base_uri + fragment)

        return uri_ref

    @staticmethod
    def _get_prefix_for_uri(uri):
        """
        Determine appropriate namespace prefix for URI

        Args:
            uri: Base URI string

        Returns:
            Suggested prefix string
        """
        # Extract domain or path component
        if 'sikt.no' in uri:
            return 'sikt'
        elif 'example.org' in uri:
            return 'ex'
        else:
            return 'inst'  # Generic "instance" prefix

    @classmethod
    def get_format_info(cls, format_key=None):
        """
        Get information about supported formats

        Args:
            format_key: Specific format, or None for all

        Returns:
            Format config dict or dict of all formats
        """
        if format_key:
            return cls.FORMATS.get(format_key, {})
        return cls.FORMATS
