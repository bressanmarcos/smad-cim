import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import datetime
from random import random
from uuid import uuid4
from pathlib import Path

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol, FipaSubscribeProtocol, FipaContractNetProtocol)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump, validate

from information_model import SwitchingCommand as swc
from information_model import OutageEvent as out

from rede.rdf2mygrid import carregar_topologia


class SubscreverACom(FipaSubscribeProtocol):
    def __init__(self, agent: AgenteSMAD, message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)
        
    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Inscrito em ACom')

    def handle_inform(self, message: ACLMessage):    
        """Receve notificação de evento do ACom. \\
        ``message.content`` é recebida no formato OutageEvent
        """
        """Sequência de operações realizada:
            - 1) Análise de descoordenação
            -- a) Encontrar alimentador da chave (ver topologia carregada)
            -- b) 
        """
        lista_de_chaves = {'chaves': [], 'leitura_falta': []}
        root: out.OutageEvent = out.parseString(to_string(message.content))
        for switch in root.get_Outage().get_ProtectedSwitch():
            switch: out.ProtectedSwitch
            switchId = switch.get_mRID()

            lista_de_chaves['chaves'] = []

            for discrete_meas in switch.get_Discrete_Measurement():
                discrete_meas: out.Discrete
                discrete_meas_name = discrete_meas.get_name()
                discrete_meas_value = discrete_meas.get_DiscreteValue().get_value().get_valueOf_()
                if discrete_meas_name == out.Discrete_Meas.BREAKER_POSITION:
                    if discrete_meas_value == '1':
                        lista_de_chaves['chaves'].append(switchId)
                elif discrete_meas_name == out.Discrete_Meas.BREAKER_FAILURE:
                    if discrete_meas_value == '1':
                        if not '50BF' in lista_de_chaves:
                            lista_de_chaves['50BF'] = []
                        lista_de_chaves['50BF'].append(switchId)

        print(lista_de_chaves)
        lista_de_chaves = {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13'], '50BF': ['CH14']}

        #Inicio da analise de descoordenacao
        dados_falta = self.agent.analise_descoordenacao(lista_de_chaves)

        if dados_falta["coordenado"] == False:
            #Corrigir descoordenacao
            #ALE: antigo agente de controle
            content = {"dados": dados_falta}

            content2 = dict()
            content2["chave_falta"] = content["dados"]["chave_falta"]
            display_message(self.agent.aid.name, "Iniciando correcao de Descoordenacao")
            # Verifica se o pacote de dados tem a tag
            # "correc_descoord" indicando que houve 50BF
            # dentre as funcoes de protecao obtidas
            if "correc_descoord" in content["dados"]:
                if content["dados"]["correc_descoord"] in content["dados"]["chaves"]:
                    pass
                elif content["dados"]["correc_descoord"] not in self.agent.enderecos_IEDs.keys():
                    display_message(self.agent.aid.name, str(
                        "Chave " + content["dados"]["correc_descoord"] + " nao possui IP cadastrado"))
                    content2["correc_descoord_realizada"] = False
                else:
                    display_message(self.agent.aid.name,
                                    f"Isolando trecho sob Falta [CH:{content['dados']['correc_descoord']}]")
                    content2["correc_descoord_realizada"] = True

            # Se nao houver, a descoordenacao deve
            # ser corrigida normalmente
            elif content["dados"]["chave_falta"] not in self.agent.enderecos_IEDs.keys():
                display_message(self.agent.aid.name, str(
                    "Chave " + content["dados"]["chave_falta"] + " nao possui IP cadastrado"))
                content2["correc_descoord_realizada"] = False
            else:
                display_message(self.agent.aid.name,
                                "Isolando trecho sob Falta [CH:{CH}]".format(CH=content["dados"]["chave_falta"]))
                content2["correc_descoord_realizada"] = True

            # Opera as chaves para isolamento do setor
            # sob falta, com ou seu descoordenacao
            # self.agent.operacao_chaves()

            # Verifica quais as chaves que devem ser
            # operadas a fim de reenergizar os trechos
            # desenergizados por descoordenacao
            if content2["correc_descoord_realizada"] is True:
                for chave in content["dados"]["chaves"]:
                    if "correc_descoord" in content["dados"]:
                        if chave != content["dados"]["chave_falta"] and chave != content["dados"]["correc_descoord"]:
                            # Verifica cadastro de chave
                            if chave in self.agent.enderecos_IEDs:
                                display_message(self.agent.aid.name, str(
                                    "Reestabelecendo trecho descoordenado [CH: " + chave + "]"))
                                content2["correc_descoord_realizada"] = True
                            # self.agent.operacao_chaves()
                            else:
                                display_message(self.agent.aid.name, str(
                                    "Chave " + chave + " nao possui IP cadastrado"))
                                content2["correc_descoord_realizada"] = False
                    else:
                        if chave != content["dados"]["chave_falta"] and chave in self.agent.enderecos_IEDs.keys():
                            display_message(self.agent.aid.name, str(
                                "Reestabelecendo trecho descoordenado [CH: " + chave + "]"))
                            content2["correc_descoord_realizada"] = True

                        elif chave != content["dados"]["chave_falta"]:
                            display_message(self.agent.aid.name, str(
                                "Chave " + chave + " nao possui IP cadastrado"))
                            content2["correc_descoord_realizada"] = False
            else:
                display_message(self.agent.aid.name,
                                "Impossivel corrigir descoordenacao.")

            # Se a chave aberta for a menos profunda
            # em relacao a chave que indicou 50BF
            # nao é possivel corrigir descoordenacao
            if "correc_descoord" in content["dados"] and content["dados"]["chaves"] == [
                content["dados"]["correc_descoord"]]:
                display_message(self.agent.aid.name,
                                "Impossivel corrigir descoordenacao.")
            print("final do ant ag controle:" + str(content2))
            #ALE: Final antigo agente de controle
            #Voltando para o Agente diagnostico
            content = self.agent.analise_isolamento(content2["chave_falta"])
            print("voltando para o ag diag: " + str(content))
            #Final do Agente diagnostico
            #Voltando para o agente de controle
            # Indica inicio da analise
            display_message(self.agent.aid.name, "Iniciando Isolamento de Trecho")
            # Para todas as chaves que devem ser
            # operadas no pacote de dados, chama a
            # funcao de operacao de chave
            for chave in content["chaves"]:
                # Verifica se a chave faz parte da SE com conexo TCP-IP
                if chave in self.agent.enderecos_IEDs.keys():
                    display_message(self.agent.aid.name, str(
                        "Isolando Trecho Defeituoso [CH:" + chave + "]"))
                    content["isolamento_realizado"] = True
                # self.agent.operacao_chaves()
                else:
                    display_message(self.agent.aid.name, str(
                        "Chave " + chave + " nao possui IP cadastrado"))
                    content["isolamento_realizado"] = False
            print(content)
            #final agente de controle

        else:
            self.agent.analise_isolamento(dados_falta["chave_falta"])


class EnviarComando(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=True)

    def handle_not_understood(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Mensagem não compreendida')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')

    def handle_failure(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Falha em execução de comando')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')

    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Chaveamento realizado')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')


class AgenteDC(AgenteSMAD):
    def __init__(self, aid: AID, subestacao: str, debug=False):
        super().__init__(aid, subestacao, debug)
        self.behaviours.append(EnviarComando(self))
        display_message(self.aid.name, "Agente instanciado")

        #Inicio cod Tiago para o agente diagnostico
        self.subestacao = subestacao
        self.relatorios_restauracao = list()
        self.topologia_subestacao = carregar_topologia(Path('./rede/rede-cim.xml'), subestacao)

        display_message(self.aid.name,"Subestacao {SE} carregada com sucesso".format(SE=subestacao))
        self.podas = list()
        self.podas_possiveis = list()
        self.setores_faltosos = list()
        #comportamento_requisicao = CompRequest1(self)
        #self.behaviours.append(comportamento_requisicao)
        #comp_contractnet_participante = CompContractNet1(self)
        #self.behaviours.append(comp_contractnet_participante)
        #Final cod Tiago para o agente diagnostico

    def enviar_comando_de_chave(self, switching_command: swc.SwitchingCommand, acom_aid: AID):
        """Envia um objeto de informação do tipo SwitchingCommand ao ACom fornecido"""
        # Valida objeto de informação
        validate(switching_command)
        # Monta envelope de mensagem ACL
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(acom_aid)
        message.set_ontology('SwitchingCommand')
        message.set_content(to_elementtree(switching_command))
        def later():
            # Se o ACom já estiver na tabela
            if hasattr(self, 'agentInstance') and acom_aid.name in self.agentInstance.table:
                # Envia mensagem
                self.send(message)
            else:
                # Reenvia mensagem 5 segundos mais tarde
                self.call_later(5.0, later)
        later()


    def subscribe_to(self, acom_aid: AID):
        """Subcribe to ``AgenteCom``"""
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.add_receiver(acom_aid)
        self.subscribe_behaviour = SubscreverACom(self, message, is_initiator=True)
        self.behaviours.append(self.subscribe_behaviour)
        def later():
            if hasattr(self, 'agentInstance') and acom_aid.name in self.agentInstance.table:
                # Envia mensagem
                self.subscribe_behaviour.on_start()
            else:
                # Reenvia mensagem mais tarde
                self.call_later(2.0, later)
        later()


    #Inicio Cod Tiago
    def buscar_alimentador(self, chave):
        for alimentador in self.topologia_subestacao.alimentadores.keys():
            if chave in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():
                # Proucura em qual alimentador da SE "chave" está.
                if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].estado == 1:
                    # "chave" pertence ao "alimentador" e seu estado é fechado (provavelmente NF)
                    return alimentador

    def analise_descoordenacao(self, dados_falta=dict):
        # Exemplo de mensagem {'chaves': ['CH14', 'CH13'], 'leitura_falta': ['CH14', 'CH13'], 'ctime': 'Fri Jul  3 18:20:58 2020'}
        
        # Assume que todas as chaves estão sob o mesmo Alimentador
        nome_alimentador = self.buscar_alimentador(dados_falta["chaves"][0])
        dados_falta["alimentador"] = nome_alimentador
        display_message(self.aid.name, "------------------------")
        display_message(self.aid.name, f"Analise de Descoordenacao em {nome_alimentador}")

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

            display_message(self.aid.name,
                            "Setores a serem isolados: {lista}".format(lista=dados_isolamento["setores_isolados"]))
            # Preparando Mensagem para Isolamento de trecho faltoso
            content = dict()
            content["dados"] = dados_isolamento

            #***Comandar chaves
            print("Dentro da funcao analise isolamento: " + str(dados_isolamento))
            return dados_isolamento

        else:
            display_message(self.aid.name, "Nenhum setor precisa ser isolado")
            self.analise_recomposicao(dados_isolamento)


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
    adc_antigo.subscribe_to(AID('acom@localhost:20001'))
    start_loop([adc_antigo])