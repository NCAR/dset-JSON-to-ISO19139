import requests
import argparse
import os

PROGRAM_DESCRIPTION = '''

A program for uploading files to Zenodo.  

An API token for Zenodo is required.  Before running the program, set the API token value as follows:

 export ZENODO_TOKEN='<my_token>'
 
Also required is a path to a folder with files to upload.  All files in the folder and its sub-folders 
will be uploaded.  If the upload folder contains spaces, then surround the path in single quotes.

Example usage:

       python zenodo_create.py --folder <local_folder_with_files>

Optional arguments:

       --test                 Upload to Zenodo's sandbox server instead; requires a separate API TOKEN
       --resume <bucket_url>  Resume uploading to a specific bucket URL
       --version              Print the program version and exit.
       --help                 Print the program description and exit.

Tested with python 3.8.

Program Version: '''

__version_info__ = ('2025', '01', '23')
__version__ = '-'.join(__version_info__)

#
#  Parse the command line options.
#

programHelp = PROGRAM_DESCRIPTION + __version__
parser = argparse.ArgumentParser(description=programHelp)
parser.add_argument("--test", help="Upload to Zenodo Sandbox server", action='store_const', const=True)
parser.add_argument("--resume", nargs=1, help="Resume uploading to bucket URL", default=['None'])
parser.add_argument('--version', action='version', version="%(prog)s (" + __version__ + ")")

requiredArgs = parser.add_argument_group('required arguments')
requiredArgs.add_argument("--folder", nargs=1, required=True, help="File Upload Folder")

args = parser.parse_args()

upload_folder = args.folder[0]
bucket_url = args.resume[0]
TEST_UPLOAD = args.test


if TEST_UPLOAD:
    upload_url = 'https://sandbox.zenodo.org/api/deposit/depositions'
else:
    upload_url = 'https://zenodo.org/api/deposit/depositions'

#
# Get the environment variable 'ZENODO_TOKEN'
#

api_token = os.environ.get('ZENODO_TOKEN')
params = {'access_token': api_token}

print(f'upload_url == {upload_url}')
print(f'TEST_UPLOAD == {TEST_UPLOAD}')
print(f'bucket_url == {bucket_url}')
print(f'api_token == "{api_token}"')
print(f'upload_folder == "{upload_folder}"\n\n')

#
#  Get the file paths for upload.
#

#files = glob.glob(upload_folder + '/**/*', recursive=True)

upload_folder = os.path.abspath(upload_folder)
file_info = []

for root, subdirs, files in os.walk(upload_folder):
    for file_name in files:
        print('    ' + file_name)
        file_path = os.path.join(root, file_name)
        file_info.append((file_name, file_path))


#
#  Create a new dataset on Zenodo if no bucket URL is provided.
#
if bucket_url == 'None':
    headers = {"Content-Type": "application/json"}
    r = requests.post(upload_url, params=params,json={},headers=headers)

    # Exit if status code is not success.
    if r.status_code != 201:
        print(r.json)
        exit(r.status_code)

    bucket_url = r.json()["links"]["bucket"]

print(f'\n\n  UPLOAD BUCKET_URL = {bucket_url}\n\n')

#
#  Upload files.
#
for (file_name, file_path) in file_info:
    with open(file_path, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, file_name),
            data=fp,
            params=params,
        )
        checksum = r.json()['checksum']
        size =  r.json()['size']
        print(f'{file_name}:  checksum={checksum}, size={size}')