#
#  Highest-level code for modifying elements in a ISO 19139 XML file.
#
from api.translate.dset_tiers.required    import transformRequiredFields
from api.translate.dset_tiers.recommended import transformRecommendedFields
from api.translate.dset_tiers.optional    import transformOptionalFields

import api.util.xml as xml


def transformDSETToISO(record, pathToTemplateFileISO):
    """ Transform a JSON record to ISO 19139 XML using a XML template file. """
    root = xml.getXMLTree(pathToTemplateFileISO)

    root = transformRequiredFields(root, record)

    root = transformRecommendedFields(root, record)

    root = transformOptionalFields(root, record)

    recordAsISO = xml.toString(root)
    return recordAsISO




