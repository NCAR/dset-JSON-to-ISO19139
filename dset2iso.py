# Python script:  
#
# 1. Translate DataCite JSON records to ISO 19139 XML records
# 2. Push ISO records to a CSW Server like GeoNetwork.
#

import argparse
import sys
import os.path

PROGRAM_VERSION = 'Version: 0.1.0'

PROGRAM_DESCRIPTION = '''

A program for translating JSON metadata into ISO 19139 metadata.


Here are some working examples showing the two main uses of this program:  

  * Convert a single DSET metadata record using STDIN and STDOUT:

       python json2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml


  * Perform batch DSET metadata record processing:

       python dset2iso.py --inputDir ./defaultInputRecords --outputDir ./defaultOutputRecords

'''

class PrintHelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def checkDirectoryExistence(directoryPath, directoryType):
    ''' generate an error if directory does not exist. '''
    if not os.path.isdir(directoryPath):
        message = directoryType + ' does not exist: %s\n' % directoryPath
        parser.error(message)

#
#  Parse and validate command line options.
#
programHelp = PROGRAM_DESCRIPTION + PROGRAM_VERSION
parser = PrintHelpOnErrorParser(description=programHelp, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("--inputDir", nargs=1, help="base directory for input records")
parser.add_argument("--outputDir", nargs=1, help="base directory for output records")
args = parser.parse_args()

# Require that --input-dir and --output-dir both be used if either is used.
if len([x for x in (args.inputDir,args.outputDir) if x is not None]) == 1:
    parser.error('--inputDir and --outputDir must be given together')

# Check that input and output directories exist.
readSTDIN = (args.inputDir == None)
if not readSTDIN:
    checkDirectoryExistence(args.inputDir[0], 'Input directory')
    checkDirectoryExistence(args.outputDir[0], 'Output directory')



import api.json_dset as dset
import api.iso_api as iso

import pprint

DSET_TEMPLATE_PATH = './templates_ISO19139/dset_full.xml'


###
### START OF MAIN PROGRAM
###


if readSTDIN:
    inputText = sys.stdin.readlines()
    inputText = "".join(inputText)

    jsonData = dset.getJSONData(inputText)
    #pprint.pprint(jsonData)

    isoText = iso.transformDSETToISO(jsonData, DSET_TEMPLATE_PATH)
    print(isoText)

else:
    inputDir = args.inputDir[0]
    outputDir = args.outputDir[0]
    print inputDir
    jsonFiles = dset.getJSONFileNames(inputDir)
    print("Found " + str(len(jsonFiles)) + " input files.")
    for inputFile in jsonFiles:
        with open(inputFile, 'r') as myfile:
            inputText = myfile.readlines()
            inputText = "".join(inputText)
        jsonData = dset.getJSONData(inputText)

        print("  Translating file: " + inputFile)
        isoText = iso.transformDSETToISO(jsonData, DSET_TEMPLATE_PATH)

        outputFile = dset.prepareOutputFile(inputFile, inputDir, outputDir)
        print(inputFile + " -> " + outputFile)

        file = open(outputFile, 'w')
        file.write(isoText)
        file.close()
