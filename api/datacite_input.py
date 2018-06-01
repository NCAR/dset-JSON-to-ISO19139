#
#  Functions for pulling DataCite records and converting them to JSON.
#

import iso_api 
import urllib2
import simplejson


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


def getJSONData(jsonText):
    """ Transform a text version of JSON data into a python dictionary. """
    jsonData = simplejson.loads(jsonText)
    return jsonData


def getDataCiteRecords(doi=None):
    """ Return a list of JSON records obtained from the DataCite DOI website. """
    dataCiteURL = 'https://search.datacite.org/api'
    filterQuery = '&fq=prefix:10.5065&fq=is_active:true&wt=json'
    filterResult = '&fl=doi,relatedIdentifier,resourceTypeGeneral,title,description,publicationYear,subject,creator,contributor,contributorType,publisher'

    if doi:
        textFilter = '?q=' + doi
    else:
        textFilter = '?q=*'

    fullQuery = dataCiteURL + textFilter + filterQuery + filterResult

    # Determine number of records
    response = urllib2.urlopen(fullQuery + '&rows=0')
    jsonData = simplejson.load(response)
    response = jsonData["response"]
    numRecords = response["numFound"]

    # Get the records
    response = urllib2.urlopen(fullQuery + '&rows=' + str(numRecords))
    jsonData = simplejson.load(response)
    response = jsonData["response"]
    records = response["docs"]
    return records


def getRelatedIdentifierParts(relatedIdentifier):
    """ Return the parts of a DataCite relatedIdentifier object. """
    relatedIdentifierParts = relatedIdentifier.split(":")
    namePart = "Related Resource: " + relatedIdentifierParts[0]
    typePart = relatedIdentifierParts[1]
    urlPart = ':'.join(relatedIdentifierParts[2: ])
    return namePart, typePart, urlPart



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
    try:
        recordISO, recordID = iso_api.transformDataCiteToISO(record, templateFile, roleMappingDataCiteToISO)
    except (KeyError, IndexError):
        print record
        sys.exit()

    headerXML = '<?xml version="1.0" encoding="UTF-8"?>\n'
    outputXML = headerXML + recordISO
    return outputXML

