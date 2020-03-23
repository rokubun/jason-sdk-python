import sys
import time
from docopt import docopt

from . import InvalidResponse, jason

def process(rover_file, process_type="GNSS", base_file=None, base_lonlathgt=None, **kwargs):
    """
    Submit a process to Jason and wait for it to end so that the results file
    is also download
    """

    sys.stderr.write('Process file {}\n'.format(rover_file))

    process_id = submit(rover_file, process_type=process_type, 
                        base_file=base_file, base_lonlathgt=base_lonlathgt)

    if process_id is None:
        sys.stderr.write('Could not submit [ {} ] for processing\n'.format(rover_file))
        return None

    ELAPSED_TIME_THRESHOLD = 60

    start_time = time.time()
    while True:

        if status(process_id) == 'FINISHED':
            return download(process_id)
        elif status(process_id) == 'ERROR':
            sys.stderr.write('An unexpected error occurred in the task!\n')
            return None

        time.sleep(3)
        elapsed_time = time.time() - start_time
        if (elapsed_time > ELAPSED_TIME_THRESHOLD):
            break

    sys.stderr.write('Time Out!')
    return None

def status(process_id, **kwargs):
    """
    Get the status of the given process_id
    """
    
    ret, return_code = jason.get_status(process_id)

    if return_code == 200:
        status = ret['process']['status']
        sys.stdout.write('{}\n'.format(status))
        return status
    else:
        return None

def submit(rover_file, process_type="GNSS", base_file=None, base_lonlathgt=None, **kwargs):
    """
    Submit a process to the server without waiting for it to end
    """

    process_id = None

    ret, return_code = jason.submit_process(rover_file, 
                        process_type=process_type, 
                        base_file=base_file, base_lonlathgt=base_lonlathgt)
    
    if return_code == 200:
        process_id = ret['id']

    return process_id


def download(process_id, **kwargs):
    """
    Download the results for the given process_id
    """

    filename = jason.download_results(process_id)

    sys.stderr.write('Results file [ {} ] for process id [ {} ] downloaded\n'.format(filename, process_id))

    return filename

def list_processes(**kwargs):
    """
    List the processes issues by the user
    """

    processes = jason.list_processes()

    header_printed = False
    for process in processes:

        if not header_printed:
            fields = process.keys()

            header_printed = True

            sys.stdout.write('# {}\n'.format(','.join(fields)))

        process_str = ','.join([str(process[k]) for k in process])
        sys.stdout.write(process_str + '\n')            

    return None
