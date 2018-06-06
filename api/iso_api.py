#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

import iso_util as iso
import xml_util as xml
import datacite_input as datacite
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
     'supportContact'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact',
     'resourceType'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "Resource Type")]/../../../../gmd:keyword/gco:CharacterString',
     'legalConstraints'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
     'accessConstraints'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',

     'citation'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:credit/gco:CharacterString',
     'keyword'             : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "GCMD")]/../../../../gmd:keyword',

     'spatialRepType'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialRepresentationType',
     'spatialResolution'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution',
     'topicCategory'       : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory',
     'geoExtent'           : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement',
     'temporalExtent'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent',
     'temporalResolution'  : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:description/gco:CharacterString',

     'relatedLink'         : '/gmd:MD_Metadata/gmd:metadataExtensionInfo',
     'alternateTitle'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:alternateTitle',
     'resourceVersion'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:edition',
     'progressCode'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:status/gmd:MD_ProgressCode',
     'resourceFormat'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceFormat',
     'softwareLanguage'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:environmentDescription/gco:CharacterString',
     'additionalInfo'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:supplementalInformation',
     'distributor'         : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor',
     'distributionFormat'  : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat',
     'assetSize'           : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions',
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

    # - Metadata Record ID: not repeatable
    xml.setElementValue(root, parentXPaths['fileIdentifier'], record['metadata_id'])

    # - ISO Asset Type (default value: dataset): not repeatable
    if record['asset_type']:
        xml.setElementValue(root, parentXPaths['assetType'], record['asset_type'], True)

    # - Metadata Point of Contact: not repeatable
    element = xml.getElement(root, parentXPaths['metadataContact'])
    iso.modifyContactData(element, record['metadata_contact'], 'pointOfContact')

    # - Metadata Date (not repeatable): Use current time if not present in the record. 
    if 'metadata_date' in record:
        xml.setElementValue(root, parentXPaths['metadataDate'], record['metadata_date'])
    else:
        currentTime = datetime.now().isoformat()
        xml.setElementValue(root, parentXPaths['metadataDate'], currentTime)


    # - Landing Page: not repeatable
    xml.setElementValue(root, parentXPaths['landingPage'], record['landing_page'])

    # - Title: not repeatable
    xml.setElementValue(root, parentXPaths['title'], record['title'])

    # - Publication Date: not repeatable
    xml.setElementValue(root, parentXPaths['publicationDate'], record['publication_date'])

    # - Author
    authors = record['author']
    for author in authors:
        iso.appendContactData(citedContactParent, emptyContactElement, author, 'author')

    # - Publisher
    iso.appendContactData(citedContactParent, emptyContactElement, record['publisher'], 'publisher')

    # - Abstract: not repeatable
    xml.setElementValue(root, parentXPaths['abstract'], record['abstract'])

    # - Resource Support Contact
    element = xml.getElement(root, parentXPaths['supportContact'])
    iso.modifyContactData(element, record['resource_support'], 'pointOfContact')

    # - DataCite Resource Type: not repeatable
    xml.setElementValue(root, parentXPaths['resourceType'], record['resource_type'])

    # - Legal Constraints: not repeatable
    xml.setElementValue(root, parentXPaths['legalConstraints'], record['legal_constraints'])

    # - Access Constraints: not repeatable
    xml.setElementValue(root, parentXPaths['accessConstraints'], record['access_constraints'])


    return root


    #############################
    #    RECOMMENDED FIELDS
    #############################
def transformDSETRecommendedFields(root, emptyContactElement, citedContactParent, record):

    # - Other Responsible Individual/Organization: repeatable
    if 'other_responsible_party' in record:
        parties = record['other_responsible_party']
        for party in parties:
            iso.appendContactData(citedContactParent, emptyContactElement, party)

    # - Citation: not repeatable
    if 'citation' in record:
        element = xml.getElement(root, parentXPaths['citation'])
        xml.setTextOrMarkMissing(element, record['citation'])

    # - Science Support Contact: repeatable
    if 'science_support' in record:
        parties = record['science_support']
        for party in parties:
            elementCopy = xml.getElement(root, parentXPaths['supportContact'], True)
            iso.modifyContactData(elementCopy, party, 'principalInvestigator')

    # - Keywords: repeatable
    if 'keywords' in record:
        keywordElement, keywordParent = xml.cutElement(root, parentXPaths['keyword'])
        iso.addKeywords(keywordElement, keywordParent, record['keywords'])

    # - Keyword Vocabulary:   Not included at this point.
    
    # - Reference System:  potentially very complex, not shown in DASH Search, not included at this point.

    # - Spatial Representation: repeatable
    if 'spatial_representation' in record:
        childXPath = 'gmd:MD_SpatialRepresentationTypeCode'
        valueList = record['spatial_representation']
        setCodeList = True
        xml.addChildList(root, parentXPaths['spatialRepType'], childXPath, valueList, setCodeList)
    else:
        xml.cutElement(root, parentXPaths['spatialRepType'])

    # - Spatial Resolution: repeatable
    if 'spatial_resolution' in record:
        iso.addSpatialResolutionDistances(root, parentXPaths['spatialResolution'], record['spatial_resolution'])
    else:
        xml.cutElement(root, parentXPaths['spatialResolution'])

    # - ISO Topic Category: repeatable
    if 'topic_category' in record:
        childXPath = 'gmd:MD_TopicCategoryCode'
        valueList = record['topic_category']
        xml.addChildList(root, parentXPaths['topicCategory'], childXPath, valueList)
    else:
        xml.cutElement(root, parentXPaths['topicCategory'])

    # - GeoLocation: not repeatable
    if 'geolocation' in record:
        bboxElement = xml.getElement(root, parentXPaths['geoExtent'])
        iso.modifyBoundingBox(bboxElement, record['geolocation'])
    else:
        xml.cutElement(root, parentXPaths['geoExtent'])

    # - Temporal Coverage: not repeatable
    if 'temporal_coverage' in record:
        extentElement = xml.getElement(root, parentXPaths['temporalExtent'])
        iso.modifyTemporalExtent(extentElement, record['temporal_coverage'])
    else:
        xml.cutElement(root, parentXPaths['temporalExtent'])

    # - Temporal Resolution: not repeatable
    if 'temporal_resolution' in record:
        xml.setElementValue(root, parentXPaths['temporalResolution'], record['temporal_resolution'])

    # - Vertical Extent: potentially very complicated in ISO 19139; not included at this point. 

    return root


def transformDSETOptionalFields(root, record):

    # //OPTIONAL FIELDS
    # - Related Link: repeatable
    if 'related_link' in record:
        emptyLinkElement, parent, originalIndex = xml.cutElement(root, parentXPaths['relatedLink'], True)
        indexCounter = 0
        for link in record['related_link']:
            elementCopy = xml.copyElement(emptyLinkElement)
            onlineResourceChild = xml.getElement(elementCopy, 'gmd:MD_MetadataExtensionInformation/gmd:extensionOnLineResource/gmd:CI_OnlineResource')
            name = link['name']
            url = link['linkage']
            description = link['description']
            iso.modifyOnlineResource(onlineResourceChild, url, name, description)
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['relatedLink'])

    # - Alternate Identifier: repeatable
    if 'alternate_identifier' in record:
        emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['alternateTitle'], True)
        indexCounter = 0
        for title in record['alternate_identifier']:
            elementCopy = xml.copyElement(emptyElement)
            xml.setElementValue(elementCopy, 'gco:CharacterString', title)
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['alternateTitle'])

    # - Resource Version: not repeatable
    if 'resource_version' in record:
        versionElement = xml.getElement(root, parentXPaths['resourceVersion'])
        xml.setElementValue(versionElement, 'gco:CharacterString', record['resource_version'])
    else:
        xml.cutElement(root, parentXPaths['resourceVersion'])

    # - Progress: not repeatable
    if 'progress' in record:
        setProgressCode = True
        progressElement = xml.getElement(root, parentXPaths['progressCode'])
        xml.setTextOrMarkMissing(progressElement, record['progress'], setProgressCode)
    else:
        xml.cutElement(root, parentXPaths['resourceVersion'])

    # - Resource Format: repeatable
    if 'resource_format' in record:
        emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['resourceFormat'], True)
        indexCounter = 0
        for format in record['resource_format']:
            elementCopy = xml.copyElement(emptyElement)
            xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:name/gco:CharacterString', format['name'])
            # "format" entry is optional
            xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:version/gco:CharacterString', format.get('version', []))
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['resourceFormat'])

    # - Software Implementation Language: not repeatable
    if 'software_implementation_language' in record:
        languageElement = xml.getElement(root, parentXPaths['softwareLanguage'])
        xml.setTextOrMarkMissing(languageElement, record['software_implementation_language'])
    else:
        xml.cutElement(root, parentXPaths['softwareLanguage'])

    # - Additional Information: not repeatable
    if 'additional_information' in record:
        informationElement = xml.getElement(root, parentXPaths['additionalInfo'])
        xml.setElementValue(informationElement, 'gco:CharacterString', record['additional_information'])
    else:
        xml.cutElement(root, parentXPaths['additionalInfo'])

    # - Distributor: not repeatable
    if 'distributor' in record:
        distributorElement = xml.getElement(root, parentXPaths['distributor'])
        contactElement = xml.getElement(distributorElement, 'gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty')
        iso.modifyContactData(contactElement, record['distributor'], 'distributor')
    else:
        xml.cutElement(root, parentXPaths['distributor'])

    # - Distribution Format: repeatable
    if 'distribution_format' in record:
        emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['distributionFormat'], True)
        indexCounter = 0
        for format in record['distribution_format']:
            elementCopy = xml.copyElement(emptyElement)
            xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:name/gco:CharacterString', format)
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['distributionFormat'])

    # - Asset Size: not repeatable
    if 'asset_size_MB' in record:
        sizeElement = xml.getElement(root, parentXPaths['assetSize'])
        xml.setElementValue(sizeElement, 'gmd:MD_DigitalTransferOptions/gmd:transferSize/gco:Real', record['asset_size_MB'])
    else:
        xml.cutElement(root, parentXPaths['assetSize'])

    # - Author Identifier: currently not well defined for "old ISO".

    return root





def transformDataCiteToISO(record, templateFileISO, roleMapping):
    # Load the ISO template file as an XML element tree
    root = xml.getXMLTree(templateFileISO)

    # Put DOI in fileIdentifier
    xml.setElementValue(root, parentXPaths['fileIdentifier'], record['doi'])

    # Put current time in dateStamp
    currentTime = datetime.now().isoformat()
    xml.setElementValue(root, parentXPaths['metadataDate'], currentTime)

    # Put resourceTypeGeneral in hierarchyLevelName
    if record.has_key("resourceTypeGeneral"):
        xml.setElementValue(root, parentXPaths['resourceType'], record['resourceTypeGeneral'])

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
    xml.setElementValue(root, parentXPaths['publicationDate'], record["publicationYear"])

    # Make DOI URL the Landing Page
    url = "http://dx.doi.org/" + record["doi"]
    xml.setElementValue(root, parentXPaths['landingPage'], url)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifier", [])
    for relatedIdentifier in relatedIdentifierList:
        namePart, typePart, urlPart = datacite.getRelatedIdentifierParts(relatedIdentifier)
        if typePart == "URL":
            online = xml.getElement(root, parentXPaths['relatedLink'], True)
            iso.modifyOnlineResource(online, urlPart, namePart)

    # Add "subject" keywords.  Fill existing element first, then create copies.
    if record.has_key("subject"):
        keywordElement, keywordParent = xml.cutElement(root, parentXPaths['keyword'])
        iso.addKeywords(keywordElement, keywordParent, record['subject'])

    # Cut out the template's citedContact element, so we can paste in multiple copies of it later.
    emptyContactElement, contactParent = xml.cutElement(root, parentXPaths['citedContact'])

    # Add creators as authors.  Fill existing element first, then create copies.
    creatorList = record["creator"]
    for creator in creatorList:
        iso.appendContactData(contactParent, emptyContactElement, {"name": creator}, 'author')

    # Add contributors
    contributorList = record.get("contributor", [])
    contributorTypeList = record.get("contributorType", [])
    for i in range(len(contributorList)):
        name = contributorList[i]
        roleDataCite = contributorTypeList[i]
        roleISO = roleMapping[roleDataCite]
        if roleISO == 'pointOfContact':
            # Insert Resource Support Contact
            element = xml.getElement(root, parentXPaths['supportContact'])
            iso.modifyContactData(element, {"name": name}, 'pointOfContact')
        else:
            iso.appendContactData(contactParent, emptyContactElement, {"name": name}, roleISO)

    # Add publisher
    publisher = record.get("publisher", None)
    if publisher:
        #contact = xml.getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', True)
        #iso.modifyContact(contact, publisher, "", "publisher")
        iso.appendContactData(contactParent, emptyContactElement, {"name": publisher}, 'publisher')

    # Return ISO record and record identifier
    recordAsISO = xml.toString(root)
    return recordAsISO, record["doi"]

