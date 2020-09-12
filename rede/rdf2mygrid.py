if __name__ == "__main__":
    import os
    os.sys.path.insert(0, os.getcwd())

from mygrid.rede import Subestacao, Alimentador, Setor, Chave
from mygrid.rede import Trecho, Barramento, NoDeCarga, Transformador, Condutor
from mygrid.util import Fasor
from xml.etree import ElementTree as ET
from rede.models.cim_profile.network_v1_8 import *
from si_prefix import si_parse
import numpy

def carregar_topologia(filename, subestacao=''):
    doc = DocumentCIMRDF()
    doc.fromfile(filename)
    resources = doc.resources

    chaves = _gerar_chaves(resources)
    nos = _gerar_nos_de_carga(resources)  # cargas
    setores = _gerar_setores(resources, nos)  # equipamentos entre chaves
    _associar_chaves_aos_setores(resources, chaves, setores)
    condutores = _gerar_condutores(resources)
    trechos = _gerar_trechos(resources, nos, chaves, condutores)
    alimentadores = _gerar_alimentadores(resources, setores, trechos, chaves, subestacao)
    transformadores = _gerar_transformadores(resources, subestacao)
    subestacoes = _gerar_subestacaoes(resources, alimentadores, transformadores, subestacao)

    if subestacao != '':
        return subestacoes[subestacao]
    else:   
        return subestacoes


def _gerar_chaves(resources):
    # Busca e instanciamento dos objetos do tipo Chave
    # print 'Gerando chaves...'
    chaves_rdf = filter(lambda res: isinstance(res, Switch), resources)
    chaves = dict()
    for chave in chaves_rdf:
        chave: Switch
        if chave.Switch_open == False:
            chaves[chave.IdentifiedObject_mRID] = Chave(
                nome=chave.IdentifiedObject_mRID, estado=1)
        elif chave.Switch_open == True:
            chaves[chave.IdentifiedObject_mRID] = Chave(
                nome=chave.IdentifiedObject_mRID, estado=0)
        # print 'Chave %s criada.' % chaves[chave['nome']].nome

    return chaves


def _gerar_nos_de_carga(resources):
    # Busca e instanciamento dos objetos do tipo NoDeCarga
    # print 'Gerando Nos de Carga...'
    def encontrar_vizinhos(no: EnergyConsumer):
        chaves_do_no = []
        vizinhos = []

        # Loop para o caso de barramentos com muitos terminais
        for terminal_do_no in no.ConductingEquipment_Terminals:
            cn_do_no = terminal_do_no.Terminal_ConnectivityNode
            
            # Segue por cada um dos trechos a partir do nó
            for terminal_inicial in cn_do_no.ConnectivityNode_Terminals:
                # Loop nos terminais de trechos
                if terminal_inicial is terminal_do_no:
                    # Ignora o terminal do próprio nó de carga
                    continue

                # Terminais a serem visitados até que se encontre um outro nó
                terminais_a_visitar = [terminal_inicial]

                # Ordenação de terminais
                ordem_de_elementos = [EnergyConsumer, BusbarSection, PowerTransformer, ACLineSegment, Switch]
                
                # Caminha ao longo da linha, até encontrar 
                while len(terminais_a_visitar):
                    terminais_a_visitar.sort(key=lambda t: ordem_de_elementos.index(t.Terminal_ConductingEquipment.__class__))
                    terminal_1 = terminais_a_visitar.pop(0)
                    equipamento = terminal_1.Terminal_ConductingEquipment
                    if isinstance(equipamento, Switch):
                        chaves_do_no.append(equipamento.IdentifiedObject_mRID)
                    if isinstance(equipamento, Switch) or isinstance(equipamento, ACLineSegment):
                        terminal_2 = [t for t in equipamento.ConductingEquipment_Terminals if t is not terminal_1][0]
                        cn_2 = terminal_2.Terminal_ConnectivityNode
                        if not cn_2:
                            continue
                        terminais_cn_2 = cn_2.ConnectivityNode_Terminals
                        terminais_a_visitar.extend([t for t in terminais_cn_2 if t is not terminal_2])
                        continue
                    if isinstance(equipamento, BusbarSection) or isinstance(equipamento, EnergyConsumer):
                        vizinhos.append(equipamento.IdentifiedObject_mRID)
                    break

        return chaves_do_no, vizinhos

    nos_rdf = filter(lambda res: any(isinstance(res, dtype)
                                     for dtype in (EnergyConsumer, BusbarSection)), resources)
    nos = dict()

    for no in nos_rdf:
        chaves_do_no, vizinhos = encontrar_vizinhos(no)

        if isinstance(no, EnergyConsumer):
            active_value, active_multiplier = no.EnergyConsumer_p.ActivePower_value, no.EnergyConsumer_p.ActivePower_multiplier.value
            active_multiplier = '' if active_multiplier == 'none' else active_multiplier
            reactive_value, reactive_multiplier = no.EnergyConsumer_q.ReactivePower_value, no.EnergyConsumer_q.ReactivePower_multiplier.value
            reactive_multiplier = '' if reactive_multiplier == 'none' else reactive_multiplier
            potencia_ativa = si_parse(str(active_value)+active_multiplier)
            potencia_reativa = si_parse(str(reactive_value)+reactive_multiplier)
        elif isinstance(no, BusbarSection):
            potencia_ativa = 0
            potencia_reativa = 0

        nos[no.IdentifiedObject_mRID] = NoDeCarga(nome=no.IdentifiedObject_mRID,
                                                  vizinhos=vizinhos,
                                                  potencia=Fasor(real=potencia_ativa,
                                                                 imag=potencia_reativa,
                                                                 tipo=Fasor.Potencia),
                                                  chaves=chaves_do_no)
        # print 'NoDeCarga %s criado.' % nos[no_tag['nome']].nome
    return nos


def _gerar_setores(resources, nos):
    # Busca e instanciamento dos objetos do tipo Setor
    # print 'Gerando Setores...'
    setores_rdf = list(filter(lambda res: isinstance(res, TopologicalNode), resources))
    setores = dict()

    def chaves_e_nos(setor):
        cn_equipments = [[terminal.Terminal_ConductingEquipment for terminal in cn.ConnectivityNode_Terminals]
                         for cn in setor.TopologicalNode_ConnectivityNodes]
        equipments = set(item for sublist in cn_equipments for item in sublist)
        chaves = list(filter(lambda eq: isinstance(eq, Switch), equipments))
        nos = list(filter(lambda eq: isinstance(eq, EnergyConsumer)
                          or isinstance(eq, BusbarSection), equipments))
        return chaves, nos

    for setor in setores_rdf:
        setor: TopologicalNode
        chaves, nos_do_setor = chaves_e_nos(setor)

        nomes_nos_do_setor = list(map(lambda no: no.IdentifiedObject_mRID, nos_do_setor))
        mygrid_nos_do_setor = [no for no in nos.values() if no.nome in nomes_nos_do_setor]
        
        vizinhos_do_setor = []
        for setor_2 in setores_rdf:
            if setor is setor_2:
                continue
            chaves_2, _ = chaves_e_nos(setor_2)
            if any(ch2 in chaves for ch2 in chaves_2):
                vizinhos_do_setor.append(setor_2.IdentifiedObject_mRID)

        setores[setor.IdentifiedObject_mRID] = Setor(nome=setor.IdentifiedObject_mRID,
                                    vizinhos=vizinhos_do_setor,
                                    nos_de_carga=mygrid_nos_do_setor)

    return setores


def _associar_chaves_aos_setores(resources, chaves, setores):
    # Associação das chaves aos setores
    for chave in chaves.values():
        chave_resource: Switch
        chave_resource = next(filter(lambda switch: isinstance(switch, Switch) and switch.IdentifiedObject_mRID == chave.nome, resources))
        for terminal in chave_resource.ConductingEquipment_Terminals:
            # Cada terminal da chave
            cn_terminal = terminal.Terminal_ConnectivityNode
            if not cn_terminal:
                continue
            nome_setor = cn_terminal.ConnectivityNode_TopologicalNode.IdentifiedObject_mRID
            if terminal.Terminal_sequenceNumber == 1:
                chave.n1 = setores[nome_setor]
            elif terminal.Terminal_sequenceNumber == 2:
                chave.n2 = setores[nome_setor]


def _gerar_condutores(resources):
    # Busca e instanciamento dos objetos do tipo Condutor
    # print 'Gerando Condutores...'
    condutores_rdf_perlength = filter(lambda res: isinstance(res, PerLengthSequenceImpedance), resources)
    condutores = dict()

    for condutor in condutores_rdf_perlength:
        condutor: PerLengthSequenceImpedance
        nome = condutor.IdentifiedObject_mRID
        multi = condutor.PerLengthSequenceImpedance_r.ResistancePerLength_multiplier.value
        multi = '' if multi == 'none' else multi
        rp = si_parse(str(condutor.PerLengthSequenceImpedance_r.ResistancePerLength_value)+multi)
        multi = condutor.PerLengthSequenceImpedance_r0.ResistancePerLength_multiplier.value
        multi = '' if multi == 'none' else multi
        rz = si_parse(str(condutor.PerLengthSequenceImpedance_r0.ResistancePerLength_value)+multi)
        multi = condutor.PerLengthSequenceImpedance_x.ReactancePerLength_multiplier.value
        multi = '' if multi == 'none' else multi
        xp = si_parse(str(condutor.PerLengthSequenceImpedance_x.ReactancePerLength_value)+multi)
        multi = condutor.PerLengthSequenceImpedance_x0.ReactancePerLength_multiplier.value
        multi = '' if multi == 'none' else multi
        xz = si_parse(str(condutor.PerLengthSequenceImpedance_x0.ReactancePerLength_value)+multi)
        
        condutor_limitset: OperationalLimitSet = next(filter(lambda res: isinstance(res, OperationalLimitSet) and res.IdentifiedObject_mRID == nome, resources))
        ampacidade: CurrentLimit = condutor_limitset.OperationalLimitSet_OperationalLimitValue[0]
        multi = ampacidade.CurrentLimit_value.CurrentFlow_multiplier.value
        multi = '' if multi == 'none' else multi
        ampacidade = si_parse(str(ampacidade.CurrentLimit_value.CurrentFlow_value)+multi)
        
        condutores[nome] = Condutor(nome=nome,
                                                    rp=rp,
                                                    xp=xp,
                                                    rz=rz,
                                                    xz=xz,
                                                    ampacidade=ampacidade)

    return condutores


def _gerar_trechos(resources, nos, chaves, condutores):
    # Busca e instanciamento dos objetos do tipo Alimentador
    # print 'Gerando Trechos...'
    trechos_rdf = filter(lambda res: isinstance(res, ACLineSegment), resources)
    trechos = dict()

    for trecho in trechos_rdf:
        trecho: ACLineSegment
        nome = trecho.IdentifiedObject_mRID
        condutor = condutores[trecho.ACLineSegment_PerLengthImpedance.IdentifiedObject_mRID]
        multiplicador = trecho.Conductor_length.Length_multiplier.value
        multiplicador = '' if multiplicador == 'none' else multiplicador
        comprimento = si_parse(str(trecho.Conductor_length.Length_value)+multiplicador)
        for terminal in trecho.ConductingEquipment_Terminals:
            cn = terminal.Terminal_ConnectivityNode
            next_cn_terminals = filter(lambda term: id(term) != id(terminal), cn.ConnectivityNode_Terminals)
            next_equipments = map(lambda term: term.Terminal_ConductingEquipment, next_cn_terminals)
            next_equipment = next(filter(lambda eq: not isinstance(eq, ACLineSegment), next_equipments))
            if isinstance(next_equipment, Switch):
                my_grid_equiment = chaves[next_equipment.IdentifiedObject_mRID]
            elif isinstance(next_equipment, EnergyConsumer) or isinstance(next_equipment, BusbarSection):
                my_grid_equiment = nos[next_equipment.IdentifiedObject_mRID]
            if terminal.Terminal_sequenceNumber == 1:
                n1 = my_grid_equiment
            elif terminal.Terminal_sequenceNumber == 2:
                n2 = my_grid_equiment

        trechos[nome] = Trecho(nome=nome,
                                             n1=n1,
                                             n2=n2,
                                             condutor=condutor,
                                             comprimento=comprimento)

    return trechos


def _gerar_alimentadores(resources, setores, trechos, chaves, se):
    # Busca e instanciamento dos objetos do tipo Alimentador
    # print 'Gerando Alimentadores...'
    alimentadores_rdf = filter(lambda res: isinstance(res, Feeder), resources)
    alimentadores = dict()    

    def chaves_e_trechos(setor):
        cn_equipments = [[terminal.Terminal_ConductingEquipment for terminal in cn.ConnectivityNode_Terminals]
                         for cn in setor.TopologicalNode_ConnectivityNodes]
        equipments = set(item for sublist in cn_equipments for item in sublist if not isinstance(item, BusbarSection))
        chaves = list(filter(lambda eq: isinstance(eq, Switch), equipments))
        trechos = list(filter(lambda eq: isinstance(eq, ACLineSegment), equipments))
        return chaves, trechos

    for alimentador in alimentadores_rdf:
        alimentador: Feeder
        subestacao = alimentador.Feeder_FeedingSubstation
        if subestacao and subestacao.IdentifiedObject_mRID != se and se != '':
            continue
        nome = alimentador.IdentifiedObject_mRID

        setores_rdf = alimentador.ConnectivityNodeContainer_TopologicalNode
        nomes_dos_setores = list(map(lambda setor: setor.IdentifiedObject_mRID, setores_rdf))
        
        nomes_das_chaves = set()
        nomes_dos_trechos = set()
        for setor in setores_rdf:
            chaves_do_setor, trechos_do_setor = chaves_e_trechos(setor)
            nomes_dos_trechos |= set(map(lambda line: line.IdentifiedObject_mRID, trechos_do_setor))
            if all(not isinstance(terminal.Terminal_ConductingEquipment, BusbarSection) for cn in setor.TopologicalNode_ConnectivityNodes for terminal in cn.ConnectivityNode_Terminals):
                # Não incluir os setores do barramento da subestação
                nomes_das_chaves |= set(map(lambda sw: sw.IdentifiedObject_mRID, chaves_do_setor))
       
        trechos_do_alimentador = [trecho for trecho in trechos.values() if trecho.nome in nomes_dos_trechos]
        setores_do_alimentador = [setor for setor in setores.values() if setor.nome in nomes_dos_setores]
        chaves_do_alimentador = [chave for chave in chaves.values() if chave.nome in nomes_das_chaves]

        barramento = next(busbar for busbar in resources if isinstance(busbar, BusbarSection) and busbar.Equipment_EquipmentContainer is subestacao)
        setor_raiz = barramento.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode.ConnectivityNode_TopologicalNode

        alimentadores[nome] = Alimentador(nome=nome,
                                            setores=setores_do_alimentador,
                                            trechos=trechos_do_alimentador,
                                            chaves=chaves_do_alimentador)
        alimentadores[nome].ordenar(raiz=setor_raiz.IdentifiedObject_mRID)

        alimentadores[nome].gerar_arvore_nos_de_carga()
            # print 'Alimentador %s criado.' % alimentadores[alimen_tag['nome']].nome
    return alimentadores


def _gerar_transformadores(resources, se):
    # Busca e instanciamento dos objetos do tipo Transformador
    # print 'Gerando Transformadores'

    transformadores_rdf = filter(lambda res: isinstance(res, PowerTransformer), resources)
    transformadores = dict()

    for transformador in transformadores_rdf:
        transformador: PowerTransformer
        subestacao = transformador.Equipment_EquipmentContainer.IdentifiedObject_mRID
        if subestacao != se and se != '':
            continue
        nome = transformador.IdentifiedObject_mRID

        for enrolamento in transformador.PowerTransformer_PowerTransformerEnd:
            valor, multi = enrolamento.PowerTransformerEnd_ratedU.Voltage_value, enrolamento.PowerTransformerEnd_ratedU.Voltage_multiplier.value
            tensao = si_parse(str(valor)+multi)
            if enrolamento.PowerTransformerEnd_endNumber == 1:
                tensao_primario = tensao

                valor, multi = enrolamento.PowerTransformerEnd_r.Resistance_value, enrolamento.PowerTransformerEnd_r.Resistance_multiplier.value
                multi = '' if multi == 'none' else multi
                resistencia = si_parse(str(valor)+multi)
                valor, multi = enrolamento.PowerTransformerEnd_x.Reactance_value, enrolamento.PowerTransformerEnd_x.Reactance_multiplier.value
                multi = '' if multi == 'none' else multi
                reatancia = si_parse(str(valor)+multi)

            elif enrolamento.PowerTransformerEnd_endNumber == 2:
                tensao_secundario = tensao
        
        valor, multi = enrolamento.PowerTransformerEnd_ratedS.ApparentPower_value, enrolamento.PowerTransformerEnd_ratedS.ApparentPower_multiplier.value
        potencia = si_parse(str(valor)+multi)

        transformadores[nome] = Transformador(nome=nome,
                                            tensao_primario=Fasor(mod=tensao_primario, ang=0.0,
                                                                    tipo=Fasor.Tensao),
                                            tensao_secundario=Fasor(mod=tensao_secundario, ang=0.0,
                                                                    tipo=Fasor.Tensao),
                                            potencia=Fasor(
                                                mod=potencia, ang=0.0, tipo=Fasor.Potencia),
                                            impedancia=Fasor(real=resistencia, imag=reatancia,
                                                            tipo=Fasor.Impedancia))
    return transformadores


def _gerar_subestacaoes(resources, alimentadores, transformadores, se):
    # Busca e instanciamento dos objetos do tipo Subestacao
    # print 'Gerando Subestações...'
    subestacoes_rdf = filter(lambda res: isinstance(res, Substation), resources)
    subestacoes = dict()

    for subestacao in subestacoes_rdf:
        subestacao: Substation
        nome = subestacao.IdentifiedObject_mRID
        if nome != se and se != '':
            continue

        alimentadores_da_subestacao = subestacao.Substation_SubstationFeeder
        alimentadores_da_subestacao = map(lambda ali: ali.IdentifiedObject_mRID, alimentadores_da_subestacao)
        alimentadores_da_subestacao = [alimentadores[ali]
                                       for ali in alimentadores_da_subestacao]

        trafos_da_subestacao = filter(lambda trf: isinstance(trf, PowerTransformer), subestacao.EquipmentContainer_Equipments)
        trafos_da_subestacao = map(lambda trf: trf.IdentifiedObject_mRID, trafos_da_subestacao)
        trafos_da_subestacao = [transformadores[trf] for trf in trafos_da_subestacao]

        subestacoes[nome] = Subestacao(nome=nome,
                                        alimentadores=alimentadores_da_subestacao,
                                        transformadores=trafos_da_subestacao,
                                        impedancia_equivalente_positiva=1+1j,
                                        impedancia_equivalente_zero=1+1j)
            # print 'Subestacao %s criada.' % subestacoes[sub_tag['nome']].nome
    return subestacoes


def poda_cim(poda: tuple):
    """Converte poda ao formato CIM"""
    setores, arvore_setores, rnp_setores, nos, arvore_nos, rnp_nos, chaves, trechos = poda
    
    # Setores
    topological_nodes = {}
    for nome, setor in setores.items():
        topological_nodes[nome] = TopologicalNode(
            IdentifiedObject_mRID=nome
        )

    # Chaves
    switches = {}
    for nome, chave in chaves.items():
        switches[nome] = Switch(
            IdentifiedObject_mRID=nome,
            Switch_open=(chave.estado == 0),
            ConductingEquipment_Terminals=[
                Terminal(Terminal_sequenceNumber=1),
                Terminal(Terminal_sequenceNumber=2)
            ]
        )

    # Trechos
    segments = {}
    for nome, trecho in trechos.items():
        segments[nome] = ACLineSegment(
            IdentifiedObject_mRID=nome, 
            ConductingEquipment_Terminals=[
                Terminal(Terminal_sequenceNumber=1),
                Terminal(Terminal_sequenceNumber=2)
            ],
            Conductor_length=Length(
                Length_value=str(trecho.comprimento),
                Length_multiplier=UnitMultiplier('none'),
                Length_unit=UnitSymbol('m')
            ),
            ACLineSegment_PerLengthImpedance=PerLengthSequenceImpedance(
                IdentifiedObject_mRID=trecho.condutor.nome, 
                PerLengthSequenceImpedance_r=ResistancePerLength(
                    ResistancePerLength_value=str(trecho.condutor.rp),
                    ResistancePerLength_multiplier=UnitMultiplier('none'),
                    ResistancePerLength_unit=UnitSymbol('ohmPerm')
                ), 
                PerLengthSequenceImpedance_r0=ResistancePerLength(
                    ResistancePerLength_value=str(trecho.condutor.rz),
                    ResistancePerLength_multiplier=UnitMultiplier('none'),
                    ResistancePerLength_unit=UnitSymbol('ohmPerm')
                ), 
                PerLengthSequenceImpedance_x=ReactancePerLength(
                    ReactancePerLength_value=str(trecho.condutor.xp),
                    ReactancePerLength_multiplier=UnitMultiplier('none'),
                    ReactancePerLength_unit=UnitSymbol('ohmPerm')
                ), 
                PerLengthSequenceImpedance_x0=ReactancePerLength(
                    ReactancePerLength_value=str(trecho.condutor.xz),
                    ReactancePerLength_multiplier=UnitMultiplier('none'),
                    ReactancePerLength_unit=UnitSymbol('ohmPerm')
                )
            ),
            Equipment_OperationalLimitSet=[
                OperationalLimitSet(
                    IdentifiedObject_mRID=trecho.condutor.nome,
                    OperationalLimitSet_OperationalLimitValue=[
                        CurrentLimit(
                            CurrentLimit_value=CurrentFlow(
                                CurrentFlow_value=str(trecho.condutor.ampacidade),
                                CurrentFlow_multiplier=UnitMultiplier('none'),
                                CurrentFlow_unit=UnitSymbol('A')
                            )
                        )
                    ]
                )
            ]
        )

    # Nos de carga
    energy_consumers = {}
    for nome, no in nos.items():
        energy_consumers[nome] = EnergyConsumer(
            IdentifiedObject_mRID=nome,
            ConductingEquipment_Terminals=[
                Terminal()
            ],
            EnergyConsumer_p=ActivePower(
                ActivePower_value=str(no.potencia.real),
                ActivePower_multiplier=UnitMultiplier('none'),
                ActivePower_unit=UnitSymbol('W')
            ),
            EnergyConsumer_q=ReactivePower(
                ReactivePower_value=str(no.potencia.imag),
                ReactivePower_multiplier=UnitMultiplier('none'),
                ReactivePower_unit=UnitSymbol('VAr')
            )
        )
   
    # Trechos <-( ConnectivityNode )-> Switch/EnergyConsumer
    for nome, segment in segments.items():
        trecho = trechos[nome]

        for i in [0, 1]:
            # n2 do trecho
            terminal_segmento = segment.ConductingEquipment_Terminals[i]
            equipamento = getattr(trecho, f'n{i+1}')
            equipamento_oposto = getattr(trecho, f'n{(i+1)%2+1}')
            
            if isinstance(equipamento, NoDeCarga):
                etype = NoDeCarga
                no = equipamento
                terminal_equipamento = energy_consumers[no.nome].ConductingEquipment_Terminals[0]
                cn_nome = no.nome
            elif isinstance(equipamento, Chave):
                etype = Chave
                chave = equipamento
                no = equipamento_oposto
                setor_ligado_pelo_trecho = no.setor
                if chave.n1 and setor_ligado_pelo_trecho == chave.n1.nome:
                    terminal_equipamento = switches[chave.nome].ConductingEquipment_Terminals[0]
                    cn_nome = chave.nome + '_1'
                elif chave.n2 and setor_ligado_pelo_trecho == chave.n2.nome:
                    terminal_equipamento = switches[chave.nome].ConductingEquipment_Terminals[1]
                    cn_nome = chave.nome + '_2'

            if etype == NoDeCarga and energy_consumers[no.nome].ConductingEquipment_Terminals[0].Terminal_ConnectivityNode:
                # Captura o ConnectivityNode do EnergyConsumer
                cn = terminal_equipamento.Terminal_ConnectivityNode
                terminal_segmento.Terminal_ConnectivityNode = cn
            else:
                # Cria um novo ConnectivityNode
                cn = ConnectivityNode(
                    IdentifiedObject_mRID=cn_nome,
                    ConnectivityNode_TopologicalNode=topological_nodes[no.setor],
                    ConnectivityNode_Terminals=[
                        terminal_segmento,
                        terminal_equipamento
                    ]
                )


    doc = DocumentCIMRDF()
    doc.add_recursively(cn)
    return doc.pack().getroot()


def cim_poda(poda_ET: ET.Element):
    """Converte CIM XML a uma poda"""
    doc = DocumentCIMRDF()
    doc.fromstring(ET.tostring(poda_ET))
    resources = doc.resources

    # Captura qualquer chave nas extremidades da poda
    chave_raiz = next(chave for chave in resources if isinstance(chave, Switch) and chave.Switch_open)
    chave_raiz.Switch_open = False # Fecha para que faça parte do Alimentador falso
    terminal_nulo_chave_raiz = next(t for t in chave_raiz.ConductingEquipment_Terminals if t.Terminal_ConnectivityNode is None)
    terminal_chave_raiz = next(t for t in chave_raiz.ConductingEquipment_Terminals if t.Terminal_ConnectivityNode is not None)
    cn_chave_raiz = terminal_chave_raiz.Terminal_ConnectivityNode
    setor_raiz = cn_chave_raiz.ConnectivityNode_TopologicalNode
    trecho_raiz = next(t.Terminal_ConductingEquipment for t in cn_chave_raiz.ConnectivityNode_Terminals if isinstance(t.Terminal_ConductingEquipment, ACLineSegment))
    cn_no_de_carga_raiz = next(t.Terminal_ConnectivityNode for t in trecho_raiz.ConductingEquipment_Terminals if t.Terminal_ConnectivityNode is not cn_chave_raiz)
    no_de_carga_raiz = next(t.Terminal_ConductingEquipment for t in cn_no_de_carga_raiz.ConnectivityNode_Terminals if isinstance(t.Terminal_ConductingEquipment, EnergyConsumer))

    # Constroi uma topologia falsa que atualizará a informação da poda
    setor_falso = TopologicalNode(IdentifiedObject_mRID='alimentador')
    barramento_falso = BusbarSection(
        IdentifiedObject_mRID='barramento_falso'
    )
    terminal_barramento_falso = Terminal(
        Terminal_sequenceNumber=1, 
        Terminal_ConductingEquipment=barramento_falso)
    cn_falso = ConnectivityNode(
        IdentifiedObject_mRID='cn_barramento_falso',
        ConnectivityNode_Terminals=[terminal_barramento_falso],
        ConnectivityNode_TopologicalNode=setor_falso
    )
    terminal_trecho_falso_1 = Terminal(
        Terminal_sequenceNumber=1, 
        Terminal_ConnectivityNode=cn_falso)
    trecho_falso = ACLineSegment(
        IdentifiedObject_mRID='trecho_falso',
        ACLineSegment_PerLengthImpedance=trecho_raiz.ACLineSegment_PerLengthImpedance, 
        Conductor_length=trecho_raiz.Conductor_length,
        ConductingEquipment_Terminals=[terminal_trecho_falso_1],
        Equipment_OperationalLimitSet=trecho_raiz.Equipment_OperationalLimitSet
        )
    terminal_trecho_falso_2 = Terminal(
        Terminal_sequenceNumber=2,
        Terminal_ConductingEquipment=trecho_falso
    )
    cn_falso_2 = ConnectivityNode(
        IdentifiedObject_mRID='cn_chave_falso',
        ConnectivityNode_Terminals=[terminal_trecho_falso_2, terminal_nulo_chave_raiz],
        ConnectivityNode_TopologicalNode=setor_falso
    )
    alimentador_falso = Feeder(
        IdentifiedObject_mRID='alimentador_falso',
        ConnectivityNodeContainer_TopologicalNode=[setor_falso] + [setor for setor in resources if isinstance(setor, TopologicalNode)]
    )
    doc.add_recursively(alimentador_falso)

    chaves = _gerar_chaves(resources)
    nos = _gerar_nos_de_carga(resources)  # cargas
    setores = _gerar_setores(resources, nos)  # equipamentos entre chaves
    _associar_chaves_aos_setores(resources, chaves, setores)
    condutores = _gerar_condutores(resources)
    trechos = _gerar_trechos(resources, nos, chaves, condutores)
    alimentadores = _gerar_alimentadores(resources, setores, trechos, chaves, '')

    # Reconstroi a poda original, com todos os campos preenchidos
    poda = alimentadores['alimentador_falso'].podar(setor_raiz.IdentifiedObject_mRID, True)

    return poda

if __name__ == '__main__':
    from pprint import pprint
    import pickle
    
    poda_string = b'\x80\x03(}q\x00(X\x01\x00\x00\x00Jq\x01cmygrid.rede\nSetor\nq\x02)\x81q\x03}q\x04(X\x04\x00\x00\x00nomeq\x05h\x01X\n\x00\x00\x00prioridadeq\x06K\x00X\x08\x00\x00\x00vizinhosq\x07]q\x08(X\x01\x00\x00\x00Gq\tX\x01\x00\x00\x00Iq\nX\x01\x00\x00\x00Lq\x0beX\x0e\x00\x00\x00rnp_associadasq\x0c}q\r(h\tcmygrid.rede\nNoDeCarga\nq\x0e)\x81q\x0f}q\x10(h\x05X\x02\x00\x00\x00G1q\x11h\x07]q\x12(X\x02\x00\x00\x00H1q\x13X\x02\x00\x00\x00S1q\x14X\x02\x00\x00\x00J1q\x15eX\x08\x00\x00\x00potenciaq\x16cmygrid.util\nFasor\nq\x17)\x81q\x18}q\x19(X\x0c\x00\x00\x00_Fasor__tipoq\x1aK\x03X\x0c\x00\x00\x00_Fasor__baseq\x1bNX\n\x00\x00\x00_Fasor__puq\x1cNX\x0c\x00\x00\x00_Fasor__realq\x1dGA;\xd9\x92\x00\x00\x00\x00X\x0c\x00\x00\x00_Fasor__imagq\x1eGA;\xd9\x92\x00\x00\x00\x00X\x0b\x00\x00\x00_Fasor__modq\x1fcnumpy.core.multiarray\nscalar\nq cnumpy\ndtype\nq!X\x02\x00\x00\x00f8q"\x89\x88\x87q#Rq$(K\x03X\x01\x00\x00\x00<q%NNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00tq&bC\x08\xe7\x1cu\x15^\xb1CAq\'\x86q(Rq)X\x0b\x00\x00\x00_Fasor__angq*h h$C\x08\x00\x00\x00\x00\x00\x80F@q+\x86q,Rq-ubX\x0b\x00\x00\x00potencia_eqq.h\x17)\x81q/}q0(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q1\x86q2Rq3h*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q4\x86q5Rq6ubX\x06\x00\x00\x00tensaoq7h\x17)\x81q8}q9(h\x1aK\x00h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q:\x86q;Rq<h*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q=\x86q>Rq?ubX\x06\x00\x00\x00chavesq@]qA(X\x04\x00\x00\x00CH10qBX\x03\x00\x00\x00CH9qCX\x04\x00\x00\x00CH19qDeX\x05\x00\x00\x00setorqEh\tubcnumpy.core.multiarray\n_reconstruct\nqFcnumpy\nndarray\nqGK\x00\x85qHC\x01bqI\x87qJRqK(K\x01K\x02K\x01\x86qLh!X\x03\x00\x00\x00U21qM\x89\x88\x87qNRqO(K\x03h%NNNKTK\x04K\x08tqPb\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00J\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00qQtqRb\x86qSh\nh\x0e)\x81qT}qU(h\x05X\x02\x00\x00\x00I1qVh\x07]qW(h\x15h\x14eh\x16h\x17)\x81qX}qY(h\x1aK\x03h\x1bNh\x1cNh\x1dGAE#\x9f\x00\x00\x00\x00h\x1eGAE#\x9f\x00\x00\x00\x00h\x1fh h$C\x08`O-\x1d0\xe5MAqZ\x86q[Rq\\h*h h$C\x08\x00\x00\x00\x00\x00\x80F@q]\x86q^Rq_ubh.h\x17)\x81q`}qa(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00qb\x86qcRqdh*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00qe\x86qfRqgubh7h8h@]qh(X\x04\x00\x00\x00CH14qiX\x04\x00\x00\x00CH13qjehEh\nubhFhGK\x00\x85qkhI\x87qlRqm(K\x01K\x02K\x01\x86qnh!X\x03\x00\x00\x00U21qo\x89\x88\x87qpRqq(K\x03h%NNNKTK\x04K\x08tqrb\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00J\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00qstqtb\x86quh\x0bh\x0e)\x81qv}qw(h\x05X\x02\x00\x00\x00L1qxh\x07]qy(X\x02\x00\x00\x00M1qzh\x15eh\x16h\x17)\x81q{}q|(h\x1aK\x03h\x1bNh\x1cNh\x1dGA9\xd67\x00\x00\x00\x00h\x1eGA9\xd67\x00\x00\x00\x00h\x1fh h$C\x08\xc2\x19q\xc7\xf4DBAq}\x86q~Rq\x7fh*h h$C\x08\x00\x00\x00\x00\x00\x80F@q\x80\x86q\x81Rq\x82ubh.h\x17)\x81q\x83}q\x84(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q\x85\x86q\x86Rq\x87h*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q\x88\x86q\x89Rq\x8aubh7h8h@]q\x8b(X\x04\x00\x00\x00CH16q\x8cX\x04\x00\x00\x00CH15q\x8dehEh\x0bubhFhGK\x00\x85q\x8ehI\x87q\x8fRq\x90(K\x01K\x02K\x01\x86q\x91h!X\x03\x00\x00\x00U21q\x92\x89\x88\x87q\x93Rq\x94(K\x03h%NNNKTK\x04K\x08tq\x95b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00J\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00q\x96tq\x97b\x86q\x98uX\x0c\x00\x00\x00nos_de_cargaq\x99}q\x9ah\x15h\x0e)\x81q\x9b}q\x9c(h\x05h\x15h\x07]q\x9d(hxhVh\x11eh\x16h\x17)\x81q\x9e}q\x9f(h\x1aK\x03h\x1bNh\x1cNh\x1dGA,/x\x00\x00\x00\x00h\x1eGA,/x\x00\x00\x00\x00h\x1fh h$C\x08\x90\xdf\xa7\\\x1b\xee3Aq\xa0\x86q\xa1Rq\xa2h*h h$C\x08\x00\x00\x00\x00\x00\x80F@q\xa3\x86q\xa4Rq\xa5ubh.h\x17)\x81q\xa6}q\xa7(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q\xa8\x86q\xa9Rq\xaah*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q\xab\x86q\xacRq\xadubh7h8h@]q\xae(h\x8dhihDehEh\x01ubsX\r\x00\x00\x00no_de_ligacaoq\xafhTX\x05\x00\x00\x00dtypeq\xb0cbuiltins\nstr\nq\xb1X\x06\x00\x00\x00arvoreq\xb2}q\xb3h\x15]q\xb4sX\x04\x00\x00\x00raizq\xb5h\x15X\x07\x00\x00\x00_arvoreq\xb6NX\x10\x00\x00\x00arestas_reservasq\xb7]q\xb8X\x03\x00\x00\x00rnpq\xb9hmubh\x0bh\x02)\x81q\xba}q\xbb(h\x05h\x0bh\x06K\x00h\x07]q\xbc(h\x01X\x01\x00\x00\x00Mq\xbdeh\x0c}q\xbe(h\x01h\x9bhFhGK\x00\x85q\xbfhI\x87q\xc0Rq\xc1(K\x01K\x02K\x01\x86q\xc2h!X\x03\x00\x00\x00U21q\xc3\x89\x88\x87q\xc4Rq\xc5(K\x03h%NNNKTK\x04K\x08tq\xc6b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00q\xc7tq\xc8b\x86q\xc9h\xbdh\x0e)\x81q\xca}q\xcb(h\x05hzh\x07]q\xcc(X\x02\x00\x00\x00N1q\xcdhxeh\x16h\x17)\x81q\xce}q\xcf(h\x1aK\x03h\x1bNh\x1cNh\x1dGA=\xdd\x00\x00\x00\x00\x00h\x1eGA=\xdd\x00\x00\x00\x00\x00h\x1fh h$C\x08\xe6,\xd7\xd2\xd4\x1dEAq\xd0\x86q\xd1Rq\xd2h*h h$C\x08\x00\x00\x00\x00\x00\x80F@q\xd3\x86q\xd4Rq\xd5ubh.h\x17)\x81q\xd6}q\xd7(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q\xd8\x86q\xd9Rq\xdah*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00q\xdb\x86q\xdcRq\xddubh7h8h@]q\xde(X\x04\x00\x00\x00CH17q\xdfh\x8cehEh\xbdubhFhGK\x00\x85q\xe0hI\x87q\xe1Rq\xe2(K\x01K\x02K\x01\x86q\xe3h!X\x03\x00\x00\x00U21q\xe4\x89\x88\x87q\xe5Rq\xe6(K\x03h%NNNKTK\x04K\x08tq\xe7b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00q\xe8tq\xe9b\x86q\xeauh\x99}q\xebhxhvsh\xafh\x9bh\xb0h\xb1h\xb2}q\xechx]q\xedsh\xb5hxh\xb6Nh\xb7]q\xeeh\xb9h\xc1ubu}q\xef(h h!X\x02\x00\x00\x00U1q\xf0\x89\x88\x87q\xf1Rq\xf2(K\x03h%NNNK\x04K\x04K\x08tq\xf3bC\x04J\x00\x00\x00q\xf4\x86q\xf5Rq\xf6]q\xf7h\x0bah h!X\x02\x00\x00\x00U1q\xf8\x89\x88\x87q\xf9Rq\xfa(K\x03h%NNNK\x04K\x04K\x08tq\xfbbC\x04L\x00\x00\x00q\xfc\x86q\xfdRq\xfe]q\xffh\x01auhFhGK\x00\x85r\x00\x01\x00\x00hI\x87r\x01\x01\x00\x00Rr\x02\x01\x00\x00(K\x01K\x02K\x02\x86r\x03\x01\x00\x00h!X\x03\x00\x00\x00U21r\x04\x01\x00\x00\x89\x88\x87r\x05\x01\x00\x00Rr\x06\x01\x00\x00(K\x03h%NNNKTK\x04K\x08tr\x07\x01\x00\x00b\x89BP\x01\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00J\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r\x08\x01\x00\x00tr\t\x01\x00\x00b}r\n\x01\x00\x00(h\x15h\x9bhxhvu}r\x0b\x01\x00\x00(h h!X\x02\x00\x00\x00U2r\x0c\x01\x00\x00\x89\x88\x87r\r\x01\x00\x00Rr\x0e\x01\x00\x00(K\x03h%NNNK\x08K\x04K\x08tr\x0f\x01\x00\x00bC\x08J\x00\x00\x001\x00\x00\x00r\x10\x01\x00\x00\x86r\x11\x01\x00\x00Rr\x12\x01\x00\x00]r\x13\x01\x00\x00h h!X\x02\x00\x00\x00U2r\x14\x01\x00\x00\x89\x88\x87r\x15\x01\x00\x00Rr\x16\x01\x00\x00(K\x03h%NNNK\x08K\x04K\x08tr\x17\x01\x00\x00bC\x08L\x00\x00\x001\x00\x00\x00r\x18\x01\x00\x00\x86r\x19\x01\x00\x00Rr\x1a\x01\x00\x00ah h!X\x02\x00\x00\x00U2r\x1b\x01\x00\x00\x89\x88\x87r\x1c\x01\x00\x00Rr\x1d\x01\x00\x00(K\x03h%NNNK\x08K\x04K\x08tr\x1e\x01\x00\x00bC\x08L\x00\x00\x001\x00\x00\x00r\x1f\x01\x00\x00\x86r \x01\x00\x00Rr!\x01\x00\x00]r"\x01\x00\x00h\x15auhFhGK\x00\x85r#\x01\x00\x00hI\x87r$\x01\x00\x00Rr%\x01\x00\x00(K\x01K\x02K\x02\x86r&\x01\x00\x00h!X\x03\x00\x00\x00U21r\'\x01\x00\x00\x89\x88\x87r(\x01\x00\x00Rr)\x01\x00\x00(K\x03h%NNNKTK\x04K\x08tr*\x01\x00\x00b\x89BP\x01\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00J\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r+\x01\x00\x00tr,\x01\x00\x00b}r-\x01\x00\x00(h\x8ccmygrid.rede\nChave\nr.\x01\x00\x00)\x81r/\x01\x00\x00}r0\x01\x00\x00(h\x05h\x8cX\x06\x00\x00\x00estador1\x01\x00\x00K\x00X\x02\x00\x00\x00n1r2\x01\x00\x00h\x02)\x81r3\x01\x00\x00}r4\x01\x00\x00(h\x05h\xbdh\x06K\x00h\x07]r5\x01\x00\x00(X\x01\x00\x00\x00Nr6\x01\x00\x00h\x0beh\x0c}r7\x01\x00\x00(j6\x01\x00\x00Nh\x0bNuh\x99}r8\x01\x00\x00hzh\xcash\xafNh\xb0h\xb1h\xb2}r9\x01\x00\x00hz]r:\x01\x00\x00sh\xb5Nh\xb6Nh\xb7]r;\x01\x00\x00ubX\x02\x00\x00\x00n2r<\x01\x00\x00h\xbaubh\x8dj.\x01\x00\x00)\x81r=\x01\x00\x00}r>\x01\x00\x00(h\x05h\x8dj1\x01\x00\x00K\x01j<\x01\x00\x00h\xbaj2\x01\x00\x00h\x03ubhij.\x01\x00\x00)\x81r?\x01\x00\x00}r@\x01\x00\x00(h\x05hij1\x01\x00\x00K\x00j<\x01\x00\x00h\x03j2\x01\x00\x00h\x02)\x81rA\x01\x00\x00}rB\x01\x00\x00(h\x05h\nh\x06K\x00h\x07]rC\x01\x00\x00(X\x02\x00\x00\x00S1rD\x01\x00\x00h\x01eh\x0c}rE\x01\x00\x00(jD\x01\x00\x00h\x0e)\x81rF\x01\x00\x00}rG\x01\x00\x00(h\x05h\x14h\x07]rH\x01\x00\x00(hVh\x11X\x02\x00\x00\x00E1rI\x01\x00\x00X\x02\x00\x00\x00A1rJ\x01\x00\x00eh\x16h\x17)\x81rK\x01\x00\x00}rL\x01\x00\x00(h\x1aK\x03h\x1bNh\x1cNh\x1dK\x00h\x1eK\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00rM\x01\x00\x00\x86rN\x01\x00\x00RrO\x01\x00\x00h*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00rP\x01\x00\x00\x86rQ\x01\x00\x00RrR\x01\x00\x00ubh.h\x17)\x81rS\x01\x00\x00}rT\x01\x00\x00(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00rU\x01\x00\x00\x86rV\x01\x00\x00RrW\x01\x00\x00h*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00rX\x01\x00\x00\x86rY\x01\x00\x00RrZ\x01\x00\x00ubh7h8h@]r[\x01\x00\x00(hjhCX\x03\x00\x00\x00CH6r\\\x01\x00\x00X\x03\x00\x00\x00CH1r]\x01\x00\x00ehEjD\x01\x00\x00ubhFhGK\x00\x85r^\x01\x00\x00hI\x87r_\x01\x00\x00Rr`\x01\x00\x00(K\x01K\x02K\x01\x86ra\x01\x00\x00h!X\x03\x00\x00\x00U21rb\x01\x00\x00\x89\x88\x87rc\x01\x00\x00Rrd\x01\x00\x00(K\x03h%NNNKTK\x04K\x08tre\x01\x00\x00b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00I\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00rf\x01\x00\x00trg\x01\x00\x00b\x86rh\x01\x00\x00h\x01h\x9bhFhGK\x00\x85ri\x01\x00\x00hI\x87rj\x01\x00\x00Rrk\x01\x00\x00(K\x01K\x02K\x01\x86rl\x01\x00\x00h!X\x03\x00\x00\x00U21rm\x01\x00\x00\x89\x88\x87rn\x01\x00\x00Rro\x01\x00\x00(K\x03h%NNNKTK\x04K\x08trp\x01\x00\x00b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00I\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00rq\x01\x00\x00trr\x01\x00\x00b\x86rs\x01\x00\x00uh\x99}rt\x01\x00\x00hVhTsh\xafjF\x01\x00\x00h\xb0h\xb1h\xb2}ru\x01\x00\x00hV]rv\x01\x00\x00sh\xb5hVh\xb6Nh\xb7]rw\x01\x00\x00h\xb9j`\x01\x00\x00ububhDj.\x01\x00\x00)\x81rx\x01\x00\x00}ry\x01\x00\x00(h\x05hDj1\x01\x00\x00K\x00j2\x01\x00\x00h\x02)\x81rz\x01\x00\x00}r{\x01\x00\x00(h\x05h\th\x06K\x00h\x07]r|\x01\x00\x00(jD\x01\x00\x00X\x01\x00\x00\x00Hr}\x01\x00\x00h\x01eh\x0c}r~\x01\x00\x00(jD\x01\x00\x00jF\x01\x00\x00hFhGK\x00\x85r\x7f\x01\x00\x00hI\x87r\x80\x01\x00\x00Rr\x81\x01\x00\x00(K\x01K\x02K\x01\x86r\x82\x01\x00\x00h!X\x03\x00\x00\x00U21r\x83\x01\x00\x00\x89\x88\x87r\x84\x01\x00\x00Rr\x85\x01\x00\x00(K\x03h%NNNKTK\x04K\x08tr\x86\x01\x00\x00b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r\x87\x01\x00\x00tr\x88\x01\x00\x00b\x86r\x89\x01\x00\x00j}\x01\x00\x00h\x0e)\x81r\x8a\x01\x00\x00}r\x8b\x01\x00\x00(h\x05h\x13h\x07]r\x8c\x01\x00\x00(X\x02\x00\x00\x00K2r\x8d\x01\x00\x00h\x11eh\x16h\x17)\x81r\x8e\x01\x00\x00}r\x8f\x01\x00\x00(h\x1aK\x03h\x1bNh\x1cNh\x1dGA4\xcd\xb4\x00\x00\x00\x00h\x1eGA4\xcd\xb4\x00\x00\x00\x00h\x1fh h$C\x08\x05J\x96|\xaek=Ar\x90\x01\x00\x00\x86r\x91\x01\x00\x00Rr\x92\x01\x00\x00h*h h$C\x08\x00\x00\x00\x00\x00\x80F@r\x93\x01\x00\x00\x86r\x94\x01\x00\x00Rr\x95\x01\x00\x00ubh.h\x17)\x81r\x96\x01\x00\x00}r\x97\x01\x00\x00(h\x1aK\x03h\x1bNh\x1cNh\x1dG\x00\x00\x00\x00\x00\x00\x00\x00h\x1eG\x00\x00\x00\x00\x00\x00\x00\x00h\x1fh h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00r\x98\x01\x00\x00\x86r\x99\x01\x00\x00Rr\x9a\x01\x00\x00h*h h$C\x08\x00\x00\x00\x00\x00\x00\x00\x00r\x9b\x01\x00\x00\x86r\x9c\x01\x00\x00Rr\x9d\x01\x00\x00ubh7h8h@]r\x9e\x01\x00\x00(X\x04\x00\x00\x00CH11r\x9f\x01\x00\x00hBehEj}\x01\x00\x00ubhFhGK\x00\x85r\xa0\x01\x00\x00hI\x87r\xa1\x01\x00\x00Rr\xa2\x01\x00\x00(K\x01K\x02K\x01\x86r\xa3\x01\x00\x00h!X\x03\x00\x00\x00U21r\xa4\x01\x00\x00\x89\x88\x87r\xa5\x01\x00\x00Rr\xa6\x01\x00\x00(K\x03h%NNNKTK\x04K\x08tr\xa7\x01\x00\x00b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r\xa8\x01\x00\x00tr\xa9\x01\x00\x00b\x86r\xaa\x01\x00\x00h\x01h\x9bhFhGK\x00\x85r\xab\x01\x00\x00hI\x87r\xac\x01\x00\x00Rr\xad\x01\x00\x00(K\x01K\x02K\x01\x86r\xae\x01\x00\x00h!X\x03\x00\x00\x00U21r\xaf\x01\x00\x00\x89\x88\x87r\xb0\x01\x00\x00Rr\xb1\x01\x00\x00(K\x03h%NNNKTK\x04K\x08tr\xb2\x01\x00\x00b\x89C\xa80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\x00\x00\x001\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r\xb3\x01\x00\x00tr\xb4\x01\x00\x00b\x86r\xb5\x01\x00\x00uh\x99}r\xb6\x01\x00\x00h\x11h\x0fsh\xafjF\x01\x00\x00h\xb0h\xb1h\xb2}r\xb7\x01\x00\x00h\x11]r\xb8\x01\x00\x00sh\xb5h\x11h\xb6Nh\xb7]r\xb9\x01\x00\x00h\xb9j\x81\x01\x00\x00ubj<\x01\x00\x00h\x03ubu}r\xba\x01\x00\x00(X\x06\x00\x00\x00J1CH15r\xbb\x01\x00\x00cmygrid.rede\nTrecho\nr\xbc\x01\x00\x00)\x81r\xbd\x01\x00\x00}r\xbe\x01\x00\x00(h\x05j\xbb\x01\x00\x00j2\x01\x00\x00h\x9bj<\x01\x00\x00j=\x01\x00\x00X\x0b\x00\x00\x00no_montanter\xbf\x01\x00\x00NX\n\x00\x00\x00no_jusanter\xc0\x01\x00\x00NX\x08\x00\x00\x00condutorr\xc1\x01\x00\x00cmygrid.rede\nCondutor\nr\xc2\x01\x00\x00)\x81r\xc3\x01\x00\x00}r\xc4\x01\x00\x00(h\x05X\t\x00\x00\x00CU 95 mm2r\xc5\x01\x00\x00X\x02\x00\x00\x00rpr\xc6\x01\x00\x00G?\xccS\x8e\xf3Mj\x16X\x02\x00\x00\x00xpr\xc7\x01\x00\x00G?\xda?\x14\x12\x05\xbc\x02X\x02\x00\x00\x00rzr\xc8\x01\x00\x00G?\xd9\x897K\xc6\xa7\xf0X\x02\x00\x00\x00xzr\xc9\x01\x00\x00G?\xf9;\xcd5\xa8XyX\n\x00\x00\x00ampacidader\xca\x01\x00\x00G@{`\x00\x00\x00\x00\x00ubX\x0b\x00\x00\x00comprimentor\xcb\x01\x00\x00G@\x8d\x88\x00\x00\x00\x00\x00ubX\x06\x00\x00\x00CH14J1r\xcc\x01\x00\x00j\xbc\x01\x00\x00)\x81r\xcd\x01\x00\x00}r\xce\x01\x00\x00(h\x05j\xcc\x01\x00\x00j2\x01\x00\x00j?\x01\x00\x00j<\x01\x00\x00h\x9bj\xbf\x01\x00\x00Nj\xc0\x01\x00\x00Nj\xc1\x01\x00\x00j\xc3\x01\x00\x00j\xcb\x01\x00\x00G@\x8d\x88\x00\x00\x00\x00\x00ubX\x06\x00\x00\x00CH19J1r\xcf\x01\x00\x00j\xbc\x01\x00\x00)\x81r\xd0\x01\x00\x00}r\xd1\x01\x00\x00(h\x05j\xcf\x01\x00\x00j2\x01\x00\x00jx\x01\x00\x00j<\x01\x00\x00h\x9bj\xbf\x01\x00\x00Nj\xc0\x01\x00\x00Nj\xc1\x01\x00\x00j\xc2\x01\x00\x00)\x81r\xd2\x01\x00\x00}r\xd3\x01\x00\x00(h\x05X\r\x00\x00\x00CCA 266.8 MCMr\xd4\x01\x00\x00j\xc6\x01\x00\x00G?\xce\x9a\xd4,<\x9e\xedj\xc7\x01\x00\x00G?\xd8@\xb7\x804m\xc6j\xc8\x01\x00\x00G?\xda\xae\xfb*\xae)tj\xc9\x01\x00\x00G?\xf8\xe5\x01\xe2XOLj\xca\x01\x00\x00G@}\xb0\x00\x00\x00\x00\x00ubj\xcb\x01\x00\x00GA.\x80\x98\x00\x00\x00\x00ubX\x06\x00\x00\x00L1CH16r\xd5\x01\x00\x00j\xbc\x01\x00\x00)\x81r\xd6\x01\x00\x00}r\xd7\x01\x00\x00(h\x05j\xd5\x01\x00\x00j2\x01\x00\x00hvj<\x01\x00\x00j/\x01\x00\x00j\xbf\x01\x00\x00Nj\xc0\x01\x00\x00Nj\xc1\x01\x00\x00j\xc3\x01\x00\x00j\xcb\x01\x00\x00G?\xf8\x00\x00\x00\x00\x00\x00ubX\x06\x00\x00\x00CH15L1r\xd8\x01\x00\x00j\xbc\x01\x00\x00)\x81r\xd9\x01\x00\x00}r\xda\x01\x00\x00(h\x05j\xd8\x01\x00\x00j2\x01\x00\x00j=\x01\x00\x00j<\x01\x00\x00hvj\xbf\x01\x00\x00Nj\xc0\x01\x00\x00Nj\xc1\x01\x00\x00j\xc3\x01\x00\x00j\xcb\x01\x00\x00G?\xf8\x00\x00\x00\x00\x00\x00ubutr\xdb\x01\x00\x00.'
    
    poda = pickle.loads(poda_string)
    etree = poda_cim(poda)


    poda_2 = cim_poda(etree)
    
    etree_2 = poda_cim(poda_2)
    pass
    # carregar_topologia('rede/models/rede-cim-2.xml')
