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

def getRecordAsISO(record, templateFileISO):
    # Load the ISO template file as an XML element tree
    tree = ElementTree.parse(templateFileISO)
    root = tree.getroot()

    # Put DOI in fileIdentifier
    fileIdentifier = getElement(root, './/gmd:fileIdentifier/gco:CharacterString')
    fileIdentifier.text = record["doi"]

    # Put resourceTypeGeneral in hierarchyLevelName
    if record.has_key("resourceTypeGeneral"):
        hierarchyLevelName = getElement(root, './/gmd:hierarchyLevelName/gco:CharacterString')
        hierarchyLevelName.text = record["resourceTypeGeneral"]

    # Put title in title
    title = getElement(root, './/gmd:CI_Citation/gmd:title/gco:CharacterString')
    title.text = getFirst( record["title"] )

    # Put description in abstract
    if record.has_key("description"):
        abstract = getElement(root, './/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString')
        abstract.text = getFirst( record["description"] )
    else:
        abstract = getElement(root, './/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString')
        abstract.getparent().remove(abstract)

    # Put publicationYear in CI_Citation/date
    date = getElement(root, './/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date')
    date.text = record["publicationYear"]

    # Put DOI URL in existing onlineResource
    onlineParent = getElement(root, './/gmd:MD_DigitalTransferOptions')
    url = "http://dx.doi.org/" + record["doi"]
    name = "Landing Page"
    modifyOnlineResource(onlineParent, url, name)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifier", [])
    for relatedIdentifier in relatedIdentifierList:
        namePart, typePart, urlPart = getRelatedIdentifierParts(relatedIdentifier)
        if typePart == "URL":
            online = getElement(root, './/gmd:MD_DigitalTransferOptions/gmd:onLine', True)
            modifyOnlineResource(online, urlPart, namePart)

    # Add "subject" keywords.  Fill existing element first, then create copies.
    if record.has_key("subject"):
        subjectList = record["subject"]
        for i in range(len(subjectList)):
            keyword = getElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword', i > 0)
            keyword[0].text = subjectList[i]
    else:
        keyword = getElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword', False)
        keyword.getparent().remove(keyword)

    # Add creators.  Fill existing element first, then create copies.
    creatorList = record["creator"]
    for i in range(len(creatorList)):
        contact = getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', i > 0)
        modifyContact(contact, creatorList[i], "creator")

    # Add contributors
    contributorList = record.get("contributor", [])
    contributorTypeList = record.get("contributorType", [])
    for i in range(len(contributorList)):
        contact = getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', True)
        modifyContact(contact, contributorList[i], contributorTypeList[i])

    # Add publisher
    publisher = record.get("publisher", None)
    if publisher:
        contact = getElement(root, './/gmd:MD_DataIdentification/gmd:pointOfContact', True)
        modifyContact(contact, publisher, "publisher")

    # Return ISO record and record identifier
    recordAsISO = ElementTree.tostring(root, pretty_print=True)
    return recordAsISO, record["doi"]


###
### START OF MAIN PROGRAM
###

# Create file for pushed record IDs, so deleting records through CSW is possible.
id_file = open('pushedRecordIDs.txt', 'w')

# Get records
records = getDataCiteRecords()

print "##"
print "## Pushing " + str(len(records)) + " Records..."
print "##"

# Loop over DataCite Records
for record in records:
    try:
        recordISO, recordID = getRecordAsISO(record, ISO_TEMPLATE_PATH)
    except (KeyError, IndexError):
        print record
        sys.exit()

    XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xmlOutput = XML_HEADER + recordISO

    # Write the ISO record to a file for debugging purposes
    #f = open('output.xml', 'w')

        uniqueID = recordID.split('/')[1]

        outputFilePath = 'output/' + uniqueID + '.xml'
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
