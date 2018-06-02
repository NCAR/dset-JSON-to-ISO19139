#
# Utilities for inserting values into ISO 19139 documents
#

from lxml import etree as ElementTree       # ISO XML parser
from copy import deepcopy                   # Allows deep copy of ISO elements

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


# We need XML namespace mappings in order to search the ISO element tree
XML_NAMESPACE_MAP = {'gmd': 'http://www.isotc211.org/2005/gmd',
                     'xlink': 'http://www.w3.org/1999/xlink', 
                     'gco': 'http://www.isotc211.org/2005/gco', 
                     'gml': 'http://www.opengis.net/gml'}

def getXMLTree(templateFilePath):
    tree = ElementTree.parse(templateFilePath)
    root = tree.getroot()
    return root


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
        parent = element.getparent()
        insertIndex = parent.index(element)+1
        parent.insert(insertIndex, elementCopy)
        element = elementCopy
    return element


# Search XML element tree and cut the first matching element.
# Return the cut element and the parent it was cut from.
#
def cutElement(baseElement, elementPath):
    elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
    element = getFirst(elements)
    try:
        assert element != None
    except AssertionError:
        print "Failed to find any element matching: " + elementPath

    parent = element.getparent()
    parent.remove(element)
    #return element, parent, baseElement
    return element, parent

def copyElement(element):
    elementCopy = deepcopy(element)
    return elementCopy


def setTextOrMarkMissing(element, fillText):
    if len(fillText) > 0:
        element.text = fillText
    else:
        element.getparent().attrib['{http://www.isotc211.org/2005/gco}nilReason'] = "missing"


def toString(xml_tree):
    outputString = ElementTree.tostring(xml_tree, pretty_print=True)
    return outputString

    


