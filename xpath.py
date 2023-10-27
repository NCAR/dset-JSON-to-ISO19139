import argparse
import sys
from lxml import etree as ElementTree  # ISO XML parser

import os.path
from pathlib import Path

__version_info__ = ('2022', '01', '27')
__version__ = '-'.join(__version_info__)

PROGRAM_DESCRIPTION = '''
    A utility for extracting xml tag values from stdin or a directory with files.
 '''

xpaths = {"resourceType": ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords' +
                           '/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString'),
          "geoExtent": ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent' +
                        '/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox'),
          "timeExtent": ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent' +
                         '/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent'),
          "resourceFormat": '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceFormat',
          }

childXPaths = {
    'individual': 'gmd:individualName/gco:CharacterString',
    'organisation': 'gmd:organisationName/gco:CharacterString',
    'roleCode': 'gmd:role/gmd:CI_RoleCode',
    'keyword': 'gmd:keyword/gco:CharacterString',
    'formatName': 'gmd:MD_Format/gmd:name/gco:CharacterString'
}

# We need XML namespace mappings in order to search the ISO element tree
ISO_NAMESPACES = {'gmd': 'http://www.isotc211.org/2005/gmd',
                  'xlink': 'http://www.w3.org/1999/xlink',
                  'gco': 'http://www.isotc211.org/2005/gco',
                  'gml': 'http://www.opengis.net/gml'}


def checkDirectoryExistence(directoryPath, directoryType):
    """ generate an error if directory does not exist. """
    if not os.path.isdir(directoryPath):
        message = directoryType + ' does not exist: %s\n' % directoryPath
        parser.error(message)


class PrintHelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


#
# Tree-wide operations
#
def getXMLTree(source):
    try:
        etree = ElementTree.parse(source)
        root = etree.getroot()
    except Exception:
        print(f"Unable to parse {source}")
        root = None
    return root


def getElementsMatchingRole(roleString, contactXPath, roleCodeXPath, xml_tree):
    """ Get all XML contact elements matching a specific role for the given contact XPath.
    """
    matchingContactElements = []
    contactElements = xml_tree.xpath(contactXPath, namespaces=ISO_NAMESPACES)

    for contactElement in contactElements:
        roleCodeElements = contactElement.xpath(roleCodeXPath, namespaces=ISO_NAMESPACES)

        if roleCodeElements and roleCodeElements[0].get('codeListValue') == roleString:
            matchingContactElements.append(contactElement)

    return matchingContactElements


def getFirstChildTextForRole(roleString, contactXPath, childXPath, roleCodeXPath, xml_tree):
    """ Get child string from the first matching role found at the given contact XPath.
    """
    foundTextValue = ''

    matchingContactElements = getElementsMatchingRole(roleString, contactXPath, roleCodeXPath, xml_tree)

    if matchingContactElements:
        foundText = matchingContactElements[0].findtext(childXPath, namespaces=ISO_NAMESPACES)

        if foundText:
            foundTextValue = foundText

    return foundTextValue


def printPublisher(file):
    citedContact = '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation' \
                   '/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty'
    elementsToSearch = [childXPaths['individual'], childXPaths['organisation']]
    publisher_text = []

    tree = getXMLTree(file)
    if tree is not None:
        for element in elementsToSearch:
            publisher_text = getFirstChildTextForRole('publisher', citedContact, element, childXPaths['roleCode'], tree)
            if publisher_text:
                print(str(publisher_text), file=sys.stdout)
                break
        if len(publisher_text) == 0:
            print(f"Warning: publisher string not found for {file}")


def getChildTextList(parentXPath, childXPath, xml_tree):
    """ Loop over children of a parent XPath and return the text associated with all child elements.
        If no children are found or no child element has text, return the empty list.
    """
    childTextList = []
    parentElements = xml_tree.xpath(parentXPath, namespaces=ISO_NAMESPACES)

    for parentElement in parentElements:
        childElements = parentElement.xpath(childXPath, namespaces=ISO_NAMESPACES)

        for childElement in childElements:
            if childElement.text:
                childTextList.append(childElement.text)

    return childTextList


def printResourceFormats(file):
    tree = getXMLTree(file)
    if tree is not None:
        formats = getChildTextList(xpaths["resourceFormat"], childXPaths["formatName"], tree)
        for fmt in formats:
            print(fmt, file=sys.stdout)
        # Indicate that the file is missing format information
        if not formats:
            #print(f"UNDEFINED FORMAT in {file}", file=sys.stdout)
            print(f"UNDEFINED FORMAT", file=sys.stdout)



def getDataCiteResourceType(thesaurusXPath, keywordXPath, xml_tree):
    """ Get the first resource type keyword by searching thesaurus titles containing "Resource Type".
        Strip whitespace and return lowercase version of string.
    """
    resourceType = ''
    for thesaurus in xml_tree.xpath(thesaurusXPath, namespaces=ISO_NAMESPACES):
        if "Resource Type" in thesaurus.text:
            keywordElement = thesaurus.getparent().getparent().getparent().getparent()

            for keyword in keywordElement.xpath(keywordXPath, namespaces=ISO_NAMESPACES):
                if keyword.text:
                    resourceType = keyword.text.strip().lower()
                    # Substitute ambiguous keywords with more understandable versions.
                    if resourceType == 'text':
                        resourceType = 'publication'

                    # Return the first match found.
                    return resourceType

    return resourceType


def isDatasetRecord(tree):
    resourceType = getDataCiteResourceType(xpaths["resourceType"], childXPaths["keyword"], tree)
    return resourceType.lower() == 'dataset'


def printXPathExists(file, xpath_list, checkNonDatasets=True):
    tree = getXMLTree(file)
    isIsoRecord = tree is not None
    isDataset = isIsoRecord and isDatasetRecord(tree)

    if not isIsoRecord:
        message = "not_a_iso_record"
    elif not (isDataset or checkNonDatasets):
        message = "not_a_dataset_record"
    elif isDataset or checkNonDatasets:
        exists = True
        for xpath in xpath_list:
            xmlElement = tree.xpath(xpath, namespaces=ISO_NAMESPACES)
            if not xmlElement:
                exists = False
        if exists:
            message = "xpath_exists"
        else:
            message = "xpath_missing"
    else:
        # If this statement is reached, there is a logic error.
        assert False

    # print out the XML file name as a something that could be stripped off later.
    print(f'{message}  {file}', file=sys.stdout)


#
#  Parse and validate command line options.
#
programHelp = PROGRAM_DESCRIPTION + __version__
parser = PrintHelpOnErrorParser(description=programHelp, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--inputDir', nargs=1, help="base dir for XML files")
parser.add_argument('--file', nargs=1, help="XML file to search")
parser.add_argument('--attribute', nargs=1, help="limit output to elements with the given attribute value")
parser.add_argument('--version', action='version', version="%(prog)s (" + __version__ + ")")
args = parser.parse_args()


###
### START OF MAIN PROGRAM
###

def performOperation(file):
    """ Change this Highest-level function to define the program's current operation.
    """
    # printPublisher(file)
    printResourceFormats(file)

    # Decide whether to print stats for non-dataset records, which can't have spatio-temporal information.
    #checkNonDatasets = False
    #checkNonDatasets = True

    # printXPathExists(file, [xpaths['geoExtent']], checkNonDatasets)         # check geographical extent existence
    # printXPathExists(file, [xpaths['timeExtent']], checkNonDatasets)      # check temporal extent existence
    # printXPathExists(file, [xpaths['resourceFormat']], checkNonDatasets)  # check resource format existence

    # check spatio-temporal extent existence
    #printXPathExists(file, [xpaths['timeExtent'], xpaths['geoExtent']], checkNonDatasets)

    # check resource format existence
    #printXPathExists(file, [xpaths['resourceFormat']], checkNonDatasets)


# readSTDIN = (args.inputDir == None)
# if readSTDIN:
#     tree = getXMLTree(sys.stdin)
readFile = (args.file is not None)
if readFile:
    performOperation(args.file[0])
else:
    checkDirectoryExistence(args.inputDir[0], 'Input directory')
    for path in Path(args.inputDir[0]).rglob('*.xml'):
        performOperation(path.as_posix())
