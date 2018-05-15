# 
# Python package for exporting a JSON metadata record to ISO 19139
#


from datetime import datetime

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


# Location of the ISO-19139 template file
ISO_TEMPLATE_FILE = '/usr/lib/ckan/default/src/ckanext-publish_to_waf/ckanext/publish_to_waf/ISO_TEMPLATE.xml'


from lxml import etree as ElementTree       # ISO XML parser
from copy import deepcopy                   # Allows deep copy of ISO elements

# We need XML namespace mappings in order to search the ISO element tree
XML_NAMESPACE_MAP = {'gmd': 'http://www.isotc211.org/2005/gmd',
                     'xlink': 'http://www.w3.org/1999/xlink', 
                     'gco': 'http://www.isotc211.org/2005/gco', 
                     'gml': 'http://www.opengis.net/gml'}


# Return first item in a list if list is nonempty (returns None otherwise).
def getFirst(someList): 
    if someList:
        return someList[0]
    else:
        log.debug('Found empty list!')


# Search XML element tree and return the first matching element
# If createCopy is true, append a copy of the element to the parent element. 
def getElement(baseElement, elementPath, createCopy=False):
    elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
    element = getFirst(elements)
    try:
        assert element != None
    except AssertionError:
        print "Failed to find any element matching: " + elementPath

    if createCopy:
        elementCopy = deepcopy(element)
        element.getparent().append(elementCopy)
        element = elementCopy
    return element

def setTextOrMarkMissing(element, fillText):
    if len(fillText) > 0:
        element.text = fillText
    else:
        element.getparent().attrib['{http://www.isotc211.org/2005/gco}nilReason'] = "missing"



def transformToISO(templateFilePath, data_dict):
    # Load the ISO template file as an XML element tree
    tree = ElementTree.parse(templateFilePath)
    root = tree.getroot()

    # Put id in fileIdentifier
    fileIdentifier = getElement(root, './/gmd:fileIdentifier/gco:CharacterString')
    fileIdentifier.text = data_dict["id"]

    # Put current time in dateStamp
    fileIdentifier = getElement(root, './/gmd:dateStamp/gco:DateTime')
    dateTimeISO = datetime.now().isoformat()
    fileIdentifier.text = dateTimeISO

    # Put maintainer and maintainer_email in gmd:contact
    contact = getElement(root, './/gmd:contact')
    maintainer = data_dict["maintainer"]
    maintainer_email = data_dict["maintainer_email"]
    modifyContact(contact, maintainer, maintainer_email, "pointOfContact")

    # Put title in title
    elementTitle = getElement(root, './/gmd:CI_Citation/gmd:title/gco:CharacterString')
    title = data_dict["title"]
    setTextOrMarkMissing(elementTitle, title)

    # Put notes in abstract
    elementAbstract = getElement(root, './/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString')
    abstract = data_dict["notes"]
    setTextOrMarkMissing(elementAbstract, abstract)

    # Put Dataset URL in existing onlineResource
    onlineResource = getElement(root, './/gmd:CI_OnlineResource')
    url = data_dict["url"]
    name = "Dataset Home Page"
    modifyOnlineResource(onlineResource, url, name)

    # NOTE: data_dict does not contain the list of dataset resources (like URLs).  
    #       It may be possible to obtain the resource list through CKAN api calls.
    #
    # Put additional CKAN resources in copies of the onlineResource
    #for resource in other_dict["resources"]:
    #   if len(resource["url"]) > 0:
    #       onlineResource = getElement(root, './/gmd:CI_OnlineResource', True)
    #       url = resource["url"]
    #       name = resource["name"]
    #       description = resource["description"]
    #       modifyOnlineResource(onlineResource, url, name, description)

    # Put author and author_email in pointOfContact
    contact = getElement(root, './/gmd:citedResponsibleParty')
    author = data_dict["author"]
    author_email = data_dict["author_email"]
    modifyContact(contact, author, author_email, "author")

    # Return ISO record as a string
    recordAsISO = ElementTree.tostring(root, pretty_print=True)
    return recordAsISO


def getFileName(data_dict):
    fileName = data_dict["name"] + "_" + data_dict["id"] + ".xml"
    return fileName


def exportToISO(data_dict, exportFolder):
    xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>\n'
    isoRecord = transformToISO(data_dict)
    xmlOutput = xmlHeader + isoRecord
    
    outputFile = getFileName(data_dict)
    outputFilePath = exportFolder + '/' + outputFile
    log.debug("Exported dataset to output file: " + outputFilePath)

    # Write the ISO record to a file 
    f = open(outputFilePath, 'w')
    f.write(xmlOutput)
    f.close()

    return outputFile

