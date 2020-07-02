import datetime
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol,
                                       FipaSubscribeProtocol, TimedBehaviour)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump, validate
from core.acom import AgenteCom

import sys
sys.path.insert(0, '../') # Adiciona a pasta pai no Path para ser usada na linha abaixo
from information_model import SwitchingCommand as swc

class SubscreverACom(FipaSubscribeProtocol):
    def __init__(self, agent: AgenteSMAD, message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)
        
    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Inscrito em ACom')

    def handle_inform(self, message: ACLMessage):    
        # TODO: Funções chamadas de acordo com a ontologia da mensagem
        def handle_outage(message):
            display_message(self.agent.aid.name, 'Mensagem INFORM recebida de %s' % message.sender.localname)
            print(message.content)

        # Chama a função que corresponde à ontologia da mensagem
        try:
            locals()[f'handle_{message.ontology}'](message)
        except:
            display_message(self.agent.aid.name, 'Mensagem não reconhecida')
            not_understood = message.create_reply()
            not_understood.set_performative(ACLMessage.NOT_UNDERSTOOD)
            self.agent.send(not_understood)

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

#inicio codigo do Tiago Agente diagnostico de falta
"""
Comportamentos: ***Gerar relatórios***

    CompRequest1 = Comportamento FIPA Request Participante necessario
para receber todas as mensagens do sistema a fim de gerar relatorio.

"""

class CompRequest1(FipaRequestProtocol):
    def __init__(self, agent):
        super(CompRequest1, self).__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):

        if message.ontology == "ontogrid":
            # Dados de falta do Agente Monitoramento
            content = json.loads(message.content)
            mensagem_nova = '{"func_prot": {"CH14": ["XCBR", "PTOC"], "CH13": ["XCBR", "PTOC"]}, "dados": {"chaves": ["CH14", "CH13"], "leitura_falta": ["CH14", "CH13"], "ctime": "Tue Aug 27 12:20:26 2019"}}'
            content = json.loads(mensagem_nova)
            # print message.sender.name

            #			display_message(self.aid.name, "**** message.content: "+str(message.content))
            #			display_message(self.aid.name, "**** content: "+str(content))
            print("**** Mensagem recebida: " + str(message.content))
            print("**** Mensagem substituta para funcionar o agente diag_falta: " + str(content))

            # Inicializa relatorio da secao
            self.relatorio = Document()

            self.relatorio.add_heading("Relatorio de Falta (SE: " + self.agent.subestacao + ")", 0)

            self.relatorio.add_heading("Diagrama do Sistema de Distribuicao", level=1)

            pic1 = self.relatorio.add_picture('./rede/rede.png', width=Inches(2.5))
            parag_foto = self.relatorio.add_paragraph("(Fonte: XML)")
            parag_foto.alignment = WD_ALIGN_PARAGRAPH.CENTER

            self.relatorio.add_heading("Registro de Eventos", level=1)
            parag1 = self.relatorio.add_paragraph("Recebimento do TRIP: ")
            parag1.add_run(
                "{time}".format(time=content["dados"]["ctime"])).bold = True

            table_trip = self.relatorio.add_table(rows=3, cols=2)
            table_trip.alignment = WD_TABLE_ALIGNMENT.CENTER
            linha_1 = table_trip.rows[0].cells
            parag_linha1_col1 = linha_1[0].add_paragraph("")
            parag_linha1_col1.add_run("DESCRICAO DO EVENTO").bold = True
            parag_linha1_col1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col2 = linha_1[1].add_paragraph("")
            parag_linha1_col2.add_run("SEQUENCIA DE EVENTOS").bold = True
            parag_linha1_col2.alignment = WD_ALIGN_PARAGRAPH.CENTER

            linha_2 = table_trip.rows[1].cells
            linha_2[0].text = "Chaves Abertas Permanente [52a]:"

            chaves_aux = list()
            for chave in content["dados"]["chaves"]:
                if content["dados"]["chaves"].index(chave) != len(content["dados"]["chaves"]) - 1:
                    chaves_aux.append(str(chave + ", "))
                else:
                    chaves_aux.append(str(chave))

            linha_2[1].text = chaves_aux

            linha_3 = table_trip.rows[2].cells
            linha_3[0].text = "Funcoes de Protecao: "
            linha_3[1].text = "Chave : Funcoes"
            for chave in content["func_prot"].keys():
                linha_3[1].add_paragraph("{CH} : {func}".format(CH=chave, func=content["func_prot"][chave]))

            self.relatorio.add_page_break()

            if content["dados"]["chaves"] == content["dados"]["leitura_falta"]:
                self.relatorio.add_heading("Diagnostico de Atuacao da Protecao", level=1)

                parag_topo = self.relatorio.add_paragraph("ATUACAO DA PROTECAO: ")
                parag_topo.add_run("COORDENADA").bold = True

            self.relatorio.save("relatorio_falta_" + self.agent.subestacao + ".docx")


        elif message.ontology == "R_02":
            # Dados de falta do Agente Monitoramento
            content = json.loads(message.content)

            if content["dados"]["coordenado"] == False:

                self.relatorio.add_heading("Diagnostico de Atuacao da Protecao", level=1)

                parag_topo = self.relatorio.add_paragraph("ATUACAO DA PROTECAO: ")
                parag_topo.add_run("DESCOORDENADA").bold = True

                if "correc_descoord" in content["dados"] and content["dados"]["chaves"] == [
                    content["dados"]["correc_descoord"]]:

                    parag_desc = self.relatorio.add_paragraph("\tDevido Falha de Disjuntor na chave [")
                    parag_desc.add_run(content["dados"]["50BF"]).bold = True
                    parag_desc.add_run("] a descoordenacao nao pode ser corrigida para esta falta.")

                else:
                    chaves_aux = list()
                    for chave in content["dados"]["chaves"]:
                        if chave != content["dados"]["chave_falta"]:
                            if content["dados"]["chaves"].index(chave) != len(content["dados"]["chaves"]) - 1:
                                chaves_aux.append(str(chave + ", "))
                            else:
                                chaves_aux.append(str(chave))

                    table_correc_coordenacao = self.relatorio.add_table(rows=3, cols=3)
                    table_correc_coordenacao.alignment = WD_TABLE_ALIGNMENT.CENTER

                    linha_1 = table_correc_coordenacao.rows[0].cells
                    parag_linha1_col1 = linha_1[0].add_paragraph("")
                    parag_linha1_col1.add_run("OPERACAO").bold = True
                    parag_linha1_col1.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    parag_linha1_col2 = linha_1[1].add_paragraph("")
                    parag_linha1_col2.add_run("CHAVES").bold = True
                    parag_linha1_col2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    parag_linha1_col3 = linha_1[2].add_paragraph("")
                    parag_linha1_col3.add_run("COMANDO").bold = True
                    parag_linha1_col3.alignment = WD_ALIGN_PARAGRAPH.CENTER

                    linha_2 = table_correc_coordenacao.rows[1].cells
                    linha_2[0].text = "Isolamento Setor Defeituoso:"

                    if "correc_descoord" in content["dados"]:
                        linha_2[1].text = content["dados"]["correc_descoord"]
                    else:
                        linha_2[1].text = content["dados"]["chave_falta"]

                    linha_2[2].text = "ABERTURA DE CHAVE"

                    linha_3 = table_correc_coordenacao.rows[2].cells
                    linha_3[0].text = "Correcao de Descoordenacao: "
                    linha_3[1].text = chaves_aux
                    linha_3[2].text = "FECHAMENTO DE CHAVE"

                self.relatorio.save("relatorio_falta_" + self.agent.subestacao + ".docx")


        elif message.ontology == "R_03":
            # Dados de Isolamento do Agente Controle
            content = json.loads(message.content)

            self.relatorio.add_paragraph("")

            self.relatorio.add_heading("Dados de Isolamento", level=1)

            table_isolamento = self.relatorio.add_table(rows=2, cols=4)
            table_isolamento.alignment = WD_TABLE_ALIGNMENT.CENTER

            linha_1 = table_isolamento.rows[0].cells
            parag_linha1_col1 = linha_1[0].add_paragraph("")
            parag_linha1_col1.add_run("SETOR SOB FALTA").bold = True
            parag_linha1_col1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col2 = linha_1[1].add_paragraph("")
            parag_linha1_col2.add_run("ALIMENTADOR").bold = True
            parag_linha1_col2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col3 = linha_1[2].add_paragraph("")
            parag_linha1_col3.add_run("TRECHO ISOLADO").bold = True
            parag_linha1_col3.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col4 = linha_1[3].add_paragraph("")
            parag_linha1_col4.add_run("POTENCIA TOTAL").bold = True
            parag_linha1_col4.alignment = WD_ALIGN_PARAGRAPH.CENTER

            setores = list()
            for setor in content["dados"]["setores_isolados"]:
                if content["dados"]["setores_isolados"].index(setor) != len(
                        content["dados"]["setores_isolados"]) - 1:
                    setores.append(str(setor + ", "))
                else:
                    setores.append(str(setor))

            linha_2 = table_isolamento.rows[1].cells
            linha_2[0].text = content["dados"]["setor_falta"]
            linha_2[1].text = content["dados"]["alimentador"]
            linha_2[2].text = setores
            linha_2[3].text = "(Nos de Carga)"

            for no in content["dados"]["nos_de_carga"].keys():
                linha_2[3].add_paragraph("{no}: {S} [kVA]".format(
                    no=no, S=content["dados"]["nos_de_carga"][no]))

            self.relatorio.save("relatorio_falta_" + self.agent.subestacao + ".docx")


        elif message.ontology == "R_04":
            # Dados de Recomposicao por mesma SE do Agente Controle
            content = json.loads(message.content)

            # Inicializa relatorio da secao
            self.agent.relatorio_rest_mesma = Document()

            self.agent.relatorio_rest_mesma.add_heading(
                "Relatorio de Restauracao (SE: " + self.agent.subestacao + ")", 0)

            self.agent.relatorio_rest_mesma.add_heading("Diagrama do Sistema de Distribuicao", level=1)

            pic1 = self.agent.relatorio_rest_mesma.add_picture('./rede/rede.png', width=Inches(2.5))
            parag_foto = self.agent.relatorio_rest_mesma.add_paragraph("(Fonte: XML)")
            parag_foto.alignment = WD_ALIGN_PARAGRAPH.CENTER

            self.agent.relatorio_rest_mesma.add_heading("Registro de Restauracao pela mesma SE", level=1)

            parag = self.agent.relatorio_rest_mesma.add_paragraph("Alimentador Colaborador: ", style="ListBullet")
            parag.add_run(content["alim_colab"]).bold = True

            table_rest = self.agent.relatorio_rest_mesma.add_table(rows=2, cols=2)
            table_rest.alignment = WD_TABLE_ALIGNMENT.CENTER

            linha_1 = table_rest.rows[0].cells
            parag_linha1_col1 = linha_1[0].add_paragraph("")
            parag_linha1_col1.add_run("TRECHO RESTAURADO").bold = True
            parag_linha1_col1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col2 = linha_1[1].add_paragraph("")
            parag_linha1_col2.add_run("POTENCIA TOTAL").bold = True
            parag_linha1_col2.alignment = WD_ALIGN_PARAGRAPH.CENTER

            linha_2 = table_rest.rows[1].cells

            setores = list()
            for setor in content["ramo_recomp"]:
                if content["ramo_recomp"].index(setor) == len(content["ramo_recomp"]) - 1:
                    setores.append(str(setor))
                else:
                    setores.append(str(setor + ", "))

            linha_2[0].text = setores

            linha_2[1].text = "(Nos de Carga)"
            for no in content["nos_de_carga"].keys():
                linha_2[1].add_paragraph("{no}: {S} [kVA]".format(
                    no=no, S=content["nos_de_carga"][no]))

            self.agent.relatorio_rest_mesma.save("relatorio_restauracao_" + self.agent.subestacao + ".docx")

        elif message.ontology == "R_05":
            pass
        # # Podas a serem recompostas
        # podas = pickle.loads(message.content)

        # for poda in podas:
        # 	print poda[0].keys()

        elif message.ontology == "R_06":
            content = json.loads(message.content)

            # Inicializa relatorio da secao
            self.agent.relatorio_rest = Document()

            self.agent.relatorio_rest.add_heading("Relatorio de Restauracao (SE: " + self.agent.subestacao + ")", 0)

            self.agent.relatorio_rest.add_heading("Diagrama do Sistema de Distribuicao", level=1)

            pic1 = self.agent.relatorio_rest.add_picture('./rede/rede.png', width=Inches(2.5))
            parag_foto = self.agent.relatorio_rest.add_paragraph("(Fonte: XML)")
            parag_foto.alignment = WD_ALIGN_PARAGRAPH.CENTER

            self.agent.relatorio_rest.add_heading("Registro de Restauracao", level=1)

            table_rest = self.agent.relatorio_rest.add_table(rows=2, cols=2)
            table_rest.alignment = WD_TABLE_ALIGNMENT.CENTER

            linha_1 = table_rest.rows[0].cells
            parag_linha1_col1 = linha_1[0].add_paragraph("")
            parag_linha1_col1.add_run("TRECHO RESTAURADO").bold = True
            parag_linha1_col1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col2 = linha_1[1].add_paragraph("")
            parag_linha1_col2.add_run("POTENCIA TOTAL").bold = True
            parag_linha1_col2.alignment = WD_ALIGN_PARAGRAPH.CENTER

            linha_2 = table_rest.rows[1].cells

            setores = list()
            for setor in content["ramo"]:
                if content["ramo"].index(setor) == len(content["ramo"]) - 1:
                    setores.append(str(setor))
                else:
                    setores.append(str(setor + ", "))

            linha_2[0].text = setores

            linha_2[1].text = "(Nos de Carga)"
            for no in content["nos_de_carga"].keys():
                linha_2[1].add_paragraph("{no}: {S} [kVA]".format(
                    no=no, S=content["nos_de_carga"][no]))

            # Faz requerimento ao Agente Diagnostico Correspondente
            # dos dados de restauracao
            messag_dados = ACLMessage(ACLMessage.REQUEST)
            messag_dados.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            messag_dados.set_content(json.dumps(content))
            messag_dados.set_ontology("R_07")
            messag_dados.add_receiver(AID(str(self.agent.subestacao + '_ADiag')))

            comp_requisicao = CompRequest2(self.agent, messag_dados)
            self.agent.behaviours.append(comp_requisicao)
            comp_requisicao.on_start()

            # Salva relatorio de restauracao
            self.agent.relatorio_rest.save("relatorio_restauracao_" + self.agent.subestacao + ".docx")

class CompRequest2(FipaRequestProtocol):
    def __init__(self, agent, message):
        super(CompRequest2, self).__init__(
            agent=agent, message=message, is_initiator=True)

    def handle_inform(self, message):
        content = json.loads(message.content)

        for item in content.keys():

            self.agent.relatorio_rest.add_page_break()

            parag = self.agent.relatorio_rest.add_paragraph("Registro de Tentativas para o Trecho:",
                                                            style="ListBullet")

            table = self.agent.relatorio_rest.add_table(rows=1, cols=4)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            linha_1 = table.rows[0].cells
            parag_linha1_col1 = linha_1[0].add_paragraph("")
            parag_linha1_col1.add_run("TRECHO TENTATIVA").bold = True
            parag_linha1_col1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col2 = linha_1[1].add_paragraph("")
            parag_linha1_col2.add_run("CARREG CONDUTORES").bold = True
            parag_linha1_col2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col3 = linha_1[2].add_paragraph("")
            parag_linha1_col3.add_run("NIVEL TENSAO").bold = True
            parag_linha1_col3.alignment = WD_ALIGN_PARAGRAPH.CENTER
            parag_linha1_col4 = linha_1[3].add_paragraph("")
            parag_linha1_col4.add_run("CARREG SUBESTACAO").bold = True
            parag_linha1_col4.alignment = WD_ALIGN_PARAGRAPH.CENTER

            i = 1
            for item2 in content[item]["tentativas"].keys():
                if item2 != []:
                    table.add_row()

                    linha = table.rows[i].cells

                    linha[0].text = item2

                    if content[item]["tentativas"][item2]["carreg_cond"] is None:
                        linha[1].text = "\t------"
                    else:
                        linha[1].text = str(content[item]["tentativas"][item2]["carreg_cond"])

                    if content[item]["tentativas"][item2]["nivel_tensao"] is None:
                        linha[2].text = "\t------"
                    else:
                        linha[2].text = "No: {no}, {tensao}".format(
                            no=content[item]["tentativas"][item2]["nivel_tensao"][0],
                            tensao=str(content[item]["tentativas"][item2]["nivel_tensao"][1]))

                    linha[3].text = "{carreg}  %".format(carreg=content[item]["tentativas"][item2]["carreg_SE"])
                    i += 1

            self.agent.relatorio_rest.save("relatorio_restauracao_" + self.agent.subestacao + ".docx")

class AgenteDC(AgenteSMAD):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, subestacao, debug)
        self.behaviours.append(EnviarComando(self))
        display_message(self.aid.name, "Agente instanciado")

    def enviar_comando_de_chave(self, switching_command: swc.SwitchingCommand, acom_aid: AID):
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
                self.call_later(5.0, later)
        later()



    #Continuacao do codigo do Tiago recebe requisições e corrige descoordenação
    def handle_request(self, message):
        display_message(self.agent.aid.name, "Mensagem REQUEST Recebida")
        # Mensagem para operar correcao de descoordenacao
        if message.ontology == "R_02": #***Como vai ficar essa mensagem???***
            # Carrega conteudo da mensagem desta ontologia
            content = json.loads(message.content)
            # Cria um reply para prosseguir protocolo Request
            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.INFORM)
            content2 = dict()
            content2["chave_falta"] = content["dados"]["chave_falta"]
            resposta.set_ontology("R_02") #apllicar nova forma de mensagem
            # print(content2)
            # Indica inicio da Correcao
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
                                    "Isolando trecho sob Falta [CH:{CH}]".format(
                                        CH=content["dados"]["correc_descoord"]))
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
                            if chave in self.agent.enderecos_IEDs.keys():
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

            # Envia resposta do FIPA Request
            resposta.set_content(json.dumps(content2))
            self.agent.send(resposta)

        # Mensagem para operar isolamento de trecho
        elif message.ontology == "R_03":
            # Carrega conteudo da mensagem
            content = json.loads(message.content)

            # Cria reply para prosseguir protocolo
            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.INFORM)

            # Indica inicio da analise
            display_message(self.agent.aid.name, "Iniciando Isolamento de Trecho")

            # Para todas as chaves que devem ser
            # operadas no pacote de dados, chama a
            # funcao de operacao de chave
            for chave in content["dados"]["chaves"]:

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

            # Envia INFORM resposta
            resposta.set_content(json.dumps(content))
            self.agent.send(resposta)


        # Mensagem para restauracao de ramo
        # pela mesma SE
        elif message.ontology == "R_04":
            # Carrega conteudo da mensagem
            content = json.loads(message.content)

            # Cria reply para prosseguir protocolo
            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.INFORM)

            # Indica inicio da analise
            display_message(self.agent.aid.name,
                            "------------------------")
            display_message(self.agent.aid.name,
                            "Iniciando Restauracao do Ramo: {ram} pela mesma SE".format(ram=content["ramo_recomp"]))

            # Para cada chave indicada no pacote de dados
            # opera fechamento de chave
            for chave in content["chaves"]:
                if chave in self.agent.enderecos_IEDs.keys():
                    display_message(self.agent.aid.name,
                                    "Operando Chave [CH: {ch}]".format(ch=chave))
                    content["restaur_realiz"] = True
                # self.agent.operacao_chaves()

                else:
                    display_message(self.agent.aid.name,
                                    "Chave {ch} nao possui IP cadastrado".format(ch=chave))
                    content["restaur_realiz"] = False

            # Envia INFORM resposta
            resposta.set_content(json.dumps(content))
            self.agent.send(resposta)

            display_message(self.agent.aid.name, "------------------------")

        # Mensagem para restauracao de ramo
        # por outra SE
        elif message.ontology == "R_06":
            # Carrega conteudo da mensagem
            content = json.loads(message.content)

            # Cria reply para prosseguir protocolo
            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.INFORM)

            # Indica inicio da analise
            display_message(self.agent.aid.name,
                            "Iniciando Restauracao do Ramo: {ram}".format(ram=content["ramo"]))

            # Opera todas as chaves previstas no pacote
            for chave in content["chaves"]:
                if chave in self.agent.enderecos_IEDs.keys():
                    display_message(self.agent.aid.name,
                                    "Operando Chave [CH: {ch}]".format(ch=chave))
                    content["restaur_realiz"] = True
                # self.agent.operacao_chaves()

                else:
                    display_message(self.agent.aid.name,
                                    "Chave {ch} nao possui IP cadastrado".format(ch=chave))
                    content["restaur_realiz"] = False

            # Envia INFORM resposta
            resposta.set_content(json.dumps(content))
            self.agent.send(resposta)
