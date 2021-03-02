import requests
import os
import os.path
import urllib
import tempfile

from roktools import logger

from . import AuthenticationError, API_URL

def status(platform, app_version, api_key=None, secret_token=None):
    """
    Check status before starting using the API

    >>> status("web", "1.0")
    """

    url='{}/status'.format(API_URL)

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    headers = __build_headers__(api_key)

    params = { 
        'platform' : platform,
        'app_version' : app_version
    }

    if secret_token:
        params.update({'token': secret_token})

    r = requests.get(url, headers=headers, params=params)

    return r.json(), r.status_code

# ------------------------------------------------------------------------------

def submit_process(rover_file, process_type="GNSS", 
                    base_file=None, base_lonlathgt=None, camera_metadata_file=None,
                    api_key=None, secret_token=None, rover_dynamics='dynamic',
                    strategy='PPK/PPP', label="jason-gnss"):
    """
    Submit a process to Jason PaaS

    :param rover_file: Filename with the GNSS measurements of the rover receiver
    :param process_type: Type of process to submit to Jason (GNSS or CONVERSION)
    :param base_file: Filename with the GNSS measurements of the base receiver
    :param base_lonlathgt: Array with the longitude, latitude and height
    :param camera_metadata_file: Filename with the exif data of the images in the folder
    :param api_key: Jason API key, if not provided will be fetched from the 
                    environement variables
    :param secret_token: Your Jason user secret token, if not provided will be 
                    fetched from the environement variables
    :param strategy: Force processing strategy (e.g. PPP or PPK). If left to None
                    Jason will work on a best effort basis, trying to pick
                    the most accurate strategy given the data provided by the
                    user.
    :param rover_dynamics: Dynamics of the rover receiver ('static' or 'dynamic')
    :param label: specify a label for the process to submit
    """

    if not os.path.isfile(rover_file):
        logger.critical("Rover file [ {} ] does not exist!".format(rover_file))
        return None, None
    elif base_file and not os.path.isfile(base_file):
        logger.critical("Base file [ {} ] specified but does not exist!".format(base_file))
        return None, None

    rover_file_fh = open(rover_file, 'rb')
    base_file_fh = open(base_file, 'rb') if base_file else None
    camera_metadata_file_fh = open(camera_metadata_file, 'rb') if camera_metadata_file else None

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    logger.debug('Submitting job to end-point {}'.format(API_URL))

    url='{}/processes'.format(API_URL)
    
    headers = __build_headers__(api_key)

    files = {
        'type' : (None, process_type),
        'token' : (None, secret_token),
        'rover_file': (rover_file, rover_file_fh),
        'rover_dynamics': (None, rover_dynamics),
        'label': (None, label),
        'camera_metadata_file': (camera_metadata_file, camera_metadata_file_fh)
    }

    if base_file:
        files.update({'base_file' : (base_file, base_file_fh)})

    config_file, config_file_fh = __create_config_file__(base_lonlathgt)
    if config_file:
        files.update({'config_file' : ('config_file', config_file_fh)})

    if camera_metadata_file:
        files.update({'camera_metadata_file' : (camera_metadata_file, camera_metadata_file_fh)})

    if base_lonlathgt:
        lon = base_lonlathgt[0]
        lat = base_lonlathgt[1]
        hgt = base_lonlathgt[2]
        pos_str = '{},{},{}'.format(lat, lon, hgt)
        files.update({'external_base_station_position' : (None, pos_str)})

    if strategy:
        files.update({'user_strategy' : (None, strategy)})

    logger.debug('Query parameters {}'.format(files))

    r = requests.post(url, headers=headers, files=files)

    rover_file_fh.close()
    if base_file_fh:
        base_file_fh.close()
    if config_file_fh:
        config_file_fh.close()
        os.remove(config_file)
    if camera_metadata_file_fh:
        camera_metadata_file_fh.close()

    return r.json(), r.status_code

# ------------------------------------------------------------------------------

def get_status(process_id, api_key=None, secret_token=None):
    """
    Check the status of a specific process_id
    """

    __check_process_id__(process_id)
    
    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    url='{}/processes/{}'.format(API_URL, process_id)

    headers = __build_headers__(api_key)
    params = { 'token' : secret_token }

    r = requests.get(url, headers=headers, params=params)

    return r.json(), r.status_code

# ------------------------------------------------------------------------------

def download_results(process_id, api_key=None, secret_token=None):
    """
    Get the file bundle (compressed file) with the processing results
    """

    status, status_code = get_status(process_id,
                                     api_key=api_key, secret_token=secret_token)

    if (status_code != 200):
        return None

    if status['process']['status'] != 'FINISHED':
        return None

    zip_result = list(filter(lambda x: (x['type'] == 'zip'), status['results']))[0]

    url = zip_result["value"]
    r = requests.get(url)

    basename = zip_result["name"]
    results_file_name = os.path.join(os.getcwd(), basename)
    f = open(results_file_name, 'wb')
    f.write(r.content)
    f.close()
    
    return results_file_name

# ------------------------------------------------------------------------------

def list_processes(api_key=None, secret_token=None):
    """
    List the processess that the user has issued
    """

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    url='{}/users/{}/processes'.format(API_URL, secret_token)

    headers = __build_headers__(api_key)
    params = {}

    r = requests.get(url, headers=headers, params=params)

    processes = []
    if r.status_code == 200:
        processes = [__filter_process_info__(p) for p in r.json()]    

    return processes

# ------------------------------------------------------------------------------

def api_status(api_key=None):
    """
    Get the API status, containing the version of the software running the versions
    """

    api_key, _ = __fetch_credentials__(api_key, None)

    url='{}/status'.format(API_URL)

    headers = __build_headers__(api_key)
    params = {}

    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        out = r.json()
        out.pop('success')
    else:
        out = None

    return out

# ------------------------------------------------------------------------------

def __filter_process_info__(process_info):

    FIELDS = ['id', 'type', 'status', 'source_file', 'created']

    out = { k:process_info[k] for k in FIELDS}

    out['source_file'] = process_info['source_file'].split('/')[-1]

    return out

# ------------------------------------------------------------------------------


def __build_headers__(api_key):
    """
    Build the headers for the API call, which are common to all interactions
    with the API
    """

    headers = {
        'accept': 'application/json',
        'ApiKey': api_key
    }

    return headers

# ------------------------------------------------------------------------------

def __fetch_credentials__(api_key, secret_token):

    if api_key is None:
        api_key = os.getenv('JASON_API_KEY', api_key)

    if secret_token is None:
        secret_token = os.getenv('JASON_SECRET_TOKEN', secret_token)

    if api_key is None or secret_token is None:
        raise AuthenticationError("Missing Api key and/or secret token\n")

    return api_key, secret_token

# ------------------------------------------------------------------------------

def __create_config_file__(base_lonlathgt=None):

    fh, name = tempfile.mkstemp(prefix='config_file_', text=True)
    fh = open(name, 'w')

    dynamics = 'dynamic'
    fh.write('rover_dynamics:\n    {}\n'.format(dynamics))

    if base_lonlathgt:
        lat = base_lonlathgt[1]
        lon = base_lonlathgt[0]
        hgt = base_lonlathgt[2]
        latlonstr = '{},{},{}'.format(lat, lon, hgt)

        fh.write('external_base_station_position:\n    {}\n'.format(latlonstr))

    fh.close()

    fh = open(name, 'r')

    return name, fh

# ------------------------------------------------------------------------------

def __check_process_id__(process_id):

    import re

    process_id_str = str(process_id)
    pattern = re.compile('[0-9]')
    result = pattern.findall(process_id_str)

    if len(result) != len(process_id_str):
        raise ValueError('Process ID [ {} ] does not seem correct, only numbers are allowed\n'.format(process_id_str))
