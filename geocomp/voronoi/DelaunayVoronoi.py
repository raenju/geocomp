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

# Trata um evento-ponto
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
 
# Trata um evento-círculo
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

# Dadas duas retas (desritas como os pontos equidistantes de um par de pontos), encontra a intersecção delas
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

# Classe auxiliar para desenhar e remover o desenho dos eventos-círculo
class draw_circ_events:
	def __init__(self):
		self.points = {}

	def add_point(self,x,y):
		key = (x,y)
		if key not in self.points.keys():
			self.points[key] = [None, 0]
		if self.points[key][1] == 0:
			self.points[key][0] = control.plot_disc(x,y,config.COLOR_PRIM,3)
		self.points[key][1] = self.points[key][1] + 1

	def rem_point(self,x,y):
		key = (x,y)
		if key not in self.points.keys():
			return
		if self.points[key][1] == 1:
			control.plot_delete(self.points[key][0])
			self.points[key][0] = None
		self.points[key][1] = self.points[key][1] - 1

## Chamadas diferentes para a versão com ou sem o desenho da triangulação de Delaunay
def fortEnv(l):
	fortune(l,True)

def vorEnv(l):
	fortune(l,False)
##

# Desenha uma aresta de Delaunay entre (a,b) e (c,d)
def drawDelaunayEdge(a,b,c,d):
	if DelaunayTriangDraw == True:
		control.plot_segment(a,b,c,d,color=config.COLOR_ALT3)


### Funções para remover pontos de entrada repetidos
def greater_point(p1,p2):
	if p1.y > p2.y or (p1.y == p2.y and p1.x > p2.x):
		return True
	return False

def sort_by_point(l):
	if len(l) <= 1:
		return l
	m = int((len(l))/2)
	l1 = l[:m]
	l2 = l[m:]
	l1 = sort_by_point(l1)
	l2 = sort_by_point(l2)
	vec = []
	i = 0
	j = 0
	while i < len(l1) and j < len(l2):
		if greater_point(l1[i][0],l2[j][0]):
			vec.append(l2[j])
			j = j+1
		else:
			vec.append(l1[i])
			i = i+1
	while i < len(l1):
		vec.append(l1[i])
		i = i+1
	while j < len(l2):
		vec.append(l2[j])
		j = j+1
	return vec

def sort_by_index(l):
	if len(l) <= 1:
		return l
	m = int((len(l))/2)
	l1 = l[:m]
	l2 = l[m:]
	l1 = sort_by_index(l1)
	l2 = sort_by_index(l2)
	vec = []
	i = 0
	j = 0
	while i < len(l1) and j < len(l2):
		if l1[i][1] < l2[j][1]:
			vec.append(l2[j])
			j = j+1
		else:
			vec.append(l1[i])
			i = i+1
	while i < len(l1):
		vec.append(l1[i])
		i = i+1
	while j < len(l2):
		vec.append(l2[j])
		j = j+1
	return vec


def unique_points(l):
	vec = [[l[i],i] for i in range(len(l))]
	sort_by_point(vec)
	vec2 = [vec[0]]
	for i in range(1,len(vec)):
		if vec[i][0].x != vec2[-1][0].x or vec[i][0].y != vec2[-1][0].y:
			vec2.append(vec[i])
	sort_by_index(vec2)
	vec3 = [vec2[i][0] for i in range(len(vec2))]
	return vec3
###

# Função principal
def fortune(l, triang):
	# Inicializa as estruturas de dados
	Q = EventQueue()
	Beach = BeachLine()
	Vor = dcel()
	CircDraw = draw_circ_events()
	#
	# Remove pontos repetidos na entrada
	l = unique_points(l)
	# Inicializa as variáveis
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
	#
	# Busca a bounding box dos pontos, e insere os pontos na fila
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
	#
	# Define os bounds da tela
	yd = max_y - min_y
	xd = max_x - min_x
	dd = max(yd,xd)
	mfactor = 0.7
	bounds = {"maxx":(max_x + min_x)/2 + dd*mfactor, "minx":(max_x + min_x)/2 - dd*mfactor, "maxy":(max_y + min_y)/2 + dd*mfactor,"miny":(max_y + min_y)/2 - dd*mfactor}
	Beach.bounds = bounds

	# Caso os primeiros pontos tenham a mesma y-coordenada, trata este caso particular
	if y_count > 1:
		aligned = []
		for i in range(y_count):
			aligned.append(Q.takeHighest())
		aligned = list(reversed(aligned))
		for i in range(len(aligned)-1):
			drawDelaunayEdge(aligned[i].x,aligned[i].y,aligned[i+1].x,aligned[i+1].y)
		Beach.create_particular(aligned)

	# Loop principal
	while Q.n > 0:
		atual = Q.takeHighest()
		## Remove o desenho do ponto evento círculo da iteração anterior, e desenha a nova posição da linha de varredura
		control.freeze_update()
		if cur_c is not None:
			control.plot_delete(cur_c)
			cur_c = None
		lineid = control.plot_horiz_line(atual.y)
		##

		# Trata evento ponto ou círculo
		if atual.isPonto:
			trataPonto(atual, Q, Beach, CircDraw)
		else:
			cur_c = control.plot_disc(atual.x,atual.y,config.COLOR_ALT5,4)
			CircDraw.rem_point(atual.x,atual.y)
			trataCirculo(atual, Q, Beach, CircDraw)
		#

		# Desenha as parábolas e as arestas de Voronoi parciais
		parabola_list = Beach.draw_parabolas(atual.y)
		partiallines = Beach.draw_partial(atual.y)
		control.thaw_update()
		control.update()
		control.sleep()
		# Remove o desenho das parábolas e da linha de varredura desta iteração
		if lineid is not None: control.plot_delete(lineid)
		if parabola_list is not None:
			for i in parabola_list:
				control.plot_delete(i)

		# Remove as parábolas que 'sairam da tela', remove seus respectivos eventos e o desenho destes eventos 
		evlist = Beach.trata_extremos(atual.y)
		for ev in evlist:
			CircDraw.rem_point(ev.x,ev.y)
			Q.take(ev)
		last_y = atual.y

	# Atualiza o desenho para a última iteração
	lower = last_y - 2*(Beach.bounds["maxy"]-Beach.bounds["miny"])
	partiallines = Beach.draw_partial(lower)
	if cur_c is not None:
		control.plot_delete(cur_c)
		cur_c = None

	# Desenha as arestas de Delaunay que não foram consideradas durante o algoritmo (por conta das parabolas serem removidas)
	if Beach.llist:
		for i in range(len(Beach.llist)-1):
			p1,q1 = Beach.llist[i]
			p2,q2 = Beach.llist[i+1]
			x,y = lineIntersect(p1,q1,p2,q2)
			if x is not None and x < Beach.bounds["minx"]:
				Beach.llist[i+1] = [p1,q1]
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
				Beach.rlist[i+1] = [p1,q1]
				if q1 == p2:
					drawDelaunayEdge(p1.x,p1.y,q2.x,q2.y)
				elif q1 == p1:
					drawDelaunayEdge(p2.x,p2.y,q2.x,q2.y)
				elif q2 == p2:
					drawDelaunayEdge(p1.x,p1.y,q1.x,q1.y)
				else:
					drawDelaunayEdge(p2.x,p2.y,q1.x,q1.y)

	# Constroi a DCEL
	Vor.constroi(edges)

	return Vor