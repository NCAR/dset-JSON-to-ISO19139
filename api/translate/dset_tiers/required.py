from datetime import datetime

import api.util.iso19139 as iso
import api.util.xml as xml


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
}


def transformRequiredFields(root, emptyContactElement, citedContactParent, record):

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

