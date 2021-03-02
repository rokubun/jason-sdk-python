import sys
import time
import json
import jason_gnss.exif as exif
from docopt import docopt

from roktools import logger


from . import InvalidResponse, jason

def process(rover_file, process_type="GNSS", base_file=None, base_lonlathgt=None, images_folder=None, timeout=None, **kwargs):
    """
    Submit a process to Jason and wait for it to end so that the results file
    is also download
    """

    logger.info('Process file [ {} ]'.format(rover_file))
    logger.debug('Timeout  {}'.format(timeout))

    process_id = submit(rover_file, process_type=process_type, 
                 base_file=base_file, base_lonlathgt=base_lonlathgt, images_folder=images_folder, **kwargs)

    if process_id is None:
        logger.critical('Could not submit [ {} ] for processing'.format(rover_file))
        return None
    
    logger.info('Submitted process with ID {}'.format(process_id))

    start_time = time.time()
    spinner = __spinning_cursor__()
    while True:

        process_status = status(process_id)
        logger.debug('Processing status {}'.format(process_status))

        if process_status == 'FINISHED':
            logger.info('Completed process with ID {}'.format(process_id))
            return download(process_id)
        elif process_status == 'ERROR':
            logger.critical('An unexpected error occurred in the task!')
            return None

        # Spinner
        sys.stderr.write(next(spinner))
        sys.stderr.flush()
        time.sleep(1)
        sys.stderr.write('\b')

        if (timeout and time.time() - start_time > timeout):
            logger.critical("Time Out! The process did not end in " +
                            "[ {} ] seconds, ".format(timeout) +
                            "but might be available for download at a later stage.")
            return None

    logger.critical('Unexpected error occured')
    return None

# ------------------------------------------------------------------------------

def status(process_id, **kwargs):
    """
    Get the status of the given process_id
    """

    res = None
    
    ret, return_code = jason.get_status(process_id)

    logger.debug('Return code {}'.format(ret))
    if return_code == 200:
        res = ret['process']['status']
    
    return res

# ------------------------------------------------------------------------------

def submit(rover_file, process_type="GNSS", base_file=None, base_lonlathgt=None, images_folder=None, **kwargs):
    """
    Submit a process to the server without waiting for it to end
    """

    res = None
    camera_metadata_file = exif.get_exif_tags_file(images_folder=images_folder) if images_folder else None

    if camera_metadata_file:
        ret, return_code = jason.submit_process(rover_file,
                            process_type=process_type, base_file=base_file,
                            base_lonlathgt=base_lonlathgt, camera_metadata_file=camera_metadata_file, **kwargs)

        if return_code == 200:
            res =  ret['id']
    else:
        logger.critical('It was not possible to generate the camera metadata file.')

    return res

# ------------------------------------------------------------------------------

def download(process_id, **kwargs):
    """
    Download the results for the given process_id
    """

    filename = jason.download_results(process_id)

    logger.info('Results file [ {} ] for process id [ {} ] downloaded\n'.format(filename, process_id))

    return filename

# ------------------------------------------------------------------------------

def list_processes(**kwargs):
    """
    List the processes issued by the user
    """

    processes = jason.list_processes()

    res = None

    header_printed = False
    for process in processes:

        if not header_printed:
            fields = process.keys()

            header_printed = True

            sys.stdout.write('# {}\n'.format(','.join(fields)))

        if res is None:
            res = ""
        res += ','.join([str(process[k]) for k in process])

    return res

# ------------------------------------------------------------------------------

def api_status():

    return jason.api_status()

# ------------------------------------------------------------------------------

def __spinning_cursor__(flavour='basic'):

    FLAVOUR = {
        'basic': '-\|/-\|/',
        'braille': "⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿"
    }
    
    cursors = FLAVOUR.get(flavour, 'basic')

    while True:
        for cursor in cursors:
                yield cursor

