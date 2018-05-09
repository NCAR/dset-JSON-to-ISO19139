# dset-datacite-harvester-python
A python command-line script for translating JSON metadata records to XML, following these conventions:

* ISO 19139:2005 standard for output files written in XML.
* DataCite 3.4 metadata standard for JSON-based input files.
* NCAR DSET Metadata Dialect version 10 rules for JSON-based input files. 

These scripts assume python 2.7 is being used; using python 3 is untested.

The following python packages are required.

* lxml 
* simplejson
* requests

These are the package versions that have been tested: 

* lxml==3.6.0
* simplejson==3.8.2
* requests==2.10.0

