# Python script:  
#
# 1. Translate DataCite JSON records to ISO 19139 XML records
# 2. Push ISO records to a CSW Server like GeoNetwork.
#


import requests                             # Allows simple POST requests
from requests.auth import HTTPBasicAuth     # Allows POST basic authentication

import datacite
import iso_api 

ISO_TEMPLATE_PATH = './templates_ISO19139/insertCSW.xml'


###
### START OF MAIN PROGRAM
###

# Create file for pushed record IDs, so deleting records through CSW is possible.
id_file = open('pushedRecordIDs.txt', 'w')

# Get records
records = datacite.getDataCiteRecords()

print "##"
print "## Pushing " + str(len(records)) + " Records..."
print "##"

# Loop over DataCite Records
for record in records:
    try:
        recordISO, recordID = iso_api.transformToISO(record, ISO_TEMPLATE_PATH)
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
        #GeoNetworkBaseURL = 'http://localhost:8080'
        GeoNetworkBaseURL = 'https://geonetwork.prototype.ucar.edu'
        url = GeoNetworkBaseURL + '/geonetwork/srv/eng/csw-publication?SERVICE=CSW&VERSION=2.0.2&REQUEST=INSERT'
        header = {'Content-Type': 'text/xml'}

        try:
            response = requests.post(url, auth=HTTPBasicAuth('admin', '******'), headers=header, data=xmlOutput)

            # Save recordID as a way to allow later deletion through CSW
            id_file.write(recordID + '\n')

        except requests.ConnectionError:
            print 'ConnectionError: failed to connect: ' + url

        if response.status_code != 200:
            print response.text
            raise OSError("Response " + str(response.status_code) + ": " + response.content)

        print response.status_code

# Close the file with pushed record IDs
id_file.close()

print '...Finished Pushing Records.'
