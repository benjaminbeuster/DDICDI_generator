import pandas as pd
from lxml import etree

# Define the namespace
nsmap = {'cdi': 'http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/'}

def add_cdi_element(parent, tag, text=None):
    """
    Adds a new subelement with the given tag and text to the parent element using the cdi namespace prefix.

    Parameters:
    parent (etree.Element): The parent element to which the new subelement will be added.
    tag (str): The name of the subelement to be added.
    text (str): The text content to be included in the subelement (optional).

    Returns:
    etree.Element: The newly created subelement.

    """
    element = etree.SubElement(parent, etree.QName(nsmap['cdi'], tag), nsmap=nsmap)
    if text is not None:
        element.text = str(text)
    return element

def add_identifier(parent, id, agency='int.esseric'):
    identifier = add_cdi_element(parent, 'identifier')
    ddiIdentifier = add_cdi_element(identifier, 'ddiIdentifier')
    add_cdi_element(ddiIdentifier, 'dataIdentifier', id)
    add_cdi_element(ddiIdentifier, 'registrationAuthorityIdentifier', agency)
    add_cdi_element(ddiIdentifier, 'versionIdentifier', 1)

def add_ddiref(parent, id, agency, validType):
    ddiReference = add_cdi_element(parent, 'ddiReference')
    add_cdi_element(ddiReference, 'dataIdentifier', id)
    add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', agency)
    add_cdi_element(ddiReference, 'versionIdentifier', 1)
    add_cdi_element(parent, 'validType', validType)

def remove_empty_elements(element):
    """
    Recursively removes all empty elements or elements that contain only empty subelements from the given element.

    Parameters:
    element (etree.Element): The element to be checked and potentially removed.

    """
    for child in element.getchildren():
        remove_empty_elements(child)
    if element.text is None and len(element) == 0:
        element.getparent().remove(element)
    elif element.text is not None and not element.text.strip() and len(element) == 0:
        element.getparent().remove(element)

#
def add_refitem(row, element, element_id, element_agency, element_version, element_name):
    # Multiple Agents
    if '|' in row[element_id]:
        id = row[element_id].split(" | ")
    else:
        id = [row[element_id]]
    if '|' in row[element_agency]:
        agency = row[element_agency].split(" | ")
    else:
        agency = [row[element_agency]]
    if '|' in str(row[element_version]):
        version = str(row[element_version]).split(" | ")
    else:
        version = [str(row[element_version])]
    sub_Ags = list(zip(id, agency, version))
    for a,b,c in sub_Ags:
        if len(sub_Ags) > 0:
            command = add_cdi_element(element, element_name)
            ddiReference = add_cdi_element(command, 'ddiReference', row['ddiReference'])
            add_cdi_element(ddiReference, 'dataIdentifier', a)
            add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', b)
            add_cdi_element(ddiReference, 'versionIdentifier', c)
        else:
            command = add_cdi_element(element, element_name)
            ddiReference = add_cdi_element(command, 'ddiReference', row['ddiReference'])
            add_cdi_element(ddiReference, 'dataIdentifier', row['dataIdentifierAg'])
            add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', row['registrationAuthorityIdentifierAg'])
            add_cdi_element(ddiReference, 'versionIdentifier', str(row['versionIdentifierAg']))
#
# def add_uri_elements(row, element, element_name, element_uri, element_type):
#     """
#     Adds elements to the specified CDI element based on the URI(s) provided in the input row.
#
#     Args:
#         row (pandas Series): The row containing the URI(s) to be used in the entityUsed element(s).
#         element (Element): The CDI element to which the element(s) should be added.
#
#     Returns:
#         None.
#     """
#     # Multiple elements
#     if '|' in row[element_uri]:
#         uri = row[element_uri].split(" | ")
#     else:
#         uri = [row[element_uri]]
#     if '|' in row[element_type]:
#         etype = row[element_type].split(" | ")
#     else:
#         etype = [row[element_type]]
#     uris = list(zip(uri, etype))
#     if len(uri) > 0:
#         for i, x in uris:
#             command = add_cdi_element(element, element_name)
#             add_cdi_element(command, 'description', x)
#             add_cdi_element(command, 'uri', i)
#     else:
#         command = add_cdi_element(element, element_name)
#         add_cdi_element(command, 'description', row[element_type])
#         add_cdi_element(command, 'uri', row[element_uri])
#
#
# def add_uri_elements2(row, element, element_name, element_uri, element_type, element_description):
#     """
#     Adds elements to the specified CDI element based on the URI(s) provided in the input row.
#
#     Args:
#         row (pandas Series): The row containing the URI(s) to be used in the entityUsed element(s).
#         element (Element): The CDI element to which the element(s) should be added.
#
#     Returns:
#         None.
#     """
#     # Multiple elements
#     if '|' in row[element_uri]:
#         uri = row[element_uri].split(" | ")
#     else:
#         uri = [row[element_uri]]
#     if '|' in row[element_type]:
#         etype = row[element_type].split(" | ")
#     else:
#         etype = [row[element_type]]
#     if '|' in row[element_description]:
#         edesc = row[element_description].split(" | ")
#     else:
#         edesc = [row[element_type]]
#     uris = list(zip(uri, etype, edesc))
#     if len(uri) > 0:
#         for i, x, y in uris:
#             command = add_cdi_element(element, element_name)
#             add_cdi_element(command, 'description', y)
#             add_cdi_element(command, 'uri', i)
#             add_cdi_element(command, 'validType', x)
#     else:
#         command = add_cdi_element(element, element_name)
#         add_cdi_element(command, 'description', row[element_description])
#         add_cdi_element(command, 'uri', row[element_uri])
#         add_cdi_element(command, 'validType', row[element_type])
#
# def add_refitem_cat(row, element, element_id, element_agency, element_version, element_name, agent_name, agentName):
#     # Multiple Agents
#     if '|' in row[element_id]:
#         id = row[element_id].split(" | ")
#     else:
#         id = [row[element_id]]
#     if '|' in row[element_agency]:
#         agency = row[element_agency].split(" | ")
#     else:
#         agency = [row[element_agency]]
#     if '|' in str(row[element_version]):
#         version = str(row[element_version]).split(" | ")
#     else:
#         version = [str(row[element_version])]
#     if '|' in str(row[agent_name]):
#         agent = str(row[agent_name]).split(" | ")
#     else:
#         agent = [str(row[agent_name])]
#     sub_Ags = list(zip(id, agency, version, agent))
#     for a,b,c,d in sub_Ags:
#         if len(sub_Ags) > 0:
#             command = add_cdi_element(element, element_name)
#             esub = add_cdi_element(command, agentName)
#             languageSpecificString = add_cdi_element(esub, 'languageSpecificString')
#             add_cdi_element(languageSpecificString, 'content', d)
#             # names shouls not have language
#             #add_cdi_element(languageSpecificString, 'language', 'en')
#             reference = add_cdi_element(command, 'reference')
#             ddiReference = add_cdi_element(reference, 'ddiReference', row['ddiReference'])
#             add_cdi_element(ddiReference, 'dataIdentifier', a)
#             add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', b)
#             add_cdi_element(ddiReference, 'versionIdentifier', c)
#         else:
#             command = add_cdi_element(element, element_name)
#             ddiReference = add_cdi_element(command, 'ddiReference', row['ddiReference'])
#             add_cdi_element(ddiReference, 'dataIdentifier', row['dataIdentifierAg'])
#             add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', row['registrationAuthorityIdentifierAg'])
#             add_cdi_element(ddiReference, 'versionIdentifier', str(row['versionIdentifierAg']))
#
# def add_refitem_pos(row, element, element_id, element_agency, element_version, element_name, validType):
#     # Multiple Agents
#     if '|' in row[element_id]:
#         id = row[element_id].split(" | ")
#     else:
#         id = [row[element_id]]
#     if '|' in row[element_agency]:
#         agency = row[element_agency].split(" | ")
#     else:
#         agency = [row[element_agency]]
#     if '|' in str(row[element_version]):
#         version = str(row[element_version]).split(" | ")
#     else:
#         version = [str(row[element_version])]
#     sub_Ags = list(zip(id, agency, version))
#     for a,b,c in sub_Ags:
#         if len(sub_Ags) > 0:
#             command = add_cdi_element(element, element_name)
#             ddiReference = add_cdi_element(command, 'ddiReference', row['ddiReference'])
#             add_cdi_element(ddiReference, 'dataIdentifier', a)
#             add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', b)
#             add_cdi_element(ddiReference, 'versionIdentifier', c)
#             add_cdi_element(command, 'validType', str(row['validType']))
#         else:
#             command = add_cdi_element(element, element_name)
#             ddiReference = add_cdi_element(command, 'ddiReference', row['ddiReference'])
#             add_cdi_element(ddiReference, 'dataIdentifier', row['dataIdentifierAg'])
#             add_cdi_element(ddiReference, 'registrationAuthorityIdentifier', row['registrationAuthorityIdentifierAg'])
#             add_cdi_element(ddiReference, 'versionIdentifier', str(row['versionIdentifierAg']))
#             add_cdi_element(command, 'validType', str(row['validType']))