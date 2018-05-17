# Python script:  
#
# 1. Translate DataCite JSON records to ISO 19139 XML records
# 2. Push ISO records to a CSW Server like GeoNetwork.
#


import json_input
import iso_api 
import push_csw

import sys
import pprint

DATACITE_TEMPLATE_PATH = './templates_ISO19139/insertCSW.xml'
DSET_TEMPLATE_PATH = './templates_ISO19139/dset_full_v10.xml'



def translateDataCiteRecords():
    # Create file for pushed record IDs, so deleting records through CSW is possible.
    id_file = open('pushedRecordIDs.txt', 'w')

    # Get records
    records = json_input.getDataCiteRecords()

    print "##"
    print "## Pushing " + str(len(records)) + " Records..."
    print "##"

    # Loop over DataCite Records
    for record in records:
        try:
            recordISO, recordID = iso_api.transformDataCiteToISO(record, DATACITE_TEMPLATE_PATH)
        except (KeyError, IndexError):
            print record
            sys.exit()

        XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xmlOutput = XML_HEADER + recordISO

        # Write the ISO record to a file for debugging purposes
        #f = open('output.xml', 'w')

        uniqueID = recordID.split('/')[1]

        outputFilePath = 'defaultOutputRecords/' + uniqueID + '.xml'
        f = open(outputFilePath, 'w')
        f.write(xmlOutput)
        f.close()

        # Post the resulting XML to GeoNetwork CSW service.  
        # Eventually, a check for Response code 200 should be made.
        POST_RESULT = False
        if POST_RESULT:
            push_csw.pushToCSW(xmlOutput)

    # Close the file with pushed record IDs
    id_file.close()

    print '...Finished Pushing Records.'



###
### START OF MAIN PROGRAM
###

inputText = sys.stdin.readlines()
inputText = "".join(inputText)

jsonData = json_input.getJSONData(inputText)
#pprint.pprint(jsonData)

isoText = iso_api.transformDSETToISO(jsonData, DSET_TEMPLATE_PATH)
print(isoText)
