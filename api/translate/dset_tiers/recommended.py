#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

import api.util.iso19139 as iso
import api.util.xml as xml


parentXPaths = {
     'citedContact'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty',
     'citation'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:credit/gco:CharacterString',
     'keyword'             : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "GCMD")]/../../../../gmd:keyword',
     'supportContact'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact',
     'spatialRepType'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialRepresentationType',
     'spatialResolution'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution',
     'topicCategory'       : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory',
     'geoExtent'           : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement',
     'temporalExtent'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent',
     'temporalResolution'  : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:description/gco:CharacterString',
}


#def transformRecommendedFields(root, emptyContactElement, citedContactParent, record):
def transformRecommendedFields(root, record):

    # - Other Responsible Individual/Organization: repeatable
    if record.has_key('other_responsible_party'):
        for party in record['other_responsible_party']:
            iso.appendContactData(root, parentXPaths['citedContact'], party)

    # - Citation: not repeatable
    if record.has_key('citation'):
        element = xml.setElementValue(root, parentXPaths['citation'], record['citation'])

    # - Science Support Contact: repeatable
    # Note: data for Resource Support Contact information was inserted, so we must preserve existing elements.
    if record.has_key('science_support'):
        supportElement, supportParent, originalIndex = xml.cutElement(root, parentXPaths['supportContact'], True)
        supportParent.insert(originalIndex, supportElement)
        insertCounter = 1
        for party in record['science_support']:
            elementCopy = xml.copyElement(supportElement)
            iso.modifyContactData(elementCopy, party, 'principalInvestigator')
            supportParent.insert(originalIndex + insertCounter, elementCopy)
            insertCounter += 1


    # - Keywords: repeatable
    if record.has_key('keywords'):
        iso.addKeywords(root, parentXPaths['keyword'], record['keywords'])

    # - Keyword Vocabulary:   Not included at this point.
    
    # - Reference System:  potentially very complex, not shown in DASH Search, not included at this point.

    # - Spatial Representation: repeatable
    if record.has_key('spatial_representation'):
        childXPath = 'gmd:MD_SpatialRepresentationTypeCode'
        setCodeList = True
        xml.addChildList(root, parentXPaths['spatialRepType'], childXPath, record['spatial_representation'], setCodeList)
    else:
        xml.cutElement(root, parentXPaths['spatialRepType'])

    # - Spatial Resolution: repeatable
    if record.has_key('spatial_resolution'):
        iso.addSpatialResolutionDistances(root, parentXPaths['spatialResolution'], record['spatial_resolution'])
    else:
        xml.cutElement(root, parentXPaths['spatialResolution'])

    # - ISO Topic Category: repeatable
    if record.has_key('topic_category'):
        childXPath = 'gmd:MD_TopicCategoryCode'
        xml.addChildList(root, parentXPaths['topicCategory'], childXPath, record['topic_category'])
    else:
        xml.cutElement(root, parentXPaths['topicCategory'])

    # - GeoLocation: not repeatable
    if record.has_key('geolocation'):
        iso.modifyBoundingBox(root, parentXPaths['geoExtent'], record['geolocation'])
    else:
        xml.cutElement(root, parentXPaths['geoExtent'])

    # - Temporal Coverage: not repeatable
    if record.has_key('temporal_coverage'):
        iso.modifyTemporalExtent(root, parentXPaths['temporalExtent'], record['temporal_coverage'])
    else:
        xml.cutElement(root, parentXPaths['temporalExtent'])

    # - Temporal Resolution: not repeatable
    if record.has_key('temporal_resolution'):
        xml.setElementValue(root, parentXPaths['temporalResolution'], record['temporal_resolution'])

    # - Vertical Extent: potentially very complicated in ISO 19139; not included at this point. 

    return root

