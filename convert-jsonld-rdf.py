from rdflib import Graph, plugin
from rdflib.serializer import Serializer
import rdflib

# Create a graph
g = Graph()

# Define base URIs
g.bind('sikt', 'https://sikt.no/cdi/RDF/')

# Parse JSON-LD file
g.parse("ess/ESS11-subset.jsonld", format="json-ld")

# Create new graph with transformed URIs
new_g = Graph()
for s, p, o in g:
    # Transform file:/// URIs to https://sikt.no/cdi/RDF/
    if str(s).startswith('file:///'):
        s = rdflib.URIRef('https://sikt.no/cdi/RDF/' + str(s).split('/')[-1])
    if str(o).startswith('file:///'):
        o = rdflib.URIRef('https://sikt.no/cdi/RDF/' + str(o).split('/')[-1])
    new_g.add((s, p, o))

# Serialize to N-Triples with explicit UTF-8 encoding
new_g.serialize(destination="ess/output.nt", format="nt", encoding="utf-8")