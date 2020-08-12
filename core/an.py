import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour, FipaContractNetProtocol
from core.common import AgenteSMAD
import information_model as im
from pade.misc.utility import display_message

import pickle, json

class ReceberPoda(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        if message.ontology == "R_05":
            content = pickle.loads(message.content)
            display_message(self.agent.aid.name, "Mensagem REQUEST Recebida")

            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.INFORM)
            resposta.set_ontology("R_05")
            self.agent.send(resposta)

            self.agent.preparar_negociacao(content)


class GerenciarNegociacao(FipaContractNetProtocol):
    def __init__(self, agent, message=None):
        super().__init__(agent=agent, message=message, is_initiator=True)
        self.cfp = message

    def handle_all_proposes(self, proposes):
        super().handle_all_proposes(proposes)

        propostas_impossiveis = list()
        propostas_realizaveis = list()
        display_message(self.agent.aid.name, "Analisando propostas")

        # Elimina propositores que tem chaves de encontro
        # mas que nao puderam contribuir na restauracao
        for message in proposes:
            if message.performative == "propose":
                content = json.loads(message.content)

                if content["setores"] == []:
                    name = message.sender.localname
                    ramo = list(pickle.loads(self.cfp.content)[0].keys())
                    display_message(self.agent.aid.name, f"Agente {name} possui chave de encontro, mas nao pode colaborar para o ramo {ramo}.")

                    propostas_impossiveis.append(message)
                else:
                    propostas_realizaveis.append(message)

        # Cria variaveis auxiliares
        melhor_proposta = None
        ramo_cfp = pickle.loads(self.cfp.content)
        setores_atendidos = 0

        # Escolha do melhor propositor sob algum criterio
        if self.agent.criterios["carreg_SE"] and self.agent.criterios["carga_prior"]:
            pass

        elif self.agent.criterios["carreg_SE"] and self.agent.criterios["perdas"]:
            pass

        elif self.agent.criterios["carreg_SE"] and self.agent.criterios["chaveamentos"]:
            pass

        # Apenas carregamento da SE e qtd de setores atendidos
        else:

            # Varre todas as propostas recebidas
            for message in propostas_realizaveis:
                display_message(self.agent.aid.name,
                                f"Analisando proposta {propostas_realizaveis.index(message) + 1} de {len(propostas_realizaveis)}")

                # Carrega conteudo da mensagem analisada
                content = json.loads(message.content)
                name = message.sender.name.split("@")[0]

                display_message(self.agent.aid.name,
                                f"Agente {name} pode restaurar ramo {content['setores']} com carregamento de {content['carreg_SE']}%  da sua SE")

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

        display_message(self.agent.aid.name, "------------------------")

        if propostas_realizaveis is not None:  # Se houver melhor proposta

            for proposta in propostas_realizaveis:
                # Precisa verificar ainda se as intersecoes sao vazias

                # print json.loads(proposta.content)

                # Prepara mensagem de Accept-Proposal para Agente Ganhador
                resposta = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
                resposta.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
                resposta.set_ontology("CN_04")
                resposta.set_content(proposta.content)
                resposta.add_receiver(proposta.sender)
                self.agent.send(resposta)

            # Prepara mensagem de Reject-Proposal para os demais
            resposta = ACLMessage(ACLMessage.REJECT_PROPOSAL)
            resposta.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
            resposta.set_ontology("CN_05")
            resposta.set_content(None)
            # for message in propostas_realizaveis:
            # 	if message != melhor_proposta:
            # 		resposta.add_receiver(message.sender)
            for message in propostas_impossiveis:
                # if message.sender not in resposta.receivers:
                resposta.add_receiver(message.sender)
            self.agent.send(resposta)

        else:
            display_message(self.agent.aid.name, "Nenhuma proposta foi acatada.")

    def handle_refuse(self, message):
        super().handle_refuse(message)
        display_message(self.agent.aid.name, f"Mensagem REFUSE recebida de {message.sender.name}")

    def handle_propose(self, message):
        super().handle_propose(message)
        display_message(self.agent.aid.name, f"Mensagem PROPOSE recebida de {message.sender.name}")

    def handle_inform(self, message):
        super().handle_inform(message)
        display_message(self.agent.aid.name, "Mensagem INFORM Recebida")

    def solicitar_propostas(self, poda):
        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.set_ontology("CN_01")
        message.set_content(pickle.dumps(poda))
        for aid in self.agent.adc_vizinhos:
            message.add_receiver(aid)

        self.message = message
        self.cfp = message
        self.on_start()
        # content = json.loads(message.content)
        # self.agent.organiza_ramos(content)

class AgenteN(AgenteSMAD):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, subestacao, debug=False)

        # Criterios para Agente Negociacao da aplicacao
        criterios = {"chaveamentos": False,
                     "carreg_SE": True,
                     "perdas": False,
                     "carga_prior": False}

        self.busy = False

        self.subestacao = subestacao
        self.criterios_rest = criterios

        self.ramos_remanesc = list()

        self.criterios = {"chaveamentos": False,
                 "carreg_SE": True,
                 "perdas": False,
                 "carga_prior": False}

        # Determina os ADCs vizinhos para os quais as solicitações de recomposição
        # serão enviadas
        self.adc_vizinhos = list()

        self.manage_negotiation_behaviour = GerenciarNegociacao(self)
        self.behaviours.append(self.manage_negotiation_behaviour)

        self.receive_prune_behaviour = ReceberPoda(self)
        self.behaviours.append(self.receive_prune_behaviour)

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

    def preparar_negociacao(self, dados):

        for poda in dados["ramos"]:

            if self.busy == True:
                pass
            else:
                self.busy = True
                # Variaveis auxiliares
                i = dados["ramos"].index(poda)
                self.ramos_remanesc.append(poda)

                display_message(self.aid.name, f"Tratando Ramo {poda[0].keys()}: {i+1} de {len(dados['ramos'])}")

                self.manage_negotiation_behaviour.solicitar_propostas(poda)


    def organiza_ramos(self, recomp_realiz):

        setores_desernerg = list()
        #
        for ramo in self.ramos_remanesc:

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
                # 	if setor == ramo[2][1,i]:
                # 		array1 = np.append(array1, ramo[2][1,i])

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

if __name__ == "__main__":
    from pade.misc.utility import start_loop

    an = AgenteN(AID('agenten@localhost:60012'), 'S1')
    an.add_adc_vizinho(AID('agentedc-2@localhost:60021'))
    an.add_adc_vizinho(AID('agentedc-3@localhost:60031'))
    an.ams['port'] = 60000


    start_loop([an])


