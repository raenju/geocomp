from .Queue import Ponto
from geocomp.common import prim

def esq(x1,y1,x2,y2,x3,y3):
	if (x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) >= 0:
		return True
	return False

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

	# Função de comparação. Retorna True se edge1 está depois de edge2 em sentido horario ao redor do vértice u de edge1/edge2 (Que deve ser o mesmo). O intervalo começa e termina em "12h"
	def greater(self,edge1,edge2):
		e1 = [edge1.v.x-edge1.u.x,edge1.v.y-edge1.u.y]
		e2 = [edge2.v.x-edge2.u.x,edge2.v.y-edge2.u.y]

		if e1[0] >= 0 and e2[0] < 0:
			return False
		if e1[0] < 0 and e2[0] >= 0:
			return True
		if esq(0,0,e1[0],e1[1],e2[0],e2[1]):
			return True
		return False

	def ordena(self,lista):
		if len(lista) <= 1:
			return lista
		m = int((len(lista))/2)
		l1 = lista[:m]
		l2 = lista[m:]
		l1 = self.ordena(l1)
		l2 = self.ordena(l2)
		l = []
		i = 0
		j = 0
		while i < len(l1) and j < len(l2):
			if self.greater(l1[i],l2[j]):
				l.append(l2[j])
				j = j+1
			else:
				l.append(l1[i])
				i = i+1
		while i < len(l1):
			l.append(l1[i])
			i = i+1
		while j < len(l2):
			l.append(l2[j])
			j = j+1
		return l

	def constroi(self,edges):
		for e in edges:
			u = e[0]
			v = e[1]
			a = aresta(u,v)
			twin = aresta(v,u,twin=a)
			a.twin = twin
			self.arestas.append(a)
			self.arestas.append(twin)
			pu = (u.x,u.y)
			pv = (v.x,v.y)
			if pu not in self.vertices.keys():
				self.vertices[pu] = []  #edges that LEAVE u
			if pv not in self.vertices.keys():
				self.vertices[pv] = []  #edges that LEAVE v
			self.vertices[pu].append(a)
			self.vertices[pv].append(twin)
		for key in self.vertices.keys():
			self.vertices[key] = self.ordena(self.vertices[key])
			for i in range(len(self.vertices[key])-1):
				self.vertices[key][i].twin.prox = self.vertices[key][i+1]
				self.vertices[key][i+1].ant = self.vertices[key][i].twin
			self.vertices[key][-1].twin.prox = self.vertices[key][0]
			self.vertices[key][0].ant = self.vertices[key][-1].twin