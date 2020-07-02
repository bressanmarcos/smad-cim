import pytest
import time
import multiprocessing

from random import randint

from pade.acl.aid import AID
from conftest import start_loop

import sys
sys.path.insert(0, '../')
from core.ied import IED # pylint: disable=import-error
from core.acom import AgenteCom # pylint: disable=import-error


class MockIED(IED):
    pass

def test_ied(run_ams):
    sniffer = run_ams
    enderecos_S1 = {"CH1": "192.168.0.101",
                "CH2": "192.168.0.102",
                "CH3": "192.168.0.103",
                "CH6": "192.168.0.106",
                "CH7": "192.168.0.107",
                "CH8": "192.168.0.108",
                "CH9": "192.168.0.109",
                "CH10": "192.168.0.110",
                "CH11": "192.168.0.111",
                "CH13": "192.168.0.113",
                "CH14": "192.168.0.114",
                "CH15": "192.168.0.115",
                "CH16": "192.168.0.116"}
    acom = AgenteCom(AID(f'acom@localhost:{randint(10000, 60000)}'), 'S1', enderecos_S1, True)
    acom.ams = sniffer.ams

    start_loop([acom])

