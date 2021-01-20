import os
if __name__ == "__main__":
    os.sys.path.insert(0, os.getcwd())

import pytest
import datetime
import time
from random import randint
from queue import Queue
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.core.agent import Agent_

from core.common import to_elementtree, to_string, dump, validate, randomport

from core.acom import AgenteCom
from core.an import AgenteN
from core.adc import AgenteDC
from core.adc import ACHandler

from core.ied import FileIED
import information_model.SwitchingCommand as swc
import information_model.DistributionNetwork as dn

from tests.conftest import start_loop_test

@pytest.fixture(scope='function')
def queue_command(monkeypatch):
    """Injeta um retorno das mensagens recebidas pela função
    ``comandar_chave`` na fila ``queue``"""
    queue = Queue()
    def queue_insert(*args): 
        queue.put_nowait(args)
        print(args)
    monkeypatch.setattr(AgenteCom, 'comandar_chave', queue_insert)
    yield queue


def old_test_handle_request(deactivate_send_message, queue_command):
    """Testa (sem Rede) o ReceberComando::handle_request do ACom"""
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
    enderecos_S2 = {"CH4": ("localhost", 50000+4),
                    "CH5": ("localhost", 50000+5),
                    "CH3": ("localhost", 50000+3),
                    "CH8": ("localhost", 50000+8),
                    "CH11": ("localhost", 50000+11),
                    "CH12": ("localhost", 50000+12),
                    "CH16": ("localhost", 50000+16)}
    enderecos_S3 = {"CH17": ("localhost", 50000+17),
                    "CH18": ("localhost", 50000+18),
                    "CH16": ("localhost", 50000+16)}

    acom = AgenteCom(AID(f'acom1@localhost:{randint(10000, 60000)}'), 'S1', enderecos_S1)

    #################################################
    # Exemplo de Arquivo para ser recebido pelo ACOM
    swt13 = swc.ProtectedSwitch(
        mRID='CH13', name='Switch que protege minha casa')
    swt14 = swc.ProtectedSwitch(
        mRID='CH14', name='Switch do portão')
    acao1 = swc.SwitchAction(
        executedDateTime=datetime.datetime.now(),
        isFreeSequence=False,
        issuedDateTime=datetime.datetime.now(),
        kind=swc.SwitchActionKind.CLOSE,
        plannedDateTime=datetime.datetime.now(),
        sequenceNumber=1,
        OperatedSwitch=swt13)
    acao0 = swc.SwitchAction(
        executedDateTime=datetime.datetime.now(),
        isFreeSequence=False,
        issuedDateTime=datetime.datetime.now(),
        kind=swc.SwitchActionKind.OPEN,
        plannedDateTime=datetime.datetime.now(),
        sequenceNumber=0,
        OperatedSwitch=swt14)
    plano = swc.SwitchingPlan(
        mRID=str(uuid4()), 
        createdDateTime=datetime.datetime.now(),
        name='Plano de Teste', 
        purpose=swc.Purpose.COORDINATION, 
        SwitchAction=[acao1, acao0])
    root = swc.SwitchingCommand(SwitchingPlan=plano)
    validate(root)
    # Monta envelope de mensagem ACL
    message = ACLMessage(performative=ACLMessage.REQUEST)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.set_ontology(swc.__name__)
    message.set_content(to_elementtree(root))

    # Simula recepção de mensagem
    acom.handle_request(message)      

    # Testa valores retornados
    assert queue_command.get_nowait()[1:] == \
        ('CH14', swc.SwitchActionKind.OPEN)
    assert queue_command.get_nowait()[1:] == \
        ('CH13', swc.SwitchActionKind.CLOSE)



# V3.0

@pytest.fixture
def mock_receive_ied_event(monkeypatch, queue):
    """AgenteCom, ao receber mensagem do IED, somente imprime e joga na queue"""
    def print_and_queue(self, switch, *args):
        print(args)
        queue.put_nowait(args)

    monkeypatch.setattr(AgenteCom, 'receive_ied_event', print_and_queue)


def test_ied_messages(start_runtime, mock_receive_ied_event, queue):
    """Testa a geração de mensagens pelo IED e envia ao ACom"""

    # Test preparation
    acom = AgenteCom(
        AID('acom@localhost:60002'),
        substation='AQZ',
        IEDs=[
            FileIED('CH13', ('localhost', 50000), 'tests/ied-events/CH13.txt')
        ],
        debug=True)
    acom.ams = start_runtime

    # Start test
    with start_loop_test([acom]):

        # Delay to initiate agents
        time.sleep(2)

        # Simulate an IED event
        with open('tests/ied-events/CH13.txt', 'w') as file:
            file.write('XCBR BRKF')

        assert queue.get(timeout=10) == ('XCBR', 'BRKF')
        


@pytest.fixture
def mock_smt(monkeypatch, queue):
    """Walking through"""
    def print_and_queue(self, *args):
        print(args)
        queue.put_nowait(args)
    monkeypatch.setattr(AgenteDC, 'isolamento', print_and_queue)


def test_ac_adc(start_runtime, mock_smt, queue):
    """Testa informe de AC ao ADC após recepção de evento"""

    # Test preparation
    acom_AQZ = AgenteCom(
        aid=AID(f'acom@localhost:{randomport()}'),
        substation='AQZ',
        IEDs=[
            FileIED(nome_ied, ('localhost', randomport()),
                    f'tests/ied-events/{nome_ied}.txt')
            for nome_ied in ('AQZ-21I4', 'AQZ-21I5', 'AQZ-21I6', 'AQZ-21I7',
                             'R1', 'R2', 'R3', 'R4', 'R5',
                             'Tie1', 'Tie2', 'Tie3', 'Tie4', 'Tie5', 'Tie6')
        ],
        debug=False)
    acom_AQZ.ams = start_runtime

    adc_AQZ = AgenteDC(
        aid=AID(f'adc@localhost:{randomport()}'),
        substation='AQZ',
        network_file='tests/adc/network.xml',
        debug=False)
    adc_AQZ.ams = start_runtime

    adc_AQZ.add_acom(acom_AQZ.aid)

    # Start test
    with start_loop_test([acom_AQZ, adc_AQZ]):

        # Simulate an IED events after 20 secs
        time.sleep(20)
        with open('tests/ied-events/AQZ-21I7.txt', 'w') as file:
            file.write('XCBR')
        with open('tests/ied-events/R1.txt', 'w') as file:
            file.write('XCBR')

        print(queue.get())


def test_c(start_runtime, mock_smt, queue):

    """Testa informe de AC ao ADC após recepção de evento"""

    # Import information about switches
    network_file = 'tests/adc/network.xml'
    doc = dn.DocumentCIMRDF()
    doc.fromfile(network_file)

    ieds = [
        FileIED(id=switch.mRID,
                host=('localhost', randomport()),
                filename=f'tests/ied-events/{switch.mRID}.txt',
                initial_breaker_position='open' if switch.open else 'close')
        for switch in doc.resources if isinstance(switch, dn.Switch)
    ]
    # Test preparation
    acom_AQZ = AgenteCom(
        aid=AID(f'acom_AQZ@localhost:{randomport()}'),
        substation='AQZ',
        IEDs=[
            ied for ied in ieds
            if ied.id in ('AQZ-21I4', 'AQZ-21I5', 'AQZ-21I6', 'AQZ-21I7',
                          'R1', 'R2', 'R3', 'R4', 'R5',
                          'Tie1', 'Tie2', 'Tie3', 'Tie4', 'Tie5', 'Tie6')
        ])
    adc_AQZ = AgenteDC(
        aid=AID(f'adc_AQZ@localhost:{randomport()}'),
        substation='AQZ',
        network_file=network_file)
    an_AQZ = AgenteN(AID(f'an_AQZ@localhost:{randomport()}'),
                     'AQZ')

    acom_JAB = AgenteCom(
        aid=AID(f'acom_JAB@localhost:{randomport()}'),
        substation='JAB',
        IEDs=[
            ied for ied in ieds
            if ied.id in ('JAB-21F8', 'Tie3')
        ])
    adc_JAB = AgenteDC(
        aid=AID(f'adc_JAB@localhost:{randomport()}'),
        substation='JAB',
        network_file=network_file)
    an_JAB = AgenteN(AID(f'an_JAB@localhost:{randomport()}'),
                     'JAB')

    acom_MSJ = AgenteCom(
        aid=AID(f'acom_MSJ@localhost:{randomport()}'),
        substation='MSJ',
        IEDs=[
            ied for ied in ieds
            if ied.id in ('MSJ-21M3', 'Tie4')
        ])
    adc_MSJ = AgenteDC(
        aid=AID(f'adc_MSJ@localhost:{randomport()}'),
        substation='MSJ',
        network_file=network_file)
    an_MSJ = AgenteN(AID(f'an_MSJ@localhost:{randomport()}'),
                     'MSJ')

    acom_AGF = AgenteCom(
        aid=AID(f'acom_AGF@localhost:{randomport()}'),
        substation='AGF',
        IEDs=[
            ied for ied in ieds
            if ied.id in ('AGF-21I7', 'Tie5', 'Tie6')
        ])
    adc_AGF = AgenteDC(
        aid=AID(f'adc_AGF@localhost:{randomport()}'),
        substation='AGF',
        network_file=network_file)
    an_AGF = AgenteN(AID(f'an_AGF@localhost:{randomport()}'),
                     'AGF')

    acom_AQZ.ams, adc_AQZ.ams, an_AQZ.ams = [start_runtime] * 3
    acom_JAB.ams, adc_JAB.ams, an_JAB.ams = [start_runtime] * 3
    acom_MSJ.ams, adc_MSJ.ams, an_MSJ.ams = [start_runtime] * 3
    acom_AGF.ams, adc_AGF.ams, an_AGF.ams = [start_runtime] * 3

    adc_AQZ.add_acom(acom_AQZ.aid)
    adc_JAB.add_acom(acom_JAB.aid)
    adc_MSJ.add_acom(acom_MSJ.aid)
    adc_AGF.add_acom(acom_AGF.aid)

    adc_AQZ.set_an(an_AQZ.aid)
    adc_JAB.set_an(an_JAB.aid)
    adc_MSJ.set_an(an_MSJ.aid)
    adc_AGF.set_an(an_AGF.aid)

    an_AQZ.add_adc_vizinho(adc_JAB.aid)
    an_AQZ.add_adc_vizinho(adc_MSJ.aid)
    an_AQZ.add_adc_vizinho(adc_AGF.aid)
    an_JAB.add_adc_vizinho(adc_AQZ.aid)
    an_JAB.add_adc_vizinho(adc_MSJ.aid)
    an_JAB.add_adc_vizinho(adc_AGF.aid)
    an_MSJ.add_adc_vizinho(adc_AQZ.aid)
    an_MSJ.add_adc_vizinho(adc_JAB.aid)
    an_MSJ.add_adc_vizinho(adc_AGF.aid)
    an_AGF.add_adc_vizinho(adc_AQZ.aid)
    an_AGF.add_adc_vizinho(adc_JAB.aid)
    an_AGF.add_adc_vizinho(adc_MSJ.aid)

    # Start test
    with start_loop_test([
        adc_AQZ, acom_AQZ, an_AQZ,
        adc_JAB, acom_JAB, an_JAB,
        adc_MSJ, acom_MSJ, an_MSJ,
        adc_AGF, acom_AGF, an_AGF,
    ]):

        # Simulate an IED events after 20 secs
        time.sleep(20)
        with open('tests/ied-events/AQZ-21I7.txt', 'w') as file:
            file.write('XCBR')

        print(queue.get())

if __name__ == "__main__":
    from pade.core import new_ams
    import subprocess
    # # Define IP e porta do AMS
    ams_dict = {'name': 'localhost', 'port': 8000}

    # Executa AMS num subprocesso com ``python new_ams.py user email pass {porta}``
    commands = ['python', new_ams.__file__, 'pade_user',
                'email@', '12345', str(ams_dict['port'])]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)

    # Pausa para iniciar AMS
    time.sleep(4)

    class mocker():
        get = lambda: time.sleep(1000)
    test_c(ams_dict, None, mocker)

