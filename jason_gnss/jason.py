import requests
import os
import os.path
import sys
import urllib
import tempfile

from . import AuthenticationError, API_URL, API_KEY_ENV_NAME, SECRET_TOKEN_ENV_NAME

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


def submit_process(rover_file, process_type="GNSS", 
                    base_file=None, base_lonlathgt=None,
                    api_key=None, secret_token=None):
    """
    Submit a process to Jason PaaS
    """

    if not os.path.isfile(rover_file):
        sys.stderr.write("Rover file [ {} ] does not exist!".format(rover_file))
        return None, None
    elif base_file and not os.path.isfile(base_file):
        sys.stderr.write("Base file [ {} ] specified but does not exist!".format(base_file))
        return None, None

    rover_file_fh = open(rover_file, 'rb')
    base_file_fh = open(base_file, 'rb') if base_file else None

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    url='{}/processes'.format(API_URL)
    
    headers = __build_headers__(api_key)

    files = {
        'type' : (None, process_type),
        'token' : (None, secret_token),
        'rover_file': (rover_file, rover_file_fh)
    }

    if base_file:
        files.update({'base_file' : (base_file, base_file_fh)})

    config_file, config_file_fh = __create_config_file__(base_lonlathgt)
    if config_file:
        files.update({'config_file' : ('config_file', config_file_fh)})

    r = requests.post(url, headers=headers, files=files)

    rover_file_fh.close()
    if base_file_fh:
        base_file_fh.close()
    if config_file_fh:
        config_file_fh.close()
        os.remove(config_file)

    return r.json(), r.status_code

def get_status(process_id, api_key=None, secret_token=None):
    """
    Check the status of a specific process_id
    """

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    url='{}/processes/{}'.format(API_URL, process_id)

    headers = __build_headers__(api_key)
    params = { 'token' : secret_token }

    r = requests.get(url, headers=headers, params=params)

    return r.json(), r.status_code


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

    ZIP_FILE_POS = -1
    url = status['results'][ZIP_FILE_POS]['url']
    results_file_name = os.path.join(os.getcwd(), status['results'][ZIP_FILE_POS]['name'])

    r = requests.get(url)
    f = open(results_file_name, 'wb')
    f.write(r.content)
    f.close()
    
    return results_file_name

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

def __filter_process_info__(process_info):

    FIELDS = ['id', 'type', 'status', 'source_file', 'created']

    out = { k:process_info[k] for k in FIELDS}

    out['source_file'] = process_info['source_file'].split('/')[-1]

    return out


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

def __fetch_credentials__(api_key, secret_token):

    if api_key is None:
        api_key = os.getenv(API_KEY_ENV_NAME, api_key)

    if secret_token is None:
        secret_token = os.getenv(SECRET_TOKEN_ENV_NAME, secret_token)

    return api_key, secret_token

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