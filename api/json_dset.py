#
#  Functions for finding and loading text files containing DSET JSON.
#


import os.path
import simplejson


def getJSONData(jsonText):
    """ Transform a text version of JSON data into a python dictionary. """
    jsonData = simplejson.loads(jsonText)
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

def prepareOutputFile(inputFile, inputDir, outputDir):
    outputFile = inputFile.replace(inputDir,outputDir,1)
    outputFile = os.path.splitext(outputFile)[0] + '.xml'

    outputFileDir = os.path.dirname(outputFile)
    if not os.path.exists(outputFileDir):
        os.makedirs(outputFileDir)

    return outputFile
