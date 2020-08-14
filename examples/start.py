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
from core.adc import AgenteDC, SubscreverAEventos, EnviarComandoDeChaves # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from core.an import AgenteN, ReceberPoda, GerenciarNegociacao # pylint: disable=import-error,no-name-in-module
from core.ied import IED  # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

from rede.rede_simu import Network

if __name__ == "__main__":

    ## Executar IEDs
    # Instancia classe
    network = Network()
    # S1
    enderecos_S1 = {"CH1": ("localhost", 50001),
                    "CH2": ("localhost", 50002),
                    "CH3": ("localhost", 50003),
                    "CH6": ("localhost", 50006),
                    "CH7": ("localhost", 50007),
                    "CH8": ("localhost", 50008),
                    "CH9": ("localhost", 50009),
                    "CH10": ("localhost", 50010),
                    "CH11": ("localhost", 50011),
                    "CH13": ("localhost", 50013),
                    "CH14": ("localhost", 50014),
                    "CH15": ("localhost", 50015),
                    "CH16": ("localhost", 50016), 
                    "CH19": ("localhost", 50019)}
    acom = AgenteCom(AID('agentecom@localhost:60010'), 'S1', enderecos_S1)

    adc = AgenteDC(AID('agentedc@localhost:60011'), 'S1')
    adc.subscrever_a(AID('agentecom@localhost:60010'))
    adc.set_an(AID('agenten@localhost:60012'))

    an = AgenteN(AID('agenten@localhost:60012'), 'S1')
    an.add_adc_vizinho(AID('agentedc-2@localhost:60021'))
    an.add_adc_vizinho(AID('agentedc-3@localhost:60031'))

    # S2
    enderecos_S2 = {"CH4": ("localhost", 50004),
                    "CH5": ("localhost", 50005),
                    "CH3": ("localhost", 50003),
                    "CH8": ("localhost", 50008),
                    "CH11": ("localhost", 50011),
                    "CH12": ("localhost", 50012)}
    acom2 = AgenteCom(AID('agentecom-2@localhost:60020'), 'S2', enderecos_S2)

    adc2 = AgenteDC(AID('agentedc-2@localhost:60021'), 'S2')
    adc2.subscrever_a(AID('agentecom-2@localhost:60020'))
    adc2.set_an(AID('agenten-2@localhost:60022'))

    an2 = AgenteN(AID('agenten-2@localhost:60022'), 'S2')
    an2.add_adc_vizinho(AID('agentedc@localhost:60011'))
    an2.add_adc_vizinho(AID('agentedc-3@localhost:60031'))
    
    # S3
    enderecos_S3 = {"CH17": ("localhost", 50017),
                    "CH18": ("localhost", 50018),
                    "CH16": ("localhost", 50016)}
    acom3 = AgenteCom(AID('agentecom-3@localhost:60030'), 'S3', enderecos_S3)

    adc3 = AgenteDC(AID('agentedc-3@localhost:60031'), 'S3')
    adc3.subscrever_a(AID('agentecom-3@localhost:60030'))
    adc3.set_an(AID('agenten-3@localhost:60032'))

    an3 = AgenteN(AID('agenten-3@localhost:60032'), 'S3')
    an3.add_adc_vizinho(AID('agentedc@localhost:60011'))
    an3.add_adc_vizinho(AID('agentedc-2@localhost:60021'))


    start_loop([acom, adc, an, acom2, adc2, an2, acom3, adc3, an3])