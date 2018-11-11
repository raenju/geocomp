import math
import copy
from .Queue import Ponto
from geocomp.common.guiprim import *
from geocomp.common import control
def area(a,b,c):
	return ((a.x-c.x)*(b.y-c.y)-(a.y-c.y)*(b.x-c.x))/2

class TNode:
	def __init__(self, value):
		self.left = None
		self.right = None
		self.parent = None
		self.balance = 0
		self.value = value # par de pontos [p,q] caso seja nó interno, e um ponto s caso seja folha
		self.event = None # Evento circulo relacionado ao arco
		self.startp = None # Ponto inicial da linha a ser desenhada

	def __str__(self):
		if isinstance(self.value, list):
			return str(self.value[0].x) + " " + str(self.value[0].y) + " " + str(self.value[1].x) + " " + str(self.value[1].y)
		else:
			return str(self.value.x) + " " + str(self.value.y)

class BeachLine:
	def __init__(self):
		self.root = None
		self.bounds = None

	# Encontra o 'próximo' node
	def next_leaf(self,node):
		cnode = node
		while cnode.parent is not None:
			if cnode == cnode.parent.left:
				cnode = cnode.parent.right
				while cnode.left is not None:
					cnode = cnode.left
				break
			cnode = cnode.parent
		if cnode.parent is None:
			return None
		return cnode

	# Encontra o node 'anterior'
	def prev_leaf(self,node):
		cnode = node
		while cnode.parent is not None:
			if cnode == cnode.parent.right:
				cnode = cnode.parent.left
				while cnode.right is not None:
					cnode = cnode.right
				break
			cnode = cnode.parent
		if cnode.parent is None:
			return None
		return cnode

	# Insere o ponto value (arco de parabola correspondente). Devolve uma lista com [a folha que contem o evento circulo, evento circulo a ser removido, dados para desenhar]
	def insert(self, value, c): # c é a y-coord da linha de varredura
		if self.root is None:
			self.root = TNode(value)
			return [[], None, []]
		else:
			return self.insertRec(value, self.root, c)

	def insertRec(self, value, node, c):
		if node.right is None and node.left is None: # é uma folha
			# if node.value.y == value.y:
			# 	newnode = TNode([node.value, value])
			# 	newnode.parent = node.parent
			# 	newnode.balance = 0
			# 	node.parent = newnode

			# 	newnode3 = TNode(value)
			# 	newnode3.parent = newnode
			# 	if node.value.x < value.x:
			# 		newnode.left = node
			# 		newnode.right = newnode3
			# 	else:
			# 		newnode.left = newnode3
			# 		newnode.right = node
			# 	return [[], None, []]

			# Armazena o evento circulo do arco
			removeEvent = node.event
			node.event = None
			# Cria os novos nós internos e folhas da árvore
			newnode = TNode([node.value, value])
			newnode.parent = node.parent
			newnode.balance = 1
			newnode.left = node
			node.parent = newnode
			if newnode.parent is not None:
				if newnode.parent.left == node:
					newnode.parent.left = newnode
				else:
					newnode.parent.right = newnode
			newnode2 = TNode([value, node.value])
			newnode2.parent = newnode
			newnode.right = newnode2
			lleaf = TNode(value)
			rleaf = TNode(node.value)
			lleaf.parent = newnode2
			rleaf.parent = newnode2
			newnode2.left = lleaf
			newnode2.right = rleaf
			#

			# Encontra o ponto da parábola diretamente acima do ponto adicionado
			p = node.value
			q = value
			stpy = (q.y*q.y - (p.x-q.x)*(p.x-q.x) - p.y*p.y)/(2*(q.y-p.y))
			stp = Ponto(q.x,stpy)

			newnode.startp = stp
			newnode2.startp = stp
			#

			control.plot_disc (stp.x, stp.y, config.COLOR_ALT1, 5)

			# Atualiza o apontador da raiz, caso seja necessário
			if self.root == node:
				self.root = node.parent

			# Encontra o 'próximo' node, para termos as triplas que determinam eventos-circulo
			circleevents = []
			cnode = self.next_leaf(newnode2)
			if cnode is not None:
				lp = self.circleLowerPoint(cnode.value, node.value, value)
				if lp is None: # Os pontos não formam um circulo
					rleaf.event = None
				else:
					lp.leaf = rleaf
					rleaf.event = lp 
					circleevents.append(rleaf)
			else:
				p = newnode2.value[0]
				q = newnode2.value[1]
				x0 = self.bounds["maxx"]
				yv = 0
				pt = None
				ptc = None
				if(p.y == q.y):
					ptc = Ponto((p.x+q.x)/2,self.bounds["miny"])
				else:
					yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
					ptc = Ponto(x0,yv)
				dt = math.sqrt((ptc.x-stp.x)*(ptc.x-stp.x) + (ptc.y-stp.y)*(ptc.y-stp.y))
				pt = Ponto(ptc.x,ptc.y-dt,isPonto=False)
				pt.leaf = rleaf
				pt.isInf = True
				pt.center = ptc
				rleaf.startp = stp
				rleaf.event = pt
				circleevents.append(rleaf)

			# Encontra o node 'anterior', para termos as triplas que determinam eventos-circulo
			cnode = self.prev_leaf(newnode)
			if cnode is not None:
				lp = self.circleLowerPoint(cnode.value, node.value, value)
				if lp is None: # Os pontos não formam um circulo
					node.event = None
				else:
					lp.leaf = node
					node.event = lp
					circleevents.append(node)
			else:
				p = newnode.value[0]
				q = newnode.value[1]
				x0 = self.bounds["minx"]
				yv = 0
				pt = None
				ptc = None
				if(p.y == q.y):
					ptc = Ponto((p.x+q.x)/2,self.bounds["miny"])
				else:
					yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
					ptc = Ponto(x0,yv)
				dt = math.sqrt((ptc.x-stp.x)*(ptc.x-stp.x) + (ptc.y-stp.y)*(ptc.y-stp.y))
				pt = Ponto(ptc.x,ptc.y-dt,isPonto=False)
				pt.leaf = node
				pt.isInf = True
				pt.center = ptc
				node.startp = stp
				node.event = pt
				circleevents.append(node)

			####
			#Propagar as mudanças de balance
			#Balancear!!
			####

			arc = [newnode, lleaf, newnode2]

			return [circleevents, removeEvent, arc]

		else:
			p = node.value[0]
			q = node.value[1]

			x = self.parabolaIntersectX(p,q,c)
			if value.x <= x:
				return self.insertRec(value, node.left, c)
			else:
				return self.insertRec(value, node.right, c)

	def search(self, value, c):
		if self.root is None:
			return None
		else:
			return self.searchRec(value, self.root, c)

	def searchRec(self,value,node,c):
		if node.right is None and node.left is None:
			return node
		else:
			p = node.value[0]
			q = node.value[1]
			if p.y == c:
				if p.x > value.x:
					return self.searchRec(value, node.left, c)
				else:
					return self.searchRec(value, node.right, c)
			if q.y == c:
				if q.x > value.x:
					return self.searchRec(value, node.left, c)
				else:
					return self.searchRec(value, node.right, c)

			x = self.parabolaIntersectX(p,q,c)
			if value.x <= x:
				return self.searchRec(value, node.left, c)
			else:
				return self.searchRec(value, node.right, c)

	def parabolaIntersectX(self, p, q, c): # p e q são os pontos que definem as duas parabolas, c é a y-coord da linha de varredura

		# Casos degenerados
		if p.y == c:
			return p.x
		if q.y == c:
			return q.x
		if p.y == q.y:
			return (p.x+q.x)/2
		
		eqa = (1/(p.y-c) - 1/(q.y-c))
		eqb = 2*(q.x/(q.y-c) - p.x/(p.y-c))
		eqc = (((p.x*p.x+p.y*p.y-c*c)/(p.y-c)) - ((q.x*q.x+q.y*q.y-c*c)/(q.y-c)))

		delta = eqb*eqb - 4*eqa*eqc
		sqdelta = math.sqrt(delta) # Não deveria ser possível o delta ser negativo neste algoritmo

		x1 = (-eqb + sqdelta)/(2*eqa)
		x2 = (-eqb - sqdelta)/(2*eqa)

		if x1 > x2:
			x1,x2 = x2,x1

		if x1 <= p.x and x2 <= p.x:
			if x1 <= q.x and x2 <= q.x:
				print("os dois estão antes dos dois pontos")
			if x1 <= q.x:
				return x1
			if x2 <= q.x:
				return x2
		if x1 <= p.x:
			return x2
		if x2 <= p.x:
			return x1

		if p.x <= q.x:
			if p.x <= x1 and x1 <= q.x:
				return x1
			else:
				return x2
		else:
			if q.x <= x1 and x1 <= p.x:
				return x1
			else:
				return x2

	def circleLowerPoint(self, p, q, r):
		if area(p,q,r) == 0:
			return None
		if p.x == q.x:
			aux = q
			q = r
			r = aux
		if q.x == r.x:
			aux = p
			p = q
			q = aux
		if p.y == q.y:
			aux = p
			p = r
			r = aux
		grad1 = (q.y-p.y)/(q.x-p.x)
		grad2 = (r.y-q.y)/(r.x-q.x)
		cx = (grad1*grad2*(p.y-r.y)+grad2*(p.x+q.x)-grad1*(q.x+r.x))/(2*(grad2-grad1))
		cy = -(cx - (p.x+q.x)/2)/grad1 + (p.y+q.y)/2
		rad = math.sqrt((cx-p.x)*(cx-p.x)+(cy-p.y)*(cy-p.y))
		return Ponto(cx,cy-rad,isPonto=False,center=Ponto(cx,cy))   # <<< A y-coord da linha de varredura diminui ao longo do alg

	def removeInf(self,leaf):
		prox = None
		proxn = None
		ant = None
		antn = None
		cnode = self.next_leaf(leaf)
		if cnode is not None:
			prox = cnode.value
			proxn = cnode

		cnode = self.prev_leaf(leaf)
		if cnode is not None:
			ant = cnode.value
			antn = cnode

		if ant == prox:
			print('collapse')
			if ant is None and prox is None:
				print("----a")

		pred = None
		suc = None
		novo = None

		if prox is not None:
			suc = TNode([leaf.value, prox])
		if ant is not None:
			pred = TNode([ant,leaf.value])
		if ant is not None and prox is not None:
			novo = TNode([antn,proxn])

		if cnode == self.root:
			print("what?")
		if leaf == self.root:
			print("what??")
		cnode = leaf.parent
		nroot = None
		if cnode.left == leaf:
			nroot = cnode.right
		else:
			if cnode.right == leaf:
				nroot = cnode.left
			else:
				print('Erro? leaf deveria ser filho de cnode')
		if cnode == self.root:
			self.root = nroot
			nroot.parent = None
		else:
			nroot.parent = cnode.parent
			if cnode.parent.left == cnode:
				cnode.parent.left = nroot
			else:
				cnode.parent.right = nroot

		circleevents = []
		# if antn is not None:
		# 	parent = antn.parent
		# 	if parent is not None: #Acho que é impossivel que seja None
		# 		p = parent.value[0]
		# 		q = parent.value[1]
		# 		stp = parent.startp
		# 		y0 = self.bounds["miny"]
		# 		ptc = None
		# 		pt = None
		# 		if p.x == q.x:
		# 			ptc = Ponto(self.bounds["maxx"],(p.y+q.y)/2)
		# 		else:
		# 			x0 = (q.x*q.x + q.y*q.y - 2*y0*q.y - p.x*p.x - p.y*p.y + 2*p.y*y0)/(2*(q.x-p.x))
		# 			ptc = Ponto(x0,y0)
		# 		dt = math.sqrt((ptc.x-stp.x)*(ptc.x-stp.x) + (ptc.y-stp.y)*(ptc.y-stp.y))
		# 		pt = Ponto(ptc.x,ptc.y-dt,isPonto=False)
		# 		pt.leaf = antn
		# 		pt.isInf = True
		# 		pt.center = ptc
		# 		antn.startp = stp
		# 		antn.event = pt
		# 		circleevents.append(antn)
		# if proxn is not None:
		# 	parent = proxn.parent
		# 	if parent is not None: #Acho que é impossivel que seja None
		# 		p = parent.value[0]
		# 		q = parent.value[1]
		# 		stp = parent.startp
		# 		y0 = self.bounds["miny"]
		# 		ptc = None
		# 		pt = None
		# 		if p.x == q.x:
		# 			ptc = Ponto(self.bounds["minx"],(p.y+q.y)/2)
		# 		else:
		# 			x0 = (q.x*q.x + q.y*q.y - 2*y0*q.y - p.x*p.x - p.y*p.y + 2*p.y*y0)/(2*(q.x-p.x))
		# 			ptc = Ponto(x0,y0)
		# 		dt = math.sqrt((ptc.x-stp.x)*(ptc.x-stp.x) + (ptc.y-stp.y)*(ptc.y-stp.y))
		# 		pt = Ponto(ptc.x,ptc.y-dt,isPonto=False)
		# 		pt.leaf = proxn
		# 		pt.isInf = True
		# 		pt.center = ptc
		# 		proxn.startp = stp
		# 		proxn.event = pt
		# 		circleevents.append(proxn)

		return [pred,suc,novo,circleevents]

	def remove(self, leaf):
		prox = None
		proxn = None
		ant = None
		antn = None

		cnode = self.next_leaf(leaf)
		if cnode is not None:
			prox = cnode.value
			proxn = cnode

		cnode = self.prev_leaf(leaf)
		if cnode is not None:
			ant = cnode.value
			antn = cnode

		if ant == prox:
			print('collapse')
			if ant is None and prox is None:
				print("----a")

		# Os nós internos a serem removidos são (leaf.value, prox) e (ant, leaf.value)

		pred = None
		suc = None
		novo = None

		if prox is not None:
			suc = TNode([leaf.value, prox])
		else:
			print("prox is none")
		if ant is not None:
			pred = TNode([ant,leaf.value])
		else:
			print("ant is none")
		if ant is not None and prox is not None:
			novo = TNode([antn,proxn])

		# Encontra os dois nós internos que vão ser removidos, de acordo com a distancia da folha
		if prox is not None and ant is not None:
			low = None
			high = None
			cnode = leaf.parent
			proxtaken = False
			anttaken = False
			while cnode is not None:
				if (not proxtaken) and ((cnode.value[0] == leaf.value and cnode.value[1] == prox) or (cnode.value[1] == leaf.value and cnode.value[0] == prox)):
					proxtaken = True
					suc.value = cnode.value
					suc.startp = cnode.startp
					suc.event = cnode.event
					if low is None:
						low = cnode
					else:
						if high is None:
							high = cnode
						else:
							print('erro? Nós internos repetido 1')
				if (not anttaken) and ((cnode.value[0] == ant and cnode.value[1] == leaf.value) or (cnode.value[1] == ant and cnode.value[0] == leaf.value)):
					anttaken = True
					pred.value = cnode.value
					pred.startp = cnode.startp
					pred.event = cnode.event
					if low is None:
						low = cnode
					else:
						if high is None:
							high = cnode
						else:
							print('erro? Nós internos repetidos 2')
				cnode = cnode.parent

			if low is None or high is None:
				print('Erro. low ou high é None, ambos deviam ter valor')
			if low is not None and high is None:
				print(low.value[0].x,low.value[0].y,low.value[1].x,low.value[1].y)
			high.value = [ant,prox]
			high.startp = leaf.event.center
			novo.startp = leaf.event.center
			nroot = None
			if low.left == leaf:
				nroot = low.right
			else:
				if low.right == leaf:
					nroot = low.left
				else:
					print('Erro? leaf deveria ser filho de low')
			nroot.parent = low.parent
			if low.parent.left == low:
				low.parent.left = nroot
			else:
				low.parent.right = nroot
		else: # Certamente não devia acontecer. Um evento circulo precisa ter uma proxima regiao, e uma regiao anterior
			print("Devia contecer?")
			cnode = leaf.parent
			nroot = None
			if cnode.left == leaf:
				nroot = cnode.right
			else:
				if cnode.right == leaf:
					nroot = cnode.left
				else:
					print('Erro? leaf deveria ser filho de cnode')
			if cnode == self.root:
				self.root = nroot
				nroot.parent = None
			else:
				nroot.parent = cnode.parent
				if cnode.parent.left == cnode:
					cnode.parent.left = nroot
				else:
					cnode.parent.right = nroot

		# Retorna os nós internos das divisões que sumiram, e a divisão nova.
		# Precisa adicionar os eventos circulo da divisão nova (novo[0], novo[1], prox(novo[1])) (ant(novo[0]),novo[0],novo[1])
		return [pred,suc,high]

	def atualiza_eventos(self,novo):
		print("atualiza")
		circleevents = []
		p = novo.value[0]
		q = novo.value[1]

		nxt = self.next_leaf(novo)
		ant = self.prev_leaf(novo)
		stp = novo.startp
		if (nxt is not None) and (nxt.value == p):
			nxt = self.next_leaf(nxt)
			ant = self.prev_leaf(ant)
			r = p
			p = q
			q = r
		if nxt is not None:
			q_leaf = self.prev_leaf(nxt)
			lp = self.circleLowerPoint(nxt.value, p, q)
			if lp is None:
				q_leaf.event = None
			else:
				lp.leaf = q_leaf
				q_leaf.event = lp
				circleevents.append(q_leaf)
		else:
			y0 = self.bounds["miny"]
			q_leaf = novo.right
			ptc = None
			pt = None
			while q_leaf.left is not None:
				q_leaf = q_leaf.left
			if p.x == q.x:
				ptc = Ponto(self.bounds["maxx"],(p.y+q.y)/2)
			else:
				x0 = (q.x*q.x + q.y*q.y - 2*y0*q.y - p.x*p.x - p.y*p.y + 2*p.y*y0)/(2*(q.x-p.x))
				ptc = Ponto(x0,y0)
			dt = math.sqrt((ptc.x-stp.x)*(ptc.x-stp.x) + (ptc.y-stp.y)*(ptc.y-stp.y))
			pt = Ponto(ptc.x,ptc.y-dt,isPonto=False)
			pt.leaf = q_leaf
			pt.isInf = True
			pt.center = ptc
			q_leaf.startp = stp
			q_leaf.event = pt
			circleevents.append(q_leaf)

		if ant is not None:
			p_leaf = self.next_leaf(ant)
			lp = self.circleLowerPoint(ant.value, p, q)
			if lp is None:
				p_leaf.event = None
			else:
				lp.leaf = p_leaf
				p_leaf.event = lp
				circleevents.append(p_leaf)
		else:
			y0 = self.bounds["miny"]
			p_leaf = novo.left
			ptc = None
			pt = None
			while p_leaf.right is not None:
				p_leaf = p_leaf.right
			if p.x == q.x:
				ptc = Ponto(self.bounds["minx"],(p.y+q.y)/2)
			else:
				x0 = (q.x*q.x + q.y*q.y - 2*y0*q.y - p.x*p.x - p.y*p.y + 2*p.y*y0)/(2*(q.x-p.x))
				ptc = Ponto(x0,y0)
			dt = math.sqrt((ptc.x-stp.x)*(ptc.x-stp.x) + (ptc.y-stp.y)*(ptc.y-stp.y))
			pt = Ponto(ptc.x,ptc.y-dt,isPonto=False)
			pt.leaf = p_leaf
			pt.isInf = True
			pt.center = ptc
			p_leaf.startp = stp
			p_leaf.event = pt
			circleevents.append(p_leaf)

		return circleevents

	def draw_parabolas(self, c):
		if self.root is None:
			return []
		id_list = []
		cnode = self.root
		while cnode.left is not None:
			cnode = cnode.left
		antx = self.bounds["minx"]
		nnode = self.next_leaf(cnode)
		while nnode is not None:
			proxx = self.parabolaIntersectX(cnode.value,nnode.value,c)
			line_id = control.plot_parabola(c,cnode.value.x,cnode.value.y,antx,proxx)
			id_list.append(line_id)
			antx = proxx
			cnode = nnode
			nnode = self.next_leaf(nnode)
		proxx = self.bounds["maxx"]
		line_id = control.plot_parabola(c,cnode.value.x,cnode.value.y,antx,proxx)
		id_list.append(line_id)
		return id_list

	def test_r2lprint(self):
		r = self.root
		if r is not None:
			print("vvvv")
			self.test_r2lprintrec(r)
			print("^^^^")

	def test_r2lprintrec(self, r):
		if r.left is None and r.right is None:
			print(r.value.x, r.value.y)
			return
		else:
			self.test_r2lprintrec(r.left)
			self.test_r2lprintrec(r.right)
			return