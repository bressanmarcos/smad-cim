import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import xml.etree.ElementTree as ET

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour, FipaContractNetProtocol
from core.common import AgenteSMAD
import information_model as im
from pade.misc.utility import display_message

from rede import rdf2mygrid

import pickle, json

class Carregar_Ontologia()