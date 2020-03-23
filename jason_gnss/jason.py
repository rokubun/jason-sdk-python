import requests
import os
import urllib

from . import AuthenticationError, API_URL, API_KEY_ENV_NAME, SECRET_TOKEN_ENV_NAME

def status(platform, app_version, api_key=None, secret_token=None):
    """
    Check status before starting using the API

    >>> status("web", "1.0")
    """

    url='{}/status'.format(API_URL)

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    import sys
    sys.stderr.write(api_key + '\n')

    headers = __build_headers__(api_key)

    params = { 
        'platform' : platform,
        'app_version' : app_version
    }

    if secret_token:
        params.update({'token': secret_token})

    r = requests.get(url, headers=headers, params=params)

    return r.json(), r.status_code


def submit_process(rover_file, process_type="GNSS", base_file=None, base_position=None,
                    api_key=None, secret_token=None):
    """
    """

    api_key, secret_token = __fetch_credentials__(api_key, secret_token)

    url='{}/processes'.format(API_URL)
    
    headers = __build_headers__(api_key)
    
    with open(rover_file, 'rb') as fh:
        files = {
            'type' : (None, process_type),
            'token' : (None, secret_token),
            'rover_file': (rover_file, fh)
        }
    
        r = requests.post(url, headers=headers, files=files)

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


def download_results(process_id):
    """
    Get the file bundle (compressed file) with the processing results
    """

    status, status_code = get_status(process_id)

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
