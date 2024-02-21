# dset-JSON-to-ISO19139

A collection of python command-line programs for examining or producing metadata records according to the ISO XML 19139:2005 standard. 

There are three command-line utilities:

* **datacite2iso.py** : produce an ISO XML file from DOI published on the DataCite metadata service.
* **dset2iso.py** : produce an ISO XML file from a JSON file containing elements from the NCAR DSET Metadata Dialect, version 12.
* **xpath.py** :  print text values for a given XML element in an ISO record or group of records.

These utilities require python 3 and the python 'lxml' library (version 3.6 or greater).

## Installation Instructions

See [INSTALL.md](./INSTALL.md) for instructions on how to install these commands in a user environment. 

## Command-Line Usage 


### datacite2iso.py

A utility for translating DataCite JSON metadata into ISO 19139 metadata.

DataCite metadata is obtained from the DataCite website, so an internet connection is required.

    usage: 

        python datacite2iso.py --doi DOI [--template <template_file>] [--help] [--version]

    required arguments:

        --doi DOI            Digital Object Identifier (DOI)

    optional arguments:

        -h, --help           show this help message and exit
        --template TEMPLATE  custom ISO template to use from the 'templates' folder.  Default: datacite.xml
        --version            show program's version number and exit

    example usages:

        # Create ISO record for a specific DOI using the default DataCite XML output template
        python datacite2iso.py --doi 10.5065/D6WD3XH5   > datacite_D6WD3XH5.xml

        # Insert metadata into a special XML output template with hard-coded values specific to a particular researcher
        python datacite2iso.py --doi 10.5065/d6bc3x95 --template ral_vigh_dois.xml > test_vigh.xml

### dset2iso.py

A utility for translating JSON metadata into ISO 19139 metadata.

See the JSON input file found at [test_dset_full.txt](defaultInputRecords/test_dset_full.txt) for a complete example of the different metadata concepts that can be converted.  The converted file can be found at [test_dset_full.xml](defaultOutputRecords/test_dset_full.xml).

    usage: 

        dset2iso.py [--inputDir INPUTDIR] [--outputDir OUTPUTDIR] [--help] [--version]

    optional arguments:

        -h, --help              show this help message and exit
        --inputDir INPUTDIR     base directory for input records
        --outputDir OUTPUTDIR   base directory for output records
        --template XML_FILE_PATH  specify the XML file template to use.  Default path: './templates_ISO19139/dset_full.xml' 
        --version               show program's version number and exit

    example usages:

        # Convert a single DSET metadata record using STDIN and STDOUT:
        python dset2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml

        # Convert a collection of records in a given input folder, and save to an output folder: 
        python dset2iso.py --inputDir ./defaultInputRecords --outputDir ./defaultOutputRecords
        

### xpath.py

A utility for reporting existence of xml elements, or extracting element values, from a file or directory of files.

    usage: 

        xpath.py --type {publisher,resourceFormat,standardResourceFormat,geoExtent,timeExtent} [--inputDir INPUTDIR] [--file FILE] [--datasetsOnly] [--attribute ATTRIBUTE] [--version] [--help]

    required arguments:

        --type {publisher,resourceFormat,standardResourceFormat,geoExtent,timeExtent}  Type of XML element

    optional arguments:

        --inputDir INPUTDIR   base dir for XML files
        --file FILE           XML file to search
        --datasetsOnly        Limit output to records with resource type 'Dataset'
        --version             show program's version number and exit
        -h, --help            show this help message and exit

    example usages:

        # Print all resource format strings in the EOL WAF to a file
        python xpath.py --type resourceFormat --inputDir /data/repos/dash-eol-prod  > EOL_FORMATS.txt

        # Print whether geoExtent exists for Dataset records in the CISL WAF
        python xpath.py --type geoExtent --datasetOnly --inputDir /data/repos/dash-cisl-prod 