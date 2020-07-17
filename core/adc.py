import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

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
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')

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
        display_message(self.agent.aid.name, 'Chaveamento realizado')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')
        callback_inform, _, awaits = self.retrieve_state(message.conversation_id)
        if awaits == 0:
            # Se não houver mais nenhuma mensagem de retorno, chama a função
            # de callback
            callback_inform()

    def handle_failure(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Falha em execução de comando')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')
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

        #Inicio cod Tiago para o agente diagnostico
        self.subestacao = subestacao
        self.enderecos_IEDs = enderecos_IEDs[subestacao]
        self.relatorios_restauracao = list()
        self.topologia_subestacao = rdf2mygrid.carregar_topologia(Path('./rede/rede-cim.xml'), subestacao)

        display_message(self.aid.name, f"Subestacao {subestacao} carregada com sucesso")
        self.podas = list()
        self.podas_possiveis = list()
        self.setores_faltosos = list()
        #comportamento_requisicao = CompRequest1(self)
        #self.behaviours.append(comportamento_requisicao)
        #comp_contractnet_participante = CompContractNet1(self)
        #self.behaviours.append(comp_contractnet_participante)
        #Final cod Tiago para o agente diagnostico

    def subscrever_a(self, acom_aid: AID):
        """Subcribe to ``AgenteCom``"""
        self.subscribe_behaviour.subscrever(acom_aid)

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
            #ALE: antigo agente de controle
            content = {"dados": dados_falta}

            content2 = dict()
            content2["chave_falta"] = content["dados"]["chave_falta"]
            # Verifica se o pacote de dados tem a tag
            # "correc_descoord" indicando que houve 50BF
            # dentre as funcoes de protecao obtidas
            if "correc_descoord" in content["dados"]:
                if content["dados"]["correc_descoord"] in content["dados"]["chaves"]:
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
                display_message(self.aid.name, f"Comando para isolar trecho sob Falta [CH:{content['dados']['chave_falta']}]")
                conversation_id = str(uuid4())
                self.command_behaviour.register_state(conversation_id, lambda: self.pos_coordenacao((content, content2, 'success')), lambda: self.pos_coordenacao((content, content2, 'failure')))
                self.command_behaviour.enviar_comando_de_chave(lista_de_comandos={content["dados"]["chave_falta"]: 'open'}, proposito='coordination', conversation_id=conversation_id)

            # Opera as chaves para isolamento do setor
            # sob falta, com ou seu descoordenacao
            # self.agent.operacao_chaves()

        else:
            self.analise_isolamento(dados_falta["chave_falta"])

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
                    callback_inform=lambda: self.analise_isolamento(content2["chave_falta"]), 
                    callback_failure=lambda: self.analise_isolamento(content2["chave_falta"]))
                self.command_behaviour.enviar_comando_de_chave(
                    lista_de_comandos=lista_de_comandos, 
                    proposito='coordination', 
                    conversation_id=conversation_id)
                return
        else:
            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")
        
        if "correc_descoord" in content["dados"] and content["dados"]["chaves"] == [content["dados"]["correc_descoord"]]:
            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")

        self.analise_isolamento(content2["chave_falta"])
    
    def enviar_comando_de_chave(self, lista_de_comandos, proposito, conversation_id):
        self.command_behaviour.enviar_comando_de_chave(lista_de_comandos, proposito, conversation_id)

    #Inicio Cod Tiago
    def buscar_alimentador(self, chave):
        for alimentador in self.topologia_subestacao.alimentadores.keys():
            if chave in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():
                # Proucura em qual alimentador da SE "chave" está.
                if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].estado == 1:
                    # "chave" pertence ao "alimentador" e seu estado é fechado (provavelmente NF)
                    return alimentador

    def analise_descoordenacao(self, dados_falta=dict):
        # Exemplo de entrada {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13'], 'ctime': 'Fri Jul  3 18:20:58 2020'}
        # Exemplo de saída {'chaves': ['CH13', 'CH14'], 'leitura_falta': ['CH13'], '50BF': ['CH14'], 'alimentador': 'S1_AL1', 'chave_falta': 'CH14', 'coordenado': False, 'correc_descoord': 'CH13'}

        # Assume que todas as chaves estão sob o mesmo Alimentador
        nome_alimentador = self.buscar_alimentador(dados_falta["chaves"][0])
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
            setor_jusante = alimentador.chaves[chave].n2.nome
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

    def analise_isolamento(self, chave_falta=list):

        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, "Iniciando Analise de Isolamento")

        nome_alimentador = self.buscar_alimentador(chave_falta)
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
            self.podas.append(alimentador.podar(setor, True))

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

            display_message(self.aid.name, f"Setores a serem isolados: {dados_isolamento['setores_isolados']}")
            # Preparando Mensagem para Isolamento de trecho faltoso
            content = dict()
            content["dados"] = dados_isolamento

            lista_de_comandos = {}
            for chave in content["dados"]["chaves"]:
                lista_de_comandos[chave] = 'open'

            conversation_id = str(uuid4())
            self.command_behaviour.register_state(
                state_id=conversation_id, 
                callback_inform=lambda: self.pos_isolamento((content, lista_de_comandos, 'success')), 
                callback_failure=lambda: self.pos_isolamento((content, lista_de_comandos, 'failure')))
            self.command_behaviour.enviar_comando_de_chave(
                lista_de_comandos=lista_de_comandos, 
                proposito='coordination', 
                conversation_id=conversation_id)
 
        else:
            display_message(self.aid.name, "Nenhum setor precisa ser isolado")
            self.analise_recomposicao(dados_isolamento)

    def pos_isolamento(self, state):
        content, lista_de_comandos, result = state
        if result == 'success':
            display_message(self.aid.name, f"Trecho Defeituoso isolado [CH:{lista_de_comandos}]")
            content["isolamento_realizado"] = True
        else:
            display_message(self.aid.name, f"Erro ao isolar trecho Defeituoso [CH:{lista_de_comandos}]")
            content["isolamento_realizado"] = False
        
        pacote = content["dados"]
        pacote["isolamento_realizado"] = content["isolamento_realizado"]
        self.analise_recomposicao(pacote)
        

    def analise_recomposicao(self, dados_isolamento=dict):
        # TODO: Parei aqui
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
                display_message(self.aid.name, f"Analisando Ramo {i+1} de {len(self.podas)}")
                display_message(self.aid.name, f"Setores do Ramo {i}: {setores_poda}")
                # Varre os alimentadores da propria subestacao verificando se há possibilidade de recompor
                # pela mesma SE
                for alimentador in self.topologia_subestacao.alimentadores:
                    # Verifica se alguma das chaves da poda pertence a outro alimentador
                    # da mesma SE
                    if dados_isolamento["alimentador"] != alimentador:
                        # Faz uma varredura nas chaves da poda e verifica se a chave pertence ao alimentador
                        # do laco for em questao (diferente do alimentador faltoso)
                        for chave in poda[6].keys():
                            if chave in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():  # Pertence
                                display_message(self.aid.name, f"Possivel Restauracao de Ramo {i} pela mesma SE atraves de [CH: {chave}]")
                                podas_mesma_SE.append([poda, chave, alimentador])
                            elif chave in dados_isolamento[
                                "chaves_NA_alim"]:  # Nao Pertence mas a poda tem chave NA
                                display_message(self.aid.name,
                                                "Possivel Restauracao de Ramo {i} por outra SE atraves de [CH: {ch}]".format(
                                                    i=i + 1, ch=chave))
            # Tenta recompor os ramos possiveis pela mesma SE
            if len(podas_mesma_SE) > 0:
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
                        # Elabora mensagem a ser enviada para o Acontrole correspondente
                        #***verificar proximas linhas
                        # Lanca Comportamento Request Iniciante
                        #comp_mesma_se = CompRequest4(self, message)
                        #self.behaviours.append(comp_mesma_se)
                        #comp_mesma_se.on_start()
                        # Atualiza a lista de podas do agente
                        self.podas.remove(poda[0])

            # Pega todos os dados de recomposicao que nao foram restaurados na mesma SE
            # e envia ao Agente Negociacao para que ele comece os ciclos de negociacao

            #***Refazer a comunicacao das proximas linhas
            # content2 = dict()
            # content2["ramos"] = self.podas
            # message2 = ACLMessage(ACLMessage.REQUEST)
            # message2.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            # message2.set_content(pickle.dumps(content2))
            # message2.set_ontology("R_05")
            # message2.add_receiver(AID(str(self.subestacao + '_ANeg')))
            # comp_ramos = CompRequest5(self, message2)
            # self.behaviours.append(comp_ramos)
            # comp_ramos.on_start()

        elif len(dados_isolamento["setores_isolados"]) > 0:
            display_message(self.aid.name, "Restauracao nao pode ser realizada [Falta nao isolada]")
        else:
            display_message(self.aid.name, "Falta em Final de Trecho")
        #Final cod Tiago

if __name__ == "__main__":
    from pade.misc.utility import start_loop
    from random import randint
    adc_antigo = AgenteDC(AID(f'agentedc@localhost:{randint(10000, 60000)}'), 'S1')
    adc_antigo.subscrever_a(AID('acom@localhost:20001'))
    start_loop([adc_antigo])
