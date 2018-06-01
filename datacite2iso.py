#
# Python program for translating DataCite metadata to ISO 19139.
#

import argparse
import sys
import os.path

import api.datacite_input as datacite

PROGRAM_DESCRIPTION = '''

A program for translating DataCite JSON metadata into ISO 19139 metadata.

DataCite metadata is obtained from the DataCite website, so an internet connection is required.

Example usage:

       python datacite2iso.py --doi 10.5065/D6WD3XH5   > test_datacite.xml

'''

class OverrideErrorParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def getTemplateFile(templateArg):
    ''' Return the path to the ISO output template file.'''
    templateFolder = './templates_ISO19139/'
    defaultTemplate= 'dset_min.xml'

    if templateArg:
        template = templateArg[0]
    else:
        template = defaultTemplate

    templatePath = templateFolder + template
    return templatePath

#
#  Parse the command line options.
#
parser = OverrideErrorParser(description=PROGRAM_DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--template", nargs=1, help="custom ISO template to use from the 'templates' folder")

requiredArgs = parser.add_argument_group('required arguments')
requiredArgs.add_argument("--doi", nargs=1, required=True, help="Digital Object Identifier (DOI)")

args = parser.parse_args()


doi = args.doi[0]
records = datacite.getDataCiteRecords(doi)

template = getTemplateFile(args.template)
if not os.path.isfile(template):
    message = 'Template file does not exist: %s\n' % template
    parser.error(message)

#
#  Perform the translation.
#
if len(records) > 0:
    record = records[0]
    output = datacite.translateDataCiteRecord(record, template)
    print(output)
else:
    print("DOI " + doi + " was not found.\n")