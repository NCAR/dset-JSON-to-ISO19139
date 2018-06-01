#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

import iso_util as iso
import xml_util as xml
import json_datacite
from datetime import datetime

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
     'citedContact'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty',
     'abstract'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
     'supportContact'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty',
     'resourceType'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "Resource Type")]/../../../../gmd:keyword/gco:CharacterString',
     'legalConstraints'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
     'accessConstraints'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',

     'citation'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:credit/gco:CharacterString',
     'keyword'             : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "GCMD")]/../../../../gmd:keyword',

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


def transformDSETToISO(record, pathToTemplateFileISO):
    """ Transform a JSON record to ISO 19139 XML using a XML template file. """
    root = xml.getXMLTree(pathToTemplateFileISO)

    # Cut out the template's citedContact element, so we can paste in multiple copies of it later.
    emptyContactElement, contactParent = xml.cutElement(root, parentXPaths['citedContact'])

    root = transformDSETRequiredFields(root, emptyContactElement, contactParent, record)

    root = transformDSETRecommendedFields(root, emptyContactElement, contactParent, record)

    root = transformDSETOptionalFields(root, record)

    recordAsISO = xml.toString(root)
    return recordAsISO



    #########################
    #  DSET REQUIRED FIELDS
    #########################

def transformDSETRequiredFields(root, emptyContactElement, citedContactParent, record):

    # - Metadata Record ID
    iso.setElementValue(root, parentXPaths['fileIdentifier'], record['metadata_id'])

    # - ISO Asset Type (default value: dataset)
    if record['asset_type']:
        iso.setElementValue(root, parentXPaths['assetType'], record['asset_type'], True)

    # - Metadata Point of Contact
    element = xml.getElement(root, parentXPaths['metadataContact'])
    iso.modifyContactData(element, record['metadata_contact'], 'pointOfContact')

    # - Metadata Date
    iso.setElementValue(root, parentXPaths['metadataDate'], record['metadata_date'])

    # - Landing Page
    iso.setElementValue(root, parentXPaths['landingPage'], record['landing_page'])

    # - Title
    iso.setElementValue(root, parentXPaths['title'], record['title'])

    # - Publication Date
    iso.setElementValue(root, parentXPaths['publicationDate'], record['publication_date'])

    # - Author
    authors = record['author']
    for author in authors:
        iso.appendContactData(citedContactParent, emptyContactElement, author, 'author')

    # - Publisher
    iso.appendContactData(citedContactParent, emptyContactElement, record['publisher'], 'publisher')

    # - Abstract
    iso.setElementValue(root, parentXPaths['abstract'], record['abstract'])

    # - Resource Support Contact
    element = xml.getElement(root, parentXPaths['supportContact'])
    iso.modifyContactData(element, record['resource_support'], 'pointOfContact')

    # - DataCite Resource Type
    iso.setElementValue(root, parentXPaths['resourceType'], record['resource_type'])

    # - Legal Constraints
    iso.setElementValue(root, parentXPaths['legalConstraints'], record['legal_constraints'])

    # - Access Constraints
    iso.setElementValue(root, parentXPaths['accessConstraints'], record['access_constraints'])


    return root


    #############################
    #    RECOMMENDED FIELDS
    #############################
def transformDSETRecommendedFields(root, emptyContactElement, citedContactParent, record):

    # - Other Responsible Individual/Organization
    if 'other_responsible_party' in record:
        parties = record['other_responsible_party']
        for party in parties:
            iso.appendContactData(citedContactParent, emptyContactElement, party)

    # - Citation
    if 'citation' in record:
        element = xml.getElement(root, parentXPaths['citation'])
        xml.setTextOrMarkMissing(element, record['citation'])

    # - Science Support Contact
    if 'science_support' in record:
        parties = record['science_support']
        for party in parties:
            elementCopy = xml.getElement(root, parentXPaths['supportContact'], True)
            iso.modifyContactData(elementCopy, party, 'principalInvestigator')

    # - Keywords
    if 'keywords' in record:
        keywordElement, keywordParent = xml.cutElement(root, parentXPaths['keyword'])
        iso.addKeywords(keywordElement, keywordParent, record['keywords'])

    # - Keyword Vocabulary:   Not included at this point.
    
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
    return root


def transformDSETOptionalFields(root, record):

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

    return root





def transformDataCiteToISO(record, templateFileISO):
    # Load the ISO template file as an XML element tree
    root = xml.getXMLTree(templateFileISO)

    # Put DOI in fileIdentifier
    iso.setElementValue(root, parentXPaths['fileIdentifier'], record['doi'])

    # Put current time in dateStamp
    currentTime = datetime.now().isoformat()
    iso.setElementValue(root, parentXPaths['metadataDate'], currentTime)

    # Put resourceTypeGeneral in hierarchyLevelName
    if record.has_key("resourceTypeGeneral"):
        #hierarchyLevelName = xml.getElement(root, './/gmd:hierarchyLevelName/gco:CharacterString')
        #hierarchyLevelName.text = record["resourceTypeGeneral"]
        # - DataCite Resource Type
        iso.setElementValue(root, parentXPaths['resourceType'], record['resourceTypeGeneral'])

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
    iso.setElementValue(root, parentXPaths['publicationDate'], record["publicationYear"])

    # Make DOI URL the Landing Page
    url = "http://dx.doi.org/" + record["doi"]
    iso.setElementValue(root, parentXPaths['landingPage'], url)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifier", [])
    for relatedIdentifier in relatedIdentifierList:
        namePart, typePart, urlPart = json_datacite.getRelatedIdentifierParts(relatedIdentifier)
        if typePart == "URL":
            online = xml.getElement(root, parentXPaths['relatedLink'], True)
            iso.modifyOnlineResource(online, urlPart, namePart)

    # Add "subject" keywords.  Fill existing element first, then create copies.
    if record.has_key("subject"):
        #     subjectList = record["subject"]
        #     for i in range(len(subjectList)):
        #         keyword = xml.getElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword', i > 0)
        #         keyword[0].text = subjectList[i]
        # else:
        #     keyword = xml.getElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword', False)
        #     keyword.getparent().remove(keyword)
        keywordElement, keywordParent = xml.cutElement(root, parentXPaths['keyword'])
        iso.addKeywords(keywordElement, keywordParent, record['subject'])

    # Cut out the template's citedContact element, so we can paste in multiple copies of it later.
    emptyContactElement, contactParent = xml.cutElement(root, parentXPaths['citedContact'])

    # Add creators.  Fill existing element first, then create copies.
    creatorList = record["creator"]
    #for i in range(len(creatorList)):
    #    contact = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', i > 0)
    #    iso.modifyContact(contact, creatorList[i], "", "creator")
    for creator in creatorList:
        iso.appendContactData(contactParent, emptyContactElement, {"name": creator}, 'creator')

    # Add contributors
    contributorList = record.get("contributor", [])
    contributorTypeList = record.get("contributorType", [])
    for i in range(len(contributorList)):
        name = contributorList[i]
        role = contributorTypeList[i]
        if role == 'ContactPerson':
            # Insert Resource Support Contact
            element = xml.getElement(root, parentXPaths['supportContact'])
            iso.modifyContactData(element, {"name": name}, 'pointOfContact')
            # Insert Metadata Contact
            #element = xml.getElement(root, parentXPaths['metadataContact'])
            #iso.modifyContactData(element, {"name": name}, 'pointOfContact')
        else:
            iso.appendContactData(contactParent, emptyContactElement, {"name": name}, role)

    # Add publisher
    publisher = record.get("publisher", None)
    if publisher:
        #contact = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', True)
        #iso.modifyContact(contact, publisher, "", "publisher")
        iso.appendContactData(contactParent, emptyContactElement, {"name": publisher}, 'publisher')

    # Return ISO record and record identifier
    recordAsISO = xml.toString(root)
    return recordAsISO, record["doi"]

