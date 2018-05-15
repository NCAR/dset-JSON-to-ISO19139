#
#  Functions for pulling DataCite records and converting them to JSON.
#


import urllib2                              # Allows HTTP request output for simplejson
import simplejson                           # Allows JSON to dict conversion


def getDataCiteRecords():
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


# Return the parts of a DataCite relatedIdentifier
def getRelatedIdentifierParts(relatedIdentifier):
    relatedIdentifierParts = relatedIdentifier.split(":")
    namePart = "Related Resource: " + relatedIdentifierParts[0]
    typePart = relatedIdentifierParts[1]
    urlPart = ':'.join(relatedIdentifierParts[2: ])
    return namePart, typePart, urlPart

