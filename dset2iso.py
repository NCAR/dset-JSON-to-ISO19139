# Python script:  
#
# 1. Translate DataCite JSON records to ISO 19139 XML records
# 2. Push ISO records to a CSW Server like GeoNetwork.
#

import argparse
import sys
import os.path

__version_info__ = ('2018','06','14')
__version__ = '-'.join(__version_info__)

PROGRAM_DESCRIPTION = '''

A program for translating JSON metadata into ISO 19139 metadata.


Here are some working examples showing the two main uses of this program:  

  * Convert a single DSET metadata record using STDIN and STDOUT:

       python dset2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml


  * Perform batch DSET metadata record processing:

       python dset2iso.py --inputDir ./defaultInputRecords --outputDir ./defaultOutputRecords


Program Version: '''

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
programHelp = PROGRAM_DESCRIPTION + __version__
parser = PrintHelpOnErrorParser(description=programHelp, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--inputDir', nargs=1, help="base directory for input records")
parser.add_argument('--outputDir', nargs=1, help="base directory for output records")
parser.add_argument('--version', action='version', version="%(prog)s ("+__version__+")")
args = parser.parse_args()

# Require that --input-dir and --output-dir both be used if either is used.
if len([x for x in (args.inputDir,args.outputDir) if x is not None]) == 1:
    parser.error('--inputDir and --outputDir must be given together')

# Check that input and output directories exist.
readSTDIN = (args.inputDir == None)
if not readSTDIN:
    checkDirectoryExistence(args.inputDir[0], 'Input directory')
    checkDirectoryExistence(args.outputDir[0], 'Output directory')



import api.inputjson as dset_input
import api.translate.dset as dset_translate
import api.output as dset_output

import pprint

DSET_TEMPLATE_PATH = './templates_ISO19139/dset_full.xml'


###
### START OF MAIN PROGRAM
###


if readSTDIN:
    inputText = sys.stdin.readlines()
    inputText = "".join(inputText)

    jsonData = dset_input.getJSONData(inputText)
    #pprint.pprint(jsonData)

    isoText = dset_translate.transformDSETToISO(jsonData, DSET_TEMPLATE_PATH)

    # Python 3 needs conversion from byte array to string
    isoText = str(isoText)
    print(isoText, file=sys.stdout)

else:
    inputDir = args.inputDir[0]
    outputDir = args.outputDir[0]
    print(inputDir, file=sys.stdout)
    jsonFiles = dset_input.getJSONFileNames(inputDir)
    print("Found " + str(len(jsonFiles)) + " input files.", file=sys.stdout)
    for inputFile in jsonFiles:
        with open(inputFile, 'r') as myfile:
            inputText = myfile.readlines()
            inputText = "".join(inputText)
        jsonData = dset_input.getJSONData(inputText)

        print(("  Translating file: " + inputFile), file=sys.stdout)
        isoText = dset_translate.transformDSETToISO(jsonData, DSET_TEMPLATE_PATH)

        outputFile = dset_output.prepareOutputFile(inputFile, inputDir, outputDir)
        print((inputFile + " -> " + outputFile), file=sys.stdout)

        file = open(outputFile, 'w')
        file.write(isoText)
        file.close()
