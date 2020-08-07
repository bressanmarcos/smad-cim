# coding=utf-8

class IED(object):

    def __init__(self,name,nmax,gativo):

        self.name = name					# name do IED
        self.grupoAjuste = dict()			# dicionario com todos os grupos de ajustes cadastrados no ied
        self.gativo = gativo				# indica qual o grupo ativo

        for i in range(nmax):

        	tag = 'G' + str(i+1)

        	self.grupoAjuste[tag] = None


class GrupoAjuste(object):
	"""docstring for GrupoAjuste"""
	def __init__(self, ipk51p,ipk50p,curvap,dialp,ipk51n,ipk50n,curvan,dialn):
		
		self.ipk51p = ipk51p
		self.ipk50p = ipk50p
		self.curvap = curvap
		self.dialp = dialp

		self.ipk51n = ipk51n
		self.ipk50n = ipk50n
		self.curvan = curvan
		self.dialn = dialn

