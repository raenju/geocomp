from .BalancedTree import *
from .Queue import *
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point

def trataPonto(atual,Q,beach):
	ins = beach.insert(atual,atual.y)
	if ins[0]:
		evc = ins[0]
		rem = ins[1]
		arc = ins[2]
		#Q.take(rem.event) << Ta crashando
		for ev in evc:
			c = ev.event
			Q.put(c,c)
		# Desenhar
 
def trataCirculo(atual,Q,beach):
	pred,suc,novo = beach.remove(atual.leaf)
	print("-----")
	beach.test_r2lprint()
	# Atualiza Eventos ?
	c = atual.center

def fortune(l):
	Q = EventQueue()
	Beach = BeachLine()
	#Vor = DCEL
	lineid = None
	print(l)
	for p in l:
		Q.put(Ponto(p.x, p.y), Ponto(p.x,p.y))
	while Q.root is not None:
		atual = Q.takeHighest()

		# Desenha a linha de varredura
		control.freeze_update()
		if lineid is not None: control.plot_delete (lineid)
		lineid = control.plot_horiz_line(atual.y)
		control.thaw_update()
		control.update()
		control.sleep()
		#

		if atual.isPonto:
			trataPonto(atual, Q, Beach)
		else:
			trataCirculo(atual, Q, Beach)
		#Pontos infinitos
