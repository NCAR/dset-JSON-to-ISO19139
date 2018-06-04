# dset-JSON-to-ISO19139

A python command-line program for translating JSON metadata records to XML, conforming to these metadata standards:

* Output files: ISO 19139:2005 standard  (XML).
* Input files: DataCite 3.4 metadata standard (JSON).
* Input files: NCAR DSET Metadata Dialect, version 10 (JSON). 

These scripts assume python 2.7 is being used; using python 3 is untested.

The following python packages are required.

* lxml 
* simplejson
* requests

These are the package versions that have been tested: 

* lxml==3.6.0
* simplejson==3.8.2
* requests==2.10.0

## Installation Instructions

### Prerequisites 

You must be on a machine with python installed, where the python "virtualenv" command is available.  This command is needed to create a python environment where you can install the python libraries lxml, simplejson, and requests.

On most versions of Linux, the "virtualenv" command should be available already.  For Mac OSX, however, the pre-installed version of python does not include the "virtualenv" command.   If you wish to run on Mac OSX, you have two main courses of action: 

*  Install XCode, and the "homebrew" package manager (somewhat painful to install and manage), *OR*
*  Install Anaconda (much less painful to install and manage).  

Anaconda can be downloaded here:   

https://www.anaconda.com/download/#macos

You can probably download either the Python 3 DMG installer or the Python 2.7 DMG installer, but only the 2.7 installer has been tested, so it is the safer choice. 

Once Anaconda is installed, you should be able to run the "virtualenv" command: 

     which virtualenv 
     


