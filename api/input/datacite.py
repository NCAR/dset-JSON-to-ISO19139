#
#  Functions for pulling DataCite records and converting them to JSON.
#

import urllib2
import simplejson



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

