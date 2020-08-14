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
from pade.misc.utility import display_message
from pade.core.agent import Agent_

from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module
from core.adc import AgenteDC, SubscreverAEventos, EnviarComandoDeChaves # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from core.an import AgenteN, ReceberPoda, GerenciarNegociacao
from core.ied import IED  # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

from tests.conftest import start_loop

queue = None
@pytest.fixture(scope='function')
def testar_recepcao_de_mensagem_2(monkeypatch):
    """Injeta um retorno das mensagens recebidas pelos
    comandos EnviarComando::handle_inform do ADC e 
    ReceberComando::handle_request do ACom
    Valores podem ser recuperados pela Fila ``queue``"""
    global queue
    queue = multiprocessing.Queue()
    def stash(original, queue):
        """Executa função original, mas insere seus
        argumentos antes na queue."""
        def wrapper(self, *args):
            queue.put(args)
            return original(self, *args)
        return wrapper
    def do_nothing(queue):
        """Somente insere na queue os argumentos"""
        def wrapper(self, *args):
            queue.put(args)
            return
        return wrapper
    monkeypatch.setattr(EnviarComando, 'handle_inform', do_nothing(queue))
    monkeypatch.setattr(ReceberComando, 'handle_request', stash(ReceberComando.handle_request, queue))
    monkeypatch.setattr(IED, 'operate', stash(IED.operate, queue))

def test_UC_Comando_de_Chaves_Cenario_Principal(run_ams, testar_recepcao_de_mensagem_2):

    sniffer = run_ams
    # Define lista de chaves do ACom
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
                "CH16": ("localhost", 50016)}
    # Definir agentes ADC e ACom
    acom_aid = AID(f'acom@localhost:{randint(10000, 60000)}')
    adc_aid = AID(f'agentdc@localhost:{randint(10000, 60000)}')
    acom = AgenteCom(acom_aid, 'S1', enderecos_IEDs=enderecos_S1, debug=True)
    adc = AgenteDC(adc_aid, 'S1', debug=True)
    # Configurar endereço do AMS de teste
    acom.ams = sniffer.ams
    adc.ams = sniffer.ams
    # Adicionar ACom às incrições de ADC
    adc.subscrever_a(acom_aid)
    # Antecede inscrição para mandar comando (não necessário em produção)
    adc.assinaturas = [acom_aid]
    # Criar objeto a enviar
    lista_de_comandos = {'CH14': 'open', 'CH13': 'close'}
    # Enviar mensagem
    adc.enviar_comando_de_chave(
        lista_de_comandos=lista_de_comandos, 
        proposito='isolation',
        callbacks={ACLMessage.INFORM: (lambda: None),
        ACLMessage.FAILURE: (lambda: None)})

    # Executa agentes em outro processo por 20 segundos
    start_loop([adc, acom])

    # Testar ordem de recepção de mensagens (performatives)
    assert queue.get_nowait()[0].performative == 'request'
    assert queue.get_nowait()[0] == 'open'
    assert queue.get_nowait()[0] == 'close'
    assert queue.get_nowait()[0].performative == 'inform'




@pytest.fixture(scope='function')
def adicionar_eventos_a_IEDs(monkeypatch):
    """ Adiciona eventos XCBR a chaves 13 e 14 para testar restauração do sistema
    logo após o ADC se registrar com o ACom"""
    def stash(original_function):
        def wrapper(self, *args):
            # Executa função original do ADC (handle agree)
            return_value = original_function(self, *args)
            # Modifica eventos dos IEDs
            with open('core/ied/CH2.txt', 'w') as file:
                file.write('XCBR BRKF')
            with open('core/ied/CH1.txt', 'w') as file:
                file.write('XCBR')
            return return_value
        return wrapper
    monkeypatch.setattr(SubscreverAEventos, 'handle_agree', stash(SubscreverAEventos.handle_agree))

def test_dev(simular_IEDs, run_ams, adicionar_eventos_a_IEDs):
    sniffer = run_ams
    ams = sniffer.ams

    # S1 {
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
    acom.ams = ams

    adc = AgenteDC(AID('agentedc@localhost:60011'), 'S1')
    adc.subscrever_a(AID('agentecom@localhost:60010'))
    adc.set_an(AID('agenten@localhost:60012'))
    adc.ams = ams

    an = AgenteN(AID('agenten@localhost:60012'), 'S1')
    an.add_adc_vizinho(AID('agentedc-2@localhost:60021'))
    an.add_adc_vizinho(AID('agentedc-3@localhost:60031'))
    an.ams = ams
    # } S1

    # S2
    enderecos_S2 = {"CH4": ("localhost", 50004),
                    "CH5": ("localhost", 50005),
                    "CH3": ("localhost", 50003),
                    "CH8": ("localhost", 50008),
                    "CH11": ("localhost", 50011),
                    "CH12": ("localhost", 50012),
                    "CH16": ("localhost", 50016)}
    acom2 = AgenteCom(AID('agentecom-2@localhost:60020'), 'S2', enderecos_S2)
    acom2.ams = ams

    adc2 = AgenteDC(AID('agentedc-2@localhost:60021'), 'S2')
    adc2.subscrever_a(AID('agentecom-2@localhost:60020'))
    adc2.set_an(AID('agenten-2@localhost:60022'))
    adc2.ams = ams

    an2 = AgenteN(AID('agenten-2@localhost:60022'), 'S2')
    an2.add_adc_vizinho(AID('agentedc@localhost:60011'))
    an2.add_adc_vizinho(AID('agentedc-3@localhost:60031'))
    an2.ams = ams
    
    # S3
    enderecos_S3 = {"CH17": ("localhost", 50017),
                    "CH18": ("localhost", 50018),
                    "CH16": ("localhost", 50016)}
    acom3 = AgenteCom(AID('agentecom-3@localhost:60030'), 'S3', enderecos_S3)
    acom3.ams = ams

    adc3 = AgenteDC(AID('agentedc-3@localhost:60031'), 'S3')
    adc3.subscrever_a(AID('agentecom-3@localhost:60030'))
    adc3.set_an(AID('agenten-3@localhost:60032'))
    adc3.ams = ams

    an3 = AgenteN(AID('agenten-3@localhost:60032'), 'S3')
    an3.add_adc_vizinho(AID('agentedc@localhost:60011'))
    an3.add_adc_vizinho(AID('agentedc-2@localhost:60021'))
    an3.ams = ams


    start_loop([acom, adc, an, acom2, adc2, an2, acom3, adc3, an3, sniffer], 99999.0)