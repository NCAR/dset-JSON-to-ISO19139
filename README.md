# dset-JSON-to-ISO19139

A python command-line program for translating JSON metadata records to XML, conforming to these metadata standards:

* Output files: ISO 19139:2005 standard  (XML).
* Input files: DataCite 3.4 or 4.0 metadata standard (JSON).
* Input files: NCAR DSET Metadata Dialect, version 12 (JSON). 

These scripts require python 3.

The following python packages are required.

* lxml 

These are the package versions that have been tested: 

* lxml>=3.6.0

## Installation Instructions

### Prerequisites 

You must be on a machine with python installed, where the "virtualenv" or "conda" command is available.  One of these commands is needed to create a python environment where you can install several python library dependencies.  If either of the following commands returns a path, then you are set:

     which conda
     which virtualenv


#### Linux
On many versions of Linux, the "virtualenv" command should be available already.  If not, then the commands

     sudo yum install python-devel
     sudo pip install virtualenv 

should provide the "virtualenv" command.

You will also need to make sure these two system packages are installed: libxml2-devel and libxslt-devel.

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

You should choose to download Python 3 DMG installer.

Once Anaconda is installed, you should be able to run the Anaconda equivalent of the "virtualenv" command: 

     cd
     conda env create pythondev
     

### Install Software in your Python Development Environment

* Navigate in your browser to https://github.com/NCAR/dset-JSON-to-ISO19139 and click the green "Clone or Download" button.   Download the zip file, which may be named "" or "master.zip".

* Decide where you want the software to reside in your user space.  You should not need administrative privileges to install.   You only need read/write privileges in the folder where you want the software to reside.

Then type these commands:

     source ~/pythondev/bin/activate
     mv <zip_file> <install_directory>
     cd <install_directory>
     unzip <zip_file>
     cd dset-JSON-to-ISO19139-master
     pip install -r ./requirements.txt
      
If the final install command completes without errors, the translator should be ready to use.   To test that your installation works correctly, the following command should run without producing errors: 

     python dset2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml
