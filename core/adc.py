from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.utility import display_message

from core.common import *

import information_model as im
import xml.etree.ElementTree as ET

#from mygrid.fluxo_de_carga.varred_dir_inv import calcular_fluxo_de_carga
from rede.xml2objects import carregar_topologia


class RecepcaoDeDados(FipaRequestProtocol):
    def __init__(self, agent):
        super(RecepcaoDeDados, self).__init__(agent, is_initiator=False)
        self.agent: AgenteDC

    def handle_request(self, message: ACLMessage):
        super(RecepcaoDeDados, self).handle_request(message)
        # RESPONDER MENSAGEM
        message = message.create_reply()
        message.set_performative(ACLMessage.INFORM)
        self.agent.send(message)

        # Executa a função que corresponde à ontologia da mensagem
        getattr(self, message.ontology)(message)

    # Funções chamadas de acordo com a ontologia da mensagem
    def outage(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Mensagem REQUEST recebida')

        # Transmite mensagem idêntica para ADF
        new_message = ACLMessage(ACLMessage.REQUEST)
        new_message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        new_message.set_ontology(message.ontology)
        new_message.add_receiver('agente_df')
        new_message.set_content(message.content)
        self.agent.call_later(0.5, self.agent.send, new_message)

        # Mapeia para SMRA do tiago
        content = dict()
        content['dados'] = dict()
        content['dados']['BRKF'] = list()
        content['dados']['chaves'] = list()
        content['dados']['leitura_falta'] = [x.text for x in message.content.findall(
            "n:ProtectedSwitch/n:mRID", namespaces={'n': 'grei.ufc.br/smad'})]
        for chave in content['dados']['leitura_falta']:
            # Lê a posição da chave
            breaker_position = message.content.findall(
                "n:ProtectedSwitch[n:mRID='{}']/n:Discrete_Measurement[n:name='BreakerPosition']/n:DiscreteValue/n:value".format(
                    chave),
                namespaces={'n': 'grei.ufc.br/smad'})
            if breaker_position and breaker_position[0].text is '1':
                content['dados']['chaves'].append(chave)
            # Verifica se houve falha
            breaker_failure = message.content.findall(
                "n:ProtectedSwitch[n:mRID='{}']/n:Discrete_Measurement[n:name='BreakerFailure']/n:DiscreteValue/n:value".format(
                    chave),
                namespaces={'n': 'grei.ufc.br/smad'})
            breaker_failure = len(
                breaker_failure) and breaker_failure[0].text is '1'
            if breaker_failure:
                content['dados']['BRKF'].append(chave)

        if content['dados'].has_key("leitura_falta"):
            dados_falta = self.agent.analise_descoordenacao(content["dados"])
            if dados_falta["coordenado"] == False:

                # Prepara mensagem para corrigir descoordenacao
                content = {"dados": dados_falta}
                message2 = ACLMessage(ACLMessage.REQUEST)
                message2.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
                message2.set_content(content)
                message2.set_ontology("R_02")
                message2.add_receiver(
                    AID(str(self.agent.subestacao + '_ACont')))
                message2.add_receiver(
                    AID(str(self.agent.subestacao + '_ADFalta')))

            else:
                self.agent.analise_isolamento(dados_falta["chave_falta"])

class AgenteDC(AgenteSMAD):
    def __init__(self, aid, subestacao, aids: dict = {}, debug=False):
        super(AgenteDC, self).__init__(aid, subestacao, debug)

        self.behaviours.append(
            RecepcaoDeDados(self)
        )
        # comportamento_requisicao = CompRequest1(self)
        # self.behaviours.append(comportamento_requisicao)

        # comp_contractnet_participante = CompContractNet1(self)
        # self.behaviours.append(comp_contractnet_participante)

        self.relatorios_restauracao = list()

        self.topologia_subestacao = carregar_topologia(subestacao)
        display_message(self.aid.name,
                        "Subestacao {SE} carregada com sucesso".format(SE=subestacao))

        self.podas = list()
        self.podas_possiveis = list()

        self.setores_faltosos = list()

        def enviar_comando():
            pass

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
                    display_message(self.aid.name, "Analisando Ramo {i} de {tot}".format(
                        i=i+1, tot=len(self.podas)))
                    display_message(self.aid.name, "Setores do Ramo {i}: {setores}".format(
                        i=i+1, setores=setores_poda))

                    # Varre os alimentadores da propria subestacao verificando se há possibilidade de recompor
                    # pela mesma SE
                    for alimentador in self.topologia_subestacao.alimentadores.keys():

                        # Verifica se alguma das chaves da poda pertence a outro alimentador
                        # da mesma SE
                        if dados_isolamento["alimentador"] != alimentador:

                            # Faz uma varredura nas chaves da poda e verifica se a chave pertence ao alimentador
                            # do laco for em questao (diferente do alimentador faltoso)
                            for chave in poda[6].keys():
                                # Pertence
                                if chave in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():

                                    display_message(self.aid.name,
                                                    "Possivel Restauracao de Ramo {i} pela mesma SE atraves de [CH: {ch}]".format(i=i+1, ch=chave))

                                    podas_mesma_SE.append(
                                        [poda, chave, alimentador])

                                # Nao Pertence mas a poda tem chave NA
                                elif chave in dados_isolamento["chaves_NA_alim"]:

                                    display_message(self.aid.name,
                                                    "Possivel Restauracao de Ramo {i} por outra SE atraves de [CH: {ch}]".format(i=i+1, ch=chave))

                # Tenta recompor os ramos possiveis pela mesma SE
                if len(podas_mesma_SE) > 0:
                    for poda in podas_mesma_SE:

                        if self.recompor_mesma_se(poda[0], poda[1], poda[2]):

                            content = dict()
                            content["ramo_recomp"] = poda[0][0].keys()
                            content["alim_colab"] = self.localizar_setor(
                                poda[0][0].keys()[0])
                            content["chaves"] = list()
                            content["nos_de_carga"] = dict()

                            for chave in poda[0][6].keys():
                                if self.topologia_subestacao.alimentadores[poda[2]].chaves[chave].estado == 1:
                                    content["chaves"].append(chave)

                            for no in poda[0][3].keys():
                                content["nos_de_carga"][no] = round(
                                    poda[0][3][no].potencia.mod/1000, 0)

                            # Elabora mensagem a ser enviada para o Acontrole correspondente
                            message = ACLMessage(ACLMessage.REQUEST)
                            message.set_protocol(
                                ACLMessage.FIPA_REQUEST_PROTOCOL)
                            message.set_content(json.dumps(content))
                            message.set_ontology("R_04")
                            message.add_receiver(
                                AID(str(self.subestacao + '_ACont')))
                            message.add_receiver(
                                AID(str(self.subestacao + '_ADFalta')))

                            # Lanca Comportamento Request Iniciante
                            comp_mesma_se = CompRequest4(self, message)
                            self.behaviours.append(comp_mesma_se)
                            comp_mesma_se.on_start()

                            # Atualiza a lista de podas do agente
                            self.podas.remove(poda[0])

                # Pega todos os dados de recomposicao que nao foram restaurados na mesma SE
                # e envia ao Agente Negociacao para que ele comece os ciclos de negociacao

                content2 = dict()
                content2["ramos"] = self.podas

                message2 = ACLMessage(ACLMessage.REQUEST)
                message2.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
                message2.set_content(pickle.dumps(content2))
                message2.set_ontology("R_05")
                message2.add_receiver(AID(str(self.subestacao + '_ANeg')))

                comp_ramos = CompRequest5(self, message2)
                self.behaviours.append(comp_ramos)
                comp_ramos.on_start()

            elif len(dados_isolamento["setores_isolados"]) > 0:
                display_message(
                    self.aid.name, "Restauracao nao pode ser realizada [Falta nao isolada]")

            else:
                display_message(self.aid.name, "Falta em Final de Trecho")

        def analise_isolamento(self, chave_falta=list):

            display_message(self.aid.name, "------------------------")
            display_message(self.aid.name, "Iniciando Analise de Isolamento")

            alim = self.localizar_chave(chave_falta)
            rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic()

            dados_falta = dict()
            dados_falta["chave_falta"] = chave_falta
            dados_falta["alimentador"] = alim
            dados_falta["setor"] = self.topologia_subestacao.alimentadores[alim].chaves[dados_falta["chave_falta"]].n2.nome

            display_message(self.aid.name, "Setor sob Falta: [Setor: {setor}]".format(
                setor=dados_falta["setor"]))

            # Verifica quem sao as chaves do alimentador
            chaves_alim = self.topologia_subestacao.alimentadores[alim].chaves.keys(
            )

            # Verifica quem sao as chaves NA
            chaves_NA = list()
            for chave in chaves_alim:
                if self.topologia_subestacao.alimentadores[alim].chaves[chave].estado == 0:
                    chaves_NA.append(chave)

            # Verifica quem sao as chaves NF
            chaves_NF = chaves_alim
            for chave in chaves_NA:
                chaves_NF.remove(chave)

            # Verifica quem sao os vizinhos do setor faltoso
            vizinhos_isolar = self.topologia_subestacao.alimentadores[
                alim].setores[dados_falta["setor"]].vizinhos

            aux = list()
            aux2 = list()

            # Verifica quais setores sao do mesmo alimentador ou qual tem uma profundidade menor que o faltoso
            for setor in vizinhos_isolar:

                if setor not in self.topologia_subestacao.alimentadores[alim].setores.keys():
                    aux2.append(setor)

                elif rnp_alim[setor] > rnp_alim[dados_falta["setor"]]:
                    aux.append(setor)

            for setor in aux2:
                vizinhos_isolar.remove(setor)

            vizinhos_isolar = aux

            # Realiza a poda dos setores a serem isolados
            for setor in vizinhos_isolar:
                self.podas.append(
                    self.topologia_subestacao.alimentadores[alim].podar(setor, True))

            # Realiza a poda do setor faltoso a fim de atualizar a RNP
            setor_faltoso = self.topologia_subestacao.alimentadores[alim].podar(
                dados_falta["setor"], True)
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
                    dados_isolamento["nos_de_carga"][no] = round(
                        poda[3][no].potencia.mod/1000, 0)

            dados_isolamento["setor_falta"] = dados_falta["setor"]
            dados_isolamento["chave_falta"] = dados_falta["chave_falta"]
            dados_isolamento["alimentador"] = alim
            dados_isolamento["chaves_NA_alim"] = chaves_NA

            if len(dados_isolamento["chaves"]) > 0:

                display_message(self.aid.name, "Setores a serem isolados: {lista}".format(
                    lista=dados_isolamento["setores_isolados"]))
                # Preparando Mensagem para Isolamento de trecho faltoso
                content = dict()
                content["dados"] = dados_isolamento

                message = ACLMessage(ACLMessage.REQUEST)
                message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
                message.set_content(json.dumps(content))
                message.set_ontology("R_03")
                message.add_receiver(AID(str(self.subestacao + '_ACont')))
                message.add_receiver(AID(str(self.subestacao + '_ADFalta')))

                #  Lancando Comportamento Request Iniciante
                comp = CompRequest3(self, message)
                self.behaviours.append(comp)
                comp.on_start()

            else:
                display_message(
                    self.aid.name, "Nenhum setor precisa ser isolado")
                self.analise_recomposicao(dados_isolamento)

        def analise_descoordenacao(self, dados_falta=dict):

            alim = self.localizar_chave(dados_falta["chaves"][0])
            dados_falta["alimentador"] = alim
            display_message(self.aid.name, "------------------------")
            display_message(self.aid.name, "Analise de Descoordenacao em {alim}".format(
                alim=dados_falta["alimentador"]))

            campo_busca = dict()

            rnp_busca = self.topologia_subestacao.alimentadores[alim].rnp_dic()

            for chave in dados_falta["leitura_falta"]:
                campo_busca[chave] = self.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome

            prof = 0
            for chave in campo_busca:
                if rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome] >= prof:
                    prof = rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome]
                    chave_falta = chave

            if dados_falta["chaves"] == [chave_falta]:
                # Coordenado

                dados_falta["chave_falta"] = chave_falta
                dados_falta["coordenado"] = True
                display_message(self.aid.name, "Protecao Coordenada")

            else:

                # Descoordenado
                dados_falta["chave_falta"] = chave_falta
                try:
                    chave_50BF = dados_falta["50BF"][0]
                except:
                    pass
                dados_falta["coordenado"] = False
                display_message(self.aid.name, "Protecao Descoordenada")

                # Verifica as chaves que nao podem ser operadas por 50BF
                if dados_falta.has_key("50BF"):
                    # Monta vetor de busca
                    ch_correc_descoord = dados_falta["leitura_falta"]

                    # Identifica profundidade da falta
                    if rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_falta].n1.nome] > rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_falta].n2.nome]:
                        prof_falta = rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_falta].n1.nome]
                    else:
                        prof_falta = rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_falta].n2.nome]

                    # Identifica profundidade da 50BF
                    if rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_50BF].n1.nome] > rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_50BF].n2.nome]:
                        prof_50BF = rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_50BF].n1.nome]
                    else:
                        prof_50BF = rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave_50BF].n2.nome]

                    if prof_50BF < prof_falta:
                        # Se a 50BF ocorreu a montante -1  da falta
                        chave_correcao = chave_falta

                    else:  # Se a 50BF na falta

                        # Retira a chave da falta com 50BF
                        ch_correc_descoord.remove(chave_falta)

                        # Remove as demais chaves com 50BF
                        for chave in ch_correc_descoord:
                            if chave in dados_falta["50BF"]:
                                ch_correc_descoord.remove(chave)

                        prof_aux = 0

                        for chave in ch_correc_descoord:
                            aux = rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave].n2.nome] + \
                                rnp_busca[self.topologia_subestacao.alimentadores[alim].chaves[chave].n1.nome]

                            if aux > prof_aux:
                                prof_aux = aux
                                chave_correcao = chave

                        dados_falta["correc_descoord"] = chave_correcao

            return dados_falta

        def localizar_chave(self, chave_busca):

            for alimentador in self.topologia_subestacao.alimentadores.keys():

                if chave_busca in self.topologia_subestacao.alimentadores[alimentador].chaves.keys():
                    # Proucura em qual alimentador da SE "chave" está.

                    if self.topologia_subestacao.alimentadores[alimentador].chaves[chave_busca].estado == 1:
                        # "chave" pertence ao "alimentador" e seu estado é fechado (provavelmente NF)
                        return alimentador

        def localizar_setor(self, setor=str):

            for alim in self.topologia_subestacao.alimentadores.keys():
                if setor in self.topologia_subestacao.alimentadores[alim].setores.keys():
                    return alim

        def recompor_mesma_se(self, poda, chave, alimentador):

            setor_isolado = poda[0].keys()[0]

            # Verifica quais dos setores vizinhos a chave pertence ao possivel alimentador colaborador
            if self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome in self.topologia_subestacao.alimentadores[alimentador].setores.keys():
                setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n1.nome
            elif self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome in self.topologia_subestacao.alimentadores[alimentador].setores.keys():
                setor_colab = self.topologia_subestacao.alimentadores[alimentador].chaves[chave].n2.nome

            # Insere a poda atraves do setor colaborador achado
            self.topologia_subestacao.alimentadores[alimentador].inserir_ramo(
                setor_colab, poda)

            # Calcula Fluxo de Carga
            calcular_fluxo_de_carga(self.topologia_subestacao)

            # Verifica Condicoes
            analise1 = self.verificar_carregamento_dos_condutores(
                self.topologia_subestacao)
            analise2 = self.verificar_nivel_de_tensao(
                self.topologia_subestacao)

            # Se todas as condicoes forem estabelecidas
            if analise1 is None and analise2 is None:
                return True

            else:  # Podar ramos finais e tentar mais uma vez
                poda = self.topologia_subestacao.alimentadores[alimentador].podar(
                    setor_isolado, True)
                return False

        def verificar_carregamento_dos_condutores(self, subestacao):

            for alimentador in subestacao.alimentadores.values():
                for trecho in alimentador.trechos.values():

                    if trecho.fluxo.mod > trecho.condutor.ampacidade:
                        display_message(self.aid.name, 'Restrição de carregamento de condutores '
                                        'atingida no trecho {t}'.format(t=trecho.nome))
                        return trecho.nome
            else:
                return None

        def verificar_nivel_de_tensao(self, subestacao):

            for alimentador in subestacao.alimentadores.values():
                for no in alimentador.nos_de_carga.values():
                    if no.tensao.mod < 0.8 * subestacao.tensao.mod or \
                            no.tensao.mod > 1.05 * subestacao.tensao.mod:
                        display_message(self.aid.name, 'Restrição de Tensão atingida '
                                        'no nó de carga {no}'.format(no=no.nome))
                        return no.nome, round(no.tensao.mod/subestacao.tensao.mod, 4)
            else:
                return None

        def calcular_carregamento_da_se(self, subestacao):

            pot_se = 0.0
            pot_utilizada = 0.0

            for trafo in subestacao.transformadores.keys():
                pot_se = pot_se + \
                    subestacao.transformadores[trafo].potencia.mod

            for alim in subestacao.alimentadores.keys():
                aux = subestacao.alimentadores[alim].calcular_potencia()
                pot_utilizada = pot_utilizada + aux.mod

            carreg = (pot_utilizada/pot_se)*100

            return round(carreg, 3)

        def inserir_poda_testar(self, poda, setor_colab):
            dados = dict()
            dados["setor_colab"] = setor_colab

            # Procura qual alimentador da subestacao pode receber a poda
            alim = self.localizar_setor(setor_colab)

            # Verifica qual o setor raiz de insercao da poda
            for setor in self.topologia_subestacao.alimentadores[alim].setores.keys():
                for set_vizinho in self.topologia_subestacao.alimentadores[alim].setores[setor].vizinhos:
                    if set_vizinho in poda[0].keys():
                        raiz = set_vizinho

            dados["setor_raiz"] = raiz

            # Insere a poda no alimentador previamente encontrado
            self.topologia_subestacao.alimentadores[alim].inserir_ramo(
                setor_colab, poda, raiz)

            # Calcula fluxo de carga para SE com a poda inserida
            calcular_fluxo_de_carga(self.topologia_subestacao)

            # Verifica Condicoes
            analise1 = self.verificar_carregamento_dos_condutores(
                self.topologia_subestacao)
            analise2 = self.verificar_nivel_de_tensao(
                self.topologia_subestacao)

            # Calcula-se o carregamento dos trafos da SE
            carreg_SE = self.calcular_carregamento_da_se(
                self.topologia_subestacao)

            # print "============================"
            # print analise1, analise2, carreg_SE, poda[0].keys()

            # Re-poda o ramo previamente inserido
            poda = self.topologia_subestacao.alimentadores[alim].podar(
                raiz, True)

            # Inicia estrutura de dados para relatorio de recomposicao
            relat_recomp = {str(poda[0].keys()): {"alimentador": str(alim),
                                                  "setor_colab": str(setor_colab),
                                                  "setor_raiz": str(raiz),
                                                  "tentativas": {
                str(poda[0].keys()): {"carreg_SE": carreg_SE,
                                      "carreg_cond": analise1,
                                      "nivel_tensao": analise2}}}}

            if analise1 is None and analise2 is None and carreg_SE <= 100:
                dados["carreg_SE"] = carreg_SE
                dados["setores"] = poda[0].keys()
                self.podas_possiveis.append(poda)

            else:

                # Reinsere a poda previamente testada
                self.topologia_subestacao.alimentadores[alim].inserir_ramo(
                    setor_colab, poda, raiz)

                # Verifica setor mais profundo daquela poda para o alimentador
                prof = 0
                rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic(
                )

                for setor in poda[0].keys():
                    if rnp_alim[setor] > prof:
                        prof = rnp_alim[setor]
                        setor_poda = setor

                # Quantidade de setores na poda

                aux = len(poda[0].keys())
                dados["setores"] = poda[0].keys()

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

                    if analise1 is None and analise2 is None and carreg_SE <= 100:
                        dados["carreg_SE"] = carreg_SE

                        # Retira o ramo mantendo a RNP em sua forma original
                        poda_final = self.topologia_subestacao.alimentadores[alim].podar(
                            raiz, True)
                        self.podas_possiveis.append(poda_final)
                        break

                    else:
                        # Proucura novo setor mais profundo
                        setores_aux = poda[0].keys()

                        for setor in ramo[0].keys():
                            setores_aux.remove(setor)

                        # Verifica setor mais profundo desta nova poda para o alimentador
                        prof = 0
                        rnp_alim = self.topologia_subestacao.alimentadores[alim].rnp_dic(
                        )

                        # Determina novo setor_poda e prof para o laco while
                        for setor in setores_aux:
                            if rnp_alim.has_key(setor) and rnp_alim[setor] > prof:
                                prof = rnp_alim[setor]
                                setor_poda = setor

            # Atualiza a pilha de relatorios
            self.relatorios_restauracao.append(relat_recomp)

            return dados

        def recompor_ramo(self, proposta):

            alim = self.localizar_setor(proposta["setor_colab"])
            chaves_operar = list()

            # Verifica quais das podas previamentes testadas corresponde
            # a poda em ocasiao
            for poda in self.podas_possiveis:

                if poda[0].keys() == proposta["setores"]:

                    # self.topologia_subestacao.alimentadores[alim].inserir_ramo(
                    # 	proposta["setor_colab"], poda, proposta["setor_raiz"])

                    # Verifica quais chaves devem ser operadas a fim de reestabelecer
                    # a poda
                    for chave in poda[6].values():
                        if chave.estado == 1:  # Adiciona todas as chaves da poda
                            chaves_operar.append(chave.nome)

                        elif chave.n1.nome == proposta["setor_colab"] or chave.n2.nome == proposta["setor_colab"]:
                            # Adiciona chave de fronteira
                            chaves_operar.append(chave.nome)

                    # Retira da poda recomposta da lista
                    self.podas_possiveis.remove(poda)

                    dados = {"chaves": chaves_operar,
                             "ramo": poda[0].keys(),
                             "nos_de_carga": dict()}

                    for no in poda[3].keys():
                        dados["nos_de_carga"][no] = round(
                            poda[3][no].potencia.mod/1000, 0)

                    return dados
