import argparse
import sys
from lxml import etree as ElementTree  # ISO XML parser

import os.path

__version_info__ = ('2022', '01', '27')
__version__ = '-'.join(__version_info__)

PROGRAM_DESCRIPTION = '''
    A utility for extracting xml tag values from stdin or a directory with files.
 '''


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
    ''' Loop over children of a parent XPath and return the text associated with all child elements.
        If no children are found or no child element has text, return the empty list.
    '''
    childTextList = []
    parentElements = xml_tree.xpath(parentXPath, namespaces=ISO_NAMESPACES)

    for parentElement in parentElements:
        childElements = parentElement.xpath(childXPath, namespaces=ISO_NAMESPACES)

        for childElement in childElements:
            if childElement.text:
                childTextList.append(childElement.text)

    return childTextList



def printResourceFormats(file):
    resourceFormat = '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceFormat'
    formatName = 'gmd:MD_Format/gmd:name/gco:CharacterString'

    tree = getXMLTree(file)
    if tree is not None:
        formats = getChildTextList(resourceFormat, formatName, tree)
        for format in formats:
            print(format, file=sys.stdout)


# We need XML namespace mappings in order to search the ISO element tree
ISO_NAMESPACES = {'gmd': 'http://www.isotc211.org/2005/gmd',
                  'xlink': 'http://www.w3.org/1999/xlink',
                  'gco': 'http://www.isotc211.org/2005/gco',
                  'gml': 'http://www.opengis.net/gml'}

childXPaths = {
    'individual': 'gmd:individualName/gco:CharacterString',
    'organisation': 'gmd:organisationName/gco:CharacterString',
    'roleCode': 'gmd:role/gmd:CI_RoleCode',
}

#
#  Parse and validate command line options.
#
programHelp = PROGRAM_DESCRIPTION + __version__
parser = PrintHelpOnErrorParser(description=programHelp, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--inputDir', nargs=1, help="base dir for XML files")
parser.add_argument('--xpath', nargs=1, help="xpath to search for")
parser.add_argument('--attribute', nargs=1, help="limit output to elements with the given attribute value")
parser.add_argument('--version', action='version', version="%(prog)s (" + __version__ + ")")
args = parser.parse_args()


###
### START OF MAIN PROGRAM
###

readSTDIN = (args.inputDir == None)
if readSTDIN:
    tree = getXMLTree(sys.stdin)
else:
    checkDirectoryExistence(args.inputDir[0], 'Input directory')
    from pathlib import Path
    for path in Path(args.inputDir[0]).rglob('*.xml'):
        #printPublisher(path.as_posix())
        printResourceFormats(path.as_posix())

