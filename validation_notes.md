# DDI-CDI Validation Process

## Prerequisites
- Apache Jena Tools installed (includes riot and shacl tools)
- JSON-LD input file
- SHACL shapes file

## Step 1: Download SHACL Shapes File
Download the latest DDI-CDI SHACL shapes file:

bash
curl https://ddi-cdi.github.io/ddi-cdi_v1.0-post/encoding/shacl/ddi-cdi.shacl.ttl > ddi-cdi.shacl.ttl

## Step 2: Convert JSON-LD to RDF
Convert the JSON-LD file to Turtle format using Jena's riot tool:

bash
riot --syntax=jsonld validation/ESS11-subset_v2.jsonld > validation/ESS11-subset_v2.ttl
This command converts your JSON-LD file to Turtle format (data.ttl), which is an RDF serialization format.

## Step 3: Validate Using SHACL
You have two options for validation:

bash
shacl validate --data=validation/ESS11-subset_v2.ttl --shapes=validation/ddi-cdi.shacl.ttl
shacl validate --data=validation/ESS11-subset_v2.jsonld --shapes=validation/ddi-cdi.shacl.ttl
This command will validate ESS11-subset_v2.ttl against new-ddi-cdi.schema.ttl and output any validation errors.

The Turtle (.ttl) format provides a more readable RDF serialization that's easier to inspect and validate.

## Additional Resources
- [DDI-CDI Documentation](https://ddi-cdi.github.io/)
- [Apache Jena Documentation](https://jena.apache.org/documentation/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)