# dset-datacite-harvester-python
Code for pulling JSON metadata records from a website, converting the metadata to ISO XML, and saving to a file.  Not currently in active development but could be useful as a starting point for future code.

A set of python scripts for converting DataCite records to ISO 19139 and pushing them to a CSW Server.

These scripts assume python 2.7 is available; using python 3 is untested.

The following python packages are required.

* lxml 
* simplejson
* requests

These are the package versions that have been tested: 

* lxml==3.6.0
* simplejson==3.8.2
* requests==2.10.0

To harvest records, type this at the command line:

$ python ./Push_DataCite_To_GeoNetwork.py

This will also store pushed record IDs to the file 'pushedRecordIDs.txt'.  You can monitor this file to track progress.

To delete harvested records, type this at the command line: 

$ python ./Delete_GeoNetwork_Records.py

This will send delete requests for all of the record IDs in 'pushedRecordIDs.txt'.
