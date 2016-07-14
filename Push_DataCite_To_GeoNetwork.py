# Python script:  
#
# 1. Translate DataCite JSON records to ISO 19139 XML records
# 2. Push ISO records to a CSW Server like GeoNetwork.
#

from lxml import etree as ElementTree       # ISO XML parser
from copy import deepcopy                   # Allows deep copy of ISO elements
import urllib2	                            # Allows HTTP request output for simplejson
import simplejson                           # Allows JSON to dict conversion
import requests                             # Allows simple POST requests
from requests.auth import HTTPBasicAuth     # Allows POST basic authentication

# We need XML namespace mappings in order to search the ISO element tree
XML_NAMESPACE_MAP = {'csw': 'http://www.opengis.net/cat/csw/2.0.2',
	'gmd': 'http://www.isotc211.org/2005/gmd',
	'xlink': 'http://www.w3.org/1999/xlink', 
	'gco': 'http://www.isotc211.org/2005/gco', 
	'gml': 'http://www.opengis.net/gml'}


def getDataCiteRecords():

	dataCiteURL = 'https://search.datacite.org/api'
	filterQuery = '&fq=prefix:10.5065&fq=is_active:true&wt=json'
	filterResult = '&fl=doi,relatedIdentifier,resourceTypeGeneral,title,description,publicationYear,subject,creator,contributor,contributorType,publisher'

	PROCESS_SINGLE_RECORD = False
	if PROCESS_SINGLE_RECORD:
		textFilter = '?q=10.5065/D68S4N4H'
	else:
		textFilter = '?q=*'

	fullQuery = dataCiteURL + textFilter + filterQuery + filterResult
	print fullQuery

	# Determine number of records
	response = urllib2.urlopen(fullQuery + '&rows=0')
	jsonData = simplejson.load(response)
	response = jsonData["response"]
	numRecords = response["numFound"]

	# Get the records
	response = urllib2.urlopen(fullQuery + '&rows=' + str(numRecords))
	jsonData = simplejson.load(response)
	response = jsonData["response"]
	records = response["docs"]
	return records


# Return first item in a list if list is nonempty (returns None otherwise).
def getFirst(someList): 
	if someList:
		return someList[0]


# Search XML element tree and return the first matching element
def getElement(baseElement, elementPath):
	elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
	return getFirst(elements)


# Search element tree for a child element and add a child copy to parent if createCopy is True
def getChildElement(rootElement, parentPath, childPath, createCopy):
	parent = getElement(rootElement, parentPath)
	child = getElement(parent, childPath)
	if createCopy:
		childCopy = deepcopy(child)
		parent.append(childCopy)
		child = childCopy
	return child

# Return the parts of a DataCite relatedIdentifier
def getRelatedIdentifierParts(relatedIdentifier):
	relatedIdentifierParts = relatedIdentifier.split(":")
	namePart = "Related Resource: " + relatedIdentifierParts[0]
	typePart = relatedIdentifierParts[1]
	urlPart = ':'.join(relatedIdentifierParts[2: ])
	return namePart, typePart, urlPart


# Modify contents of an "onLine" ISO element
def modifyOnlineResource(transferElement, url, name):
	elementURL = getElement(transferElement, './/gmd:CI_OnlineResource/gmd:linkage/gmd:URL')
	elementURL.text = url

	elementName = getElement(transferElement, './/gmd:CI_OnlineResource/gmd:name/gco:CharacterString')
	elementName.text = name


# Modify contents of a "contact" ISO element
def modifyContact(contactElement, name, contactType):
	elementName = getElement(contactElement, './/gmd:individualName/gco:CharacterString')
	elementName.text = name

	elementRole = getElement(contactElement, './/gmd:CI_RoleCode')
	elementRole.attrib['codeListValue'] = contactType


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
			online = getChildElement(root, './/gmd:MD_DigitalTransferOptions', './/gmd:onLine', True)
			modifyOnlineResource(online, urlPart, namePart)

	# Add "subject" keywords.  Fill existing element first, then create copies.
	if record.has_key("subject"):
		subjectList = record["subject"]
		for i in range(len(subjectList)):
			keyword = getChildElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords', './/gmd:keyword', i > 0)
			keyword[0].text = subjectList[i]
	else:
		keyword = getChildElement(root, './/gmd:descriptiveKeywords/gmd:MD_Keywords', './/gmd:keyword', False)
		keyword.getparent().remove(keyword)


	# Add creators.  Fill existing element first, then create copies.
	creatorList = record["creator"]
	for i in range(len(creatorList)):
		contact = getChildElement(root, './/gmd:MD_DataIdentification', './/gmd:pointOfContact', i > 0)
		modifyContact(contact, creatorList[i], "creator")

	# Add contributors
	contributorList = record.get("contributor", [])
	contributorTypeList = record.get("contributorType", [])
	for i in range(len(contributorList)):
		contact = getChildElement(root, './/gmd:MD_DataIdentification', './/gmd:pointOfContact', True)
		modifyContact(contact, contributorList[i], contributorTypeList[i])

	# Add publisher
	publisher = record.get("publisher", None)
	if publisher:
		contact = getChildElement(root, './/gmd:MD_DataIdentification', './/gmd:pointOfContact', True)
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
		recordISO, recordID = getRecordAsISO(record, 'insertCSW.xml')
	except (KeyError, IndexError):
		print record
		sys.exit()

	XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
	xmlOutput = XML_HEADER + recordISO

	# Write the ISO record to a file for debugging purposes
	f = open('output.xml', 'w')
	f.write(xmlOutput)
	f.close()

	# Post the resulting XML to GeoNetwork CSW service.  
	# Eventually, a check for Response code 200 should be made.
	POST_RESULT = True
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



