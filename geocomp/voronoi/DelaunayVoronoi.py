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
		if rem:
			#Q.take(rem.event) << Ta crashando
			print("Devia tirar um evento")
		for ev in evc:
			c = ev.event
			if c.y <= atual.y:
				Q.put(c,c)
		# Desenhar
 
def trataCirculo(atual,Q,beach):
	pred,suc,novo = beach.remove(atual.leaf)
	idc = control.plot_line(pred.startp.x,pred.startp.y,novo.startp.x,novo.startp.y)
	idc = control.plot_line(suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
	print(pred.startp.x,pred.startp.y,suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
	#print(novo.value[0].x,novo.value[0].y,novo.value[1].x,novo.value[1].y)
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
		if lineid is not None: control.plot_delete(lineid)
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

	if lineid is not None: control.plot_delete(lineid)