
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
      "Funder":                "funder",
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

    print("##")
    print("## Translating " + str(len(records)) + " Records...")
    print("##")

    # Loop over DataCite Records
    for record in records:
        xmlOutput = translateDataCiteRecord(record)

        # Isolate the second part of a DOI identifier for the output file name
        uniqueID = recordID.split('/')[1]

        outputFilePath = 'defaultOutputRecords/' + uniqueID + '.xml'
        f = open(outputFilePath, 'w')
        f.write(xmlOutput)
        f.close()

    print('...Finished Translating Records.')


def translateDataCiteRecord(record, templateFile):
    ''' Return ISO 19139 translation for a single DataCite record. '''
    recordISO, recordID = transformDataCiteToISO(record, templateFile, roleMappingDataCiteToISO)

    headerXML = '<?xml version="1.0" encoding="UTF-8"?>\n'
    outputXML = headerXML + recordISO.decode('utf-8')
    return outputXML



def transformDataCiteToISO(record, templateFileISO, roleMapping):
    # Load the ISO template file as an XML element tree
    root = xml.getXMLTree(templateFileISO)

    # Put DOI in fileIdentifier
    assert 'doi' in record
    xml.setElementValue(root, parentXPaths['fileIdentifier'], record['doi'])

    # Put current time in dateStamp
    currentTime = datetime.now().isoformat()
    xml.setElementValue(root, parentXPaths['metadataDate'], currentTime)

    # Put resourceTypeGeneral in hierarchyLevelName
    assert 'resourceTypeGeneral' in record['types'] 
    xml.setElementValue(root, parentXPaths['resourceType'], record['types']['resourceTypeGeneral'])

    # Put title in title
    assert 'title' in record['titles'][0]
    titleValue = record['titles'][0]['title']
    xml.setElementValue(root, parentXPaths['title'], titleValue)

    # Put description in abstract
    if 'description' in record['descriptions'][0]:
        fullXPath = parentXPaths['abstract'] + '/gco:CharacterString'
        descriptionValue = record['descriptions'][0]['description']
        xml.setElementValue(root, fullXPath, descriptionValue )
    else:
        xml.cutElement(parentXPaths['abstract'])

    # Put rights in legalConstraints
    if 'rightsList' in record and len(record['rightsList']) > 0:
        rightsElement = record['rightsList'][0]
        rightsText = rightsElement.get('rights', '')
        if 'rightsUri' in rightsElement:
            rightsText += ' (See also ' + rightsElement['rightsUri'] + ' )'
        sys.stderr.write('rightsText: %s\n' % rightsText)
        xml.setElementValue(root, parentXPaths['legalConstraints'], rightsText)

    # Put publicationYear in CI_Citation/date
    xml.setElementValue(root, parentXPaths['publicationDate'], record["publicationYear"])

    # Make DOI URL the Landing Page
    url = "https://doi.org/" + record["doi"]
    xml.setElementValue(root, parentXPaths['landingPage'], url)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifiers", [])
    relatedURLs = [id['relatedIdentifier'] for id in relatedIdentifierList if id['relatedIdentifierType'] == 'URL']
    relatedLinks = []
    for url in relatedURLs:
        relatedLinks.append({"name": "Unknown URL title", "linkage": url, "description": "Unknown URL description"})
    iso.addRelatedLinks(root, parentXPaths['relatedLink'], relatedLinks)

    # Add "subject" keywords.  Fill existing element first, then create copies.
    if 'subjects' in record:
        keywords = [s['subject'] for s in record['subjects']]
        iso.addKeywords(root, parentXPaths['keyword'], keywords)

    # Create list of cited contacts from three keys: "creators", "publisher", and "contributors".
    # Also obtain a list of support contacts from "contributors".
    citedContacts = getAuthors(record)

    if 'publisher' in record:
        publisherRecord = {"organization": record["publisher"], "role": "publisher"}
        citedContacts.append(publisherRecord)

    if ('contributors' in record):
        otherContacts, supportContacts = splitContributors(record["contributors"], roleMapping)
        citedContacts.extend(otherContacts)
    else:
        supportContacts = []


    # Fill in cited contacts.
    createResponsibleParties(root, parentXPaths['citedContact'], citedContacts)

    # Fill in support contacts.
    createResponsibleParties(root, parentXPaths['supportContact'], supportContacts)

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


def getAuthors(record):
    ''' Convert the list of creators into a list of author records. '''
    creatorList = record["creators"]
    authorList = [{"name": creator['name'], "role": 'author'} for creator in creatorList]
    #sys.stderr.write('authorList : %s\n' % authorList)
    return authorList


def splitContributors(contributorList, roleMapping):
    """ Split the contributors by type, since they are added to different parts of the XML tree. """
    # Remove contributors that do not have a contributorType.
    contributorsWithType = [contributor for contributor in contributorList if 'contributorType' in contributor]
    citedContacts = []
    supportContacts = []
    for contributor in contributorsWithType:
        name = contributor['name']
        roleDatacite = contributor['contributorType']
        roleISO = roleMapping[roleDatacite]
        contactRecord = {"name": name, "role": roleISO}
        if roleISO == 'pointOfContact':
            supportContacts.append(contactRecord)
        else:
            citedContacts.append(contactRecord)
    return citedContacts, supportContacts


def createResponsibleParties(root, contactXPath, contactList):
    ''' Insert XML elements for a list of contact records. '''
    contactTemplate, contactParent, contactIndex = xml.cutElement(root, contactXPath, True)
    insertCounter = 0
    for contactRecord in contactList:
        contactElement = xml.copyElement(contactTemplate)
        iso.modifyContactDataSelectively(contactElement, contactRecord)
        contactParent.insert(contactIndex + insertCounter, contactElement)
        insertCounter += 1


