#/bin/bash

#
# Runs nosetests on all test files in the current directory if possible.
# If nosetests is not available, it runs a subsitute set of commands in place of nosetests.
#


function NosetestSubstitute {
    
    testFiles='xml.py iso19139.py'

    for f in $testFiles; do
        echo 
        echo Running "python $f":
        python $f
        if [ $? != 0 ]; then
           echo ""
           echo "Errors found in $f; halting."
           echo ""
           return 1
        fi
    done
    
    echo ""
    echo "SUCCESS; all tests passed in '$testFiles'"
    echo ""
    return 0
}


# Test whether nosetests is available.

#COVER_MIN_PERCENTAGE=100
COVER_MIN_PERCENTAGE=0
COVER_PACKAGES="api.util.xml,api.util.iso19139"

which nosetests

if [ $? == 0 ]; then
   nosetests --nocapture --with-coverage --cover-package=$COVER_PACKAGES --cover-min-percentage=$COVER_MIN_PERCENTAGE *.py
else
   NosetestSubstitute
fi 
