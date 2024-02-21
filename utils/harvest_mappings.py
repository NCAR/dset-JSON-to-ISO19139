###
#    RESOURCE_FORMAT_MAPPING maps arbitrary Resource Format strings to Standardized Resource Format strings.
#
#    Algorithm Description:
#
#      * If the original Resource Format string is empty or missing, return "UNDEFINED FORMAT"
#      * Convert the original Resource Format string to lower case
#      * Loop over keys in the mapping dictionary:
#          - If the current key is found within the converted string, return the corresponding standardized value
#      * If none of the keys are found within the converted string, return "OTHER"
###

MISSING_FORMAT_STRING = "UNDEFINED FORMAT"
OTHER_FORMAT_STRING = "OTHER"

RESOURCE_FORMAT_MAPPING = {
    'netcdf': "NetCDF",
    'matlab': "Matlab",
    'pdf': "PDF",
    'hdf': "HDF",
    'grib': "GRIB",
    'csv': "CSV",
    'comma-separated': "CSV",
    'ascii': "ASCII",
    'text/plain': "ASCII",
    'jpg': "JPEG",
    'jpeg': "JPEG",
    'gif': "GIF",
    'png': "PNG",
    'portable network graphics': "PNG",
    'tiff': "TIFF",
    'zip': "Archive",
    'tar': "Archive",
    'application/x-compress': "Archive",
    'binary': "Binary",
    'octet-stream': "Binary",
    'xls': "XLS",
    'bufr': "BUFR",
    'zarr': "ZARR",
    'genpro': "GENPRO",
    'fits': "FITS",
    'physical': "Physical Media",
    'unknown': MISSING_FORMAT_STRING,
    'undefined': MISSING_FORMAT_STRING,
}


def getStandardResourceFormat(format_string):
    """
    Given a non-empty ResourceFormat string, return the standardized version
    of that resource format, or 'OTHER' if there is no match.
    If there is no format string, return 'UNDEFINED FORMAT'
    """
    if not format_string:
        return MISSING_FORMAT_STRING

    test_string = format_string.lower()
    for key, value in RESOURCE_FORMAT_MAPPING.items():
        if key in test_string:
            return value
    return OTHER_FORMAT_STRING
