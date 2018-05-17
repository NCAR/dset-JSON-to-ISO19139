#
#  Functions for pulling DataCite records and converting them to JSON.
#


import os
import urllib2
import simplejson


def getJSONFileNames(dirPath):
    """ Return a list of paths to files containing JSON records, found by recursive search in a given directory. """
    jsonExtension = '.txt'
    matches = []
    for root, dirnames, filenames in os.walk(dirPath):
        for filename in filenames:
            if filename.endswith(jsonExtension):
                matches.append(os.path.join(dirnames, filename))
    return matches


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

