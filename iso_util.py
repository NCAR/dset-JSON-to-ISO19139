#
#  Code for modifying subelements in a ISO 19139 XML file.
#

import xml_util as xml

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


childXPaths =  {
     'individual'  : 'gmd:individualName/gco:CharacterString',
     'position'    : 'gmd:positionName/gco:CharacterString',
     'organization': 'gmd:organisationName/gco:CharacterString',
     'email'       : 'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString',
     'keyword'     : 'gmd:keyword/gco:CharacterString',
     'roleCode'    : 'gmd:role/gmd:CI_RoleCode',
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

    #elementEmail = xml.getElement(contactElement, './/gmd:electronicMailAddress/gco:CharacterString')
    #xml.setTextOrMarkMissing(elementEmail, email)

    elementRole = xml.getElement(contactElement, './/gmd:CI_RoleCode')
    elementRole.attrib['codeListValue'] = contactType

# Modify contents of a "contact" ISO element
def modifyContactData(contactElement, contactData):
    """ Modify contents of a "contact" ISO element, a.k.a ResponsibleParty element. """
    if 'name' in contactData:    
        element = xml.getElement(contactElement, childXPaths['individual'])
        xml.setTextOrMarkMissing(element, contactData['name'])

    if 'position' in contactData:    
        element = xml.getElement(contactElement, childXPaths['position'])
        xml.setTextOrMarkMissing(element, contactData['position'])

    if 'organization' in contactData:    
        element = xml.getElement(contactElement, childXPaths['organization'])
        xml.setTextOrMarkMissing(element, contactData['organization'])

    if 'email' in contactData:    
        element = xml.getElement(contactElement, childXPaths['email'])
        xml.setTextOrMarkMissing(element, contactData['email'])

    if 'role' in contactData:    
        element = xml.getElement(contactElement, childXPaths['roleCode'])
        xml.setTextOrMarkMissing(element, contactData['role'])
        element.attrib['codeListValue'] = contactData['role']


