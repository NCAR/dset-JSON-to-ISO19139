#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

import iso_util as iso
import xml_util as xml
import json_input

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


parentXPaths = {
     'fileIdentifier'      : '/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
     'assetType'           : '/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode',
     'metadataContact'     : '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty',
     'metadataDate'        : '/gmd:MD_Metadata/gmd:dateStamp/gco:DateTime',
     'landingPage'         : '/gmd:MD_Metadata/gmd:dataSetURI/gco:CharacterString',
     'title'               : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
     'publicationDate'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
     'citedContact'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty',
     'abstract'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
     'supportContact'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty',
     'resourceType'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "Resource Type")]/../../../../gmd:keyword/gco:CharacterString',
     'legalConstraints'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
     'accessConstraints'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',


     'spatialRepType'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialRepresentationType',
     'spatialResolution'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance',
     'temporalResolution'  : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:description',
     'temporalExtent'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent',
     'relatedLink'         : '/gmd:MD_Metadata/gmd:metadataExtensionInfo/gmd:MD_MetadataExtensionInformation/gmd:extensionOnLineResource/gmd:CI_OnlineResource',
     'distributor'         : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty',
     'resourceVersion'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:edition',
     'softwareLanguage'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:environmentDescription',
     'assetSize'           : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:transferSize',
} 


def transformDSETToISO(record, templateFileISO):
    """ Transform a JSON record to ISO 19139 XML using a XML template file. """
    root = xml.getXMLTree(templateFileISO)

    #########################
    #  DSET REQUIRED FIELDS
    #########################

    # - Metadata Record ID
    element = xml.getElement(root, parentXPaths['fileIdentifier'])
    value = record['metadata_id']
    xml.setTextOrMarkMissing(element, value)

    # - ISO Asset Type (default value: dataset)
    if record['asset_type']:
        element = xml.getElement(root, parentXPaths['assetType'])
        value = record['asset_type']
        xml.setTextOrMarkMissing(element, value)
        element.attrib['codeListValue'] = value

    # - Metadata Point of Contact
    element = xml.getElement(root, parentXPaths['metadataContact'])
    value = record['metadata_contact']
    value['role'] = 'pointOfContact'
    iso.modifyContactData(element, value)

    # - Metadata Date
    element = xml.getElement(root, parentXPaths['metadataDate'])
    value = record['metadata_date']
    xml.setTextOrMarkMissing(element, value)

    # - Landing Page
    element = xml.getElement(root, parentXPaths['landingPage'])
    value = record['landing_page']
    xml.setTextOrMarkMissing(element, value)

    # - Title
    element = xml.getElement(root, parentXPaths['title'])
    value = record['title']
    xml.setTextOrMarkMissing(element, value)

    # - Publication Date
    element = xml.getElement(root, parentXPaths['publicationDate'])
    value = record['publication_date']
    xml.setTextOrMarkMissing(element, value)

    # - Author
    emptyContactElement, citedContactParent = xml.cutElement(root, parentXPaths['citedContact'])
    values = record['author']
    for value in values:
        value['role'] = 'author'
        elementCopy = xml.copyElement(emptyContactElement)
        iso.modifyContactData(elementCopy, value)
        citedContactParent.append(elementCopy)


    # - Publisher
    elementCopy = xml.copyElement(emptyContactElement)
    value = record['publisher']
    value['role'] = 'publisher'
    iso.modifyContactData(elementCopy, value)
    citedContactParent.append(elementCopy)

    # - Abstract
    element = xml.getElement(root, parentXPaths['abstract'])
    value = record['abstract']
    xml.setTextOrMarkMissing(element, value)

    # - Resource Support Contact
    element = xml.getElement(root, parentXPaths['supportContact'])
    value = record['resource_support']
    value['role'] = 'pointOfContact'
    iso.modifyContactData(element, value)

    # - DataCite Resource Type
    element = xml.getElement(root, parentXPaths['resourceType'])
    value = record['resource_type']
    xml.setTextOrMarkMissing(element, value)

    # - Legal Constraints
    element = xml.getElement(root, parentXPaths['legalConstraints'])
    value = record['legal_constraints']
    xml.setTextOrMarkMissing(element, value)

    element = xml.getElement(root, parentXPaths['accessConstraints'])
    value = record['access_constraints']
    xml.setTextOrMarkMissing(element, value)

    # - Access Constraints
    # 
    # // RECOMMENDED FIELDS
    # - Other Responsible Individual/Organization
    # - Other Responsible Individual/Organization
    # - Other Responsible Individual/Organization Affiliation
    # - Other Responsible Individual/Organization Role / Type
    # - Citation
    # - Science Support Contact
    # - Keywords
    # - Keyword Vocabulary
    # - Reference System
    # - Spatial Representation
    # - Spatial Resolution
    # - ISO Topic Category
    # - GeoLocation
    # - Temporal Coverage
    # - Start Date
    # - End Date
    # - Temporal Resolution
    # - Vertical Extent
    # 
    # //OPTIONAL FIELDS
    # - Related Link Identifier
    # - Related Link Name
    # - Related Link Relation Type
    # - Related Link Description
    # - Alternate Identifier
    # - Resource Version
    # - Progress
    # - Resource Format
    # - Software Implementation Language
    # - Additional Information
    # - Distributor
    # - Distribution Format
    # - Asset Size
    # - Author Identifier


    recordAsISO = xml.toString(root)
    return recordAsISO






def transformDataCiteToISO(record, templateFileISO):
    # Load the ISO template file as an XML element tree
    root = xml.getXMLTree(templateFileISO)

    # Put DOI in fileIdentifier
    fileIdentifier = xml.getElement(root, './/gmd:fileIdentifier/gco:CharacterString')
    fileIdentifier.text = record["doi"]

    # Put resourceTypeGeneral in hierarchyLevelName
    if record.has_key("resourceTypeGeneral"):
        hierarchyLevelName = xml.getElement(root, './/gmd:hierarchyLevelName/gco:CharacterString')
        hierarchyLevelName.text = record["resourceTypeGeneral"]

    # Put title in title
    title = xml.getElement(root, './/gmd:CI_Citation/gmd:title/gco:CharacterString')
    title.text = xml.getFirst( record["title"] )

    # Put description in abstract
    if record.has_key("description"):
        abstract = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString')
        abstract.text = xml.getFirst( record["description"] )
    else:
        abstract = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString')
        abstract.getparent().remove(abstract)

    # Put publicationYear in CI_Citation/date
    date = xml.getElement(root, './/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date')
    date.text = record["publicationYear"]

    # Put DOI URL in existing onlineResource
    onlineParent = xml.getElement(root, './/gmd:MD_DigitalTransferOptions')
    url = "http://dx.doi.org/" + record["doi"]
    name = "Landing Page"
    iso.modifyOnlineResource(onlineParent, url, name)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifier", [])
    for relatedIdentifier in relatedIdentifierList:
        namePart, typePart, urlPart = json_input.getRelatedIdentifierParts(relatedIdentifier)
        if typePart == "URL":
            online = xml.getElement(root, './/gmd:MD_DigitalTransferOptions/gmd:onLine', True)
            iso.modifyOnlineResource(online, urlPart, namePart)

    # Add "subject" keywords.  Fill existing element first, then create copies.
    if record.has_key("subject"):
        subjectList = record["subject"]
        for i in range(len(subjectList)):
            keyword = xml.getElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword', i > 0)
            keyword[0].text = subjectList[i]
    else:
        keyword = xml.getElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword', False)
        keyword.getparent().remove(keyword)

    # Add creators.  Fill existing element first, then create copies.
    creatorList = record["creator"]
    for i in range(len(creatorList)):
        contact = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', i > 0)
        iso.modifyContact(contact, creatorList[i], "", "creator")

    # Add contributors
    contributorList = record.get("contributor", [])
    contributorTypeList = record.get("contributorType", [])
    for i in range(len(contributorList)):
        contact = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', True)
        iso.modifyContact(contact, contributorList[i], "", contributorTypeList[i])

    # Add publisher
    publisher = record.get("publisher", None)
    if publisher:
        contact = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', True)
        iso.modifyContact(contact, publisher, "", "publisher")

    # Return ISO record and record identifier
    recordAsISO = xml.toString(root)
    return recordAsISO, record["doi"]

