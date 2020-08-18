if __name__ == "__main__":
    import os
    os.sys.path.insert(0, os.getcwd())

from mygrid.rede import Subestacao, Alimentador, Setor, Chave
from mygrid.rede import Trecho, NoDeCarga, Transformador, Condutor
from mygrid.util import Fasor
from rede.network import *
from si_prefix import si_parse

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
        subestacao = alimentador.Feeder_FeedingSubstation.IdentifiedObject_mRID
        if subestacao != se and se != '':
            continue
        nome = alimentador.IdentifiedObject_mRID

        setores_rdf = alimentador.ConnectivityNodeContainer_TopologicalNode
        nomes_dos_setores = list(map(lambda setor: setor.IdentifiedObject_mRID, setores_rdf))
        
        nomes_das_chaves = set()
        nomes_dos_trechos = set()
        for setor in setores_rdf:
            chaves_do_setor, trechos_do_setor = chaves_e_trechos(setor)
            nomes_dos_trechos |= set(map(lambda line: line.IdentifiedObject_mRID, trechos_do_setor))
            if setor.IdentifiedObject_mRID != subestacao:
                # Não incluir os setores do barramento da subestação
                nomes_das_chaves |= set(map(lambda sw: sw.IdentifiedObject_mRID, chaves_do_setor))
       
        trechos_do_alimentador = [trecho for trecho in trechos.values() if trecho.nome in nomes_dos_trechos]
        setores_do_alimentador = [setor for setor in setores.values() if setor.nome in nomes_dos_setores]
        chaves_do_alimentador = [chave for chave in chaves.values() if chave.nome in nomes_das_chaves]

        alimentadores[nome] = Alimentador(nome=nome,
                                            setores=setores_do_alimentador,
                                            trechos=trechos_do_alimentador,
                                            chaves=chaves_do_alimentador)
        alimentadores[nome].ordenar(raiz=nome.split('_')[0])

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


if __name__ == '__main__':
    from pprint import pprint
    
    top = carregar_topologia('./rede/rede-cim-2.xml')
    pprint(top)
