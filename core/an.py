import json
import os
import pickle
import xml.etree.ElementTree as ET

import information_model as im
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage

from pade.behaviours.highlevel import *

from pade.core.agent import Agent
from pade.misc.utility import display_message
from rede import rdf2mygrid

from core.common import AgenteSMAD
class AgenteN(AgenteSMAD):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, subestacao, debug=False)

        # Criterios para Agente Negociacao da aplicacao
        self.criterios = {"chaveamentos": False,
                          "carreg_SE": True,
                          "perdas": False,
                          "carga_prior": False}

        # Determina os ADCs vizinhos para os quais as solicitações de recomposição
        # serão enviadas
        self.adc_vizinhos = list()

        self.busy = False

        self.manage_negotiation_behaviour = FipaContractNetProtocol(self)
        self.receive_prune_behaviour = FipaRequestProtocol(self, False)
        self.receive_prune_behaviour.set_request_handler(self.handle_request)

    def add_adc_vizinho(self, adc_aid):
        self.adc_vizinhos.append(adc_aid)

        # inicio ontologia
    #     self.call_later(7.0, self.registrar_ontologia)

    # # inicio ontologia
    # def registrar_ontologia(self):
    #     conteudo = '{"nome":"Agente_Negociacao", "Class":"AgenteNegociacao"}'
    #     message = ACLMessage(ACLMessage.INFORM)
    #     # display_message(self.aid.localname, 'Registrando na ontologia')
    #     message.add_receiver(AID('S1_agerente'))
    #     message.set_content(conteudo)
    #     message.set_ontology('ontogrid')
    #     message.set_language('json')
    #     self.send(message)

    # final registro na ontologia

    def handle_request(self, message: ACLMessage):
        if message.ontology == "R_05":
            # Será recebida uma poda por vez
            poda_cim = message.content
            poda = rdf2mygrid.cim_poda(poda_cim)
            # poda = pickle.loads(poda_cim)

            display_message(self.aid.name, "Mensagem REQUEST Recebida")

            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.AGREE)
            resposta.set_ontology("R_05")
            self.send(resposta)

            self.preparar_negociacao(poda, message)

    def solicitar_propostas(self, poda):
        """Define função que será chamada após cada resposta"""
        poda_cim = rdf2mygrid.poda_cim(poda)
        # poda_cim = pickle.dumps(poda)

        # Elabora mensagem
        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.set_ontology("CN_01")
        message.set_content(poda_cim)
        for aid in self.adc_vizinhos:
            message.add_receiver(aid)

        propostas_realizaveis = []

        while True:
            try:
                proposta = yield self.manage_negotiation_behaviour.send_cfp(message)
                display_message(self.aid.name,
                                f"Mensagem PROPOSE recebida de {proposta.sender.name}")

                content = json.loads(proposta.content)
                proposta_realizavel = (content["setores"] != [])

                if proposta_realizavel:
                    # Salva proposta para mais tarde
                    propostas_realizaveis.append(proposta)

                else:
                    # Rejeita proposta imediatamente
                    name = message.sender.localname

                    ramo = proposta.content
                    display_message(
                        self.aid.name, f"Agente {name} possui chave de encontro, mas nao pode colaborar para o ramo {ramo}.")

                    reject_message = proposta.create_reply()
                    reject_message.set_ontology("CN_05")
                    reject_message.set_content('Proposta não realizável')
                    self.manage_negotiation_behaviour.send_reject_proposal(reject_message)


            except FipaRefuseHandler as h:
                refusal = h.message
                display_message(self.aid.name,
                                f"Mensagem REFUSE recebida de {refusal.sender.name}")

            except FipaCfpComplete:
                break

        # Dados da melhor proposta
        melhor_proposta = None
        setores_atendidos = 0

        # Escolha do melhor propositor sob algum criterio
        if self.criterios["carreg_SE"] and self.criterios["carga_prior"]:
            pass

        elif self.criterios["carreg_SE"] and self.criterios["perdas"]:
            pass

        elif self.criterios["carreg_SE"] and self.criterios["chaveamentos"]:
            pass

        # Apenas carregamento da SE e qtd de setores atendidos
        else:

            # Varre todas as propostas recebidas
            for message in propostas_realizaveis:
                display_message(
                    self.aid.name, f"Analisando proposta {propostas_realizaveis.index(message) + 1} de {len(propostas_realizaveis)}")

                # Carrega conteudo da mensagem analisada
                content = json.loads(message.content)
                name = message.sender.name

                display_message(
                    self.aid.name, f"Agente {name} pode restaurar ramo {content['setores']} com carregamento de {content['carreg_SE']}%  da sua SE")

                # Verifica se atual proposta atende maior numero de setores
                if len(content["setores"]) > setores_atendidos:
                    melhor_proposta = message
                    setores_atendidos = len(content["setores"])

                # Se atende o mesmo numero de setores, verifica carregamento
                elif len(content["setores"]) == setores_atendidos:
                    content_melhor_atual = json.loads(message.content)

                    # Se carregamento atual for maior, vira melhor proposta
                    if content["carreg_SE"] > content_melhor_atual["carreg_SE"]:
                        melhor_proposta = message
                        setores_atendidos = len(content["setores"])

        # Envia Reject-Proposal para demais agentes
        for message in propostas_realizaveis:
            if message is melhor_proposta:
                continue

            resposta = message.create_reply()
            resposta.set_ontology("CN_04")
            self.manage_negotiation_behaviour.send_reject_proposal(resposta)

        # Envia Accept-Proposal para Agente Ganhador
        if melhor_proposta is not None:

            resposta = melhor_proposta.create_reply()
            resposta.set_ontology("CN_04")
            resposta.set_content(melhor_proposta.content)

            while True:
                try:
                    result = yield self.manage_negotiation_behaviour.send_accept_proposal(resposta)
                    display_message(self.aid.name, "Mensagem INFORM Recebida")

                except FipaFailureHandler as h:
                    result = h.message
                    display_message(self.aid.name, "Mensagem FAILURE Recebida")

                except FipaProtocolComplete:
                    break

            return result 

        else:
            display_message(self.aid.name, "Nenhuma proposta foi acatada.")
            return None


    @FipaSession.session
    def preparar_negociacao(self, poda, message_adc_solicitante):
        dados = {'ramos': [poda]}
        ramos_remanesc = []

        for poda in dados['ramos']:

            if not self.busy:
                self.busy = True
                # Variaveis auxiliares
                i = dados['ramos'].index(poda)
                ramos_remanesc.append(poda)

                ramo = list(poda[0].keys())
                display_message(
                    self.aid.name, f"Tratando Ramo {ramo}: {i+1} de {len(dados['ramos'])}")

                message_adc_fornecedor = yield from self.solicitar_propostas(poda)

                if False and len(ramos_remanesc):
                    setores_desernerg = list()
                    #
                    for ramo in ramos_remanesc:
                        recomp_realiz = dict()
                        # Identifica qual dos ramos foi o ramo recomposto
                        if recomp_realiz["ramo"][0] in ramo[0].keys():
                            for setor in ramo[0].keys():
                                if setor not in recomp_realiz["ramo"]:
                                    setores_desernerg.append(setor)

                        # Remonta a poda a ser restaurada (setores nao restaurados)
                        dic1 = dict()
                        dic2 = dict()
                        dic3 = dict()
                        dic4 = dict()
                        dic5 = dict()
                        dic6 = dict()
                        array1 = ramo[2]

                        for setor in setores_desernerg:
                            dic1[setor] = ramo[0][setor]
                            dic2[setor] = ramo[1][setor]

                            # for i in range(len(ramo[2][1,:])):
                            #     if setor == ramo[2][1,i]:
                            #         array1 = np.append(array1, ramo[2][1,i])

                            # print ramo[2][1,:], len(ramo[2][1,:]), range(len(ramo[2][1,:]))

                            for no in ramo[3].keys():
                                if setor in str(no):
                                    dic3[no] = ramo[3][no]
                                    dic4[no] = ramo[4][no]

                            for chave in ramo[6].keys():
                                if ramo[6][chave].n1.nome == setor or ramo[6][chave].n2.nome == setor:
                                    dic5[chave] = ramo[6][chave]

                            for trecho in ramo[7].keys():
                                if setor in str(trecho):
                                    dic6[trecho] = ramo[7][trecho]

                        nova_poda = (dic1)

                    # print dic1, dic2, dic3, dic4, dic5, dic6

                self.busy = False

                    # Responder INFORME ao ADC solicitante
                resposta = message_adc_solicitante.create_reply()

                if message_adc_fornecedor:
                    # Inform ou Failure entram aqui
                    display_message(
                        self.aid.name, "Recomposição externa concluída")

                    if message_adc_fornecedor.performative == ACLMessage.INFORM:
                        # Encaminha chaves para concluir restauração
                        # TODO: encaminhar também relatório de restauração
                        resposta.set_ontology(message_adc_fornecedor.ontology)
                        resposta.set_content(message_adc_fornecedor.content)
                        self.receive_prune_behaviour.send_inform(resposta)

                    else:
                        self.receive_prune_behaviour.send_failure(resposta)

                else:
                    # Nenhuma proposta
                    display_message(
                        self.aid.name, "Recomposição externa não concluída")
                    # Responder FALHA ao ADC solicitante
                    self.receive_prune_behaviour.send_failure(resposta)

