
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
	def next_leaf(self,cnode):
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
	def prev_leaf(self,cnode):
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

			removeEvent = node.event # Armazena o evento circulo do arco
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

			p = node.value
			q = value

			stpy = (q.y*q.y - (p.x-q.x)*(p.x-q.x) - p.y*p.y)/(2*(q.y-p.y))
			stp = Ponto(q.x,stpy)

			newnode.startp = stp
			newnode2.startp = stp

			control.plot_disc (stp.x, stp.y, config.COLOR_ALT1, 5)

			if self.root == node:
				self.root = node.parent

			# Encontra o 'próximo' node, para termos as triplas que determinam eventos-circulo
			cnode = newnode2
			circleevents = []
			# while cnode.parent is not None:
			# 	if cnode == cnode.parent.left:
			# 		cnode = cnode.parent.right
			# 		while cnode.left is not None:
			# 			cnode = cnode.left
			# 		break
			# 	cnode = cnode.parent
			cnode = self.next_leaf(cnode)
			if cnode is not None:
				lp = self.circleLowerPoint(cnode.value, node.value, value)
				if lp is None:
					rleaf.event = None
				else:
					lp.leaf = rleaf
					rleaf.event = lp #.y
					circleevents.append(rleaf)
					#circleevents.append([cnode.value, node.value, value])
			else:
				p = newnode2.value[0]
				q = newnode2.value[1]
				x0 = self.bounds["maxx"]
				yv = 0
				pt = None
				if(p.y == q.y):
					pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
				else:
					yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
					pt = Ponto(x0,yv,isPonto=False)
				pt.leaf = rleaf
				pt.isInf = True
				rleaf.startp = stp
				rleaf.event = pt
				circleevents.append(rleaf)

			# Encontra o node 'anterior', para termos as triplas que determinam eventos-circulo
			cnode = newnode
			cnode = self.prev_leaf(cnode)
			if cnode is not None:
				lp = self.circleLowerPoint(cnode.value, node.value, value)
				if lp is None:
					node.event = None
				else:
					lp.leaf = node
					node.event = lp #.y
					circleevents.append(node)
					#circleevents.append([cnode.value, node.value, value])
			else:
				p = newnode.value[0]
				q = newnode.value[1]
				x0 = self.bounds["minx"]
				yv = 0
				pt = None
				if(p.y == q.y):
					pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
				else:
					yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
					pt = Ponto(x0,yv,isPonto=False)
				pt.leaf = node
				pt.isInf = True
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

			# Casos degenerados - Comparar com um ponto sobre a linha de varredura
			if p.y == c:
				if p.x > value.x:
					return self.insertRec(value, node.left, c)
				else:
					return self.insertRec(value, node.right, c)
			if q.y == c:
				if q.x > value.x:
					return self.insertRec(value, node.left, c)
				else:
					return self.insertRec(value, node.right, c)
			###

			x = self.parabolaIntersectX(p,q,c)
			if value.x <= x:
				return self.insertRec(value, node.left, c)
			else:
				return self.insertRec(value, node.right, c)

	def insertRecOrig(self, value, node, c):
		if node.right is None and node.left is None: # é uma folha
			if node.value.y == value.y:
				newnode = TNode([node.value, value])
				newnode.parent = node.parent
				newnode.balance = 0
				node.parent = newnode

				newnode3 = TNode(value)
				newnode3.parent = newnode
				if node.value.x < value.x:
					newnode.left = node
					newnode.right = newnode3
				else:
					newnode.left = newnode3
					newnode.right = node
				return [[], None, []]

			stp = None
			nxNone = self.next_leaf(node)
			pvNone = self.prev_leaf(node)
			nxRem = False
			pvRem = False
			# p = node.value
			# q = value
			# x0 = value.x
			# if p.y == q.y:
			# 	yv = p.y
			# else:
			# 	yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
			# initial = Ponto(x0,yv)
			if (nxNone is None or pvNone is None) and 1+1==3:
				if nxNone is None:
					x0 = self.bounds["maxx"]
					yv = 0
					p = node.value
					q = value
					if(p.x == q.x):
						stp = Ponto(self.bounds["maxx"],(p.y+q.y)/2)
						nxRem = True
					else:
						yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
						if yv > q.y:
							stp = Ponto(x0,yv)
							nxRem = True
				if pvNone is None:
					x0 = self.bounds["minx"]
					yv = 0
					p = node.value
					q = value
					if(p.x == q.x):
						stp = Ponto(self.bounds["minx"],(p.y+q.y)/2)
						pvRem = True
					else:
						yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
						if yv > q.y:
							stp = Ponto(x0,yv)
							pvRem = True

			else:
				stpy = (((node.value.x-value.x)*(node.value.x-value.x)) + ((node.value.y)*(node.value.y)) - (value.y*value.y))/(2*(node.value.y - value.y))
				stp = Ponto(value.x, stpy)

			if nxRem or pvRem: #adiciona pontos infinitos, ajusta a arvore
				if nxRem and pvRem: # corte horizontal, a arv tinha so a raiz, que é removida
					newnode = TNode(value)
					self.root = newnode
					control.plot_line(self.bounds["minx"],stp.y,self.bounds["maxx"],stp.y)
					return [[], None, []]
				else:
					if nxRem:
						removeEvent = node
						newnode2 = TNode([node.value,value])
						newnode2.parent = node.parent
						rleaf = TNode(value)
						#lleaf = TNode(node.value)
						#lleaf.parent = newnode2
						rleaf.parent = newnode2
						newnode2.left = node
						newnode2.right = rleaf
						node.parent = newnode2
						if newnode2.parent is not None:
							if newnode2.parent.left == node:
								newnode2.parent.left = newnode2
							else:
								newnode2.parent.right = newnode2
						newnode2.startp = stp
						if self.root == node:
							self.root = newnode2

						circleevents = []
						# Encontra o node 'anterior', para termos as triplas que determinam eventos-circulo
						cnode = newnode2
						cnode = self.prev_leaf(cnode)
						if cnode is not None:
							lp = self.circleLowerPoint(cnode.value, node.value, value)
							if lp is None:
								node.event = None
							else:
								lp.leaf = node
								node.event = lp #.y
								circleevents.append(node)
						else:
							p = newnode2.value[0]
							q = newnode2.value[1]
							x0 = self.bounds["minx"]
							yv = 0
							pt = None
							if(p.y == q.y):
								pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
							else:
								yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
								pt = Ponto(x0,yv,isPonto=False)
							pt.leaf = node
							pt.isInf = True
							#node.startp = initial
							node.event = pt
							circleevents.append(node)

						arc = []

						####
						#Propagar as mudanças de balance
						#Balancear!!
						####

						return [circleevents, removeEvent, arc]
					else:
						removeEvent = node
						newnode2 = TNode([value, node.value])
						newnode2.parent = node.parent
						lleaf = TNode(value)
						rleaf = node
						lleaf.parent = newnode2
						rleaf.parent = newnode2
						newnode2.left = lleaf
						newnode2.right = rleaf
						if newnode2.parent is not None:
							if newnode2.parent.left == node:
								newnode2.parent.left = newnode2
							else:
								newnode2.parent.right = newnode2
						newnode2.startp = stp
						if self.root == node:
							self.root = newnode2

						cnode = newnode2
						circleevents = []
						cnode = self.next_leaf(cnode)
						if cnode is not None:
							lp = self.circleLowerPoint(cnode.value, node.value, value)
							if lp is None:
								rleaf.event = None
							else:
								lp.leaf = rleaf
								rleaf.event = lp #.y
								circleevents.append(rleaf)
						else:
							p = newnode2.value[0]
							q = newnode2.value[1]
							x0 = self.bounds["maxx"]
							yv = 0
							pt = None
							if(p.y == q.y):
								pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
							else:
								yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
								pt = Ponto(x0,yv,isPonto=False)
							pt.leaf = rleaf
							pt.isInf = True
							#node.startp = initial
							rleaf.event = pt
							circleevents.append(rleaf)

						arc = []

						####
						#Propagar as mudanças de balance
						#Balancear!!
						####

						return [circleevents, removeEvent, arc]


			else: 
				removeEvent = node # Armazena o evento circulo do arco
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

				p = node.value
				q = value

				stpy = (q.y*q.y - (p.x-q.x)*(p.x-q.x) - p.y*p.y)/(2*(q.y-p.y))
				stp = Ponto(q.x,stpy)

				newnode.startp = stp
				newnode2.startp = stp

				if self.root == node:
					self.root = node.parent

				# Encontra o 'próximo' node, para termos as triplas que determinam eventos-circulo
				cnode = newnode
				circleevents = []
				# while cnode.parent is not None:
				# 	if cnode == cnode.parent.left:
				# 		cnode = cnode.parent.right
				# 		while cnode.left is not None:
				# 			cnode = cnode.left
				# 		break
				# 	cnode = cnode.parent
				cnode = self.next_leaf(cnode)
				if cnode is not None:
					lp = self.circleLowerPoint(cnode.value, node.value, value)
					if lp is None:
						rleaf.event = None
					else:
						lp.leaf = rleaf
						rleaf.event = lp #.y
						circleevents.append(rleaf)
						#circleevents.append([cnode.value, node.value, value])
				else:
					p = newnode2.value[0]
					q = newnode2.value[1]
					x0 = self.bounds["maxx"]
					yv = 0
					pt = None
					if(p.y == q.y):
						pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
					else:
						yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
						pt = Ponto(x0,yv,isPonto=False)
					pt.leaf = rleaf
					pt.isInf = True
					#node.startp = initial
					rleaf.event = pt
					circleevents.append(rleaf)

				# Encontra o node 'anterior', para termos as triplas que determinam eventos-circulo
				cnode = newnode
				# while cnode.parent is not None:
				# 	if cnode == cnode.parent.right:
				# 		cnode = cnode.parent.left
				# 		while cnode.right is not None:
				# 			cnode = cnode.right
				# 		break
				# 	cnode = cnode.parent
				cnode = self.prev_leaf(cnode)
				if cnode is not None:
					lp = self.circleLowerPoint(cnode.value, node.value, value)
					if lp is None:
						node.event = None
					else:
						lp.leaf = node
						node.event = lp #.y
						circleevents.append(node)
						#circleevents.append([cnode.value, node.value, value])
				else:
					p = newnode.value[0]
					q = newnode.value[1]
					x0 = self.bounds["minx"]
					yv = 0
					pt = None
					if(p.y == q.y):
						pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
					else:
						yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
						pt = Ponto(x0,yv,isPonto=False)
					pt.leaf = node
					pt.isInf = True
					#node.startp = initial
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

			# Casos degenerados - Comparar com um ponto sobre a linha de varredura
			if p.y == c:
				if p.x > value.x:
					return self.insertRec(value, node.left, c)
				else:
					return self.insertRec(value, node.right, c)
			if q.y == c:
				if q.x > value.x:
					return self.insertRec(value, node.left, c)
				else:
					return self.insertRec(value, node.right, c)
			###

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
		if p.y == q.y:
			return (p.x+q.x)/2
		
		eqa = (1/(p.y-c) - 1/(q.y-c))
		eqb = 2*(q.x/(q.y-c) - p.x/(p.y-c))
		eqc = (((p.x*p.x+p.y*p.y-c*c)/(p.y-c)) - ((q.x*q.x+q.y*q.y-c*c)/(q.y-c)))

		delta = eqb*eqb - 4*eqa*eqc
		sqdelta = math.sqrt(delta) # Não deveria ser possível o delta ser negativo neste algoritmo

		x1 = (-eqb + sqdelta)/(2*eqa)
		x2 = (-eqb - sqdelta)/(2*eqa)

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
		cnode = leaf
		prox = None
		proxn = None
		ant = None
		antn = None
		while cnode.parent is not None:
			if cnode == cnode.parent.left:
				cnode = cnode.parent.right
				while cnode.left is not None:
					cnode = cnode.left
				break
			cnode = cnode.parent
		if cnode.left is None:
			prox = cnode.value
			proxn = cnode

		cnode = leaf
		while cnode.parent is not None:
			if cnode == cnode.parent.right:
				cnode = cnode.parent.left
				while cnode.right is not None:
					cnode = cnode.right
				break
			cnode = cnode.parent
		if cnode.right is None:
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
		# 		x0 = self.bounds["maxx"]
		# 		yv = 0
		# 		pt = None
		# 		if(p.y == q.y):
		# 			pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
		# 		else:
		# 			yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
		# 			pt = Ponto(x0,yv,isPonto=False)
		# 		pt.leaf = antn
		# 		pt.isInf = True
		# 		antn.event = pt
		# 		antn.startp = parent.startp
		# 		circleevents.append(antn)
		# if proxn is not None:
		# 	parent = proxn.parent
		# 	if parent is not None: #Acho que é impossivel que seja None
		# 		p = parent.value[0]
		# 		q = parent.value[1]
		# 		x0 = self.bounds["minx"]
		# 		yv = 0
		# 		pt = None
		# 		if(p.y == q.y):
		# 			pt = Ponto((p.x+q.x)/2,self.bounds["miny"])
		# 		else:
		# 			yv = ((q.x-x0)*(q.x-x0) + q.y*q.y - (p.x-x0)*(p.x-x0) - p.y*p.y)/(2*(q.y-p.y))
		# 			pt = Ponto(x0,yv,isPonto=False)
		# 		pt.leaf = proxn
		# 		pt.isInf = True
		# 		proxn.event = pt
		# 		proxn.startp = parent.startp
		# 		circleevents.append(proxn)

		return [pred,suc,novo,circleevents]

	def remove(self, leaf):
		cnode = leaf
		prox = None
		proxn = None
		ant = None
		antn = None
		while cnode.parent is not None:
			if cnode == cnode.parent.left:
				cnode = cnode.parent.right
				while cnode.left is not None:
					cnode = cnode.left
				break
			cnode = cnode.parent
		if cnode.left is None:
			prox = cnode.value
			proxn = cnode

		cnode = leaf
		while cnode.parent is not None:
			if cnode == cnode.parent.right:
				cnode = cnode.parent.left
				while cnode.right is not None:
					cnode = cnode.right
				break
			cnode = cnode.parent
		if cnode.right is None:
			ant = cnode.value
			antn = cnode

		if ant == prox:
			print('collapse')
			if ant is None and prox is None:
				print("----a")
			#ant = None
			#prox = None

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
		else:
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

	# Remove a folha leaf, e as linhas de quebra referentes ao arco de leaf. c é a y-coord da linha de varredura
	def removeOrig(self, leaf):
		print("removing")
		print(leaf.value.x,leaf.value.y)
		self.test_r2lprint()



		cnode = leaf
		prox = None
		proxn = None
		ant = None
		antn = None
		while cnode.parent is not None:
			if cnode == cnode.parent.left:
				cnode = cnode.parent.right
				while cnode.left is not None:
					cnode = cnode.left
				break
			cnode = cnode.parent
		if cnode.left is None:
			prox = cnode.value
			proxn = cnode

		cnode = leaf
		while cnode.parent is not None:
			if cnode == cnode.parent.right:
				cnode = cnode.parent.left
				while cnode.right is not None:
					cnode = cnode.right
				break
			cnode = cnode.parent
		if cnode.right is None:
			ant = cnode.value
			antn = cnode

		if ant == prox:
			print('collapse')
			if ant is None and prox is None:
				print("----a")
			#ant = None
			#prox = None

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
		else:
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
		return [pred,suc,novo]

	def atualiza_eventos(self,novo):
		print("atualiza")
		circleevents = []
		p = novo.value[0]
		q = novo.value[1]

		#nxt = self.next_leaf(q)
		#ant = self.prev_leaf(p)
		nxt = self.next_leaf(novo)
		ant = self.prev_leaf(novo)
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
				q_leaf.event = lp #.y
				circleevents.append(q_leaf)
		if ant is not None:
			p_leaf = self.next_leaf(ant)
			lp = self.circleLowerPoint(ant.value, p, q)
			if lp is None:
				p_leaf.event = None
			else:
				lp.leaf = p_leaf
				p_leaf.event = lp #.y
				circleevents.append(p_leaf)
		return circleevents

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



# bl = BeachLine()
# p = Ponto(1,1)
# bl.insert(p, 2)
# q = Ponto(1,2)
# y = bl.insert(q, 3)
# q = Ponto(1,3)
# bl.insert(q, 4)
# q = Ponto(1,4)
# x = bl.insert(q, 5)

# print(x[0])

# leaf = x[2][2].right

# print(bl.remove(leaf))
# leaf2 = y[2][2].right
# #bl.test_r2lprint()
# print(bl.remove(leaf2))
# bl.test_r2lprint()

#x^2 - 2xx0 + x0^2 - 2yy0 + y0^2 + 2yc - c^2 = 0
#x^2 - 2xx1 + x1^2 - 2yy1 + y1^2 + 2yc - c^2 = 0

#x^2 - 2xx0 + x0^2 + y0^2 - c^2 = 2y(y0-c)
#x^2 - 2xx1 + x1^2 + y1^2 - c^2 = 2y(y1-c)

#(x^2 - 2xx0 + x0^2 + y0^2 - c^2)/2(y0-c) = y
#(x^2 - 2xx1 + x1^2 + y1^2 - c^2)/2(y1-c) = y


#(x^2 - 2xx0 + x0^2 + y0^2 - c^2)/(y0-c) = (x^2 - 2xx1 + x1^2 + y1^2 - c^2)/(y1-c)

#(1/(y0-c) - 1/(y1-c))x^2 + (2x1/(y1-c) - 2x0/(y0-c))x + ((x0^2+y0^2-c^2)/(y0-c) - (x1^2+y1^2-c^2)/(y1-c))