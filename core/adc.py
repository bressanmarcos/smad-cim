import datetime
import json
import os
import pickle
from functools import wraps
from pathlib import Path
from pprint import pprint
from random import random
from uuid import uuid4

from information_model import OutageEvent as out
from information_model import SwitchingCommand as swc
from mygrid.fluxo_de_carga.varred_dir_inv import calculate_loadflow
from pade.acl.aid import AID
from pade.acl.filters import Filter
from pade.acl.messages import ACLMessage
from pade.behaviours.highlevel import *
from pade.misc.utility import display_message
from rede import rdf2mygrid

from core.common import AgenteSMAD, dump, to_elementtree, to_string, validate

os.sys.path.insert(0, os.getcwd())
# Adiciona ao Path a pasta raiz do projeto


class ACHandler:
    """Useful methods to treat SwitchingCommand messages"""

    @staticmethod
    def read_events(message: ACLMessage):
        """Convert message from AC to a dict

        Args:
            message (ACLMessage): message from AC

        Returns:
            dict: list of switch events
        """
        switches_list = {'chaves': [], 'leitura_falta': []}

        root: out.OutageEvent = out.parseString(to_string(message.content))

        for switch in root.get_Outage().get_ProtectedSwitch():
            switch: out.ProtectedSwitch
            switchId = switch.get_mRID()

            for discrete_meas in switch.get_Discrete_Measurement():
                discrete_meas: out.Discrete
                discrete_meas_name = discrete_meas.get_name()
                discrete_meas_value = discrete_meas.get_DiscreteValue().get_value().valueOf_
                if discrete_meas_name == out.Discrete_Meas.BREAKER_POSITION:
                    if int(discrete_meas_value) == 1:
                        switches_list['chaves'].append(switchId)
                        switches_list['leitura_falta'].append(switchId)
                elif discrete_meas_name == out.Discrete_Meas.BREAKER_FAILURE:
                    if int(discrete_meas_value) == 1:
                        if not '50BF' in switches_list:
                            switches_list['50BF'] = []
                        switches_list['50BF'].append(switchId)

        return switches_list

    @staticmethod
    def pack_commands(command_list: dict, purpose: swc.Purpose):
        """Converte um dicionário de comandos em um artefato XML SwitchingCommand"""
        switch_actions = []
        sequenceNumber = 0
        for chave, comando in command_list.items():
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

        plano = swc.SwitchingPlan(
            mRID=str(uuid4()),
            createdDateTime=datetime.datetime.now(),
            purpose=purpose,
            SwitchAction=switch_actions)

        root = swc.SwitchingCommand(SwitchingPlan=plano)
        try:
            validate(root)
        except:
            pass

        return to_elementtree(root)


class AgenteDC(AgenteSMAD):
    def __init__(self, aid: AID, substation: str, network_file: str, debug=False):
        super().__init__(aid, substation, debug)

        self.network_file = network_file

        self.relatorios_restauracao = list()
        self.podas_possiveis = list()
        self.setores_faltosos = list()

        # Fatores de subtensao e sobretensão
        self.fator_subtensao = 0.95
        self.fator_sobretensao = 1.05
        # Fator de sobrecarga dos transformadores
        self.fator_sobrecarga = 1.1

        self.p_command = FipaRequestProtocol(self)
        self.p_subscribe = FipaSubscribeProtocol(self)
        self.req_restoration = FipaRequestProtocol(self)
        self.resp_negotiation = FipaContractNetProtocol(self, is_initiator=False)
        
        self.resp_negotiation.set_cfp_handler(self.handle_cfp)

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
            raise AttributeError('No Negotiation Agent (AN)')

    def on_start(self):
        super().on_start()

        # Load substation
        self.topologia_subestacao = rdf2mygrid.carregar_topologia(
            filename=Path(self.network_file), 
            subestacao=self.substation
        )

        self.subscribe_to_events()

    def subscribe_to_events(self):
        """Handle subscription to ACs"""

        @AgentSession.session
        def individual_subscription(ac_aid):
            message = ACLMessage()
            message.add_receiver(ac_aid)

            while True:
                try:
                    response = yield from self.p_subscribe.send_subscribe(message)
                    display_message(self.aid.name, 'Received INFORM')

                    # Start main activity
                    self.call_later(0, self.main_activity, response)

                except FipaAgreeHandler as h:
                    response = h.message
                    display_message(self.aid.name, 'Received AGREE')
                    display_message(self.aid.name, f'Inscrito em {response.sender.name}')

                except FipaRefuseHandler:
                    display_message(self.aid.name, 'Received REFUSE')

                except:
                    return

        for ac_aid in self.get_acoms():
            individual_subscription(ac_aid)

    @AgentSession.session
    def main_activity(self, inform: ACLMessage):
        # Inform from AC
        switches_list = ACHandler.read_events(inform)
        content = self.incoordination_analysis(switches_list)

        if not content["dados"]["coordenado"]:
            #Corrigir descoordenacao
            yield from self.incoordination_correction(content)

        podas = yield from self.isolation_analysis(content)
        podas = yield from self.restoration_analysis(content, podas)

        if podas:
            for poda in podas:
                yield from self.request_external_restoration(poda)

    def incoordination_analysis(self, dados_falta):
        """Mensagem recebida pelo ACom, já convertida no formato
        dos métodos do Tiago
        
        switches_list = {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13']}
        """
        #Inicio da analise de descoordenacao
        content = dict()
        content["dados"] = dados_falta

        # Assume que todas as chaves estão sob o mesmo Alimentador
        nome_alimentador = self.find_switch(content["dados"]["chaves"][0])
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

        return content

    def incoordination_correction(self, content):

        display_message(self.aid.name, "Iniciando correção de Descoordenação")

        response_message = None
        if "correc_descoord" in content["dados"]:
            # Houve descoordenação com falha de disjuntor
            if content["dados"]["correc_descoord"] in content["dados"]["chaves"]:
                pass

            else:
                display_message(self.aid.name, f"Comando para isolar trecho sob Falta [CH:{content['dados']['correc_descoord']}]")

                response_message = yield from self.send_switch_command(
                    command_list={content['dados']['correc_descoord']: 'open'},
                    purpose=swc.Purpose.COORDINATION)

        else:
            # Não houve falha de acionamento do disjuntor
            display_message(self.aid.name, f"Comando para isolar trecho sob Falta [CH:{content['dados']['chave_falta']}]")

            response_message = yield from self.send_switch_command(
                command_list={content['dados']['chave_falta']: 'open'},
                purpose=swc.Purpose.COORDINATION)

        # incoordination_correction_2
        content["dados"]["correc_descoord_realizada"] = \
            (response_message == None) \
            or (response_message.performative == ACLMessage.INFORM)

        # Verifica quais as chaves que devem ser
        # operadas a fim de reenergizar os trechos
        # desenergizados por descoordenacao

        response_message = None
        if content["dados"]["correc_descoord_realizada"]:

            command_list = {}
            for chave in content["dados"]["chaves"]:
                if "correc_descoord" in content["dados"]:
                    if chave != content["dados"]["chave_falta"] and chave != content["dados"]["correc_descoord"]:
                        command_list[chave] = 'close'
                else:
                    if chave != content["dados"]["chave_falta"]:
                        command_list[chave] = 'close'

            if len(command_list):
                display_message(self.aid.name, "Comando para reestabelecer trechos descoordenados [CH: " + str(command_list) + "]")
                response_message = yield from self.send_switch_command(
                    command_list=command_list,
                    purpose=swc.Purpose.COORDINATION
                )

        else:
            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")

        # incoordination_correction_3
        content["dados"]["correc_descoord_realizada"] = (response_message == None) or (
            response_message.performative == ACLMessage.INFORM)

        if "correc_descoord" in content["dados"] and content["dados"]["chaves"] == [content["dados"]["correc_descoord"]]:
            display_message(self.aid.name, "Impossivel corrigir descoordenacao.")

    def isolation_analysis(self, content):

        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, "Iniciando Analise de Isolamento")

        nome_alimentador = self.find_switch(content["dados"]["chave_falta"])
        alimentador = self.topologia_subestacao.alimentadores[nome_alimentador]
        rnp_alimentador = alimentador.rnp_dic()

        content["dados"]["alimentador"] = nome_alimentador
        content["dados"]["setor"] = alimentador.chaves[content["dados"]
                                                       ["chave_falta"]].n2.nome

        setor_faltoso = content["dados"]["setor"]
        display_message(self.aid.name, f"Setor sob Falta: [Setor: {setor_faltoso}]")

        # Verifica quem sao as chaves do alimentador
        chaves_alim = list(alimentador.chaves.keys())

        # Verifica quem sao as chaves NA
        chaves_NA = [chave for chave in chaves_alim
                     if alimentador.chaves[chave].estado == 0]

        # Verifica quem sao as chaves NF
        chaves_NF = [chave for chave in chaves_alim
                     if alimentador.chaves[chave].estado == 1]

        # Verifica quem sao os vizinhos do setor faltoso
        setores_vizinhos = alimentador.setores[setor_faltoso].vizinhos

        # Setores a jusante do setor em falta
        setores_jusante = [setor for setor in setores_vizinhos if setor in alimentador.setores and int(
            rnp_alimentador[setor]) > int(rnp_alimentador[content["dados"]["setor"]])]

        # Realiza a poda dos setores a serem isolados
        podas = [alimentador.podar(setor, True)
                 for setor in setores_jusante]

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
                content["dados"]["nos_de_carga"][no] = round(
                    poda[3][no].potencia.mod / 1000, 0)

        content["dados"]["setor_falta"] = content["dados"]["setor"]
        content["dados"]["alimentador"] = nome_alimentador
        content["dados"]["chaves_NA_alim"] = chaves_NA

        if len(content["dados"]["chaves"]):

            display_message(
                self.aid.name, f"Setores desalimentados: {content['dados']['setores_isolados']}")

            # Abre todas as chaves do trecho a ser recomposto
            display_message(
                self.aid.name, f"Enviando comando para isolar setores desalimentados {content['dados']['chaves']}")

            response_message = yield from self.send_switch_command(
                command_list={chave: 'open' for chave in content["dados"]["chaves"]},
                purpose=swc.Purpose.ISOLATION,
            )

            # Após realização do isolamento (abertura de chaves)
            content["isolamento_realizado"] = (response_message == None) or (
                response_message.performative == ACLMessage.INFORM)

            if content["isolamento_realizado"]:
                display_message(self.aid.name, f"Trecho Defeituoso isolado")
            else:
                display_message(self.aid.name, f"Erro ao isolar trecho Defeituoso")

            content["dados"]["isolamento_realizado"] = content["isolamento_realizado"]

        else:
            display_message(self.aid.name, "Nenhum setor precisa ser isolado")

        return podas

    def restoration_analysis(self, content, podas):

        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, "Iniciando Analise de Restauracao")

        podas_mesma_SE = list()

        if not len(content["dados"]["setores_isolados"]):
            display_message(self.aid.name, "Falta em Final de Trecho")
            return

        elif not content["dados"]["isolamento_realizado"]:
            display_message(self.aid.name, "Falta não isolada -> Restauracao não pôde ser realizada")
            return

        # Comeca a analise de restauracao poda por poda
        for poda in podas:

            # Define variaveis auxiliares
            i = podas.index(poda)
            setores_poda = list(poda[0].keys())

            display_message(self.aid.name, f"Analisando Ramo ({i+1} de {len(podas)})")
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
                        # Pertence
                        if chave in self.topologia_subestacao.alimentadores[alimentador].chaves:
                            display_message(self.aid.name, f"Possivel Restauracao de Ramo {i+1} pela mesma SE atraves de [CH: {chave}]")
                            podas_mesma_SE.append([poda, chave, alimentador])
                        # Nao Pertence mas a poda tem chave NA
                        elif chave in content["dados"]["chaves_NA_alim"]:
                            display_message(self.aid.name, f"Possivel Restauracao de Ramo {i+1} por outra SE atraves de [CH: {chave}]")

        # Tenta recompor os ramos possiveis pela mesma SE
        for poda, chave, alimentador in podas_mesma_SE:
            command_list = {}
            if self.restore_same_substation(poda, chave, alimentador):

                content = dict()
                content["ramo_recomp"] = list(poda[0].keys())
                content["alim_colab"] = self.find_sector(content["ramo_recomp"][0])
                content["chaves"] = list()
                content["nos_de_carga"] = dict()

                for chave in poda[6]:
                    if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].estado == 1:
                        content["chaves"].append(chave)

                for no in poda[3]:
                    content["nos_de_carga"][no] = round(poda[3][no].potencia.mod / 1000, 0)

                # Indica inicio da analise
                display_message(self.aid.name, "------------------------")
                display_message(self.aid.name, f"Iniciando Restauracao do Ramo: {content['ramo_recomp']} pela mesma SE")

                # Prepara fechamento de chaves
                for chave in content["chaves"]:
                    command_list[chave] = 'close'

                # Para cada chave indicada no pacote de dados
                # opera fechamento de chave
                if len(command_list):
                    display_message(self.aid.name, f"Comandos para operar chaves {command_list}")
                    response_message = yield from self.send_switch_command(
                        command_list=command_list,
                        purpose=swc.Purpose.RESTORATION
                    )

                # Tratar resposta do ACom
                if response_message.performative == ACLMessage.INFORM:
                    podas.remove(poda)

        return podas

    def request_external_restoration(self, poda):
        """Requests external restoration to AN"""
        display_message(self.aid.name, 'Sending request to AN')

        poda_cim = rdf2mygrid.poda_cim(poda=poda)
        # poda_cim = pickle.dumps(poda)

        message = ACLMessage()
        message.set_ontology("R_05")
        message.set_content(poda_cim)
        message.add_receiver(self.get_an())

        while True:
            try:
                response_an = yield from self.req_restoration.send_request(message)
                display_message(self.aid.name, f'Restauração externa efetivada')

            except FipaFailureHandler as h:
                response_an = h.message
                display_message(self.aid.name, f'Restauração externa falhou: {response_an.content}')

            except FipaAgreeHandler:
                display_message(self.aid.name, f'Agree recebido')

            except FipaProtocolComplete:
                break

        if response_an.ontology == swc.__name__:
            display_message(self.aid.name, f'Comando de chaves para concluir restauração internamente')
            
            response_acom = yield from self.send_switch_command(
                content=response_an.content,
                purpose=swc.Purpose.RESTORATION
            )

            display_message(self.aid.name, f'Restauração externa concluída com fechamento de chaves internas')

    @AgentSession.session
    def handle_cfp(self, message: ACLMessage):
        display_message(self.aid.name, "Mensagem CFP recebida")
        setores_colab = dict()

        # Carrega conteudo da mensagem
        poda_cim = message.content
        poda = rdf2mygrid.cim_poda(poda_cim)
        # poda = pickle.loads(poda_cim)

        # Busca o possivel alimentador e setor de recomposicao do ramo
        for alim in self.topologia_subestacao.alimentadores:
            for chave in poda[6]:
                if chave in self.topologia_subestacao.alimentadores[alim].chaves:

                    if self.topologia_subestacao.alimentadores[alim].chaves[chave].n1.nome in self.topologia_subestacao.alimentadores[alim].setores:
                        setor_colab = self.topologia_subestacao.alimentadores[alim].chaves[chave].n1.nome
                        setores_colab[setor_colab] = chave

                    elif self.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome in self.topologia_subestacao.alimentadores[alim].setores:
                        setor_colab = self.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome
                        setores_colab[setor_colab] = chave

        if len(setores_colab):  # Se houver mais de um possivel caminho de restauracao para este ramo

            # Inicia variaveis auxiliares
            aux = 0
            setor_colab = None
            alim_colab = None

            # Para cada um dos possiveis setores colaboradores
            # busca aquele mais profundo a fim de tentar recompor a poda
            for setor in setores_colab:
                alim = self.find_sector(setor)
                rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic()

                if int(rnp_alim[setor]) > aux:
                    aux = int(rnp_alim[setor])
                    setor_colab = setor
                    alim_colab = alim

            setores = self.topologia_subestacao.alimentadores[alim_colab].setores
            chaves = self.topologia_subestacao.alimentadores[alim_colab].chaves
            chave_ligacao = next(chave for chave in chaves if chave in poda[6])

            # Verifica qual o setor raiz de insercao da poda
            for setor in setores:
                for set_vizinho in setores[setor].vizinhos:
                    if set_vizinho in poda[0]:
                        setor_interno = setor
                        setor_raiz = set_vizinho

            ### Atualiza poda com informações internas
            # Setores
            poda[0][setor_raiz].rnp_associadas[setor_interno] = setores[
                next(v for v in setores[setor_interno].vizinhos
                     if v != setor_raiz)].rnp_associadas[setor_interno]
            poda[0][setor_raiz].vizinhos.append(setor_interno)
            poda[0][setor_raiz].rnp_associadas.pop('alimentador')
            poda[0][setor_raiz].vizinhos.remove('alimentador')
            # Nos
            no_raiz = next(no for no in poda[0][setor_raiz].nos_de_carga.values(
            ) if 'barramento_falso' in no.vizinhos)
            no_raiz.vizinhos.append(
                next(no.nome for no in setores[setor_interno].nos_de_carga.values()
                     if no_raiz.nome in no.vizinhos)
            )
            no_raiz.vizinhos.remove('barramento_falso')
            poda[0][setor_raiz].rnp_associadas[setor_interno] = (
                poda[0][setor_raiz].rnp_associadas[setor_interno][0], 
                poda[5]
            )
            # Chaves
            poda[6][chave_ligacao].n1 = chaves[chave_ligacao].n1
            poda[6][chave_ligacao].n2 = chaves[chave_ligacao].n2

            # Envia poda e possiveis setores de restauracao neste alimentador
            # para que a poda seja inserida e testada retornando  qual foi
            # a possivel colaboracao do alimentador
            dados = self.inserir_poda_testar(poda, setor_colab)

            if len(dados["setores"]) != 0:
                response = yield from self.send_proposal(cfp_message=message, data=dados)

                if response.performative == ACLMessage.ACCEPT_PROPOSAL:
                    yield from self.recompor_se_externa(response)

                return

            else:
                display_message(self.aid.name, f"Nao foi possível restaurar o ramo pela {self.substation}")

        else:  # Se nao houver setores para possivel colaboracao
            ramo = list(poda[0].keys())
            display_message(self.aid.name, f"SE [{self.substation}] nao possui chave de encontro com o ramo {ramo}")

        # Elabora Mensagem de Refuse para o agente iniciante
        resposta = message.create_reply()
        resposta.set_ontology("CN_02")
        resposta.set_content(None)
        self.resp_negotiation.send_refuse(resposta)

    def send_proposal(self, cfp_message, data):
        display_message(self.aid.name, f"Possivel restauracao do ramo {data['setores']} por {self.substation}")

        proposta = cfp_message.create_reply()
        proposta.set_ontology("CN_03")
        proposta.set_content(json.dumps(data))

        while True:
            try:
                response = yield from self.resp_negotiation.send_propose(proposta)
                display_message(self.aid.name, "Mensagem ACCEPT PROPOSE Recebida.")
            except FipaRejectProposalHandler as h:
                response = h.message
                display_message(self.aid.name, "Mensagem REJECT PROPOSE Recebida.")
            except FipaProtocolComplete:
                break
        return response

    def recompor_se_externa(self, message_an):

        proposta = json.loads(message_an.content)

        # Recompoe a poda da proposta
        dados = self.recompor_ramo(proposta)

        # Separa as chaves da própria SE (incluindo as de recurso NA)
        chaves_proprias = []
        chaves_externas = []
        for chave in dados['chaves']:
            if any(chave in alim.chaves for alim in self.topologia_subestacao.alimentadores.values()):
                chaves_proprias.append(chave)
            else:
                chaves_externas.append(chave)

        command_list = {chave: 'close' for chave in chaves_proprias}
        # Prepara mensagem para enviar ao respectivo Agente
        # Controle da SE para operar a restauracao da poda
        message_acom = yield from self.send_switch_command(
            command_list=command_list,
            purpose=swc.Purpose.RESTORATION
        )

        resposta = message_an.create_reply()

        if len(chaves_externas):
            # Retorna as chaves externas (não controláveis), a fim de concluir a restauração
            message_content = ACHandler.pack_commands(
                command_list={chave: 'close' for chave in chaves_externas},
                purpose=swc.Purpose.RESTORATION
            )
            resposta.set_ontology(swc.__name__)
            resposta.set_content(message_content)

        self.resp_negotiation.send_inform(resposta)

    def send_switch_command(self, purpose, command_list=None, content=None):

        if command_list:
            message_content = ACHandler.pack_commands(command_list, purpose)
        else:
            message_content = content

        def individual_request(receiver):
            message = ACLMessage()
            message.set_ontology(swc.__name__)
            message.set_content(message_content)
            message.add_receiver(receiver)

            while True:
                try:
                    response = yield from self.p_command.send_request(message)
                    display_message(self.aid.name, f'[Comando de Chave] Inform: {response.content}')
                except FipaRefuseHandler as h:
                    response = h.message
                    display_message(self.aid.name, f'[Comando de Chave] Refuse: {response.content}')
                except FipaFailureHandler as h:
                    response = h.message
                    display_message(self.aid.name, f'[Comando de Chave] Failure: {response.content}')
                except FipaAgreeHandler:
                    pass
                except FipaProtocolComplete:
                    break
            return response

        responses = yield from AgentSession.gather(
            *[individual_request(acom) for acom in self.get_acoms()]
        )
        return next(m for m in responses if m.performative == ACLMessage.INFORM)

    def find_switch(self, chave):
        for alimentador in self.topologia_subestacao.alimentadores:
            if not chave in self.topologia_subestacao.alimentadores[alimentador].chaves:
                continue
            chave_element = self.topologia_subestacao.alimentadores[alimentador].chaves[chave]
            setor = chave_element.n2
            if alimentador == self.find_sector(setor.nome):
                return alimentador

    def find_sector(self, setor=str):

        for alim in self.topologia_subestacao.alimentadores.keys():
            if setor in self.topologia_subestacao.alimentadores[alim].setores.keys():
                return alim

    def restore_same_substation(self, poda, chave, alimentador):

        setor_isolado = list(poda[0].keys())[0]

        # Verifica quais dos setores vizinhos a chave pertence ao possivel alimentador colaborador
        if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome in self.topologia_subestacao.alimentadores[alimentador].setores:
            setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome
        elif self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome in self.topologia_subestacao.alimentadores[alimentador].setores:
            setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome

        # Insere a poda atraves do setor colaborador achado
        self.topologia_subestacao.alimentadores[alimentador].inserir_ramo(setor_colab, poda)

        # Calcula Fluxo de Carga
        calculate_loadflow(self.topologia_subestacao)

        # Verifica Condicoes
        analise1 = self.verificar_carregamento_dos_condutores(self.topologia_subestacao)
        analise2 = self.verificar_nivel_de_tensao(self.topologia_subestacao)

        # Se todas as condicoes forem estabelecidas
        if analise1 is None and analise2 is None:
            return True

        else:  # Podar ramos finais e tentar mais uma vez
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
                if not self.fator_subtensao * subestacao.tensao.mod <= no.tensao.mod <= self.fator_sobretensao * subestacao.tensao.mod:
                    display_message(self.aid.name, f'Restrição de Tensão atingida no nó de carga {no.nome}')
                    print(f'{round(no.tensao.mod, 2)} V fora do intervalo [{0.8 * subestacao.tensao.mod} V, {1.05 * subestacao.tensao.mod} V]')
                    return no.nome, round(no.tensao.mod/subestacao.tensao.mod, 4)
        else:
            return None

    def inserir_poda_testar(self, poda, setor_colab):
        dados = dict()
        dados["setor_colab"] = setor_colab

        # Procura qual alimentador da subestacao pode receber a poda
        alim = self.find_sector(setor_colab)
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
        calculate_loadflow(self.topologia_subestacao)

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
        relat_recomp = {str(poda[0].keys()):
                        {"alimentador": str(alim),
                         "setor_colab": str(setor_colab),
                         "setor_raiz": str(setor_raiz),
                         "tentativas": {
                            str(poda[0].keys()):
                            {"carreg_SE": carreg_SE,
                             "carreg_cond": analise1,
                             "nivel_tensao": analise2}}}}

        if analise1 is None and analise2 is None and carreg_SE <= 100:
            dados["carreg_SE"] = carreg_SE
            dados["setores"] = list(poda[0].keys())
            self.podas_possiveis.append(poda)

        else:

            # Reinsere a poda previamente testada
            self.topologia_subestacao.alimentadores[alim].inserir_ramo(
                setor_colab, poda, setor_raiz)

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
                ramo = self.topologia_subestacao.alimentadores[alim].podar(
                    setor_poda, True)
                dados["setores"].remove(setor_poda)

                # Verifica Condicoes
                analise1 = self.verificar_carregamento_dos_condutores(
                    self.topologia_subestacao)

                analise2 = self.verificar_nivel_de_tensao(
                    self.topologia_subestacao)

                # Calcula-se o carregamento dos trafos da SE
                carreg_SE = self.calcular_carregamento_da_se(
                    self.topologia_subestacao)

                # print "================="
                # print analise1, analise2, carreg_SE, dados["setores"], ramo[0].keys()

                # Atualiza estrutura de dados para relatorio de recomposicao
                relat_recomp[str(poda[0].keys())]["tentativas"][str(dados["setores"])] = {"carreg_SE": carreg_SE,
                                                                                          "carreg_cond": analise1,
                                                                                          "nivel_tensao": analise2}

                if analise1 is None and analise2 is None and carreg_SE <= 100 * self.fator_sobrecarga:
                    dados["carreg_SE"] = carreg_SE

                    # Retira o ramo mantendo a RNP em sua forma original
                    poda_final = self.topologia_subestacao.alimentadores[alim].podar(
                        setor_raiz, True)
                    self.podas_possiveis.append(poda_final)
                    break

                else:
                    # Proucura novo setor mais profundo
                    setores_aux = list(poda[0].keys())

                    for setor in ramo[0].keys():
                        setores_aux.remove(setor)

                    # Verifica setor mais profundo desta nova poda para o alimentador
                    prof = 0
                    rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic(
                    )

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

        return round(carreg, 3)

    def recompor_ramo(self, proposta):
        alim = self.find_sector(proposta["setor_colab"])
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
                    if chave.estado == 1:  # Adiciona todas as chaves da poda
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
                    dados["nos_de_carga"][no] = round(
                        poda[3][no].potencia.mod/1000, 0)

                return dados
