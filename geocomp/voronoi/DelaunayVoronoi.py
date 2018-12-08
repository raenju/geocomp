from .BalancedTree import *
from .Queue import *
from .dcel import *
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point

max_x = None
min_x = None
max_y = None
min_y = None
edges = []
DelaunayTriangDraw = None

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
			Q.put(c,c)
	# arc contém uma aresta de voronoi, logo as regioes que divide são vizinhas, e existe uma aresta de delaunay entre seus pontos
	if arcs:
		p,q = arcs[0].value
		drawDelaunayEdge(p.x,p.y,q.x,q.y)
		#control.plot_segment(p.x,p.y,q.x,q.y,color=config.COLOR_ALT3)
 
def trataCirculo(atual,Q,beach):
	pred,suc,novo = beach.remove(atual.leaf)
	if pred is not None:
		idc = control.plot_segment(pred.startp.x,pred.startp.y,novo.startp.x,novo.startp.y)
		edges.append((Ponto(pred.startp.x,pred.startp.y),Ponto(novo.startp.x,novo.startp.y)))
	if suc is not None:
		idc = control.plot_segment(suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
		edges.append((Ponto(suc.startp.x,suc.startp.y),Ponto(novo.startp.x,novo.startp.y)))

	if novo is not None:
		p,q = novo.value
		drawDelaunayEdge(p.x,p.y,q.x,q.y)
		#control.plot_segment(p.x,p.y,q.x,q.y,color=config.COLOR_ALT3)
		evc,rem = beach.atualiza_eventos(novo,atual.y,pred,suc)
		for ev in rem:
			Q.take(ev)
		for ev in evc:
			c = ev.event
			if c.y <= atual.y:
				Q.put(c,c)

def trataInf(atual,Q,beach):
	leaf = atual.leaf
	if leaf.event is not None:
		Q.take(leaf.event)
	beach.removeInf(leaf)
	st = leaf.startp
	pt = leaf.event.center
	if pt.x == beach.bounds["minx"]:
		beach.llist.append(leaf.pair)
	elif pt.x == beach.bounds["maxx"]:
		beach.rlist.append(leaf.pair)
	else:
		beach.dlist.append(leaf.pair)
	idc = control.plot_segment(st.x,st.y,pt.x,pt.y)
	edges.append((Ponto(st.x,st.y),Ponto(pt.x,pt.y,isInf=True)))

def lineIntersect(p1,q1,p2,q2):
	if p1.y == q1.y or q2.y == p2.y:
		return None,None
	xfactor = (p1.x - q1.x)/(q1.y - p1.y) - (p2.x - q2.x)/( q2.y - p2.y)
	if xfactor == 0:
		return None,None
	constant = (q2.y*q2.y - p2.x*p2.x - p2.y*p2.y +  q2.x*q2.x)/(2*(q2.y - p2.y)) - (q1.y*q1.y - p1.x*p1.x - p1.y*p1.y + q1.x*q1.x)/(2*(q1.y - p1.y))

	x = constant/xfactor
	y  =  (2*(p1.x - q1.x)*x + q1.y*q1.y - p1.x*p1.x - p1.y*p1.y +  q1.x*q1.y)/(2*(q1.y - p1.y))

	return x,y

def fortEnv(l):
	fortune(l,True)

def vorEnv(l):
	fortune(l,False)

def drawDelaunayEdge(a,b,c,d):
	if DelaunayTriangDraw == True:
		control.plot_segment(a,b,c,d,color=config.COLOR_ALT3)

def fortune(l, triang):
	Q = EventQueue()
	Beach = BeachLine()
	Vor = dcel()
	global DelaunayTriangDraw
	DelaunayTriangDraw = triang
	lineid = None
	parabola_list = None
	max_x = min_x = l[0].x
	max_y = min_y = l[0].y
	first_y = None
	high_y = None
	y_count = 1
	for p in l:
		if p.x > max_x:
			max_x = p.x
		if p.x < min_x:
			min_x = p.x
		if p.y > max_y:
			max_y = p.y
		if p.y < min_y:
			min_y = p.y
		if high_y is None:
			high_y = p.y
		elif p.y > high_y:
			high_y = p.y
			y_count = 1
		elif p.y == high_y:
			y_count = y_count + 1
		Q.put(Ponto(p.x, p.y), Ponto(p.x,p.y))
		# Desenhas os pontos um pouco maiores
		control.plot_disc(p.x,p.y,config.COLOR_POINT,4)
	yd = max_y - min_y
	xd = max_x - min_x
	dd = max(yd,xd)
	mfactor = 0.7
	bounds = {"maxx":(max_x + min_x)/2 + dd*mfactor, "minx":(max_x + min_x)/2 - dd*mfactor, "maxy":(max_y + min_y)/2 + dd*mfactor,"miny":(max_y + min_y)/2 - dd*mfactor}
	Beach.bounds = bounds

	if y_count > 1:
		aligned = []
		for i in range(y_count):
			aligned.append(Q.takeHighest())
		aligned = list(reversed(aligned))
		for i in range(len(aligned)-1):
			drawDelaunayEdge(aligned[i].x,aligned[i].y,aligned[i+1].x,aligned[i+1].y)
			#control.plot_segment(aligned[i].x,aligned[i].y,aligned[i+1].x,aligned[i+1].y,color=config.COLOR_ALT3)
		Beach.create_particular(aligned)

	while Q.root is not None:
		atual = Q.takeHighest()
		# Desenha a linha de varredura e as parabolas
		control.freeze_update()
		if lineid is not None: control.plot_delete(lineid)
		lineid = control.plot_horiz_line(atual.y)
		if parabola_list is not None:
			for i in parabola_list:
				control.plot_delete(i)

		if atual.isInf:
			trataInf(atual, Q, Beach)
		else:
			if atual.isPonto:
				trataPonto(atual, Q, Beach)
			else:
				trataCirculo(atual, Q, Beach)
		parabola_list = Beach.draw_parabolas(atual.y)
		control.thaw_update()
		control.update()
		control.sleep()

	if lineid is not None: control.plot_delete(lineid)
	if parabola_list is not None:
		for i in parabola_list:
			control.plot_delete(i)

	if Beach.llist:
		for i in range(len(Beach.llist)-1):
			p1,q1 = Beach.llist[i]
			p2,q2 = Beach.llist[i+1]
			x,y = lineIntersect(p1,q1,p2,q2)
			if x is not None and x < Beach.bounds["minx"]:
				if q1 == p2:
					drawDelaunayEdge(p1.x,p1.y,q2.x,q2.y)
					#control.plot_segment(p1.x,p1.y,q2.x,q2.y,color=config.COLOR_ALT3)
				elif q1 == p1:
					drawDelaunayEdge(p2.x,p2.y,q2.x,q2.y)
					#control.plot_segment(p2.x,p2.y,q2.x,q2.y,color=config.COLOR_ALT3)
				elif q2 == p2:
					drawDelaunayEdge(p1.x,p1.y,q1.x,q1.y)
					#control.plot_segment(p1.x,p1.y,q1.x,q1.y,color=config.COLOR_ALT3)
				else:
					drawDelaunayEdge(p2.x,p2.y,q1.x,q1.y)
					#control.plot_segment(p2.x,p2.y,q1.x,q1.y,color=config.COLOR_ALT3)

	if Beach.rlist:
		for i in range(len(Beach.rlist)-1):
			p1,q1 = Beach.rlist[i]
			p2,q2 = Beach.rlist[i+1]
			x,y = lineIntersect(p1,q1,p2,q2)
			if x is not None and x > Beach.bounds["maxx"]:
				if q1 == p2:
					drawDelaunayEdge(p1.x,p1.y,q2.x,q2.y)
					#control.plot_segment(p1.x,p1.y,q2.x,q2.y,color=config.COLOR_ALT3)
				elif q1 == p1:
					drawDelaunayEdge(p2.x,p2.y,q2.x,q2.y)
					#control.plot_segment(p2.x,p2.y,q2.x,q2.y,color=config.COLOR_ALT3)
				elif q2 == p2:
					drawDelaunayEdge(p1.x,p1.y,q1.x,q1.y)
					#control.plot_segment(p1.x,p1.y,q1.x,q1.y,color=config.COLOR_ALT3)
				else:
					drawDelaunayEdge(p2.x,p2.y,q1.x,q1.y)
					#control.plot_segment(p2.x,p2.y,q1.x,q1.y,color=config.COLOR_ALT3)

	Vor.constroi(edges)

	return Vor