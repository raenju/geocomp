from .Queue import Ponto
from geocomp.common import prim

class aresta:
	def __init__(self, u,v, twin=None,prox=None,ant=None):
		self.u = u
		self.v = v
		self.twin = twin
		self.prox = prox
		self.ant = ant
		self.face = None

class dcel:
	def __init__(self):
		self.arestas = []
		self.vertices = {}

	def between(self,p,q):
		lp = self.vertices[(p.x,p.y)]
		if len(lp) == 1:
			return lp[0].twin, lp[0]
		else:
			for a in lp:
				a = a.twin
				b = a.prox
				if prim.left(a.u,a.v,q) and prim.left(b.u,b.v,q):
					return a,b


	def insere(self,u,v,prox=None,ant=None):
		a = aresta(u,v,prox=prox,ant=ant)
		twin = aresta(v,u,twin=a,prox=ant,ant=prox)
		a.twin = twin
		pu = (u.x,u.y)
		pv = (v.x,v.y)
		if pu not in self.vertices.keys():
			self.vertices[pu] = []  #edges that LEAVE u
		if pv not in self.vertices.keys():
			self.vertices[pv] = []  #edges that LEAVE v
		lu = self.vertices[pu]
		lv = self.vertices[pv]
		if not lu:
			twin.prox = a
			a.ant = twin
			lu.append(a)
		else:
			twin.prox, a.ant = self.between(u, v)
			twin.prox.ant = twin
			a.ant.prox = a
		if not lv:
			twin.ant = a
			a.prox = twin 
			lv.append(twin)
		else:
			a.prox, twin.ant = self.between(v, u)
			twin.ant.prox = twin
			a.prox.ant = a
			
