#! coding: utf-8

from mygrid.util import Fasor, Base
from mygrid.rede import Chave
from terminaltables import AsciiTable

def config_objects(subestacao):

	for transformador in subestacao.transformadores.values():
		subestacao.base_sub = Base(transformador.tensao_secundario.mod,
								   transformador.potencia.mod)
		break

	for alimentador in subestacao.alimentadores.values():

		for trecho in alimentador.trechos.values():

			trecho.impedancia_positiva = (trecho.condutor.rp + trecho.condutor.xp * 1j) * trecho.comprimento
			trecho.impedancia_zero = (trecho.condutor.rz + trecho.condutor.xz * 1j) * trecho.comprimento
			trecho.base = subestacao.base_sub
			trecho.impedancia_positiva = trecho.impedancia_positiva / trecho.base.impedancia
			trecho.impedancia_zero = trecho.impedancia_zero / trecho.base.impedancia

		for chave in alimentador.chaves.values():

			chave.resistencia_contato = 100
			chave.base = subestacao.base_sub
			chave.fluxo = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)

		for noDeCarga in alimentador.nos_de_carga.values():

			noDeCarga.resistencia_contato = 100
			noDeCarga.base = subestacao.base_sub
			noDeCarga.fluxo = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)

		calculaimpedanciaeq(subestacao) 


def curtoMonofasico(elemento):
	curto1 = (3.0) * elemento.base.corrente / (2 * elemento.impedancia_equivalente_positiva + elemento.impedancia_equivalente_zero)
	correntecc = Fasor(real=curto1.real, imag=curto1.imag, tipo=Fasor.Corrente)
	correntecc.base = elemento.base
	return correntecc

def curtoBifasico(elemento):
	curto2 = (3 ** 0.5) * elemento.base.corrente / (2 * elemento.impedancia_equivalente_positiva)
	correntecc = Fasor(real=curto2.real, imag=curto2.imag, tipo=Fasor.Corrente)
	correntecc.base = elemento.base
	return correntecc

def curtoTrifasico(elemento):

	curto3 = 1.0 * elemento.base.corrente / (elemento.impedancia_equivalente_positiva)
	correntecc = Fasor(real=curto3.real, imag=curto3.imag, tipo=Fasor.Corrente)
	correntecc.base = elemento.base
	return correntecc

def curtoMonofasicoMinimo(elemento):
	curto1m = 3.0 * elemento.base.corrente / (2 * elemento.impedancia_equivalente_positiva + elemento.impedancia_equivalente_zero+3*elemento.resistencia_contato/elemento.base.impedancia)
	correntecc = Fasor(real=curto1m.real, imag=curto1m.imag, tipo=Fasor.Corrente)
	correntecc.base = elemento.base
	return correntecc


def calculaimpedanciaeq(subestacao):

	for alimentador in subestacao.alimentadores.values():

		atribuirImpedanciaEq(alimentador,subestacao)

def atribuirImpedanciaEq(alimentador,elemento,fluxo=None):

	if elemento.nome == alimentador.raiz:

		alimentador.nos_de_carga[elemento.nome].impedancia_equivalente_positiva = elemento.impedancia_equivalente_positiva
		alimentador.nos_de_carga[elemento.nome].impedancia_equivalente_zero = elemento.impedancia_equivalente_zero

		if _trechosAJusante(alimentador,elemento,'direto')[0] == [] and _trechosAJusante(alimentador,elemento,'inverso')[0] != []:

			fluxo = 'inverso'

		elif _trechosAJusante(alimentador,elemento,'inverso')[0] == [] and _trechosAJusante(alimentador,elemento,'direto')[0] != []:

			fluxo = 'direto'

	if alimentador.chaves.has_key(elemento.nome) == True:  # elemento é uma chave?
	# Sim:

		if alimentador.chaves[elemento.nome].estado == 1:
			# print elemento.nome
			_atribuirImpedanciaEq(alimentador,elemento,fluxo)  # Atribui impedancia equivalente

		else:

			pass

	else: 
	# Não:

		_atribuirImpedanciaEq(alimentador,elemento,fluxo)  # Atribui impedancia equivalente

def _atribuirImpedanciaEq(alimentador,elemento,fluxo):
	
	trechosAJusante,fluxo = _trechosAJusante(alimentador,elemento,fluxo)

	if trechosAJusante == []:

		pass

	else:
		
		for trecho in trechosAJusante:

			if fluxo == 'direto':

					if hasattr(trecho.n2,'impedancia_equivalente_positiva') == True:

						pass

					else:

						trecho.n2.impedancia_equivalente_positiva = elemento.impedancia_equivalente_positiva + trecho.impedancia_positiva

						trecho.n2.impedancia_equivalente_zero = elemento.impedancia_equivalente_zero + trecho.impedancia_zero
					
						atribuirImpedanciaEq(alimentador,trecho.n2,fluxo)

			elif fluxo == 'inverso':

					if hasattr(trecho.n1,'impedancia_equivalente_positiva') == True:

						pass

					else:

						trecho.n1.impedancia_equivalente_positiva = elemento.impedancia_equivalente_positiva + trecho.impedancia_positiva

						trecho.n1.impedancia_equivalente_zero = elemento.impedancia_equivalente_zero + trecho.impedancia_zero
					
						atribuirImpedanciaEq(alimentador,trecho.n1,fluxo)                

def _trechosAJusante(alimentador,elemento,fluxo):

	trechosAJusante = []
	
	if hasattr(elemento,'chaveDeEncontro') == True:

		if elemento.chaveDeEncontro == True:

			if alimentador.chaves[elemento.nome].estado == 0:

				pass

			else:
				
				if fluxo == 'direto':

					fluxo = 'inverso'

				elif fluxo == 'inverso':

					fluxo = 'direto'

		else:

			pass

	else:

		pass

	if fluxo == 'direto':    

		for trecho in alimentador.trechos.keys():

			if alimentador.trechos[trecho].n1.nome == elemento.nome:

				trechosAJusante.append(alimentador.trechos[trecho])

	elif fluxo == 'inverso':

		for trecho in alimentador.trechos.keys():

			if alimentador.trechos[trecho].n2.nome == elemento.nome:

				trechosAJusante.append(alimentador.trechos[trecho])

	return trechosAJusante,fluxo     

def gerarRelatorio(subestacao):

	arq = open('Relatorio de Curto Circuito.txt','w')

	texto = list()
	texto.append(_gerarRelatorio(subestacao,'com pu'))

	arq.writelines(texto)
	arq.close()

def _gerarRelatorio(subestacao, tipo):

	if tipo == 'com pu':

		texto = [['NO/CHAVE','TRIFASICO (pu)', 'TRIFASICO (A)','MONOFASICO (pu)', 'MONOFASICO (A)','BIFASICO (pu)', 'BIFASICO (A)','MONOFASICO MIN. (pu)', 'MONOFASICO MIN.(A)']]
		for alimentador_atual, r in subestacao.alimentadores.iteritems():
			for noDeCarga in subestacao.alimentadores[alimentador_atual].nos_de_carga.values():

				curto3f = curtoTrifasico(noDeCarga)
				curto1f = curtoMonofasico(noDeCarga)
				curto2f = curtoBifasico(noDeCarga)
				curto1fm = curtoMonofasicoMinimo(noDeCarga)

				texto.append([noDeCarga.nome,
							str(curto3f.pu)[:5],str(curto3f.mod)[:7],
							str(curto1f.pu)[:5],str(curto1f.mod)[:7],
							str(curto2f.pu)[:5],str(curto2f.mod)[:7],
							str(curto1fm.pu)[:5],str(curto1fm.mod)[:5]])           

			for chave in subestacao.alimentadores[alimentador_atual].chaves.values():

				curto = curtoTrifasico(chave)
				curto1f = curtoMonofasico(chave)
				curto2f = curtoBifasico(chave)
				curto1fm = curtoMonofasicoMinimo(chave)

				texto.append([chave.nome,
							str(curto3f.pu)[:5],str(curto3f.mod)[:7],
							str(curto1f.pu)[:5],str(curto1f.mod)[:7],
							str(curto2f.pu)[:5],str(curto2f.mod)[:7],
							str(curto1fm.pu)[:5],str(curto1fm.mod)[:5]])  


		titulo = 'CURTO CIRCUITO'             
		table = AsciiTable(texto,titulo)
		table.justify_columns[0] = 'center'
		table.justify_columns[1] = 'center'
		table.justify_columns[2] = 'center'
		table.justify_columns[3] = 'center'
		table.justify_columns[4] = 'center'
		table.justify_columns[5] = 'center'
		table.justify_columns[6] = 'center'
		table.justify_columns[7] = 'center'
		table.justify_columns[8] = 'center'        
		
		return table.table


	elif tipo == 'sem pu':

		texto = [['NO/CHAVE',
				'CURTO 3F (A)',
				'CURTO 1F (A)',
				'CURTO 2F (A)',
				'CURTO 1F MIN.(A)']]

		for alimentador_atual, r in subestacao.alimentadores.iteritems():
			for noDeCarga in subestacao.alimentadores[alimentador_atual].nos_de_carga.values():

				curto3f = curtoTrifasico(noDeCarga)
				curto1f = curtoMonofasico(noDeCarga)
				curto2f = curtoBifasico(noDeCarga)
				curto1fm = curtoMonofasicoMinimo(noDeCarga)

				texto.append([noDeCarga.nome,
							str(curto3f.mod)[:7],
							str(curto1f.mod)[:7],
							str(curto2f.mod)[:7],
							str(curto1fm.mod)[:5]])           

			for chave in subestacao.alimentadores[alimentador_atual].chaves.values():

				curto = curtoTrifasico(chave)
				curto1f = curtoMonofasico(chave)
				curto2f = curtoBifasico(chave)
				curto1fm = curtoMonofasicoMinimo(chave)

				texto.append([chave.nome,
							str(curto3f.mod)[:7],
							str(curto1f.mod)[:7],
							str(curto2f.mod)[:7],
							str(curto1fm.mod)[:5]])  

						
		table = AsciiTable(texto)
		table.justify_columns[0] = 'center'
		table.justify_columns[1] = 'center'
		table.justify_columns[2] = 'center'
		table.justify_columns[3] = 'center'
		table.justify_columns[4] = 'center'
		table.justify_columns[5] = 'center'
		table.justify_columns[6] = 'center'
		table.justify_columns[7] = 'center'
		table.justify_columns[8] = 'center'        
		
		return table.table

	elif tipo == 'com imp':

		texto = [['NO/CHAVE',
				'R1 eq. (pu)','X1 eq. (pu)', 
				'R0 eq. (pu)','X0 eq. (pu)', 
				'CURTO 3F (A)',
				'CURTO 1F (A)',
				'CURTO 2F (A)',
				'CURTO 1F MIN.(A)']]

		for alimentador_atual, r in subestacao.alimentadores.iteritems():
			for noDeCarga in subestacao.alimentadores[alimentador_atual].nos_de_carga.values():

				curto3f = curtoTrifasico(noDeCarga)
				curto1f = curtoMonofasico(noDeCarga)
				curto2f = curtoBifasico(noDeCarga)
				curto1fm = curtoMonofasicoMinimo(noDeCarga)

				texto.append([noDeCarga.nome,str(noDeCarga.impedancia_equivalente_positiva.real)[:5],str(noDeCarga.impedancia_equivalente_positiva.imag)[:5],
							str(noDeCarga.impedancia_equivalente_zero.real)[:5],str(noDeCarga.impedancia_equivalente_zero.imag)[:5],
							str(curto3f.mod)[:7],
							str(curto1f.mod)[:7],
							str(curto2f.mod)[:7],
							str(curto1fm.mod)[:5]])           

			for chave in subestacao.alimentadores[alimentador_atual].chaves.values():

				curto = curtoTrifasico(chave)
				curto1f = curtoMonofasico(chave)
				curto2f = curtoBifasico(chave)
				curto1fm = curtoMonofasicoMinimo(chave)

				texto.append([chave.nome,str(chave.impedancia_equivalente_positiva.real)[:5],str(chave.impedancia_equivalente_positiva.imag)[:5],
							str(chave.impedancia_equivalente_zero.real)[:5],str(chave.impedancia_equivalente_zero.imag)[:5],
							str(curto3f.mod)[:7],
							str(curto1f.mod)[:7],
							str(curto2f.mod)[:7],
							str(curto1fm.mod)[:5]])  

						
		table = AsciiTable(texto)
		table.justify_columns[0] = 'center'
		table.justify_columns[1] = 'center'
		table.justify_columns[2] = 'center'
		table.justify_columns[3] = 'center'
		table.justify_columns[4] = 'center'
		table.justify_columns[5] = 'center'
		table.justify_columns[6] = 'center'
		table.justify_columns[7] = 'center'
		table.justify_columns[8] = 'center'        
		
		return table.table  


