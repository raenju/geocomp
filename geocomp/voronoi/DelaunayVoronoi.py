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

def trataPonto(atual,Q,beach,CircDraw):
	ins = beach.insere(atual,atual.y)
	circleevents = ins[0]
	toRemove = ins[1]
	arcs = ins[2]
	if toRemove:
		CircDraw.rem_point(toRemove.x,toRemove.y)
		Q.take(toRemove)
	for ev in circleevents:
		c = ev.event
		if c.y <= atual.y:
			CircDraw.add_point(c.x,c.y)
			Q.put(c,c)
	# arc contém uma aresta de voronoi, logo as regioes que divide são vizinhas, e existe uma aresta de delaunay entre seus pontos
	if arcs:
		p,q = arcs[0].value
		drawDelaunayEdge(p.x,p.y,q.x,q.y)
 
def trataCirculo(atual,Q,beach,CircDraw):
	pred,suc,novo = beach.remove_circ(atual.leaf)
	if pred is not None:
		idc = control.plot_segment(pred.startp.x,pred.startp.y,novo.startp.x,novo.startp.y)
		edges.append((Ponto(pred.startp.x,pred.startp.y),Ponto(novo.startp.x,novo.startp.y)))
	if suc is not None:
		idc = control.plot_segment(suc.startp.x,suc.startp.y,novo.startp.x,novo.startp.y)
		edges.append((Ponto(suc.startp.x,suc.startp.y),Ponto(novo.startp.x,novo.startp.y)))

	if novo is not None:
		p,q = novo.value
		drawDelaunayEdge(p.x,p.y,q.x,q.y)
		evc,rem = beach.atualiza_eventos_circ(novo,atual.y,pred,suc)
		for ev in rem:
			CircDraw.rem_point(ev.x,ev.y)
			Q.take(ev)
		for ev in evc:
			c = ev.event
			if c.y <= atual.y:
				CircDraw.add_point(c.x,c.y)
				Q.put(c,c)

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

class draw_circ_events:
	def __init__(self):
		self.points = {}

	def add_point(self,x,y):
		key = (x,y)
		if key not in self.points.keys():
			self.points[key] = [None, 0]
		if self.points[key][1] == 0:
			self.points[key][0] = control.plot_disc(x,y,config.COLOR_ALT3,3)
		self.points[key][1] = self.points[key][1] + 1

	def rem_point(self,x,y):
		key = (x,y)
		if key not in self.points.keys():
			return
		if self.points[key][1] == 1:
			control.plot_delete(self.points[key][0])
			self.points[key][0] = None
		self.points[key][1] = self.points[key][1] - 1

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
	CircDraw = draw_circ_events()
	global DelaunayTriangDraw
	DelaunayTriangDraw = triang
	lineid = None
	partiallines = None
	parabola_list = None
	max_x = min_x = l[0].x
	max_y = min_y = l[0].y
	first_y = None
	high_y = None
	cur_c = None
	y_count = 1
	last_y = None
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
		Beach.create_particular(aligned)

	#while Q.root is not None:
	while Q.n > 0:
		atual = Q.takeHighest()
		# Desenha a linha de varredura e as parabolas
		control.freeze_update()
		if lineid is not None: control.plot_delete(lineid)
		if cur_c is not None:
			control.plot_delete(cur_c)
			cur_c = None
		lineid = control.plot_horiz_line(atual.y)
		if parabola_list is not None:
			for i in parabola_list:
				control.plot_delete(i)
		if partiallines is not None:
			for i in partiallines:
				pass
				#control.plot_delete(i)

		if atual.isPonto:
			trataPonto(atual, Q, Beach, CircDraw)
		else:
			cur_c = control.plot_disc(atual.x,atual.y,config.COLOR_ALT5,4)
			CircDraw.rem_point(atual.x,atual.y)
			trataCirculo(atual, Q, Beach, CircDraw)

		parabola_list = Beach.draw_parabolas(atual.y)
		partiallines = Beach.draw_partial(atual.y)
		control.thaw_update()
		control.update()
		control.sleep()
		if lineid is not None: control.plot_delete(lineid)
		if parabola_list is not None:
			for i in parabola_list:
				control.plot_delete(i)

		evlist = Beach.trata_extremos(atual.y)
		for ev in evlist:
			CircDraw.rem_point(ev.x,ev.y)
			Q.take(ev)
		last_y = atual.y

	lower = Beach.bounds["miny"] - 2*(Beach.bounds["maxx"]-Beach.bounds["miny"])
	partiallines = Beach.draw_partial(lower)
	if cur_c is not None:
		control.plot_delete(cur_c)
		cur_c = None

	if Beach.llist:
		for i in range(len(Beach.llist)-1):
			p1,q1 = Beach.llist[i]
			p2,q2 = Beach.llist[i+1]
			x,y = lineIntersect(p1,q1,p2,q2)
			if x is not None and x < Beach.bounds["minx"]:
				if q1 == p2:
					drawDelaunayEdge(p1.x,p1.y,q2.x,q2.y)
				elif q1 == p1:
					drawDelaunayEdge(p2.x,p2.y,q2.x,q2.y)
				elif q2 == p2:
					drawDelaunayEdge(p1.x,p1.y,q1.x,q1.y)
				else:
					drawDelaunayEdge(p2.x,p2.y,q1.x,q1.y)

	if Beach.rlist:
		for i in range(len(Beach.rlist)-1):
			p1,q1 = Beach.rlist[i]
			p2,q2 = Beach.rlist[i+1]
			x,y = lineIntersect(p1,q1,p2,q2)
			if x is not None and x > Beach.bounds["maxx"]:
				if q1 == p2:
					drawDelaunayEdge(p1.x,p1.y,q2.x,q2.y)
				elif q1 == p1:
					drawDelaunayEdge(p2.x,p2.y,q2.x,q2.y)
				elif q2 == p2:
					drawDelaunayEdge(p1.x,p1.y,q1.x,q1.y)
				else:
					drawDelaunayEdge(p2.x,p2.y,q1.x,q1.y)

	Vor.constroi(edges)

	return Vor