from .BalancedTree import *
from .Queue import *
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point

def trataPonto(atual,Q,beach):
	ins = beach.insert(atual,atual.y)
	circleevents = ins[0]
	toRemove = ins[1]
	arcs = ins[2]
	if toRemove:
		Q.take(toRemove)
	for ev in circleevents:
		c = ev.event
		if c.y <= atual.y:
			control.plot_disc (c.x, c.y, config.COLOR_LINE, 5)
			Q.put(c,c)
	# arc contém uma aresta de voronoi, logo as regioes que divide são vizinhas, e existe uma aresta de delaunay entre seus pontos
	if arcs:
		p,q = arcs[0].value
		control.plot_segment(p.x,p.y,q.x,q.y,color=config.COLOR_LINE_SPECIAL)
	# if ins[0]:
	# 	evc = ins[0]
	# 	rem = ins[1]
	# 	arc = ins[2]
	# 	if arc:
	# 		p,q = arc[0].value
	# 		control.plot_segment(p.x,p.y,q.x,q.y,color=config.COLOR_LINE_SPECIAL)
	# 	if rem:
	# 		Q.take(rem)
	# 	for ev in evc:
	# 		c = ev.event
	# 		if c.y <= atual.y or c.isInf:
	# 			control.plot_disc (c.x, c.y, config.COLOR_LINE, 5)
	# 			Q.put(c,c)
		# Desenhar
 
def trataCirculo(atual,Q,beach):
	pred,suc,novo = beach.remove(atual.leaf)
	#print(novo.value[0],novo.value[1])
	#if pred.startp is None:
	#	print("pred startp is None")
	if pred is not None:
		idc = control.plot_segment(pred.startp.x,pred.startp.y,novo.startp.x,novo.startp.y)
	if suc is not None:
		idc = control.plot_segment(suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)

	# if pred is not None:
	# 	p = pred.startp
	# 	q = pred.event.center
	# 	idc = control.plot_segment(p.x,p.y,q.x,q.y)
	# if suc is not None:
	# 	p = suc.startp
	# 	q = suc.event.center
	# 	idc = control.plot_segment(p.x,p.y,q.x,q.y)
	#print(pred.startp.x,pred.startp.y,suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
	#print(novo.value[0].x,novo.value[0].y,novo.value[1].x,novo.value[1].y)
	if novo is not None:
		p,q = novo.value
		control.plot_segment(p.x,p.y,q.x,q.y,color=config.COLOR_LINE_SPECIAL)
		evc = beach.atualiza_eventos(novo)
		for ev in evc:
			c = ev.event
			if c.y <= atual.y:
				Q.put(c,c)
				control.plot_disc (c.x, c.y, config.COLOR_ALT3, 5)
	c = atual.center

def trataInf(atual,Q,beach):
	leaf = atual.leaf
	if leaf.event is not None:
		Q.take(leaf.event)
	#idc = control.plot_segment(leaf.event.x,leaf.event.y,leaf.startp.x,leaf.startp.y)
	a,b,c,circle = beach.removeInf(leaf)
	for ev in circle:
		Q.put(ev.event,ev.event)
	st = leaf.startp
	pt = leaf.event.center
	idc = control.plot_segment(st.x,st.y,pt.x,pt.y)
	#print(st.x,st.y,pt.x,pt.y)
	#idc = control.plot_segment(leaf.event.x,leaf.event.y,leaf.startp.x,leaf.startp.y)

def fortune(l):
	Q = EventQueue()
	Beach = BeachLine()
	#Vor = DCEL
	lineid = None
	parabola_list = None
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

		# Desenha a linha de varredura e as parabolas
		control.freeze_update()
		#if not atual.isInf:
		if lineid is not None: control.plot_delete(lineid)
		lineid = control.plot_horiz_line(atual.y)
		if parabola_list is not None:
			for i in parabola_list:
				control.plot_delete(i)
		# parabola_list = Beach.draw_parabolas(atual.y)
		# control.thaw_update()
		# control.update()
		# control.sleep()
		#

		if atual.isInf:
			trataInf(atual, Q, Beach)
			print("inf")
		else:
			if atual.isPonto:
				trataPonto(atual, Q, Beach)
				print("ponto")
			else:
				trataCirculo(atual, Q, Beach)
				print("circ")
		parabola_list = Beach.draw_parabolas(atual.y)
		control.thaw_update()
		control.update()
		control.sleep()
		
	if lineid is not None: control.plot_delete(lineid)
	if parabola_list is not None:
		for i in parabola_list:
			control.plot_delete(i)

max_x = None
min_x = None
max_y = None
min_y = None