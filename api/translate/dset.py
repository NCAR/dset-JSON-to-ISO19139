#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#
from api.translate.dset_tiers.required    import transformRequiredFields
from api.translate.dset_tiers.recommended import transformRecommendedFields
from api.translate.dset_tiers.optional    import transformOptionalFields

import api.util.xml as xml

parentXPaths = {
    'citedContact': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty',
}

def transformDSETToISO(record, pathToTemplateFileISO):
    """ Transform a JSON record to ISO 19139 XML using a XML template file. """
    root = xml.getXMLTree(pathToTemplateFileISO)

    # Cut out the template's citedContact element, so we can paste in multiple copies of it later.
    emptyContactElement, contactParent = xml.cutElement(root, parentXPaths['citedContact'])

    root = transformRequiredFields(root, emptyContactElement, contactParent, record)

    root = transformRecommendedFields(root, emptyContactElement, contactParent, record)

    root = transformOptionalFields(root, record)

    recordAsISO = xml.toString(root)
    return recordAsISO




