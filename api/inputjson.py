

import os.path
import json
import urllib2


#
#  Functions for finding and loading text files containing DSET JSON.
#
def getJSONData(jsonText):
    """ Transform a text version of JSON data into a python dictionary. """
    jsonData = json.loads(jsonText)
    return jsonData


def getJSONFileNames(dirPath):
    """ Return a list of paths to files containing JSON records, found by recursive search in a given directory. """
    jsonExtension = '.txt'
    matches = []
    for root, dirnames, filenames in os.walk(dirPath):
        for filename in filenames:
            if filename.endswith(jsonExtension):
                matches.append(os.path.join(root, filename))
    return matches

#
#  Functions for pulling DataCite records and converting them to JSON.
#

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
    jsonData = json.load(response)
    response = jsonData["response"]
    numRecords = response["numFound"]

    # Get the records
    response = urllib2.urlopen(fullQuery + '&rows=' + str(numRecords))
    jsonData = json.load(response)
    response = jsonData["response"]
    records = response["docs"]
    return records

