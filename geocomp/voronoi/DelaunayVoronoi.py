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
			Q.take(rem.event)
		for ev in evc:
			c = ev.event
			if c.y <= atual.y:
				Q.put(c,c)
		# Desenhar
 
def trataCirculo(atual,Q,beach):
	pred,suc,novo = beach.remove(atual.leaf)
	if pred is not None:
		idc = control.plot_line(pred.startp.x,pred.startp.y,novo.startp.x,novo.startp.y)
	if suc is not None:
		idc = control.plot_line(suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
	#print(pred.startp.x,pred.startp.y,suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
	#print(novo.value[0].x,novo.value[0].y,novo.value[1].x,novo.value[1].y)
	if novo is not None:
		evc = beach.atualiza_eventos(novo)
		for ev in evc:
			c = ev.event
			if c.y <= atual.y:
				Q.put(c,c)
	c = atual.center

def trataInf(atual,Q,beach):
	leaf = atual.leaf

def fortune(l):
	Q = EventQueue()
	Beach = BeachLine()
	#Vor = DCEL
	lineid = None
	print(l)
	max_x = min_x = l[0].x
	max_y = min_y = l[0].y
	for p in l:
		if p.x > max_x:
			max_x = p.x
		if p.x < min_x:
			min_x = p.x
		if p.y > max_y:
			max_y = p.y
		if p.y < min_y:
			min_y = p.y
		Q.put(Ponto(p.x, p.y), Ponto(p.x,p.y))
	yd = max_y - min_y
	xd = max_x - min_x
	dd = max(yd,xd)
	mfactor = 0.7
	bounds = {"maxx":(max_x + min_x)/2 + dd*mfactor, "minx":(max_x + min_x)/2 - dd*mfactor, "maxy":(max_y + min_y)/2 + dd*mfactor,"miny":(max_y + min_y)/2 - dd*mfactor}
	Beach.bounds = bounds
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

		if atual.isInf:
			trataInf(atual, Q, Beach)
		else:
			if atual.isPonto:
				trataPonto(atual, Q, Beach)
			else:
				trataCirculo(atual, Q, Beach)
		
	if lineid is not None: control.plot_delete(lineid)

max_x = None
min_x = None
max_y = None
min_y = None