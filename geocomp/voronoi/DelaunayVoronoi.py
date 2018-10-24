from .BalancedTree import *
from .Queue import *

def fortune(l):
	Q = EventQueue()
	Beach = BeachLine()
	#Vor = DCEL
	for p in l:
		Q.put(Ponto(p.x, p.y), p)
	while Q.root is not None:
		atual = Q.takeHighest()
		if atual.isPonto:
			trataPonto(atual, Q, Beach)
		else:
			trataCirculo(atual, Q, Beach)
		#Pontos infinitos

