import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import pytest
import datetime
import time
import multiprocessing
from random import randint
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent_

from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module
from core.adc import AgenteDC, SubscreverACom, EnviarComando # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from core.an import AgenteN, ReceberPoda, GerenciarNegociacao # pylint: disable=import-error,no-name-in-module
from core.ied import IED  # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error


if __name__ == "__main__":
    # S1
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
                    "CH16": "192.168.0.116", 
                    "CH19": "192.168.0.119"}
    acom = AgenteCom(AID('agentecom@localhost:60010'), 'S1', enderecos_S1)

    adc = AgenteDC(AID('agentedc@localhost:60011'), 'S1')
    adc.subscrever_a(AID('agentecom@localhost:60010'))
    adc.set_an(AID('agenten@localhost:60012'))

    an = AgenteN(AID('agenten@localhost:60012'), 'S1')
    an.add_adc_vizinho(AID('agentedc-2@localhost:60021'))
    an.add_adc_vizinho(AID('agentedc-3@localhost:60031'))

    # S2
    enderecos_S2 = {"CH4": "192.168.0.104",
                    "CH5": "192.168.0.105",
                    "CH3": "192.168.0.103",
                    "CH8": "192.168.0.108",
                    "CH11": "192.168.0.111",
                    "CH12": "192.168.0.112"}
    acom2 = AgenteCom(AID('agentecom-2@localhost:60020'), 'S2', enderecos_S2)

    adc2 = AgenteDC(AID('agentedc-2@localhost:60021'), 'S2')
    adc2.subscrever_a(AID('agentecom-2@localhost:60020'))
    adc2.set_an(AID('agenten-2@localhost:60022'))

    an2 = AgenteN(AID('agenten-2@localhost:60022'), 'S2')
    an2.add_adc_vizinho(AID('agentedc@localhost:60011'))
    an2.add_adc_vizinho(AID('agentedc-3@localhost:60031'))
    
    # S3
    enderecos_S3 = {"CH17": "192.168.0.117",
                    "CH18": "192.168.0.118",
                    "CH16": "192.168.0.116"}
    acom3 = AgenteCom(AID('agentecom-3@localhost:60030'), 'S3', enderecos_S3)

    adc3 = AgenteDC(AID('agentedc-3@localhost:60031'), 'S3')
    adc3.subscrever_a(AID('agentecom-3@localhost:60030'))
    adc3.set_an(AID('agenten-3@localhost:60032'))

    an3 = AgenteN(AID('agenten-3@localhost:60032'), 'S3')
    an3.add_adc_vizinho(AID('agentedc@localhost:60011'))
    an3.add_adc_vizinho(AID('agentedc-2@localhost:60021'))


    start_loop([acom, adc, an, acom2, adc2, an2, acom3, adc3, an3])