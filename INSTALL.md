# dset-JSON-to-ISO19139:  Installation Instructions


## Prerequisites 

You must be on a machine with python installed, where the "virtualenv" or "conda" command is available.  One of these commands is needed to create a python environment where you can install several python library dependencies.  If either of the following commands returns a path, then you are set:

     which conda
     which virtualenv


### Linux
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

### Mac OSX
For Mac OSX, the "virtualenv" command is not available in the default software environment.   If you wish to run on Mac OSX, you have two main courses of action: 

*  Install XCode, and the "homebrew" package manager (somewhat painful to install and manage) 

OR

*  Install Anaconda (much less painful to install and manage).  

Anaconda can be downloaded here:   

https://www.anaconda.com/download/#macos

You should choose to download Python 3 DMG installer.

Once Anaconda is installed, you should be able to run the Anaconda equivalent of the "virtualenv" command: 

     cd
     conda env create -n pythondev
     

## Install Software in your Python Development Environment

* Navigate in your browser to https://github.com/NCAR/dset-JSON-to-ISO19139 and click the green "Code" button.   Clone the repository or download the zip file.   The zip file may be named "dset-JSON-to-ISO19139-main.zip" or something similar.

* Activate the conda or pip-based environment:

If you are using conda, type:

    conda activate pythondev
    INSTALL_CMD='conda update -f ./requirements.txt'

If you are using pip, type:

    source ~/pythondev/bin/activate
    INSTALL_CMD='pip install -r ./requirements.txt'

* Decide where you want the software to reside in your user space.  You should not need administrative privileges to install.   You only need read/write privileges in the folder where you want the software to reside.  We will call the target directory `<install_directory>`.
* Install the software in your python environment.
  
If you cloned the repo, type these commands:

     mv <cloned-repo> <install_directory>
     cd <install_directory>
     cd dset-JSON-to-ISO19139
     $INSTALL_CMD

If you downloaded the zip file, type these commands:

     mv <zip_file> <install_directory>
     cd <install_directory>
     unzip <zip_file>
     cd dset-JSON-to-ISO19139-main
     $INSTALL_CMD

If the final install command completes without errors, the translator should be ready to use.   To test that your installation works correctly, the following command should run without producing errors: 

     python dset2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml
