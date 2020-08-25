import os

os.sys.path.insert(0, os.getcwd())
# Adiciona ao Path a pasta raiz do projeto

from pprint import pprint

import datetime
from random import random
from uuid import uuid4
from pathlib import Path
from functools import wraps

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.behaviours.protocols import (FipaRequestProtocol, FipaSubscribeProtocol, FipaContractNetProtocol)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump, validate

from information_model import SwitchingCommand as swc
from information_model import OutageEvent as out

from mygrid.fluxo_de_carga.varred_dir_inv import calcular_fluxo_de_carga
from rede import rdf2mygrid

import pickle, json

class SubscreverAEventos(FipaSubscribeProtocol):
    def __init__(self, agent: 'AgenteDC', message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)

    def subscrever(self, acom_aid):
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.add_receiver(acom_aid)
        self.agent.send_until(message)

    def handle_agree(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Inscrito em {message.sender.name}')
        # Salva também ACOMs nos quais o ADC está inscrito
        self.register(message.sender)

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

class EnviarComandoDeChaves(FipaRequestProtocol):
    """Enviar comando de chaves para AComs"""
    @staticmethod
    def filter_acom(handle_message):
        """Filtra para que somente mensagens de AComs sejam processadas"""
        @wraps(handle_message)
        def wrapper(self, message: ACLMessage):
            if message.sender not in self.agent.subscribe_behaviour.subscribers:
                return
            return handle_message(self, message)
        return wrapper

    @filter_acom.__func__
    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Chaveamento realizado: {message.content}')

    @filter_acom.__func__
    def handle_failure(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Falha em execução de comando: {message.content}')

class EnviarPoda(FipaRequestProtocol):
    @staticmethod
    def filter_an(handle_message):
        """Processa somente mensagens do AN"""
        @wraps(handle_message)
        def wrapper(self, message: ACLMessage):
            if message.sender != self.agent.get_an():
                return
            return handle_message(self, message)
        return wrapper

    @filter_an.__func__
    def handle_inform(self, message):
        display_message(self.agent.aid.name, f'Restauração efetivada: {message.content}')

    @filter_an.__func__
    def handle_failure(self, message):
        display_message(self.agent.aid.name, f'Restauração falhou: {message.content}')

class ResponderNegociacao(FipaContractNetProtocol):
    """Responder à solicitação de outras subestações"""
    def __init__(self, agent):
        super().__init__(agent = agent, message = None, is_initiator = False)

    def handle_cfp(self, message):
        self.message_cfp = message
        
        if message.ontology == "CN_01":
            display_message(self.agent.aid.name, "Mensagem CFP recebida")

            setores_colab = dict()

            # Carrega conteudo da mensagem
            poda_cim = message.content
            poda = rdf2mygrid.cim_poda(poda_cim)
            # poda = pickle.loads(poda_cim)

            # Busca o possivel alimentador e setor de recomposicao do ramo
            for alim in self.agent.topologia_subestacao.alimentadores:
                for chave in poda[6]:
                    if chave in self.agent.topologia_subestacao.alimentadores[alim].chaves:

                        if self.agent.topologia_subestacao.alimentadores[alim].chaves[chave].n1.nome in self.agent.topologia_subestacao.alimentadores[alim].setores:
                            setor_colab = self.agent.topologia_subestacao.alimentadores[alim].chaves[chave].n1.nome
                            setores_colab[setor_colab] = chave

                        elif self.agent.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome in self.agent.topologia_subestacao.alimentadores[alim].setores:
                            setor_colab = self.agent.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome
                            setores_colab[setor_colab] = chave

            if len(setores_colab): # Se houver mais de um possivel caminho de restauracao para este ramo

                # Inicia variaveis auxiliares
                aux = 0 
                setor_colab = None
                alim_colab = None

                # Para cada um dos possiveis setores colaboradores
                # busca aquele mais profundo a fim de tentar recompor a poda
                for setor in setores_colab:
                    alim = self.agent.localizar_setor(setor)
                    rnp_alim = self.agent.topologia_subestacao.alimentadores[alim].rnp_dic()

                    if int(rnp_alim[setor]) > aux:
                        aux = int(rnp_alim[setor])
                        setor_colab = setor
                        alim_colab = alim 

                setores = self.agent.topologia_subestacao.alimentadores[alim_colab].setores
                chaves = self.agent.topologia_subestacao.alimentadores[alim_colab].chaves
                chave_ligacao = next(chave for chave in chaves if chave in poda[6])
                
                # Verifica qual o setor raiz de insercao da poda
                for setor in setores:
                    for set_vizinho in setores[setor].vizinhos:
                        if set_vizinho in poda[0]:
                            setor_interno = setor
                            setor_raiz = set_vizinho

                ### Atualiza poda com informações internas
                # Setores
                poda[0][setor_raiz].rnp_associadas[setor_interno] = setores[next(v for v in setores[setor_interno].vizinhos)].rnp_associadas[setor_interno]
                poda[0][setor_raiz].vizinhos.append(setor_interno)
                poda[0][setor_raiz].rnp_associadas.pop('alimentador')
                poda[0][setor_raiz].vizinhos.remove('alimentador')
                # Nos
                no_raiz = next(no for no in poda[0][setor_raiz].nos_de_carga.values() if 'barramento_falso' in no.vizinhos)
                no_raiz.vizinhos.append(next(no.nome for no in setores[setor_interno].nos_de_carga.values() if no_raiz.nome in no.vizinhos))
                no_raiz.vizinhos.remove('barramento_falso')
                poda[0][setor_raiz].rnp_associadas[setor_interno] = (poda[0][setor_raiz].rnp_associadas[setor_interno][0], poda[5])
                # Chaves
                poda[6][chave_ligacao].n1 = chaves[chave_ligacao].n1
                poda[6][chave_ligacao].n2 = chaves[chave_ligacao].n2
      
                # Envia poda e possiveis setores de restauracao neste alimentador
                # para que a poda seja inserida e testada retornando  qual foi 
                # a possivel colaboracao do alimentador
                dados = self.agent.inserir_poda_testar(poda, setor_colab)
                # ???

                if len(dados["setores"]) != 0:
                    display_message(self.agent.aid.name, 
                        "Possivel restauracao do ramo {ram} por {se}".format(ram = dados["setores"],se=self.agent.subestacao))

                    # Preparar proposta indicando que todos os setores do ramos podem ser atendidos
                    resposta = self.message.create_reply()
                    resposta.set_performative(ACLMessage.PROPOSE)
                    resposta.set_ontology("CN_03")
                    resposta.set_content(json.dumps(dados))
                    self.agent.send(resposta)
                    return

                else:
                    display_message(self.agent.aid.name, 
                        "Nao foi possível restaurar o ramo pela {se}".format(se=self.agent.subestacao))

            else: # Se nao houver setores para possivel colaboracao
                ramo = list(poda[0].keys())
                display_message(self.agent.aid.name, f"SE [{self.agent.subestacao}] nao possui chave de encontro com o ramo {ramo}")


            # Elabora Mensagem de Refuse para o agente iniciante
            resposta = self.message.create_reply()
            resposta.set_performative(ACLMessage.REFUSE)
            resposta.set_ontology("CN_02")
            resposta.set_content(None)
            self.agent.send(resposta)


    def handle_accept_propose(self, message):
        display_message(self.agent.aid.name, "Mensagem ACCEPT PROPOSE Recebida.")
        self.proposta_aceita = message
        self.agent.recompor_se_externa(message)

    def handle_reject_propose(self, message):
        super(ResponderNegociacao, self).handle_reject_propose(message)

        if message.ontology == "CN_05":
            display_message(self.agent.aid.name,
                "Mensagem REJECT PROPOSE Recebida.")


class AgenteDC(AgenteSMAD):
    def __init__(self, aid: AID, subestacao: str, debug=False):
        super().__init__(aid, subestacao, debug)

        self.command_behaviour = EnviarComandoDeChaves(self)
        self.subscribe_behaviour = SubscreverAEventos(self)
        self.send_prone_behaviour = EnviarPoda(self)
        self.respond_negotiation_behaviour = ResponderNegociacao(self)

        self.behaviours.append(self.command_behaviour)
        self.behaviours.append(self.subscribe_behaviour)
        self.behaviours.append(self.send_prone_behaviour)

        # Inicio cod Tiago para o agente diagnostico
        self.subestacao = subestacao
        self.relatorios_restauracao = list()
        self.topologia_subestacao = rdf2mygrid.carregar_topologia(Path('./rede/rede-cim-2.xml'), subestacao)

        display_message(self.aid.name, f"Subestacao {subestacao} carregada com sucesso")
        self.podas = list()
        self.podas_possiveis = list()
        self.setores_faltosos = list()
        # comportamento_requisicao = CompRequest1(self)
        # self.behaviours.append(comportamento_requisicao)
        self.respond_negotiation_behaviour = ResponderNegociacao(self)
        self.behaviours.append(self.respond_negotiation_behaviour)
        # Final cod Tiago para o agente diagnostico

    def on_start(self):
        super().on_start()
        for acom_aid in self.__acom_aids:
            """Subcribe to ``AgenteCom``"""
            self.call_later(0.5, self.subscribe_behaviour.subscrever, acom_aid)

    def add_acom(self, acom_aid: AID):
        try:
            self.__acom_aids.append(acom_aid)
        except:
            self.__acom_aids = [acom_aid]

    def get_acoms(self):
        return self.__acom_aids

    def set_an(self, an_aid: AID):
        self.__an_aid = an_aid
    
    def get_an(self):
        try:
            return self.__an_aid
        except:
            raise AttributeError('Agente de Negociação não definido')

    def tratar_informe(self, dados_falta):
        """Mensagem recebida pelo ACom, já convertida no formato
        dos métodos do Tiago
        
        lista_de_chaves = {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13']}
        """
        #Inicio da analise de descoordenacao
        def tratar_1(dados_falta):
            content = dict()
            content["dados"] = dados_falta
            self.analise_descoordenacao(content)

            if not content["dados"]["coordenado"]:
                #Corrigir descoordenacao
                self.corrigir_descoordenacao(content)
                return
            
            self.isolamento(content)

        tratar_1(dados_falta)
        

    def analise_descoordenacao(self, content):

        # Assume que todas as chaves estão sob o mesmo Alimentador
        nome_alimentador = self.localizar_chave(content["dados"]["chaves"][0])
        content["dados"]["alimentador"] = nome_alimentador
        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, f"Analise de Descoordenacao em {nome_alimentador}")

        alimentador = self.topologia_subestacao.alimentadores[nome_alimentador]
        rnp_alimentador = alimentador.rnp_dic()
        chave_setor = {}

        for chave in content["dados"]["leitura_falta"]:
            chave_setor[chave] = alimentador.chaves[chave].n2.nome
        
        profundidade = 0
        # Busca a chave de maior profundidade (antes do setor defeituoso)
        for chave in chave_setor:
            setor_jusante = chave_setor[chave]
            i = int(rnp_alimentador[setor_jusante])
            if i >= profundidade:
                profundidade = i
                chave_falta = chave
        
        content["dados"]["chave_falta"] = chave_falta

        # Verifica se no pacote só contém a chave em questão
        if content["dados"]["chaves"] == [chave_falta]:
            # Coordenado
            content["dados"]["coordenado"] = True
            display_message(self.aid.name, "Protecao Coordenada")
        else:
            # Descoordenado
            content["dados"]["coordenado"] = False
            display_message(self.aid.name, "Protecao Descoordenada")

            # Verifica as chaves que nao podem ser operadas por 50BF
            if "50BF" in content["dados"]:
                setor_montante_falta = alimentador.chaves[chave_falta].n1.nome
                setor_jusante_falta = alimentador.chaves[chave_falta].n2.nome
                chave_50BF = content["dados"]["50BF"][0]
                setor_montante_50BF = alimentador.chaves[chave_50BF].n1.nome
                setor_jusante_50BF = alimentador.chaves[chave_50BF].n2.nome
                # Monta vetor de busca
                ch_correc_descoord = content["dados"]["leitura_falta"]

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
                        if chave in content["dados"]["50BF"]:
                            ch_correc_descoord.remove(chave_falta)
                    prof_aux = 0
                    for chave in ch_correc_descoord:
                        aux = int(rnp_alimentador[alimentador.chaves[chave].n2.nome]) + \
                              int(rnp_alimentador[alimentador.chaves[chave].n1.nome])
                        if aux > prof_aux:
                            prof_aux = aux
                            chave_correcao = chave
                    content["dados"]["correc_descoord"] = chave_correcao


    def corrigir_descoordenacao(self, content):
        
        def corrigir_descoordenacao_1(content):
            # Indica inicio da Correcao
            display_message(self.aid.name, "Iniciando correção de Descoordenação")
            
            # Verifica se o pacote de dados tem a tag
            # "correc_descoord" indicando que houve 50BF
            # dentre as funcoes de protecao obtidas
            if "correc_descoord" in content["dados"]:
                if content["dados"]["correc_descoord"] in content["dados"]["chaves"]:
                    pass
                    
                else:
                    display_message(self.aid.name, f'Comando para isolar trecho sob Falta [CH:{content["dados"]["correc_descoord"]}]')
                    self.enviar_comando_de_chave(
                        lista_de_comandos={content["dados"]["correc_descoord"]: 'open'},
                        proposito='coordination',
                        callback=lambda response_message: corrigir_descoordenacao_2(content, response_message)
                    )
                    return
                    # Código deste nível continua em ''handle_inform'' ou ''handle_failure''

            # Se nao houver, a descoordenacao deve
            # ser corrigida normalmente
            else:
                #BRESSAN: reforça a abertura da chave a montante do setor em falta...
                display_message(self.aid.name, f"Comando para isolar trecho sob Falta [CH:{content['dados']['chave_falta']}]")
                self.enviar_comando_de_chave(
                    lista_de_comandos={content["dados"]["chave_falta"]: 'open'},
                    proposito='coordination',
                    callback=lambda response_message: corrigir_descoordenacao_2(content, response_message)
                )
                return

            corrigir_descoordenacao_2(content)

        def corrigir_descoordenacao_2(content, response_message: ACLMessage = None):

            content["dados"]["correc_descoord_realizada"] = (response_message == None) or (response_message.performative == ACLMessage.INFORM)

            # Verifica quais as chaves que devem ser
            # operadas a fim de reenergizar os trechos
            # desenergizados por descoordenacao
            if content["dados"]["correc_descoord_realizada"]:

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
                    self.enviar_comando_de_chave(
                        lista_de_comandos=lista_de_comandos,
                        proposito='coordination',
                        callback=lambda response_message: corrigir_descoordenacao_3(content, response_message),
                    )
                    return

            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")
            
            corrigir_descoordenacao_3(content, None)
        
        def corrigir_descoordenacao_3(content, response_message: ACLMessage = None):

            content["dados"]["correc_descoord_realizada"] = (response_message == None) or (response_message.performative == ACLMessage.INFORM)

            if "correc_descoord" in content["dados"] and content["dados"]["chaves"] == [content["dados"]["correc_descoord"]]:
                display_message(self.aid.name, "Impossivel corrigir descoordenacao.")

            self.isolamento(content)

        corrigir_descoordenacao_1(content)

    def enviar_comando_de_chave(self, lista_de_comandos: dict, proposito: str, callback: callable):
        display_message(self.aid.name, f'Enviando comando: {lista_de_comandos} para {self.subscribe_behaviour.subscribers} ({proposito})')
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
        elif proposito == 'restoration':
            purpose = swc.Purpose.RESTORATION

        plano = swc.SwitchingPlan(
            mRID=str(uuid4()), 
            createdDateTime=datetime.datetime.now(),
            purpose=purpose, 
            SwitchAction=switch_actions)
        root = swc.SwitchingCommand(SwitchingPlan=plano)
        validate(root)
        
        # Monta envelope de mensagem ACL
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.set_ontology(swc.__name__)
        message.set_content(to_elementtree(root))
        for acom_aid in self.get_acoms():
            message.add_receiver(acom_aid)

        self.send(message, callback)

    def solicitar_recomposicao_externa(self, podas, callback):
        if not len(podas):
            return

        for poda in podas:
            # Solicitar recomposição ao AN
            poda_cim = rdf2mygrid.poda_cim(poda=poda)
            # poda_cim = pickle.dumps(poda)
            display_message(self.aid.name, 'Enviando mensagem ao AN')
            message2 = ACLMessage(ACLMessage.REQUEST)
            message2.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            message2.set_ontology("R_05")
            message2.set_content(poda_cim)
            message2.add_receiver(self.get_an())

            self.send(message2, callback)

    def localizar_chave(self, chave):
        for alimentador in self.topologia_subestacao.alimentadores:
            if not chave in self.topologia_subestacao.alimentadores[alimentador].chaves:
                continue
            chave_element = self.topologia_subestacao.alimentadores[alimentador].chaves[chave]
            setor = chave_element.n2
            if alimentador == self.localizar_setor(setor.nome):
                return alimentador

    def isolamento(self, content):

        def analise_isolamento():
            display_message(self.aid.name, "------------------------")
            display_message(self.aid.name, "Iniciando Analise de Isolamento")

            nome_alimentador = self.localizar_chave(content["dados"]["chave_falta"])
            alimentador = self.topologia_subestacao.alimentadores[nome_alimentador]
            rnp_alimentador = alimentador.rnp_dic()

            content["dados"]["alimentador"] = nome_alimentador
            content["dados"]["setor"] = alimentador.chaves[content["dados"]["chave_falta"]].n2.nome

            setor_faltoso = content["dados"]["setor"]
            display_message(self.aid.name, f"Setor sob Falta: [Setor: {setor_faltoso}]")

            # Verifica quem sao as chaves do alimentador
            chaves_alim = list(alimentador.chaves.keys())

            # Verifica quem sao as chaves NA
            chaves_NA = [chave for chave in chaves_alim if alimentador.chaves[chave].estado == 0]

            # Verifica quem sao as chaves NF
            chaves_NF = [chave for chave in chaves_alim if alimentador.chaves[chave].estado == 1]

            # Verifica quem sao os vizinhos do setor faltoso
            setores_vizinhos = alimentador.setores[setor_faltoso].vizinhos

            # Setores a jusante do setor em falta
            setores_jusante = [setor for setor in setores_vizinhos if setor in alimentador.setores and int(rnp_alimentador[setor]) > int(rnp_alimentador[content["dados"]["setor"]])]

            # Realiza a poda dos setores a serem isolados
            self.podas = [alimentador.podar(setor, True) for setor in setores_jusante]
            podas = self.podas

            # Realiza a poda do setor faltoso a fim de atualizar a RNP
            poda_setor_faltoso = alimentador.podar(setor_faltoso, True)
            self.setores_faltosos.append(poda_setor_faltoso)

            # Verifica quem sao os setores a serem isolados (meio fisico)
            content["dados"]["chaves"] = list()
            content["dados"]["setores_isolados"] = list()
            content["dados"]["nos_de_carga"] = dict()

            for poda in podas:
                for setor in poda[0]:
                    content["dados"]["setores_isolados"].append(setor)

                for chave in poda[6]:
                    if chave in chaves_NF:
                        content["dados"]["chaves"].append(chave)

                for no in poda[3]:
                    content["dados"]["nos_de_carga"][no] = round(poda[3][no].potencia.mod / 1000, 0)

            content["dados"]["setor_falta"] = content["dados"]["setor"]
            content["dados"]["alimentador"] = nome_alimentador
            content["dados"]["chaves_NA_alim"] = chaves_NA

            if len(content["dados"]["chaves"]):

                display_message(self.aid.name, f"Setores desalimentados: {content['dados']['setores_isolados']}")
                # Preparando Mensagem para Isolamento de trecho faltoso

                lista_de_comandos = {}
                for chave in content["dados"]["chaves"]:
                    display_message(self.aid.name, f"Comando para isolar Trecho Defeituoso [CH: {chave}]")
                    lista_de_comandos[chave] = 'open'

                if len(lista_de_comandos):
                    self.enviar_comando_de_chave(
                        lista_de_comandos=lista_de_comandos,
                        proposito='coordination',
                        callback=lambda response_message: pos_isolamento_por_ACom(lista_de_comandos, response_message)
                    )
                    return

            display_message(self.aid.name, "Nenhum setor precisa ser isolado")
            
            self.analise_recomposicao(content)

        def pos_isolamento_por_ACom(lista_de_comandos, response_message: ACLMessage = None):
            # Após realização do isolamento (abertura de chaves)
            content["isolamento_realizado"] = (response_message == None) or (response_message.performative == ACLMessage.INFORM)
            
            if content["isolamento_realizado"]:
                display_message(self.aid.name, f"Trecho Defeituoso isolado {lista_de_comandos}")
            else:
                display_message(self.aid.name, f"Erro ao isolar trecho Defeituoso {lista_de_comandos}")
            
            content["dados"]["isolamento_realizado"] = content["isolamento_realizado"]

            self.analise_recomposicao(content)

        analise_isolamento()

    def localizar_setor(self, setor = str):

        for alim in self.topologia_subestacao.alimentadores.keys():
            if setor in self.topologia_subestacao.alimentadores[alim].setores.keys():
                return alim

    def analise_recomposicao(self, content):
        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, "Iniciando Analise de Restauracao")
        
        def recompor_e_solicitar_recomposicao_externa():

            podas_mesma_SE = list()

            if not len(content["dados"]["setores_isolados"]):
                display_message(self.aid.name, "Falta em Final de Trecho")

            elif not content["dados"]["isolamento_realizado"]:
                display_message(self.aid.name, "Falta não isolada -> Restauracao não pôde ser realizada")
            
            else:

                # Comeca a analise de restauracao poda por poda
                for poda in self.podas:

                    # Define variaveis auxiliares
                    i = self.podas.index(poda)
                    setores_poda = list(poda[0].keys())

                    display_message(self.aid.name, f"Analisando Ramo ({i+1} de {len(self.podas)})")
                    display_message(self.aid.name, f"Setores do Ramo {i+1}: {list(setores_poda)}")
                    
                    # Varre os alimentadores da propria subestacao verificando se há possibilidade de recompor
                    # pela mesma SE
                    for alimentador in self.topologia_subestacao.alimentadores:
                        # Verifica se alguma das chaves da poda pertence a outro alimentador
                        # da mesma SE
                        if content["dados"]["alimentador"] != alimentador:
                            # Faz uma varredura nas chaves da poda e verifica se a chave pertence ao alimentador
                            # do laco for em questao (diferente do alimentador faltoso)
                            for chave in poda[6]:
                                if chave in self.topologia_subestacao.alimentadores[alimentador].chaves:  # Pertence
                                    display_message(self.aid.name, f"Possivel Restauracao de Ramo {i+1} pela mesma SE atraves de [CH: {chave}]")
                                    podas_mesma_SE.append([poda, chave, alimentador])
                                elif chave in content["dados"]["chaves_NA_alim"]:  # Nao Pertence mas a poda tem chave NA
                                    display_message(self.aid.name, f"Possivel Restauracao de Ramo {i+1} por outra SE atraves de [CH: {chave}]")
                
                # Tenta recompor os ramos possiveis pela mesma SE
                for poda in podas_mesma_SE:
                    lista_de_comandos = {}
                    if self.recompor_mesma_se(poda[0], poda[1], poda[2]):

                        def recompor_mesma_se_1():
                            content = dict()
                            content["ramo_recomp"] = list(poda[0][0].keys())
                            content["alim_colab"] = self.localizar_setor(content["ramo_recomp"][0])
                            content["chaves"] = list()
                            content["nos_de_carga"] = dict()

                            for chave in poda[0][6]:
                                if self.topologia_subestacao.alimentadores[poda[2]].chaves[chave].estado == 1:
                                    content["chaves"].append(chave)

                            for no in poda[0][3]:
                                content["nos_de_carga"][no] = round(poda[0][3][no].potencia.mod / 1000, 0)
                            
                            # Indica inicio da analise
                            display_message(self.aid.name, "------------------------")
                            display_message(self.aid.name, f"Iniciando Restauracao do Ramo: {content['ramo_recomp']} pela mesma SE")

                            # Prepara fechamento de chaves
                            for chave in content["chaves"]:
                                lista_de_comandos[chave] = 'close'

                            # Para cada chave indicada no pacote de dados
                            # opera fechamento de chave
                            if len(lista_de_comandos):
                                display_message(self.aid.name, f"Comandos para operar chaves {lista_de_comandos}")
                                self.enviar_comando_de_chave(
                                    lista_de_comandos=lista_de_comandos,
                                    proposito='restoration',
                                    callback=lambda response_message: recompor_mesma_se_2(poda, response_message),
                                )
                                return

                        def recompor_mesma_se_2(poda, response_message: ACLMessage = None):
                            # Tratar resposta do ACom
                            if response_message.performative == ACLMessage.INFORM:
                                self.podas.remove(poda[0])

                        recompor_mesma_se_1()

                # Solicita recomposição externa em 3 segundos, 
                # depois das possíveis recomposições internas
                self.call_later(
                    3.0, 
                    self.solicitar_recomposicao_externa,
                    self.podas, 
                    fim_da_recomposicao_externa
                )
                return

        def fim_da_recomposicao_externa(response_message):
            # Respostas do AN (agree ou inform)
            display_message(self.aid.name, f'Mensagem {response_message.performative} recebida do AN')
            if response_message.performative == ACLMessage.INFORM:
                display_message(self.aid.name, f'Restauração externa realizada')
            elif response_message.performative == ACLMessage.FAILURE:
                display_message(self.aid.name, f'Restauração externa não teve sucesso')

        recompor_e_solicitar_recomposicao_externa()

    def anunciar_restauracao(self, dados):

        # Prepara mensagem inform a fim de anunciar restauracao do ramo
        resposta = self.respond_negotiation_behaviour.proposta_aceita.create_reply()
        resposta.set_performative(ACLMessage.INFORM)
        resposta.set_ontology("CN_06")
        resposta.set_content(json.dumps(dados))
        self.send(resposta)

    def recompor_mesma_se(self, poda, chave, alimentador):

        setor_isolado = list(poda[0].keys())[0]

        # Verifica quais dos setores vizinhos a chave pertence ao possivel alimentador colaborador
        if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome in self.topologia_subestacao.alimentadores[alimentador].setores:
            setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome
        elif self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome in self.topologia_subestacao.alimentadores[alimentador].setores:
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
                    display_message(self.aid.name, f'Restrição de carregamento de condutores ({round(trecho.fluxo.mod, 2)} A > {trecho.condutor.ampacidade} A) atingida no trecho {trecho.nome}')
                    return trecho.nome
        else:
            return None


    def verificar_nivel_de_tensao(self, subestacao):

        for alimentador in subestacao.alimentadores.values():
                for no in alimentador.nos_de_carga.values():
                    if no.tensao.mod < 0.8 * subestacao.tensao.mod or \
                        no.tensao.mod > 1.05 * subestacao.tensao.mod:
                        display_message(self.aid.name, f'Restrição de Tensão atingida no nó de carga {no.nome}')
                        print(f'{round(no.tensao.mod, 2)} V fora do intervalo [{0.8 * subestacao.tensao.mod} V, {1.05 * subestacao.tensao.mod} V]')
                        return no.nome, round(no.tensao.mod/subestacao.tensao.mod,4)
        else:
            return None


    def inserir_poda_testar(self, poda, setor_colab):
        dados = dict()
        dados["setor_colab"] = setor_colab

        # Procura qual alimentador da subestacao pode receber a poda
        alim = self.localizar_setor(setor_colab)
        setores = self.topologia_subestacao.alimentadores[alim].setores

        # Verifica qual o setor raiz de insercao da poda
        for setor in setores:
            for set_vizinho in setores[setor].vizinhos:
                if set_vizinho in poda[0]:
                    setor_interno = setor
                    setor_raiz = set_vizinho

        dados["setor_raiz"] = setor_raiz

        # Insere a poda no alimentador previamente encontrado
        self.topologia_subestacao.alimentadores[alim].inserir_ramo(setor_colab, poda, setor_raiz)

        # Calcula fluxo de carga para SE com a poda inserida
        calcular_fluxo_de_carga(self.topologia_subestacao)

        # Verifica Condicoes
        analise1 = self.verificar_carregamento_dos_condutores(self.topologia_subestacao)
        analise2 = self.verificar_nivel_de_tensao(self.topologia_subestacao)
        
        # Calcula-se o carregamento dos trafos da SE
        carreg_SE = self.calcular_carregamento_da_se(self.topologia_subestacao)

        #print "============================"
        #print analise1, analise2, carreg_SE, poda[0].keys()

        # Re-poda o ramo previamente inserido
        poda = self.topologia_subestacao.alimentadores[alim].podar(setor_raiz, True)

        # Inicia estrutura de dados para relatorio de recomposicao
        relat_recomp = {str(poda[0].keys()):{"alimentador":str(alim),
                                        "setor_colab":str(setor_colab),
                                        "setor_raiz":str(setor_raiz),
                                        "tentativas":{
                                        str(poda[0].keys()):{"carreg_SE":carreg_SE,
                                                             "carreg_cond":analise1,
                                                             "nivel_tensao":analise2}}}}

        if analise1 is None and analise2 is None and carreg_SE <= 100:
            dados["carreg_SE"] = carreg_SE
            dados["setores"] = list(poda[0].keys())
            self.podas_possiveis.append(poda)

        else:    

            # Reinsere a poda previamente testada
            self.topologia_subestacao.alimentadores[alim].inserir_ramo(setor_colab, poda, setor_raiz)

            # Verifica setor mais profundo daquela poda para o alimentador
            prof = 0
            rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic()

            for setor in poda[0].keys():
                if int(rnp_alim[setor]) > prof:
                    prof = int(rnp_alim[setor])
                    setor_poda = setor

            # Quantidade de setores na poda

            aux = len(poda[0].keys())
            dados["setores"] = list(poda[0].keys())



            # Para o numero de setores da poda faz os testes de ramos recursivos
            while aux != 0:
                aux -= 1

                # Poda ramo/setor mais profundo, do ramo desenergizado e faz os 
                # testes mais uma vez
                ramo = self.topologia_subestacao.alimentadores[alim].podar(setor_poda, True)
                dados["setores"].remove(setor_poda)

                # Verifica Condicoes
                analise1 = self.verificar_carregamento_dos_condutores(self.topologia_subestacao)

                analise2 = self.verificar_nivel_de_tensao(self.topologia_subestacao)
            
                # Calcula-se o carregamento dos trafos da SE
                carreg_SE = self.calcular_carregamento_da_se(self.topologia_subestacao)

                # print "================="
                # print analise1, analise2, carreg_SE, dados["setores"], ramo[0].keys()

                # Atualiza estrutura de dados para relatorio de recomposicao
                relat_recomp[str(poda[0].keys())]["tentativas"][str(dados["setores"])] = {"carreg_SE":carreg_SE,
                                                                                          "carreg_cond":analise1,
                                                                                          "nivel_tensao":analise2}

                if analise1 is None and analise2 is None and carreg_SE <= 100:
                    dados["carreg_SE"] = carreg_SE

                    # Retira o ramo mantendo a RNP em sua forma original
                    poda_final = self.topologia_subestacao.alimentadores[alim].podar(setor_raiz, True)
                    self.podas_possiveis.append(poda_final)
                    break

                else:
                    # Proucura novo setor mais profundo
                    setores_aux = list(poda[0].keys())

                    for setor in ramo[0].keys():
                        setores_aux.remove(setor)

                    # Verifica setor mais profundo desta nova poda para o alimentador
                    prof = 0
                    rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic()

                    # Determina novo setor_poda e prof para o laco while
                    for setor in setores_aux:
                        if setor in rnp_alim and rnp_alim[setor] > prof:
                            prof = rnp_alim[setor]
                            setor_poda = setor
        
        # Atualiza a pilha de relatorios
        self.relatorios_restauracao.append(relat_recomp)

        return dados


    def calcular_carregamento_da_se(self, subestacao):

        pot_se = 0.0
        pot_utilizada = 0.0

        for trafo in subestacao.transformadores.keys():
            pot_se = pot_se + subestacao.transformadores[trafo].potencia.mod

        for alim in subestacao.alimentadores.keys():
            aux = subestacao.alimentadores[alim].calcular_potencia()
            pot_utilizada = pot_utilizada + aux.mod

        carreg = (pot_utilizada/pot_se)*100

        return round(carreg,3)


    def recompor_ramo(self, proposta):
        alim = self.localizar_setor(proposta["setor_colab"])
        chaves_operar = list()

        # Verifica quais das podas previamentes testadas corresponde 
        # a poda em ocasiao
        for poda in self.podas_possiveis:

            if list(poda[0].keys()) == proposta["setores"]:

                # self.topologia_subestacao.alimentadores[alim].inserir_ramo(
                #     proposta["setor_colab"], poda, proposta["setor_raiz"])

                # Verifica quais chaves devem ser operadas a fim de reestabelecer
                # a poda
                for chave in poda[6].values():
                    if chave.estado == 1: # Adiciona todas as chaves da poda
                        chaves_operar.append(chave.nome)

                    elif chave.n1 and proposta["setor_colab"] == chave.n1.nome or chave.n2 and proposta["setor_colab"] == chave.n2.nome:
                        # Adiciona chave de fronteira
                        chaves_operar.append(chave.nome)

                # Retira da poda recomposta da lista
                self.podas_possiveis.remove(poda)

                dados = {"chaves": chaves_operar,
                        "ramo": list(poda[0].keys()),
                        "nos_de_carga": dict()}

                for no in poda[3]:
                    dados["nos_de_carga"][no] = round(poda[3][no].potencia.mod/1000,0)

                return dados


    def recompor_se_externa(self, message):
 
        def controlar_chaves():
            if message.ontology == "CN_04":

                proposta = json.loads(message.content)
                
                # Recompoe a poda da proposta
                dados = self.recompor_ramo(proposta)
                lista_de_comandos = {chave: 'close' for chave in dados['chaves']}
                # Prepara mensagem para enviar ao respectivo Agente
                # Controle da SE para operar a restauracao da poda
                self.enviar_comando_de_chave(
                    lista_de_comandos=lista_de_comandos,
                    proposito='restoration',
                    callback=lambda response: informar_termino(dados, message, response)
                )
        
        def informar_termino(dados, message_an: ACLMessage, message_acom: ACLMessage):

            resposta = message_an.create_reply()
            resposta.set_performative(message_acom.performative)
            resposta.set_ontology('R_05')
            resposta.set_content(None)
            self.send(resposta)

        controlar_chaves()


if __name__ == "__main__":
    from pade.misc.utility import start_loop

    adc3 = AgenteDC(AID('agentedc-3@localhost:60031'), 'S3')
    adc3.add_acom(AID('agentecom-3@localhost:60030'))
    adc3.set_an(AID('agenten-3@localhost:60032'))
    adc3.ams['port'] = 60000

    
    start_loop([adc3])
