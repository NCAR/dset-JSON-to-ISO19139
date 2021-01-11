

import requests                             # Allows simple POST requests
from requests.auth import HTTPBasicAuth     # Allows POST basic authentication

def pushToCSW(xmlText):
    """ This function is not generalized yet: push CSW record to a specific CSW server. """

    #GeoNetworkBaseURL = 'http://localhost:8080'
    GeoNetworkBaseURL = 'https://geonetwork.prototype.ucar.edu'
    url = GeoNetworkBaseURL + '/geonetwork/srv/eng/csw-publication?SERVICE=CSW&VERSION=2.0.2&REQUEST=INSERT'
    header = {'Content-Type': 'text/xml'}

    try:
        response = requests.post(url, auth=HTTPBasicAuth('admin', '******'), headers=header, data=xmlOutput)

        # Save recordID as a way to allow later deletion through CSW
        id_file.write(recordID + '\n')

    except requests.ConnectionError:
        print('ConnectionError: failed to connect: ' + url, file=sys.stderr)

    if response.status_code != 200:
        print(response.text, file=sys.stderr)
        raise OSError("Response " + str(response.status_code) + ": " + response.content)

    print(response.status_code, file=sys.stderr)
