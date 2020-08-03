import os

os.sys.path.insert(0, os.getcwd())
# Adiciona ao Path a pasta raiz do projeto

from pprint import pprint
import pickle

import datetime
from random import random
from uuid import uuid4
from pathlib import Path
import threading

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol, FipaSubscribeProtocol, FipaContractNetProtocol)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump, validate

from information_model import SwitchingCommand as swc
from information_model import OutageEvent as out

from mygrid.fluxo_de_carga.varred_dir_inv import calcular_fluxo_de_carga
from rede import rdf2mygrid


class SubscreverACom(FipaSubscribeProtocol):
    def __init__(self, agent: 'AgenteDC', message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)

        
    def subscrever(self, acom_aid):
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.add_receiver(acom_aid)
        self.agent.send_until(message)

    def handle_agree(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Inscrito em {message.sender.name}')
        self.agent.assinaturas.append(message.sender)

    def handle_inform(self, message: ACLMessage):    
        """Recebe notificação de evento do ACom. \\
        ``message.content`` é recebida no formato OutageEvent.

        Conteúdo é convertido em dados tratáveis em Python e 
        método do agente é chamado para processá-lo.
        """
        lista_de_chaves = {'chaves': [], 'leitura_falta': []}
        root: out.OutageEvent = out.parseString(to_string(message.content))
        for switch in root.get_Outage().get_ProtectedSwitch():
            switch: out.ProtectedSwitch
            switchId = switch.get_mRID()

            for discrete_meas in switch.get_Discrete_Measurement():
                discrete_meas: out.Discrete
                discrete_meas_name = discrete_meas.get_name()
                discrete_meas_value = discrete_meas.get_DiscreteValue().get_value().get_valueOf_()
                if discrete_meas_name == out.Discrete_Meas.BREAKER_POSITION:
                    if int(discrete_meas_value) == 1:
                        lista_de_chaves['chaves'].append(switchId)
                        lista_de_chaves['leitura_falta'].append(switchId)
                elif discrete_meas_name == out.Discrete_Meas.BREAKER_FAILURE:
                    if int(discrete_meas_value) == 1:
                        if not '50BF' in lista_de_chaves:
                            lista_de_chaves['50BF'] = []
                        lista_de_chaves['50BF'].append(switchId)

        self.agent.tratar_informe(lista_de_chaves)


class EnviarComando(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=True)
        self.state_lock = threading.RLock()

    def handle_not_understood(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Mensagem não compreendida')
        display_message(self.agent.aid.name, f'Not Understood: {message.content}')

    def register_state(self, state_id: str, callback_inform=None, callback_failure=None, awaits=1):
        # Registra o conversation_id da Mensagem, 
        # para manter estado
        with self.state_lock:
            if not hasattr(self, 'states'):
                self.states = {}
            self.states[state_id] = (callback_inform, callback_failure, awaits)

    def retrieve_state(self, state_id):
        # Recupera o estado a partir do conversation_id
        with self.state_lock:
            callback_inform, callback_failure, awaits = self.states[state_id]
            awaits -= 1
            if awaits == 0:
                del self.states[state_id]
            return callback_inform, callback_failure, awaits

    def enviar_comando_de_chave(self, lista_de_comandos, proposito, conversation_id=str(uuid4())):
        """Envia um objeto de informação do tipo SwitchingCommand ao ACom fornecido"""
        switch_actions = []
        sequenceNumber = 0
        for chave, comando in lista_de_comandos.items():
            switch = swc.ProtectedSwitch(mRID=chave)
            sequenceNumber += 1
            if comando == 'open':
                action_kind = swc.SwitchActionKind.OPEN
            elif comando == 'close':
                action_kind = swc.SwitchActionKind.CLOSE
            action = swc.SwitchAction(
                isFreeSequence=False,
                issuedDateTime=datetime.datetime.now(),
                kind=action_kind,
                sequenceNumber=sequenceNumber,
                OperatedSwitch=switch)
            switch_actions.append(action)

        if proposito == 'isolation':
            purpose = swc.Purpose.ISOLATION
        elif proposito == 'coordination':
            purpose = swc.Purpose.COORDINATION

        plano = swc.SwitchingPlan(
            mRID=str(uuid4()), 
            createdDateTime=datetime.datetime.now(),
            name='Plano de Teste', 
            purpose=purpose, 
            SwitchAction=switch_actions)
        root = swc.SwitchingCommand(SwitchingPlan=plano)
        validate(root)
        
        # Monta envelope de mensagem ACL
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.set_ontology('SwitchingCommand')
        message.set_content(to_elementtree(root))
        message.set_conversation_id(conversation_id)
        for acom_aid in self.agent.assinaturas:
            message.add_receiver(acom_aid)

        self.agent.send_until(message)

    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Chaveamento realizado: {message.content}')
        callback_inform, _, awaits = self.retrieve_state(message.conversation_id)
        if awaits == 0:
            # Se não houver mais nenhuma mensagem de retorno, chama a função
            # de callback
            callback_inform()

    def handle_failure(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Falha em execução de comando: {message.content}')
        _, callback_failure, awaits = self.retrieve_state(message.conversation_id)
        if awaits == 0:
            # Se não houver mais nenhuma mensagem de retorno, chama a função
            # de callback
            callback_failure()



class AgenteDC(AgenteSMAD):
    def __init__(self, aid: AID, subestacao: str, debug=False):
        super().__init__(aid, subestacao, debug)
        self.command_behaviour = EnviarComando(self)
        self.subscribe_behaviour = SubscreverACom(self)
        self.assinaturas = []
        self.behaviours.append(self.command_behaviour)
        self.behaviours.append(self.subscribe_behaviour)

        # Inicio cod Tiago para o agente diagnostico
        self.subestacao = subestacao
        self.relatorios_restauracao = list()
        self.topologia_subestacao = rdf2mygrid.carregar_topologia(Path('./rede/rede-cim.xml'), subestacao)

        display_message(self.aid.name, f"Subestacao {subestacao} carregada com sucesso")
        self.podas = list()
        self.podas_possiveis = list()
        self.setores_faltosos = list()
        # comportamento_requisicao = CompRequest1(self)
        # self.behaviours.append(comportamento_requisicao)
        # comp_contractnet_participante = CompContractNet1(self)
        # self.behaviours.append(comp_contractnet_participante)
        # Final cod Tiago para o agente diagnostico

    def subscrever_a(self, acom_aid: AID):
        """Subcribe to ``AgenteCom``"""
        self.subscribe_behaviour.subscrever(acom_aid)

    def set_an(self, an_aid: AID):
        self.an_aid = an_aid
    
    def get_an(self):
        if hasattr(self, 'an_aid'):
            return self.an_aid
        raise AttributeError('Agente de Negociação não definido')

    def tratar_informe(self, lista_de_chaves):
        """Mensagem recebida pelo ACom, já convertida no formato
        dos métodos do Tiago
        
        lista_de_chaves = {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13']}
        """
        #Inicio da analise de descoordenacao
        dados_falta = self.analise_descoordenacao(lista_de_chaves)
        """Houve descoordenação, chave a corrigir:"""

        if dados_falta["coordenado"] == False:
            #Corrigir descoordenacao
            
            content = {"dados": dados_falta}
            #ALE: antigo agente de controle
            content2 = dict()
            content2["chave_falta"] = content["dados"]["chave_falta"]

            # Indica inicio da Correcao
            display_message(self.aid.name, "Iniciando correcao de Descoordenacao")
            
            # Verifica se o pacote de dados tem a tag
            # "correc_descoord" indicando que houve 50BF
            # dentre as funcoes de protecao obtidas
            if "correc_descoord" in content["dados"]:
                if content["dados"]["correc_descoord"] in content["dados"]["chaves"]:
                    # pass
                    self.pos_coordenacao((content, content2, 'success'))
                else:
                    display_message(self.aid.name, f'Comando para isolar trecho sob Falta [CH:{content["dados"]["correc_descoord"]}]')
                    conversation_id = str(uuid4())
                    self.command_behaviour.register_state(conversation_id, lambda: self.pos_coordenacao((content, content2, 'success')), lambda: self.pos_coordenacao((content, content2, 'failure')))
                    self.command_behaviour.enviar_comando_de_chave(lista_de_comandos={content["dados"]["correc_descoord"]: 'open'}, proposito='coordination', conversation_id=conversation_id)
                    # Código deste nível continua em ''handle_inform'' ou ''handle_failure''

            # Se nao houver, a descoordenacao deve
            # ser corrigida normalmente
            else:
                #BRESSAN: reforça a abertura da chave a montante do setor em falta...
                display_message(self.aid.name, f"Comando para isolar trecho sob Falta [CH:{content['dados']['chave_falta']}]")
                conversation_id = str(uuid4())
                self.command_behaviour.register_state(
                    conversation_id, 
                    lambda: self.pos_coordenacao((content, content2, 'success')), 
                    lambda: self.pos_coordenacao((content, content2, 'failure')))
                self.command_behaviour.enviar_comando_de_chave(
                    lista_de_comandos={content["dados"]["chave_falta"]: 'open'}, 
                    proposito='coordination', 
                    conversation_id=conversation_id)

            # Opera as chaves para isolamento do setor
            # sob falta, com ou seu descoordenacao
            # self.agent.operacao_chaves()

        else:
            self.analise_isolamento(dados_falta["chave_falta"])

    def analise_descoordenacao(self, dados_falta=dict):
        # Exemplo de entrada {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13'], 'ctime': 'Fri Jul  3 18:20:58 2020'}
        # Exemplo de saída {'chaves': ['CH13', 'CH14'], 'leitura_falta': ['CH13'], '50BF': ['CH14'], 'alimentador': 'S1_AL1', 'chave_falta': 'CH14', 'coordenado': False, 'correc_descoord': 'CH13'}

        # Assume que todas as chaves estão sob o mesmo Alimentador
        nome_alimentador = self.localizar_chave(dados_falta["chaves"][0])
        dados_falta["alimentador"] = nome_alimentador
        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, f"Analise de Descoordenacao em {nome_alimentador}")
        print(dados_falta)

        alimentador = self.topologia_subestacao.alimentadores[nome_alimentador]
        rnp_alimentador = alimentador.rnp_dic()
        chave_setor = {}

        for chave in dados_falta["leitura_falta"]:
            chave_setor[chave] = alimentador.chaves[chave].n2.nome
        
        profundidade = 0
        # Busca a chave de maior profundidade (antes do setor defeituoso)
        for chave in chave_setor:
            setor_jusante = chave_setor[chave]
            i = int(rnp_alimentador[setor_jusante])
            if i >= profundidade:
                profundidade = i
                chave_falta = chave
        
        dados_falta["chave_falta"] = chave_falta

        # Verifica se no pacote só contém a chave em questão
        if dados_falta["chaves"] == [chave_falta]:
            # Coordenado
            dados_falta["coordenado"] = True
            display_message(self.aid.name, "Protecao Coordenada")
        else:
            # Descoordenado
            dados_falta["coordenado"] = False
            display_message(self.aid.name, "Protecao Descoordenada")

            # Verifica as chaves que nao podem ser operadas por 50BF
            if "50BF" in dados_falta:
                setor_montante_falta = alimentador.chaves[chave_falta].n1.nome
                setor_jusante_falta = alimentador.chaves[chave_falta].n2.nome
                chave_50BF = dados_falta["50BF"][0]
                setor_montante_50BF = alimentador.chaves[chave_50BF].n1.nome
                setor_jusante_50BF = alimentador.chaves[chave_50BF].n2.nome
                # Monta vetor de busca
                ch_correc_descoord = dados_falta["leitura_falta"]

                # Identifica profundidade da falta
                if rnp_alimentador[setor_montante_falta] > rnp_alimentador[setor_jusante_falta]:
                    prof_falta = rnp_alimentador[setor_montante_falta]
                else:
                    prof_falta = rnp_alimentador[setor_jusante_falta]

                # Identifica profundidade da 50BF
                if rnp_alimentador[setor_montante_50BF] > rnp_alimentador[setor_jusante_50BF]:
                    prof_50BF = rnp_alimentador[setor_montante_50BF]
                else:
                    prof_50BF = rnp_alimentador[setor_jusante_50BF]
                    
                if prof_50BF < prof_falta:
                    # Se a 50BF ocorreu a montante -1  da falta
                    chave_correcao = chave_falta
                else:  # Se a 50BF na falta
                    # Retira a chave da falta com 50BF
                    ch_correc_descoord.remove(chave_falta)
                    # Remove as demais chaves com 50BF
                    for chave in ch_correc_descoord:
                        if chave in dados_falta["50BF"]:
                            ch_correc_descoord.remove(chave_falta)
                    prof_aux = 0
                    for chave in ch_correc_descoord:
                        aux = int(rnp_alimentador[alimentador.chaves[chave].n2.nome]) + \
                              int(rnp_alimentador[alimentador.chaves[chave].n1.nome])
                        if aux > prof_aux:
                            prof_aux = aux
                            chave_correcao = chave
                    dados_falta["correc_descoord"] = chave_correcao
        return dados_falta

    def pos_coordenacao(self, state):
        content, content2, result = state

        content2["correc_descoord_realizada"] = (result == 'success')
        # Verifica quais as chaves que devem ser
        # operadas a fim de reenergizar os trechos
        # desenergizados por descoordenacao
        if content2["correc_descoord_realizada"] is True:

            # Conta o número de comandos que serao enviados antes
            # para saber quantas mensagens devem ser esperadas
            lista_de_comandos = {}
            for chave in content["dados"]["chaves"]:
                if "correc_descoord" in content["dados"]:
                    if chave != content["dados"]["chave_falta"] and chave != content["dados"]["correc_descoord"]:
                        lista_de_comandos[chave] = 'close'
                else:
                    if chave != content["dados"]["chave_falta"]:
                        lista_de_comandos[chave] = 'close'
            
            if len(lista_de_comandos):
                display_message(self.aid.name, "Comando para reestabelecer trechos descoordenados [CH: " + str(lista_de_comandos) + "]")
                conversation_id = str(uuid4())
                self.command_behaviour.register_state(
                    state_id=conversation_id, 
                    callback_inform=lambda: self.pos_pos_coordenacao((content, content2, result)), 
                    callback_failure=lambda: self.pos_pos_coordenacao((content, content2, result)))
                self.command_behaviour.enviar_comando_de_chave(
                    lista_de_comandos=lista_de_comandos, 
                    proposito='coordination', 
                    conversation_id=conversation_id)
                return
        else:
            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")

        self.pos_pos_coordenacao(content2["chave_falta"])

    def pos_pos_coordenacao(self, state):
        content, content2, result = state

        if "correc_descoord" in content["dados"] and content["dados"]["chaves"] == [content["dados"]["correc_descoord"]]:
            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")

        content2["correc_descoord_realizada"] = (result == 'sucess')

        content = content2

        self.analise_isolamento(content["chave_falta"])


    def enviar_comando_de_chave(self, lista_de_comandos, proposito, conversation_id):
        display_message(self.aid.name, f'Enviando comando: {lista_de_comandos} para {self.assinaturas} ({proposito})')
        self.command_behaviour.enviar_comando_de_chave(lista_de_comandos, proposito, conversation_id)

    #Inicio Cod Tiago
    def localizar_chave(self, chave):
        for alimentador in self.topologia_subestacao.alimentadores.keys():
            if chave in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():
                # Proucura em qual alimentador da SE "chave" está.
                if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].estado == 1:
                    # "chave" pertence ao "alimentador" e seu estado é fechado (provavelmente NF)
                    return alimentador

    def analise_isolamento(self, chave_falta=list):
        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, "Iniciando Analise de Isolamento")

        nome_alimentador = self.localizar_chave(chave_falta)
        alimentador = self.topologia_subestacao.alimentadores[nome_alimentador]
        rnp_alimentador = alimentador.rnp_dic()

        dados_falta = dict()
        dados_falta["chave_falta"] = chave_falta
        dados_falta["alimentador"] = nome_alimentador
        dados_falta["setor"] = alimentador.chaves[dados_falta["chave_falta"]].n2.nome

        display_message(self.aid.name, "Setor sob Falta: [Setor: {setor}]".format(setor=dados_falta["setor"]))

        # Verifica quem sao as chaves do alimentador
        chaves_alim = list(alimentador.chaves.keys())

        # Verifica quem sao as chaves NA
        chaves_NA = list()
        for chave in chaves_alim:
            if alimentador.chaves[chave].estado == 0:
                chaves_NA.append(chave)

        # Verifica quem sao as chaves NF
        chaves_NF = chaves_alim
        for chave in chaves_NA:
            chaves_NF.remove(chave)

        # Verifica quem sao os vizinhos do setor faltoso
        vizinhos_isolar = alimentador.setores[dados_falta["setor"]].vizinhos

        aux = list()
        aux2 = list()

        # Verifica quais setores sao do mesmo alimentador ou qual tem uma profundidade menor que o faltoso
        for setor in vizinhos_isolar:

            if setor not in alimentador.setores:
                aux2.append(setor)

            elif rnp_alimentador[setor] > rnp_alimentador[dados_falta["setor"]]:
                aux.append(setor)

        for setor in aux2:
            vizinhos_isolar.remove(setor)

        vizinhos_isolar = aux

        # Realiza a poda dos setores a serem isolados
        for setor in vizinhos_isolar:
            self.podas.append(alimentador.podar(setor, True)) # TODO Ver o retorno de PODAR

        # Realiza a poda do setor faltoso a fim de atualizar a RNP
        setor_faltoso = alimentador.podar(dados_falta["setor"], True)
        self.setores_faltosos.append(setor_faltoso)

        # Verifica quem sao os setores a serem isolados (meio fisico)
        dados_isolamento = dict()
        dados_isolamento["chaves"] = list()
        dados_isolamento["setores_isolados"] = list()
        dados_isolamento["nos_de_carga"] = dict()

        for poda in self.podas:
            for setor in poda[0].keys():
                dados_isolamento["setores_isolados"].append(setor)

            for chave in poda[6].keys():
                if chave in chaves_NF:
                    dados_isolamento["chaves"].append(chave)

            for no in poda[3].keys():
                dados_isolamento["nos_de_carga"][no] = round(poda[3][no].potencia.mod / 1000, 0)

        dados_isolamento["setor_falta"] = dados_falta["setor"]
        dados_isolamento["chave_falta"] = dados_falta["chave_falta"]
        dados_isolamento["alimentador"] = nome_alimentador
        dados_isolamento["chaves_NA_alim"] = chaves_NA

        if len(dados_isolamento["chaves"]) > 0:

            display_message(self.aid.name, f"Setores desalimentados: {dados_isolamento['setores_isolados']}")
            # Preparando Mensagem para Isolamento de trecho faltoso
            content = dict()
            content["dados"] = dados_isolamento

            lista_de_comandos = {}
            for chave in content["dados"]["chaves"]:
                display_message(self.aid.name, f"Comando para isolar Trecho Defeituoso [CH: {chave}]")
                lista_de_comandos[chave] = 'open'

            if len(lista_de_comandos):
                conversation_id = str(uuid4())
                self.command_behaviour.register_state(
                    state_id=conversation_id, 
                    callback_inform=lambda: self.pos_isolamento((content, lista_de_comandos, 'success')), 
                    callback_failure=lambda: self.pos_isolamento((content, lista_de_comandos, 'failure')),
                    awaits=len(lista_de_comandos))
                self.command_behaviour.enviar_comando_de_chave(
                    lista_de_comandos=lista_de_comandos, 
                    proposito='coordination', 
                    conversation_id=conversation_id)
        else:
            display_message(self.aid.name, "Nenhum setor precisa ser isolado")
            self.analise_recomposicao(dados_isolamento)

    def pos_isolamento(self, state):
        content, lista_de_comandos, result = state

        content["isolamento_realizado"] = (result == 'success')
        if content["isolamento_realizado"]:
            display_message(self.aid.name, f"Trecho Defeituoso isolado {lista_de_comandos}")
        else:
            display_message(self.aid.name, f"Erro ao isolar trecho Defeituoso {lista_de_comandos}")
        
        pacote = content["dados"]
        pacote["isolamento_realizado"] = content["isolamento_realizado"]
        self.analise_recomposicao(pacote)

    def localizar_setor(self, setor = str):

        for alim in self.topologia_subestacao.alimentadores.keys():
            if setor in self.topologia_subestacao.alimentadores[alim].setores.keys():
                return alim

    def analise_recomposicao(self, dados_isolamento=dict):

        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, "Iniciando Analise de Restauracao")

        podas_mesma_SE = list()

        if len(dados_isolamento["setores_isolados"]) > 0 and dados_isolamento["isolamento_realizado"] is True:
            # Comeca a analise de restauracao poda por poda
            for poda in self.podas:
                # Define variaveis auxiliares
                i = self.podas.index(poda)
                setores_poda = poda[0].keys()
                # Exibe Mensagem no Terminal do SMA
                display_message(self.aid.name, f"Analisando Ramo ({i+1} de {len(self.podas)})")
                display_message(self.aid.name, f"Setores do Ramo {i+1}: {list(setores_poda)}")
                # Varre os alimentadores da propria subestacao verificando se há possibilidade de recompor
                # pela mesma SE
                for alimentador in self.topologia_subestacao.alimentadores:
                    # Verifica se alguma das chaves da poda pertence a outro alimentador
                    # da mesma SE
                    if dados_isolamento["alimentador"] != alimentador:
                        # Faz uma varredura nas chaves da poda e verifica se a chave pertence ao alimentador
                        # do laco for em questao (diferente do alimentador faltoso)
                        for chave in poda[6]:
                            if chave in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():  # Pertence
                                display_message(self.aid.name, f"Possivel Restauracao de Ramo {i+1} pela mesma SE atraves de [CH: {chave}]")
                                podas_mesma_SE.append([poda, chave, alimentador])
                            elif chave in dados_isolamento["chaves_NA_alim"]:  # Nao Pertence mas a poda tem chave NA
                                display_message(self.aid.name, f"Possivel Restauracao de Ramo {i+1} por outra SE atraves de [CH: {chave}]")
            # Tenta recompor os ramos possiveis pela mesma SE

            if len(podas_mesma_SE) > 0:

                lista_de_comandos = {}

                for poda in podas_mesma_SE:
                    if self.recompor_mesma_se(poda[0], poda[1], poda[2]):
                        content = dict()
                        content["ramo_recomp"] = poda[0][0].keys()
                        content["alim_colab"] = self.localizar_setor(poda[0][0].keys()[0])
                        content["chaves"] = list()
                        content["nos_de_carga"] = dict()

                        for chave in poda[0][6].keys():
                            if self.topologia_subestacao.alimentadores[poda[2]].chaves[chave].estado == 1:
                                content["chaves"].append(chave)

                        for no in poda[0][3].keys():
                            content["nos_de_carga"][no] = round(poda[0][3][no].potencia.mod / 1000, 0)
                        
                        # Indica inicio da analise
                        display_message(self.aid.name, "------------------------")
                        display_message(self.aid.name, f"Iniciando Restauracao do Ramo: {content['ramo_recomp']} pela mesma SE")

                        for chave in content["chaves"]:
                            lista_de_comandos[chave] = 'close'
                            #self.agent.operacao_chaves()

                        self.podas.remove(poda[0])

                # Para cada chave indicada no pacote de dados
                # opera fechamento de chave
                if len(lista_de_comandos):
                    display_message(self.aid.name, f"Comandos para operar chaves [CH: {lista_de_comandos}]")
                    conversation_id = str(uuid4())
                    self.command_behaviour.register_state(
                        state_id=conversation_id, 
                        callback_inform=lambda: self.pos_auto_recomposicao((content, 'success')), 
                        callback_failure=lambda: self.pos_auto_recomposicao((content, 'failure')), 
                        awaits=len(lista_de_comandos))
                    self.command_behaviour.enviar_comando_de_chave(
                        lista_de_comandos=lista_de_comandos, 
                        proposito='restoration', 
                        conversation_id=conversation_id)


            # Solicitar recomposição ao AN
            # TODO: mudar formato da poda
            print('ENVIANDO MENSAGEM PARA AGENTE DE NEGOCIAÇÃO')
            content2 = dict()
            content2["ramos"] = self.podas
            message2 = ACLMessage(ACLMessage.REQUEST)
            message2.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            message2.set_content(pickle.dumps(content2))
            message2.set_ontology("R_05")
            message2.add_receiver(self.get_an())
            self.send(message2)


        elif len(dados_isolamento["setores_isolados"]) > 0:
            display_message(self.aid.name, "Restauracao nao pode ser realizada [Falta nao isolada]")
        else:
            display_message(self.aid.name, "Falta em Final de Trecho")


    def pos_auto_recomposicao(self, state):
        content, result = state

        content["restaur_realiz"] = (result == 'success')
        if content["restaur_realiz"]:
            display_message(self.aid.name, 'Restauração Realizada')


    def recompor_mesma_se(self, poda, chave, alimentador):

        setor_isolado = poda[0].keys()[0]

        # Verifica quais dos setores vizinhos a chave pertence ao possivel alimentador colaborador
        if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome in self.topologia_subestacao.alimentadores[alimentador].setores.keys():
            setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome
        elif self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome in self.topologia_subestacao.alimentadores[alimentador].setores.keys():
            setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome

        # Insere a poda atraves do setor colaborador achado
        self.topologia_subestacao.alimentadores[alimentador].inserir_ramo(setor_colab, poda)

        # Calcula Fluxo de Carga
        calcular_fluxo_de_carga(self.topologia_subestacao)

        # Verifica Condicoes
        analise1 = self.verificar_carregamento_dos_condutores(self.topologia_subestacao)
        analise2 = self.verificar_nivel_de_tensao(self.topologia_subestacao)

        # Se todas as condicoes forem estabelecidas
        if analise1 is None and analise2 is None:
            return True

        else: # Podar ramos finais e tentar mais uma vez
            poda = self.topologia_subestacao.alimentadores[alimentador].podar(setor_isolado, True)
            return False

    def verificar_carregamento_dos_condutores(self, subestacao):

        for alimentador in subestacao.alimentadores.values():
            for trecho in alimentador.trechos.values():

                if trecho.fluxo.mod > trecho.condutor.ampacidade:
                    display_message(self.aid.name, 'Restrição de carregamento de condutores ' \
                            'atingida no trecho {t}'.format(t=trecho.nome))
                    return trecho.nome
        else:
            return None


    def verificar_nivel_de_tensao(self, subestacao):

        for alimentador in subestacao.alimentadores.values():
                for no in alimentador.nos_de_carga.values():
                    if no.tensao.mod < 0.8 * subestacao.tensao.mod or \
                        no.tensao.mod > 1.05 * subestacao.tensao.mod:
                        display_message(self.aid.name, 'Restrição de Tensão atingida ' \
                                'no nó de carga {no}'.format(no=no.nome))
                        return no.nome, round(no.tensao.mod/subestacao.tensao.mod,4)
        else:
            return None
    #Final cod Tiago

if __name__ == "__main__":
    from pade.misc.utility import start_loop

    adc = AgenteDC(AID(f'agentedc@localhost:60002'), 'S1')
    adc.ams['port'] = 60000
    adc.subscrever_a(AID('agentecom@localhost:60003'))
    
    start_loop([adc])
