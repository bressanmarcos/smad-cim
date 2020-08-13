import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import pytest
import time
from pathlib import Path
import multiprocessing

from random import randint

from pade.acl.aid import AID

from core.ied import IED
from core.acom import AgenteCom

from tests.conftest import start_loop

class MockIED(IED):
    pass

def test_ied(run_ams):
    sniffer = run_ams
    enderecos_S1 = {"CH1": ("localhost", 50000+1),
                "CH2": ("localhost", 50000+2),
                "CH3": ("localhost", 50000+3),
                "CH6": ("localhost", 50000+6),
                "CH7": ("localhost", 50000+7),
                "CH8": ("localhost", 50000+8),
                "CH9": ("localhost", 50000+9),
                "CH10": ("localhost", 50000+10),
                "CH11": ("localhost", 50000+11),
                "CH13": ("localhost", 50000+13),
                "CH14": ("localhost", 50000+14),
                "CH15": ("localhost", 50000+15),
                "CH16": ("localhost", 50000+16)}
    acom = AgenteCom(AID(f'acom@localhost:{randint(10000, 60000)}'), 'S1', enderecos_S1, True)
    acom.ams = sniffer.ams

    start_loop([acom])

