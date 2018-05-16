#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

import iso_util as iso
import xml_util as xml
import datacite

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


parentXPaths = {
     'supportContact'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty',
     'metadataContact'     : '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty',
     'citedContact'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty',
     'resourceType'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString',
     'resourceHomePage'    : ['/gmd:MD_Metadata/gmd:dataSetURI',
                              '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:code'],
     'legalConstraints'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation',
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



def transformToISO(record, templateFileISO):
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
        namePart, typePart, urlPart = datacite.getRelatedIdentifierParts(relatedIdentifier)
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

