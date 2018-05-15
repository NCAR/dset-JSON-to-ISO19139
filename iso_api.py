#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#

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



