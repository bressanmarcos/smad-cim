import pytest
import multiprocessing
import subprocess
import time
from pade.misc.utility import start_loop

@pytest.fixture(scope='function')
def with_ams():
    """Inicializa AMS."""
    processes = []
    ams_dict = {'name': 'localhost', 'port': 10000}

    time.sleep(1.0)
    from pade.core import new_ams
    commands = ['python', new_ams.__file__, 'user', 'email', 'pass', str(ams_dict['port'])]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)
    processes.append(p)
    time.sleep(2.0)

    from pade.core.sniffer import Sniffer
    sniffer = Sniffer(host=ams_dict['name'], port=ams_dict['port']+1)
    sniffer.ams = ams_dict

    yield sniffer
    """Finaliza AMS"""
    print('\nKilling AMS')
    for p in processes:
        p.kill()




