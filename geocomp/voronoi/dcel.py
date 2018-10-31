from .Queue import Ponto

class aresta:
	def __init__(self, u,v, twin=None,prox=None,ant=None):
		self.u = u
		self.v = v
		self.twin = twin
		self.prox = prox
		self.ant = ant

class dcel:
	def __init__(self):
		self.arestas = {}

	def insere(self,u,v,prox=None,ant=None):
		a = aresta(u,v,prox=prox,ant=ant)
		twin = aresta(v,u,twin=a,prox=ant,ant=prox)
		a.twin = twin
		self.arestas[a] = a
		self.arestas[twin] = twin