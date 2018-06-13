
import sys
from datetime import datetime

import api.util.xml as xml
import api.util.iso19139 as iso



roleMappingDataCiteToISO = {
      "Creator":               "author",
      "Publisher":             "publisher",
      "ContactPerson":         "pointOfContact",
      "DataCollector":         "",
      "DataCurator":           "custodian",
      "DataManager":           "custodian",
      "Distributor":           "distributor",
      "Editor":                "editor",
      "HostingInstitution":    "resourceProvider",
      "Producer":              "mediator",
      "ProjectLeader":         "principalInvestigator",
      "ProjectManager":        "",
      "ProjectMember":         "contributor",
      "RegistrationAgency":    "",
      "RegistrationAuthority": "",
      "RelatedPerson":         "contributor",
      "Researcher":            "contributor",
      "ResearchGroup":         "collaborator",
      "RightsHolder":          "rightsHolder",
      "Sponsor":               "sponsor",
      "Supervisor":            "",
      "WorkPackageLeader":     "",
      "Other":                 "contributor",
}


parentXPaths = {
     'fileIdentifier'      : '/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
     'assetType'           : '/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode',
     'metadataContact'     : '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty',
     'metadataDate'        : '/gmd:MD_Metadata/gmd:dateStamp/gco:DateTime',
     'landingPage'         : '/gmd:MD_Metadata/gmd:dataSetURI/gco:CharacterString',
     'title'               : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
     'publicationDate'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
     'citedContact'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty',
     'abstract'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract',
     'supportContact'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact',
     'resourceType'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "Resource Type")]/../../../../gmd:keyword/gco:CharacterString',
     'keyword'             : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "GCMD")]/../../../../gmd:keyword',
     'relatedLink'         : '/gmd:MD_Metadata/gmd:metadataExtensionInfo',
     'legalConstraints'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
     'accessConstraints'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',
}



def translateDataCiteRecords():
    ''' batch translate DataCite Records and save to output directory. '''

    # Get records
    records = getDataCiteRecords()

    print "##"
    print "## Translating " + str(len(records)) + " Records..."
    print "##"

    # Loop over DataCite Records
    for record in records:
        xmlOutput = translateDataCiteRecord(record)

        # Isolate the second part of a DOI identifier for the output file name
        uniqueID = recordID.split('/')[1]

        outputFilePath = 'defaultOutputRecords/' + uniqueID + '.xml'
        f = open(outputFilePath, 'w')
        f.write(xmlOutput)
        f.close()

    print '...Finished Translating Records.'


def translateDataCiteRecord(record, templateFile):
    ''' Return ISO 19139 translation for a single DataCite record. '''
    #try:
    #    recordISO, recordID = transformDataCiteToISO(record, templateFile, roleMappingDataCiteToISO)
    #except (KeyError, IndexError):
    #    print record
    #    sys.exit()
    recordISO, recordID = transformDataCiteToISO(record, templateFile, roleMappingDataCiteToISO)

    headerXML = '<?xml version="1.0" encoding="UTF-8"?>\n'
    outputXML = headerXML + recordISO
    return outputXML



def transformDataCiteToISO(record, templateFileISO, roleMapping):
    # Load the ISO template file as an XML element tree
    root = xml.getXMLTree(templateFileISO)

    # Put DOI in fileIdentifier
    assert record.has_key('doi')
    xml.setElementValue(root, parentXPaths['fileIdentifier'], record['doi'])

    # Put current time in dateStamp
    currentTime = datetime.now().isoformat()
    xml.setElementValue(root, parentXPaths['metadataDate'], currentTime)

    # Put resourceTypeGeneral in hierarchyLevelName
    assert record.has_key('resourceTypeGeneral')
    xml.setElementValue(root, parentXPaths['resourceType'], record['resourceTypeGeneral'])

    # Put title in title
    assert record.has_key('title')
    titleValue = xml.getFirst(record['title'])
    xml.setElementValue(root, parentXPaths['title'], titleValue)

    # Put description in abstract
    if record.has_key("description"):
        fullXPath = parentXPaths['abstract'] + '/gco:CharacterString'
        descriptionValue = xml.getFirst(record['description'])
        xml.setElementValue(root, fullXPath, descriptionValue )
    else:
        xml.cutElement(parentXPaths['abstract'])

    # Put publicationYear in CI_Citation/date
    xml.setElementValue(root, parentXPaths['publicationDate'], record["publicationYear"])

    # Make DOI URL the Landing Page
    url = "http://dx.doi.org/" + record["doi"]
    xml.setElementValue(root, parentXPaths['landingPage'], url)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifier", [])
    relatedLinks = []
    for relatedIdentifier in relatedIdentifierList:
        namePart, typePart, urlPart = getRelatedIdentifierParts(relatedIdentifier)
        if typePart == "URL":
            relatedLinks.append({"name": namePart, "linkage": urlPart, "description": ""})
    iso.addRelatedLinks(root, parentXPaths['relatedLink'], relatedLinks)

    # Add "subject" keywords.  Fill existing element first, then create copies.
    if record.has_key("subject"):
        iso.addKeywords(root, parentXPaths['keyword'], record['subject'])

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
        iso.appendContactData(contactParent, emptyContactElement, {"organization": publisher}, 'publisher')

    # Return ISO record and record identifier
    recordAsISO = xml.toString(root)
    return recordAsISO, record["doi"]



def getRelatedIdentifierParts(relatedIdentifier):
    """ Return the parts of a DataCite relatedIdentifier object. """
    relatedIdentifierParts = relatedIdentifier.split(":")
    namePart = "Related Resource: " + relatedIdentifierParts[0]
    typePart = relatedIdentifierParts[1]
    urlPart = ':'.join(relatedIdentifierParts[2: ])
    return namePart, typePart, urlPart

