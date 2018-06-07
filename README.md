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

You must be on a machine with python installed, where the python "virtualenv" command is available.  This command is needed to create a python environment where you can install several python library dependencies.

#### Linux
On most versions of Linux, the "virtualenv" command should be available already.  If not, then the commands

     sudo yum install python-devel
     sudo pip install virtualenv 

should provide the "virtualenv" command.

You will also need to make sure these two system packages are installed: 

libxml2-devel
libxslt-devel

Install them with this command: 

     sudo yum install libxml2-devel libxslt-devel

Then create your python development environment with these commands: 

cd
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

     cd
     conda env create pythondev
     

### Install Software in your Python Development Environment

* Navigate in your browser to https://github.com/NCAR/dset-JSON-to-ISO19139 and click the green "Clone or Download" button.   Download the zip file, which may be named "" or "master.zip".

* Decide where you want the software to reside in your user space.  You should not need administrative privileges to install.   You only need read/write privileges in the folder where you want the software to reside.

* Type these commands:


     source ~/pythondev/bin/activate
     mv <zip_file> <install_directory>
     cd <install_directory>
     unzip <zip_file>
     cd dset-JSON-to-ISO19139-master
     pip install -r ./requirements.txt
      
Your software should be ready to use.   To test that your installation works correctly, the following command should run without producing errors: 

     python dset2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml
