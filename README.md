# dset-JSON-to-ISO19139

A python command-line program for translating JSON metadata records to XML, conforming to these metadata standards:

* Output files: ISO 19139:2005 standard  (XML).
* Input files: DataCite 3.4 metadata standard (JSON).
* Input files: NCAR DSET Metadata Dialect, version 10 (JSON). 

These scripts assume python 2.7 is being used; using python 3 is untested.

The following python packages are required.

* lxml 
* simplejson

These are the package versions that have been tested: 

* lxml>=3.6.0
* simplejson>=3.8.2

## Installation Instructions

### Prerequisites 

You must be on a machine with python installed, where the python "virtualenv" command is available.  This command is needed to create a python environment where you can install the python libraries lxml, simplejson, and requests.

#### Linux
On most versions of Linux, the "virtualenv" command should be available already.  

You will need to make sure these two system packages are installed: 

libxml2-devel
libxslt-devel

Install them with this command: 

    sudo yum install libxml2-devel libxslt-devel

Then create your python development environment with this command: 

virtualenv pythondev

#### Mac OSX
For Mac OSX, the "virtualenv" command is not available in the default software environment.   If you wish to run on Mac OSX, you have two main courses of action: 

*  Install XCode, and the "homebrew" package manager (somewhat painful to install and manage) 
OR
*  Install Anaconda (much less painful to install and manage).  

Anaconda can be downloaded here:   

https://www.anaconda.com/download/#macos

You can probably download either the Python 3 DMG installer or the Python 2.7 DMG installer, but only the 2.7 installer has been tested, so it is the safer choice. 

Once Anaconda is installed, you should be able to run the Anaconda equivalent of the "virtualenv" command: 

     conda env create pythondev
     

### Install Software in your User Space

1.  Decide where you want the software to reside in your user space.  You should not need administrative privileges to install.   You only need read/write privileges in the folder where you want the software to reside.
2.  Open a terminal window and type:
     cd <install_directory>
     virtualenv json2iso
     . ./json2iso/bin/activate
      

