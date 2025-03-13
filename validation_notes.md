# DDI-CDI Validation Process

## Prerequisites

### 1. Apache Jena Tools Installation

#### Download and Install
1. Go to [Apache Jena Binary Distributions](https://jena.apache.org/download/#apache-jena-binary-distributions)
2. Download the latest version (e.g., `apache-jena-5.2.0.zip`)
3. Move and extract the file:

bash
Copy code
mv ~/Downloads/apache-jena-5.2.0.zip ~/apache-jena.zip
Extract the file:

bash
Copy code
unzip ~/apache-jena.zip -d ~/apache-jena
Navigate to the Jena directory to confirm the contents:

bash
Copy code
cd ~/apache-jena/apache-jena-5.2.0
Step 3: Set Up Environment Variables Correctly
Ensure the environment variable in your .zshrc file points to the correct location:
bash
Copy code
echo 'export JENA_HOME=~/apache-jena/apache-jena-5.2.0' >> ~/.zshrc
echo 'export PATH=$PATH:$JENA_HOME/bin' >> ~/.zshrc
source ~/.zshrc

### 2. Input Files
- JSON-LD file containing your DDI-CDI data
- SHACL shapes file (`.ttl` format)
  - Latest version available at: `https://ddi-cdi.github.io/ddi-cdi_v1.0-post/encoding/shacl/ddi-cdi.shacl.ttl`

### 3. System Requirements
- Java Runtime Environment (JRE) 11 or higher
- Command-line terminal access
- Sufficient disk space for working files

### 4. Recommended Tools
- Text editor with TTL/RDF syntax highlighting
- JSON-LD validator (optional)
- RDF visualization tool (optional)

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

shacl validate --data=validation/ESS11-subset.jsonld --shapes=validation/ddi-cdi.shacl.ttl

shacl validate --data=validation/CRON3W2e01_unscrambled (2).jsonld --shapes=validation/ddi-cdi.shacl.ttl

shacl validate --data=validation/CRON3W2e01_unscrambled-2_DDICDI.jsonld --shapes=validation/ddi-cdi.shacl.ttl

## Additional Resources
- [DDI-CDI Documentation](https://ddi-cdi.github.io/)
- [Apache Jena Documentation](https://jena.apache.org/documentation/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)