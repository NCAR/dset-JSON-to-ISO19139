# Python script:  
#
# 1. Translate DataCite JSON records to ISO 19139 XML records
# 2. Push ISO records to a CSW Server like GeoNetwork.
#

import argparse
from argparse import RawTextHelpFormatter

PROGRAM_DESCRIPTION = '''

A program for translating JSON metadata into ISO 19139 metadata.


Here are some working examples showing the three main uses of this program:  

  * Convert a single DSET metadata record using STDIN and STDOUT:

       python json2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml


  * Perform batch DSET metadata record processing:

       python json2iso.py --input-dir ./defaultInputRecords --output-dir ./defaultOutputRecords


  * Fetch a DataCite metadata record and produce the output in ISO 19139:

       python json2iso.py --doi 10.5065/D6WD3XH5   > test_datacite.xml


'''

parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION, formatter_class=RawTextHelpFormatter)

inputGroup = parser.add_argument_group('Optional input sources')
mutexGroup = inputGroup.add_mutually_exclusive_group()
mutexGroup.add_argument("--doi", nargs=1, help="input DOI identifier")
mutexGroup.add_argument("--input-dir", nargs=1, help="base directory for input records")


outputGroup = parser.add_argument_group('Optional output source')
outputGroup.add_argument("--output-dir", nargs=1, help="base directory for output records")
args = parser.parse_args()



import api.json_datacite as datacite
import api.json_dset
import api.iso_api 

import sys
import pprint

DSET_TEMPLATE_PATH = './templates_ISO19139/dset_full_v10.xml'


###
### START OF MAIN PROGRAM
###

EXPORT_DATACITE=True
if EXPORT_DATACITE:
    datacite.translateDataCiteRecords()

else:
    inputText = sys.stdin.readlines()
    inputText = "".join(inputText)

    jsonData = json_dset.getJSONData(inputText)
    #pprint.pprint(jsonData)

    isoText = iso_api.transformDSETToISO(jsonData, DSET_TEMPLATE_PATH)
    print(isoText)
