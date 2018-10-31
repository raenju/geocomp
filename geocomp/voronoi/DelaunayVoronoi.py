from .BalancedTree import *
from .Queue import *

def trataPonto(atual,Q,beach):
	ins = beach.insert(atual,atual.y)
	if ins[0]:
		evc = ins[0]
		rem = ins[1]
		arc = ins[2]
		Q.take(rem)
		for ev in evc:
			c = ev.event
			Q.put(c,c)
		# Desenhar
 
def trataCirculo(atual,Q,beach):
	pass

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

