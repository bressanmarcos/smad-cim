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

from examples import ip
from rede import rede_gui

if __name__ == "__main__":

    # Abre GUI e executa Network
    network_filename = 'rede/models/new-network.xml'
    ip_ied_filename = ip.__file__
    commands = ['python', rede_gui.__file__, network_filename, ip_ied_filename]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)

    # # Define IP e porta do AMS
    ams_dict = {'name': 'localhost', 'port': 8000}

    # Executa AMS num subprocesso com ``python new_ams.py user email pass {porta}``
    commands = ['python', new_ams.__file__, 'pade_user', 'email@', '12345', str(ams_dict['port'])]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)

    # Instancia Sniffer para ser executado na {porta+1}
    sniffer = Sniffer(host=ams_dict['name'], port=ams_dict['port']+1)
    sniffer.ams = ams_dict

    # Pausa para iniciar AMS
    time.sleep(4)

    ip_ied = ip.ip_ied
    ip_AQZ = {key: ip_ied[key] for key in ['AQZ-21I4', 'AQZ-21I5', 'AQZ-21I6', 'AQZ-21I7',
                                            'R1', 'R2', 'R3', 'R4', 'R5',
                                            'Tie1', 'Tie2', 'Tie3', 'Tie4', 'Tie5', 'Tie6']}
    ip_JAB = {key: ip_ied[key] for key in ['JAB-21F8', 'Tie3']}
    ip_MSJ = {key: ip_ied[key] for key in ['MSJ-21M3', 'Tie4']}
    ip_AGF = {key: ip_ied[key] for key in ['AGF-21I7', 'Tie5', 'Tie6']}


    acom1 = AgenteCom(AID('AgenteComunicação-1@localhost:60010'), 'AQZ', ip_AQZ)
    adc1 = AgenteDC(AID('AgenteDiagnósticoConfiguração-1@localhost:60011'), 'AQZ', network_filename)
    an1 = AgenteN(AID('AgenteNegociação-1@localhost:60012'), 'AQZ')
    
    acom2 = AgenteCom(AID('AgenteComunicação-2@localhost:60020'), 'JAB', ip_JAB)
    adc2 = AgenteDC(AID('AgenteDiagnósticoConfiguração-2@localhost:60021'), 'JAB', network_filename)
    an2 = AgenteN(AID('AgenteNegociação-2@localhost:60022'), 'JAB')
    
    acom3 = AgenteCom(AID('AgenteComunicação-3@localhost:60030'), 'MSJ', ip_MSJ)
    adc3 = AgenteDC(AID('AgenteDiagnósticoConfiguração-3@localhost:60031'), 'MSJ', network_filename)
    an3 = AgenteN(AID('AgenteNegociação-3@localhost:60032'), 'MSJ')

    acom4 = AgenteCom(AID('AgenteComunicação-4@localhost:60040'), 'AGF', ip_AGF)
    adc4 = AgenteDC(AID('AgenteDiagnósticoConfiguração-4@localhost:60041'), 'AGF', network_filename)
    an4 = AgenteN(AID('AgenteNegociação-4@localhost:60042'), 'AGF')
    
    acom1.ams, an1.ams, adc1.ams = 3 * [ams_dict] 
    acom2.ams, an2.ams, adc2.ams = 3 * [ams_dict] 
    acom3.ams, an3.ams, adc3.ams = 3 * [ams_dict] 
    acom4.ams, an4.ams, adc4.ams = 3 * [ams_dict] 

    adc1.add_acom(acom1.aid)
    adc2.add_acom(acom2.aid)
    adc3.add_acom(acom3.aid)
    adc4.add_acom(acom4.aid)

    adc1.set_an(an1.aid)
    adc2.set_an(an2.aid)
    adc3.set_an(an3.aid)
    adc4.set_an(an4.aid)

    an1.add_adc_vizinho(adc2.aid)
    an1.add_adc_vizinho(adc3.aid)
    an1.add_adc_vizinho(adc4.aid)
    an2.add_adc_vizinho(adc1.aid)
    an2.add_adc_vizinho(adc3.aid)
    an2.add_adc_vizinho(adc4.aid)
    an3.add_adc_vizinho(adc1.aid)
    an3.add_adc_vizinho(adc2.aid)
    an3.add_adc_vizinho(adc4.aid)
    an4.add_adc_vizinho(adc1.aid)
    an4.add_adc_vizinho(adc2.aid)
    an4.add_adc_vizinho(adc3.aid)
    
    start_loop([acom1, adc1, an1,
                acom2, adc2, an2,
                acom3, adc3, an3,
                acom4, adc4, an4,])