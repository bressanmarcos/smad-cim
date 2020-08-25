import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import pytest
import datetime
import time
import subprocess
import multiprocessing
from random import randint

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent_
from pade.core import new_ams
from pade.core.sniffer import Sniffer

from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module
from core.adc import AgenteDC, SubscreverAEventos, EnviarComandoDeChaves # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from core.an import AgenteN, ReceberPoda, GerenciarNegociacao # pylint: disable=import-error,no-name-in-module
from core.ied import IED  # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc  # pylint: disable=import-error

from rede.rede_simu import Network # pylint: disable=import-error

if __name__ == "__main__":

    ## Executar IEDs
    # Instancia classe
    network = Network()
    # Executa loop em novo processo
    p = multiprocessing.Process(target=network.run)
    p.start()

    # Define IP e porta do AMS
    ams_dict = {'name': 'localhost', 'port': 60000}

    # Executa AMS num subprocesso com ``python new_ams.py user email pass {porta}``
    commands = ['python', new_ams.__file__, 'pade_user', 'email@', '12345', str(ams_dict['port'])]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)

    # Instancia Sniffer para ser executado na {porta+1}
    sniffer = Sniffer(host=ams_dict['name'], port=ams_dict['port']+1)
    sniffer.ams = ams_dict

    # Pausa para iniciar AMS
    time.sleep(4)

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
    enderecos_S2 = {"CH4": ("localhost", 50004),
                    "CH5": ("localhost", 50005),
                    "CH3": ("localhost", 50003),
                    "CH8": ("localhost", 50008),
                    "CH11": ("localhost", 50011),
                    "CH12": ("localhost", 50012)}
    enderecos_S3 = {"CH17": ("localhost", 50017),
                    "CH18": ("localhost", 50018),
                    "CH16": ("localhost", 50016)}
    
    acom1 = AgenteCom(AID('AgenteComunicação-1@localhost:60010'), 'S1', enderecos_S1)
    adc1 = AgenteDC(AID('AgenteDiagnósticoConfiguração-1@localhost:60011'), 'S1')
    an1 = AgenteN(AID('AgenteNegociação-1@localhost:60012'), 'S1')
    
    acom2 = AgenteCom(AID('AgenteComunicação-2@localhost:60020'), 'S2', enderecos_S2)
    adc2 = AgenteDC(AID('AgenteDiagnósticoConfiguração-2@localhost:60021'), 'S2')
    an2 = AgenteN(AID('AgenteNegociação-2@localhost:60022'), 'S2')
    
    acom3 = AgenteCom(AID('AgenteComunicação-3@localhost:60030'), 'S3', enderecos_S3)
    adc3 = AgenteDC(AID('AgenteDiagnósticoConfiguração-3@localhost:60031'), 'S3')
    an3 = AgenteN(AID('AgenteNegociação-3@localhost:60032'), 'S3')
    
    acom1.ams, an1.ams, adc1.ams = 3 * [ams_dict] 
    acom2.ams, an2.ams, adc2.ams = 3 * [ams_dict] 
    acom3.ams, an3.ams, adc3.ams = 3 * [ams_dict] 

    adc1.add_acom(acom1.aid)
    adc2.add_acom(acom2.aid)
    adc3.add_acom(acom3.aid)

    adc1.set_an(an1.aid)
    adc2.set_an(an2.aid)
    adc3.set_an(an3.aid)

    an1.add_adc_vizinho(adc2.aid)
    an1.add_adc_vizinho(adc3.aid)
    an2.add_adc_vizinho(adc1.aid)
    an2.add_adc_vizinho(adc3.aid)
    an3.add_adc_vizinho(adc1.aid)
    an3.add_adc_vizinho(adc2.aid)
    
    start_loop([sniffer, acom1, acom2, acom3, adc1, adc2, adc3, an1, an2, an3])