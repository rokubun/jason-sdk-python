import jason_gnss.jason as jason

def test_status_api_key_ko():

    ret, return_code = jason.status("web", "1.0", api_key='invalid_api_key')
    assert return_code == 403
    assert 'message' in ret

def test_status_api_key_ok():

    ret, return_code = jason.status("web", "1.0")
    assert return_code == 200
    assert 'success' in ret


def test_status_default_args():

    ret, return_code = jason.status("web", "1.0")
    assert return_code == 200
    assert 'success' in ret


def test_process():

    import time

    rover_file = 'test/jason_gnss_test_file_smartphone.txt'
    ret, return_code = jason.submit_process(rover_file)
    assert return_code == 200
    assert 'message' in ret
    assert 'id' in ret

    process_id = ret['id']

    assert process_id != None


def test_get_status_ko_unauthorized_process():

    process_id = 707

    ret, return_code = jason.get_status(process_id)
    assert return_code == 403
