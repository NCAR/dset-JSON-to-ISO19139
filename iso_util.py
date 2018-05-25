#
#  Code for modifying subelements in a ISO 19139 XML file.
#

import xml_util as xml

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


childXPaths =  {
     'individual'  : './/gmd:individualName/gco:CharacterString',
     'position'    : './/gmd:positionName/gco:CharacterString',
     'organization': './/gmd:organisationName/gco:CharacterString',
     'email'       : './/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString',
     'roleCode'    : './/gmd:role/gmd:CI_RoleCode',
     'keyword'     : 'gmd:keyword/gco:CharacterString',
     'repTypeCode' : 'gmd:MD_SpatialRepresentationTypeCode',
     'distance'    : 'gco:Distance',
     'real'        : 'gco:Real',
     'string'      : 'gco:CharacterString',
     'stringURL'   : 'gco:CharacterString[starts-with(.,"http://") or starts-with(.,"https://")]',
     'linkage'     : 'gmd:linkage/gmd:URL',
     'name'        : 'gmd:name/gco:CharacterString',
     'description' : 'gmd:description/gco:CharacterString',
     'extentBegin' : 'gml:TimePeriod/gml:beginPosition',
     'extentEnd'   : 'gml:TimePeriod/gml:endPosition',
   } 

def setElementValue(xmlTreeRoot, xPath, value, setCodeListValue = False):
    """ Set the text value, and optionally the code list value, of an element in an XML tree. """
    element = xml.getElement(xmlTreeRoot, xPath)
    xml.setTextOrMarkMissing(element, value)
    if setCodeListValue:
        element.attrib['codeListValue'] = value


# Modify contents of an "onLineResource" ISO element
def modifyOnlineResource(transferElement, url, name='', description=''):
    elementURL = xml.getElement(transferElement, './/gmd:linkage/gmd:URL')
    xml.setTextOrMarkMissing(elementURL, url)

    elementName = xml.getElement(transferElement, './/gmd:name/gco:CharacterString')
    xml.setTextOrMarkMissing(elementName, name)

    elementDescription = xml.getElement(transferElement, './/gmd:description/gco:CharacterString')
    xml.setTextOrMarkMissing(elementDescription, description)


# Modify contents of a "contact" ISO element
def modifyContact(contactElement, name, email, contactType):
    elementName = xml.getElement(contactElement, './/gmd:individualName/gco:CharacterString')
    xml.setTextOrMarkMissing(elementName, name)

    elementEmail = xml.getElement(contactElement, './/gmd:electronicMailAddress/gco:CharacterString')
    xml.setTextOrMarkMissing(elementEmail, email)

    elementRole = xml.getElement(contactElement, './/gmd:CI_RoleCode')
    elementRole.attrib['codeListValue'] = contactType


def modifyContactData(contactElement, contactData, impliedRoleValue = None):
    """ Modify contents of a "contact" ISO element, a.k.a ResponsibleParty element. """

    #  For some contact elements, a specific role value is implied.  Set this value if given.
    if impliedRoleValue:
        contactData['role'] = impliedRoleValue

    nameValue = contactData.get('name', "")
    element = xml.getElement(contactElement, childXPaths['individual'])
    xml.setTextOrMarkMissing(element, nameValue)

    positionValue = contactData.get('position', "")
    element = xml.getElement(contactElement, childXPaths['position'])
    xml.setTextOrMarkMissing(element, positionValue)

    organizationValue = contactData.get('organization', "")
    element = xml.getElement(contactElement, childXPaths['organization'])
    xml.setTextOrMarkMissing(element, organizationValue)

    emailValue = contactData.get('email', "")
    element = xml.getElement(contactElement, childXPaths['email'])
    xml.setTextOrMarkMissing(element, emailValue)

    roleValue = contactData.get('role', "")
    element = xml.getElement(contactElement, childXPaths['roleCode'])
    xml.setTextOrMarkMissing(element, roleValue)
    element.attrib['codeListValue'] = roleValue


def appendContactData(citedContactParent, emptyContactElement, contactData, impliedRoleValue = None):
    """ Append a contact element to the CitedContact section of the XML document. """
    elementCopy = xml.copyElement(emptyContactElement)
    modifyContactData(elementCopy, contactData, impliedRoleValue)
    citedContactParent.append(elementCopy)


def addKeywords(keywordElement, keywordParent, keywordList):
    """ Add GCMD Keyword elements, one element per list item, to the keyword section of the XML document. """
    for keyword in reversed(keywordList):
        elementCopy = xml.copyElement(keywordElement)
        stringElement = xml.getElement(elementCopy, childXPaths['string'])
        xml.setTextOrMarkMissing(stringElement, keyword)
        keywordParent.insert(0, elementCopy)


