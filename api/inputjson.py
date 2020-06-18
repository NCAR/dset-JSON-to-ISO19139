

import os.path
import json
from urllib.request import urlopen

#import sys
#import pprint

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


def getTemplateFilePath(templateArgument, defaultTemplate):
    ''' Return the path to the ISO output template file.'''
    templateFolder = './templates_ISO19139/'

    if templateArgument:
        template = templateArgument[0]
    else:
        template = defaultTemplate

    templatePath = templateFolder + template
    return templatePath

#
#  Functions for pulling DataCite records and converting them to JSON.
#

def getDataCiteRecords(doi):
    """ Return a list of JSON records obtained from the DataCite DOI website. """
    dataCiteURL = 'https://api.datacite.org/dois/'
    filterQuery = '&fq=prefix:10.5065&fq=is_active:true&wt=json'
    filterResult = '&fl=doi,relatedIdentifier,resourceTypeGeneral,title,description,publicationYear,subject,creator,contributor,contributorType,publisher,rights,rightsURI'

    if doi:
        textFilter =  doi
    else:
        textFilter = '?q=*'

    #fullQuery = dataCiteURL + textFilter + filterQuery + filterResult
    fullQuery = dataCiteURL + textFilter 

    #print(f'fullQuery == {fullQuery}')
    #sys.stderr.write('fullQuery: %s\n' % fullQuery)

    ## Determine number of records
    #with urlopen(fullQuery + '&rows=0') as url:
    #    response = url.read()
    #jsonData = json.load(response)
    #response = jsonData["response"]
    #numRecords = response["numFound"]


    # Get the records
    #with urlopen(fullQuery + '&rows=' + str(numRecords)) as url:
    with urlopen(fullQuery) as url:
        response = url.read()
    #sys.stderr.write('response: %s\n' % response)
    jsonData = json.loads(response.decode('utf-8'))

    #pprint.pprint(jsonData)

    response = jsonData['data']['attributes']
    return response

