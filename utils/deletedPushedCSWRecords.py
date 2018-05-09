# Python script:  
# Delete DataCite records pushed to GeoNetwork

from lxml import etree as ElementTree       # ISO XML parser
import requests                             # Allows simple POST requests
from requests.auth import HTTPBasicAuth     # Allows POST basic authentication

# We need XML namespace mappings in order to search the ISO element tree
XML_NAMESPACE_MAP = {'ogc': 'http://www.opengis.net/ogc',
	'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'apiso': 'http://www.opengis.net/cat/csw/apiso/1.0'}


# Return first item in a list if list is nonempty (returns None otherwise).
def getFirst(someList): 
    if someList:
        return someList[0]


# Search XML element tree and return the first matching element
def getElement(baseElement, elementPath):
	elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
	return getFirst(elements)


def getDeleteRecord(recordID, templateFileISO):

	# Load the XML template file as an element tree
	tree = ElementTree.parse(templateFileISO)
	root = tree.getroot()

	# Put record ID in element
	elemID = getElement(root, './/ogc:Literal')
	elemID.text = recordID

    # Return record as XML 
	recordAsXML = ElementTree.tostring(root, pretty_print=True)
	return recordAsXML


###
### START OF MAIN PROGRAM
###

recordIDFile = './pushedRecordIDs.txt'
deleteISOTemplate = './deleteCSW.xml'

# Read pushed record IDs and put in a list
with open(recordIDFile,"r") as infile:
	listOfIDs = infile.read().splitlines()

print "##"
print "## Deleting " + str(len(listOfIDs)) + " Records..."
print "##"

# Loop over IDs to delete
for id in listOfIDs:

	deleteRecord = getDeleteRecord(id, deleteISOTemplate)

	XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
	xmlOutput = XML_HEADER + deleteRecord

	# Post the resulting XML to GeoNetwork CSW service.  
	POST_RESULT = True
	if POST_RESULT:
		#GeoNetworkBaseURL = 'http://localhost:8080'
		GeoNetworkBaseURL = 'https://geonetwork.prototype.ucar.edu'
		url = GeoNetworkBaseURL + '/geonetwork/srv/eng/csw-publication?SERVICE=CSW&VERSION=2.0.2&REQUEST=DELETE'
		header = {'Content-Type': 'text/xml'}

		try:
			response = requests.post(url, auth=HTTPBasicAuth('admin', 'admin'), headers=header, data=xmlOutput)
			print response.text
		except requests.ConnectionError:
			print 'ConnectionError: failed to connect: ' + url

		if response.status_code != 200:
			raise OSError("Response " + str(response.status_code) + ": " + response.content)
		print response.status_code

print '...Finished deleting records.'



