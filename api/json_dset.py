#
#  Functions for finding and loading text files containing DSET JSON.
#


import os
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

