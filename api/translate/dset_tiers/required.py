from datetime import datetime

import api.util.iso19139 as iso
import api.util.xml as xml


parentXPaths = {
    'fileIdentifier'   : '/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
    'assetType'        : '/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode',
    'metadataContact'  : '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty',
    'metadataDate'     : '/gmd:MD_Metadata/gmd:dateStamp/gco:DateTime',
    'landingPage'      : '/gmd:MD_Metadata/gmd:dataSetURI/gco:CharacterString',
    'title'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
    'publicationDate'  : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
    'citedContact'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty',
    'abstract'         : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
    'supportContact'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact',
    'resourceType'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "Resource Type")]/../../../../gmd:keyword/gco:CharacterString',
    'legalConstraints' : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
    'accessConstraints': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',
}


#def transformRequiredFields(root, emptyContactElement, citedContactParent, record):
def transformRequiredFields(root, record):
    '''Transform fields that are required according to the DSET Metadata Dialect.  
       Not all required fields must be present in the record because the ISO template may have default values for them.
    '''

    # - Metadata Record ID: not repeatable
    assert record.has_key('metadata_id')
    xml.setElementValue(root, parentXPaths['fileIdentifier'], record['metadata_id'])

    # - ISO Asset Type (default value: dataset): not repeatable
    xml.setElementValue(root, parentXPaths['assetType'], record['asset_type'], True)

    # - Metadata Point of Contact: not repeatable
    if record.has_key('metadata_contact'):
        element = xml.getElement(root, parentXPaths['metadataContact'])
        iso.modifyContactData(element, record['metadata_contact'], 'pointOfContact')

    # - Metadata Date (not repeatable): Use current time if not present in the record. 
    if record.has_key('metadata_date'):
        metadataDate = record['metadata_date']
    else:
        metadataDate = datetime.now().isoformat()
    xml.setElementValue(root, parentXPaths['metadataDate'], metadataDate)

    # - Landing Page: not repeatable
    assert record.has_key('landing_page')
    xml.setElementValue(root, parentXPaths['landingPage'], record['landing_page'])

    # - Title: not repeatable
    assert record.has_key('title')
    xml.setElementValue(root, parentXPaths['title'], record['title'])

    # - Publication Date: not repeatable
    assert record.has_key('publication_date')
    xml.setElementValue(root, parentXPaths['publicationDate'], record['publication_date'])

    # - Author: repeatable
    assert record.has_key('author')
    authors = record['author']
    firstLoopIteration = True
    for author in authors:
        #iso.appendContactData(citedContactParent, emptyContactElement, author, 'author')
        if firstLoopIteration:
            contactElement = xml.getElement(root, parentXPaths['citedContact'])
            iso.modifyContactData(contactElement, author, 'author')
        else:
            iso.appendContactData(root, parentXPaths['citedContact'], author, 'author')
        firstLoopIteration = False

    # - Publisher: not repeatable
    if record.has_key('publisher'):
        #iso.appendContactData(citedContactParent, emptyContactElement, record['publisher'], 'publisher')
        iso.appendContactData(root, parentXPaths['citedContact'], record['publisher'], 'publisher')

    # - Abstract: not repeatable
    assert record.has_key('abstract')
    xml.setElementValue(root, parentXPaths['abstract'], record['abstract'])

    # - Resource Support Contact: not repeatable
    if record.has_key('resource_support'):
        element = xml.getElement(root, parentXPaths['supportContact'])
        iso.modifyContactData(element, record['resource_support'], 'pointOfContact')

    # - DataCite Resource Type: not repeatable
    if record.has_key('resource_type'):
        xml.setElementValue(root, parentXPaths['resourceType'], record['resource_type'])

    # - Legal Constraints: not repeatable
    if record.has_key('legal_constraints'):
        xml.setElementValue(root, parentXPaths['legalConstraints'], record['legal_constraints'])

    # - Access Constraints: not repeatable
    if record.has_key('access_constraints'):
        xml.setElementValue(root, parentXPaths['accessConstraints'], record['access_constraints'])

    return root

