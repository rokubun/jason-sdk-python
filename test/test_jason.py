import subprocess
import time

import jason_gnss.jason as jason

# ------------------------------------------------------------------------------

def test_status_api_key_ko():
    '''Status :: Check for invalid API key :: Should return a 403'''

    ret, return_code = jason.status("web", "1.0", api_key='invalid_api_key')
    assert return_code == 403
    assert 'message' in ret

# ------------------------------------------------------------------------------

def test_status_api_key_ok():
    '''Status :: Check valid API key :: Should return a 200'''

    ret, return_code = jason.status("web", "1.0")
    assert return_code == 200
    assert 'success' in ret

# ------------------------------------------------------------------------------


def test_status_default_args():
    '''Status :: Get status :: Should return a 200'''

    ret, return_code = jason.status("web", "1.0")
    assert return_code == 200
    assert 'success' in ret

# ------------------------------------------------------------------------------

def test_get_status_ko_unauthorized_process():
    '''Status :: Query unauthorized process :: Should return a 403'''

    process_id = 707

    _, return_code = jason.get_status(process_id)
    assert return_code == 403

# ------------------------------------------------------------------------------

def test_get_status_ko_wrong_process_id():
    '''Status :: Query wrong process :: Should fail test'''

    process_id = '3545lldsfdf'

    try:
        jason.get_status(process_id)
    except ValueError:
        pass
 
# ------------------------------------------------------------------------------

def test_process():
    '''GNSS :: process rover only / smartphone data :: Should return a process id'''

    rover_file = 'test/jason_gnss_test_file_smartphone.txt'
    ret, return_code = jason.submit_process(rover_file, label="jason-gnss_test_process")
    assert return_code == 200
    assert 'message' in ret
    assert 'id' in ret

    process_id = ret['id']

    assert process_id != None

# ------------------------------------------------------------------------------

def test_process_force_strategy():
    '''GNSS :: process rover only / smartphone data / force PPP :: Should return a process id'''

    rover_file = 'test/jason_gnss_test_file_smartphone.txt'
    ret, return_code = jason.submit_process(rover_file, strategy="PPP", label="jason-gnss_test_process_force_strategy")
    assert return_code == 200
    assert 'message' in ret
    assert 'id' in ret

    process_id = ret['id']

    assert process_id != None

# ------------------------------------------------------------------------------

def test_process_static_geodetic_rx():
    '''GNSS :: process rover only / geodetic rx / static :: Should return a process id'''

    rover_file = 'test/jason_gnss_test_file_base.txt'
    ret, return_code = jason.submit_process(rover_file, rover_dynamics="static", label="jason-gnss_test_process_static")
    assert return_code == 200
    assert 'message' in ret
    assert 'id' in ret

    process_id = ret['id']

    assert process_id != None

# ------------------------------------------------------------------------------

def test_process_geodetic_rx_force_basepos():
    '''GNSS :: process rover only / geodetic rx / force base position :: Should return a process id'''

    rover_file = 'test/jason_gnss_test_file_base.txt'
    base_lonlathgt = [-122.447607089227205,37.890876744023892,-21.096]
    ret, return_code = jason.submit_process(rover_file, base_lonlathgt=base_lonlathgt, label="jason-gnss_test_process_geodetic_rx_force_basepos")
    assert return_code == 200
    assert 'message' in ret
    assert 'id' in ret

    process_id = ret['id']

    assert process_id != None

# ------------------------------------------------------------------------------

def test_process_force_strategy_geodetic_rx():
    '''GNSS :: process rover only / geodetic rx / force PPP :: Should return a process id'''

    rover_file = 'test/jason_gnss_test_file_base.txt'
    ret, return_code = jason.submit_process(rover_file, strategy="PPP", label="jason-gnss_test_process_force_strategy_geodetic_rx")
    assert return_code == 200
    assert 'message' in ret
    assert 'id' in ret

    process_id = ret['id']

    assert process_id != None

# ------------------------------------------------------------------------------

def test_command_process():
    '''Commands :: process :: Should return a json with the filename'''

    cmd = ["jason", "process", 'test/jason_gnss_test_file_smartphone.txt']

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()
    assert p.returncode == 0
    assert len(stdout)

# ------------------------------------------------------------------------------

def test_command_submit_status_and_download():
    '''Commands :: submit/status/download :: Should return a json with info'''

    cmd = ["jason", "submit", 'test/jason_gnss_test_file_smartphone.txt']

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_id, _ = p.communicate()
    assert p.returncode == 0
    assert process_id

    process_id = int(process_id)

    cmd = ["jason", "status", str(process_id)]

    tic = time.process_time()
    TIMEOUT_THRESHOLD_S = 5 * 60
    finished = False
    while not finished:

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status, _ = p.communicate()
        assert p.returncode == 0
        assert status

        finished = 'FINISHED' in status.decode('utf-8')

        toc = time.process_time()
        if toc - tic >= TIMEOUT_THRESHOLD_S:
            break

        time.sleep(1)

    assert finished

    cmd = ["jason", "download", str(process_id)]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()
    assert p.returncode == 0
    assert len(stdout)

# ------------------------------------------------------------------------------

def test_command_convert():
    '''Commands :: conversion :: Should return a information on the file returned'''

    cmd = ["jason", "convert", 'test/ubx_with_tim_tp.ubx']

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()
    assert p.returncode == 0
    assert len(stdout)

# ------------------------------------------------------------------------------

def test_command_list_process():
    '''Commands :: list_processes :: Should return a information on the file returned'''

    cmd = ["jason", "list_processes"]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()

    assert p.returncode == 0
    assert len(stdout)

# ------------------------------------------------------------------------------

def test_command_submit_with_exif():
    '''Commands :: submit :: Should return '''
    
    cmd = ['jason', 'submit', 'test/jason_gnss_test_file_base.txt', '--images_folder', 'test/data/exif/']

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()

    assert p.returncode == 0
    assert len(stdout)

# ------------------------------------------------------------------------------