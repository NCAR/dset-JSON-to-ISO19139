#
#  Functions for pulling DataCite records and converting them to JSON.
#

import iso_api 
import urllib2
import simplejson

DATACITE_TEMPLATE_PATH = './templates_ISO19139/dset_min.xml'

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


def getDataCiteRecords():
    """ Return a list of JSON records obtained from the DataCite DOI website. """
    dataCiteURL = 'https://search.datacite.org/api'
    filterQuery = '&fq=prefix:10.5065&fq=is_active:true&wt=json'
    filterResult = '&fl=doi,relatedIdentifier,resourceTypeGeneral,title,description,publicationYear,subject,creator,contributor,contributorType,publisher'

    PROCESS_SINGLE_RECORD = False
    if PROCESS_SINGLE_RECORD:
        textFilter = '?q=10.5065/D68S4N4H'
    else:
        textFilter = '?q=*'

    fullQuery = dataCiteURL + textFilter + filterQuery + filterResult
    print fullQuery

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
    # Create file for pushed record IDs, so deleting records through CSW is possible.

    # Get records
    records = getDataCiteRecords()

    print "##"
    print "## Translating " + str(len(records)) + " Records..."
    print "##"

    # Loop over DataCite Records
    for record in records:
        try:
            recordISO, recordID = iso_api.transformDataCiteToISO(record, DATACITE_TEMPLATE_PATH)
        except (KeyError, IndexError):
            print record
            sys.exit()

        XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xmlOutput = XML_HEADER + recordISO

        # Isolate the second part of a DOI identifier for the output file name
        uniqueID = recordID.split('/')[1]

        outputFilePath = 'defaultOutputRecords/' + uniqueID + '.xml'
        f = open(outputFilePath, 'w')
        f.write(xmlOutput)
        f.close()

    print '...Finished Translating Records.'


