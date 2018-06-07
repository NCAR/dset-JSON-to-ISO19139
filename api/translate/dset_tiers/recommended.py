#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

import api.util.iso19139 as iso
import api.util.xml as xml


parentXPaths = {
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


def transformRecommendedFields(root, emptyContactElement, citedContactParent, record):

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

