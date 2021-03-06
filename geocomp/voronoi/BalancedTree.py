import math
import copy
from .Queue import Ponto
from geocomp.common.guiprim import *
from geocomp.common import control

# Area do triângulo formado por 3 pontos com sinal.
def area(a,b,c):
	return ((a.x-c.x)*(b.y-c.y)-(a.y-c.y)*(b.x-c.x))/2

# Nó da árvore
class TNode:
	def __init__(self, value):
		self.left = None
		self.right = None
		self.parent = None
		self.balance = 0
		self.value = value # par de pontos [p,q] caso seja nó interno, e um ponto s caso seja folha
		self.event = None # Evento circulo relacionado ao arco
		self.startp = None # Ponto inicial da linha a ser desenhada
		self.still = True
		self.pair = None # Deprecated. Usado em algumas funções de teste

	def __str__(self):
		if isinstance(self.value, list):
			return str(self.value[0].x) + " " + str(self.value[0].y) + " " + str(self.value[1].x) + " " + str(self.value[1].y)
		else:
			return str(self.value.x) + " " + str(self.value.y)

# Linha da praia
class BeachLine:
	def __init__(self):
		self.root = None
		self.bounds = None
		self.llist = []
		self.rlist = []
		self.dlist = []

	# Encontra o 'próximo' node
	def next_leaf(self,node):
		if node is None:
			return None
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
		if node is None:
			return None
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

	# Insere um ponto (parábola) na árvore
	def insere(self,value,c):
		if self.root is None:
			self.root = TNode(value)
			return [[], None, []]
		else:
			return self.insereRec(value, self.root, c)

	def insereRec(self, value, node, c):
		if node.right is None and node.left is None:
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

			# Atualiza o apontador da raiz, caso seja necessário
			if self.root == node:
				self.root = node.parent

			circleevents = []
			# Encontra o 'próximo' node, para termos as triplas que determinam eventos-circulo
			cnode = self.next_leaf(newnode2)
			if cnode is not None:
				lp = self.circleLowerPoint(cnode.value, node.value, value)
				if lp is not None:
					if lp.x >= value.x:
						lp.leaf = rleaf
						rleaf.event = lp 
						circleevents.append(rleaf)

			# Encontra o node 'anterior', para termos as triplas que determinam eventos-circulo
			cnode = self.prev_leaf(newnode)
			if cnode is not None:
				lp = self.circleLowerPoint(cnode.value, node.value, value)
				if lp is not None:
					if lp.x <= value.x:
						lp.leaf = node
						node.event = lp
						circleevents.append(node)

			####
			#Propagar as mudanças de balance
			node = newnode
			c_height = 2
			while node.parent is not None:
				if node.parent.left == node:
					node.parent.balance = node.parent.balance - c_height
					if node.parent.balance + c_height >= 0:
						if node.parent.balance >= 0:
							c_height = 0
						else:
							c_height = -node.parent.balance
				else:
					node.parent.balance = node.parent.balance + c_height
					if node.parent.balance - c_height <= 0:
						if node.parent.balance <= 0:
							c_height = 0
						else:
							c_height = node.parent.balance
				node = node.parent

			# Balanceamento
			bnode = newnode.parent
			while bnode is not None:
				if bnode.balance > 1 or bnode.balance < -1:
					self.rebalance(bnode)
				bnode = bnode.parent
			####

			arc = [newnode, lleaf, newnode2]

			return [circleevents, removeEvent, arc]

		# Buscando na árvore a posição para inserir o ponto
		else:
			p = node.value[0]
			q = node.value[1]

			x = self.parabolaIntersectX(p,q,c)
			if value.x <= x:
				return self.insereRec(value, node.left, c)
			else:
				return self.insereRec(value, node.right, c)


	# Remove um nó da árvore
	def remove_circ(self, leaf):
		prox = None
		proxn = None
		ant = None
		antn = None
		if not leaf.still:
			return [None, None, None]
		leaf.still = False
		cnode = self.next_leaf(leaf)
		if cnode is not None:
			prox = cnode.value
			proxn = cnode

		cnode = self.prev_leaf(leaf)
		if cnode is not None:
			ant = cnode.value
			antn = cnode

		# Os nós internos a serem removidos são (leaf.value, prox) e (ant, leaf.value)

		pred = None
		suc = None
		novo = None

		if prox is not None:
			suc = TNode([leaf.value, prox])
		else:
			return [None,None,None]
		if ant is not None:
			pred = TNode([ant,leaf.value])
		else:
			return [None,None,None]
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

			# Remove o ponto, e atualiza os apontadores
			if low is None or high is None:
				print('Erro. low ou high é None, ambos deviam ter valor')
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

			# Rebalanceia a árvore
			bnode = nroot
			variation = -1
			while bnode.parent is not None:
				if bnode.parent.left == bnode:
					bnode.parent.balance = bnode.parent.balance - variation
					if bnode.parent.balance + variation >= 0:
						variation = 0
				else:
					bnode.parent.balance = bnode.parent.balance + variation
					if bnode.parent.balance - variation <= 0:
						variation = 0
				bnode = bnode.parent
			bnode = nroot.parent
			while bnode is not None:
				if bnode.balance > 1 or bnode.balance < -1:
					self.rebalance(bnode)
				bnode = bnode.parent

		# Retorna os nós internos das divisões que sumiram, e a divisão nova.
		# Precisa adicionar os eventos circulo da divisão nova (novo[0], novo[1], prox(novo[1])) (ant(novo[0]),novo[0],novo[1])
		return [pred,suc,high]

	# Após tratar um evento-círculo, busca novos eventos círculo que podem ter surgido.
	def atualiza_eventos_circ(self,novo,liney,apred,asuc):
		circleevents = []
		removeevents = []
		p = novo.value[0]
		q = novo.value[1]

		nxt = novo.right
		while nxt.left is not None:
			nxt = nxt.left
		ant = novo.left
		while ant.right is not None:
			ant = ant.right
		nxt = self.next_leaf(nxt)
		ant = self.prev_leaf(ant)
		stp = novo.startp
		if (nxt is not None) and (nxt.value == p):
			nxt = self.next_leaf(nxt)
			ant = self.prev_leaf(ant)
			r = p
			p = q
			q = r
		if nxt is not None and (nxt.value == p or nxt.value == q or nxt.value == apred.value[1]):
			nxt = None
		if ant is not None and (ant.value == p or ant.value == q or ant.value == apred.value[1]):
			ant = None
		# Procura o 'próximo' evento círculo
		if nxt is not None:
			q_leaf = self.prev_leaf(nxt)
			lp = self.circleLowerPoint(nxt.value, p, q)
			if lp is not None:
				if lp.center.x >= novo.startp.x:
					if q_leaf.event is not None:
						removeevents.append(q_leaf.event)
					lp.leaf = q_leaf
					q_leaf.event = lp
					circleevents.append(q_leaf)
		
		# Procura o evento-círculo 'anterior'
		if ant is not None:
			p_leaf = self.next_leaf(ant)
			lp = self.circleLowerPoint(ant.value, p, q)
			if lp is not None:
				if lp.center.x <= novo.startp.x:
					if p_leaf.event is not None:
						removeevents.append(p_leaf.event)
					lp.leaf = p_leaf
					p_leaf.event = lp
					circleevents.append(p_leaf)

		return circleevents,removeevents



	# Rebalanceia um nó por meio de rotações. Leva em conta o balance do nó para o rebalanceamento.
	# É possível que o balanço de um nó fique em [-3,+3], pela forma que a inserção funciona
	# Invariante: Todos os nós nas sub-árvores de node estão balanceados
	def rebalance(self, node):
		nnode = None
		if node.balance == 2:
			if node.right.balance >= 0:
				nnode = node.right
				if node.right.balance == 0:
					node.balance = 1
					node.right.balance = -1
					self.rotate_left(node)
				else:
					node.balance = 0
					node.right.balance = 0
					self.rotate_left(node)
					self.propagate(nnode)
			else:
				x = node
				y = x.right
				z = y.left
				zb = z.balance
				nnode = z
				if zb == 1:
					x.balance = -1
				else:
					x.balance = 0
				if zb == -1:
					y.balance = 1
				else:
					y.balance = 0
				z.balance = 0
				self.rotate_right(y)
				self.rotate_left(x)
				self.propagate(nnode)
			return
		if node.balance == 3:
			x = node
			y = x.right
			yb = y.balance
			nnode = y
			if yb == 0:
				x.balance = 2
				y.balance = -1
				self.rotate_left(x)
				self.rebalance(node)
			if yb == 1:
				x.balance = 1
				y.balance = 0
				self.rotate_left(x)
				self.propagate(nnode)
			if yb == -1:
				x.balance = 2
				y.balance = -2
				self.rotate_left(x)
				self.rebalance(node)
				self.rebalance(y)
			return
		if node.balance == -2:
			if node.left.balance <= 0:
				nnode = node.left
				if node.left.balance == 0:
					node.left.balance = 1
					node.balance = -1
					self.rotate_right(node)
				else:
					node.left.balance = 0
					node.balance = 0
					self.rotate_right(node)
					self.propagate(nnode)
			else:
				x = node
				y = x.left
				z = y.right
				zb = z.balance
				nnode = z
				if zb == 1:
					y.balance = -1
				else:
					y.balance = 0
				if zb == -1:
					x.balance = 1
				else:
					x.balance = 0
				z.balance = 0
				self.rotate_left(y)
				self.rotate_right(x)
				self.propagate(nnode)
			return
		if node.balance == -3:
			x = node
			y = x.left
			yb = y.balance
			nnode = y
			if yb == 0:
				x.balance = -2
				y.balance = 1
				self.rotate_right(x)
				self.rebalance(x)
			if yb == 1:
				x.balance = -2
				y.balance = 2
				self.rotate_right(x)
				self.rebalance(x)
				self.rebalance(y)
			if yb == -1:
				x.balance = -1
				y.balance = 0
				self.rotate_right(x)
				self.propagate(nnode)
			return

	# Rotação para a esquerda
	def rotate_left(self,node):
		if node.right is None: # Não é possível rodar para a esquerda
			print("Operação inválida (rotate_left)")
			return

		rchild = node.right
		lsub = rchild.left
		nparent = node.parent

		node.parent = rchild
		rchild.left = node
		node.right = lsub
		if lsub is not None:
			lsub.parent = node
		rchild.parent = nparent
		if nparent is None:
			self.root = rchild
		else:
			if nparent.left == node:
				nparent.left = rchild
			else:
				nparent.right = rchild

	# Rotação para a direita
	def rotate_right(self,node):
		if node.left is None: # Não é possível rodar para a direita
			print("Operação inválida (rotate_right)")
			return

		lchild = node.left
		rsub = lchild.right
		nparent = node.parent

		node.parent = lchild
		lchild.right = node
		node.left = rsub
		if rsub is not None:
			rsub.parent = node
		lchild.parent = nparent
		if nparent is None:
			self.root = lchild
		else:
			if nparent.left == node:
				nparent.left = lchild
			else:
				nparent.right = lchild

	# Função auxiliar do balanceamento. Propaga as mudanças de balance após os balanceamentos
	def propagate(self,node):
		variation = 1
		while node.parent is not None:
			if node.parent.left == node:
				node.parent.balance = node.parent.balance + variation
				if node.parent.balance - variation >= 0:
					variation = 0
			else:
				node.parent.balance = node.parent.balance - variation
				if node.parent.balance + variation <= 0:
					variation = 0
			node = node.parent

	# Cria a árvore inicial no caso de mais de um ponto estar na mesma horizontal, e serem os primeiros pontos encontrados
	def create_particular(self, vec):
		self.root, dummy = self.create_particular_rec(vec)

	def create_particular_rec(self, vec):
		n = len(vec)
		if n == 1:
			return TNode(vec[0]),1
		mid = int((n-1)/2)
		newnode = TNode([vec[mid],vec[mid+1]])
		newnode.startp = Ponto((vec[mid].x+vec[mid+1].x)/2,self.bounds["maxy"])
		lvec = vec[:mid+1]
		rvec = vec[mid+1:]
		lroot, lh = self.create_particular_rec(lvec)
		rroot, rh = self.create_particular_rec(rvec)
		newnode.balance = rh-lh
		newnode.left = lroot
		newnode.right = rroot
		lroot.parent = newnode
		rroot.parent = newnode
		hret = max(lh,rh)+1
		return newnode, hret
			

	# Funções de busca - Não usadas no projeto	
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

	# Encontra a x-coordenada na intersecção de duas parabolas. Perceba que a ordem de p e q devem estar em ordem (p deve descrever a parábola a esquerda da parábola de q)
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

		xm = (x1+x2)/2
		yp = ((p.x-xm)*(p.x-xm) + p.y*p.y - c*c)/(2*(p.y-c))
		yq = ((q.x-xm)*(q.x-xm) + q.y*q.y - c*c)/(2*(q.y-c))

		if yp < yq:
			return x2
		return x1

	# Determina o círculo que contém 3 pontos, seu ponto mais baixo e seu centro
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

	# Determina se a parábola mais a esquerda está fora da região visível
	def left_out(self,c):
		node = self.root
		if node is None:
			return False
		while node.left is not None:
			node = node.left
		nnode = self.next_leaf(node)
		if nnode is not None:
			x = self.parabolaIntersectX(node.value,nnode.value,c)
			if x < self.bounds["minx"]:
				return True
		return False

	# Determina se a parábola mais a direita está fora da região visível
	def right_out(self,c):
		node = self.root
		if node is None:
			return False
		while node.right is not None:
			node = node.right
		nnode = self.prev_leaf(node)
		if nnode is not None:
			x = self.parabolaIntersectX(nnode.value,node.value,c)
			if x > self.bounds["maxx"]:
				return True
		return False

	# Remove a parábola da esquerda, e rebalanceia a árvore
	def remove_left(self):
		node = self.root
		while node.left is not None:
			node = node.left
		node.still = False
		node.parent.stll = False
		ev = node.event
		node = node.parent
		self.llist.append(node.value)
		if node == self.root:
			self.root = node.right
			self.root.parent = None
		else:
			node.right.parent = node.parent
			node.parent.left = node.right
			bnode = node.parent.left
			variation = -1
			while bnode.parent is not None:
				if bnode.parent.left == bnode:
					bnode.parent.balance = bnode.parent.balance - variation
					if bnode.parent.balance + variation >= 0:
						variation = 0
				else:
					bnode.parent.balance = bnode.parent.balance + variation
					if bnode.parent.balance - variation <= 0:
						variation = 0
				bnode = bnode.parent
			bnode = node.parent
			while bnode is not None:
				if bnode.balance > 1 or bnode.balance < -1:
					self.rebalance(bnode)
				bnode = bnode.parent
		return ev

	# Remove a parábola da direita, e rebalanceia a árvore
	def remove_right(self):
		node = self.root
		while node.right is not None:
			node = node.right
		node.still = False
		node.parent.still = False
		ev = node.event
		node = node.parent
		self.rlist.append(node.value)
		if node == self.root:
			self.root = node.left
			self.root.parent = None
		else:
			node.left.parent = node.parent
			node.parent.right = node.left
			bnode = node.parent.right
			variation = -1
			while bnode.parent is not None:
				if bnode.parent.left == bnode:
					bnode.parent.balance = bnode.parent.balance - variation
					if bnode.parent.balance + variation >= 0:
						variation = 0
				else:
					bnode.parent.balance = bnode.parent.balance + variation
					if bnode.parent.balance - variation <= 0:
						variation = 0
				bnode = bnode.parent
			bnode = node.parent
			while bnode is not None:
				if bnode.balance > 1 or bnode.balance < -1:
					self.rebalance(bnode)
				bnode = bnode.parent
		return ev

	# Função que remove as parábolas que sairam da região visível
	def trata_extremos(self,c):
		if self.root is None:
			return
		evlist = []
		while self.left_out(c):
			ev = self.remove_left()
			if ev is not None:
				evlist.append(ev)
		while self.right_out(c):
			ev = self.remove_right()
			if ev is not None:
				evlist.append(ev)
		return evlist


	# Desenha as parábolas da linha da praia
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

	# Desenha as arestas parciais.
	def draw_partial(self,c):
		if self.root is None:
			return []
		return self.draw_partial_rec(c,self.root)

	def draw_partial_rec(self,c,node):
		if node.left is None or node.right is None:
			return
		p = node.value[0]
		q = node.value[1]
		x = self.parabolaIntersectX(p,q,c)
		id_list = []
		if p.y != c:
			y = (p.x*p.x - 2*p.x*x + x*x + p.y*p.y - c*c)/(2*(p.y-c))
			line_id = control.plot_segment(x,y,node.startp.x,node.startp.y)
			id_list = [line_id]
		id_list.append(self.draw_partial_rec(c,node.left))
		id_list.append(self.draw_partial_rec(c,node.right))
		return id_list

	# Função de teste: Imprime a árvore
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
			print(r,r.balance)
			self.test_r2lprintrec(r.right)
			return

	# Função de teste. Imprime a árvore por uma busca BFS. E checa se o baçanceamento está correto
	def test_bfsprint(self):
		if self.root is None:
			return
		self.test_consistentBalance()
		stk = [[] for i in range(20)]
		stk[0].append(self.root)
		t = False
		print("vvvv")
		for i in range(20):
			print("----")
			for p in stk[i]:
				print(p,p.balance)
				if p.left is not None:
					stk[i+1].append(p.left)
					stk[i+1].append(p.right)
					if p.right.pair-p.left.pair != p.balance:
						print('inconsistence!!!!!!!!!!!!!')
						t = True
		if t:
			print("Inconsistente")
		print("^^^^")

	def test_consistentBalance(self):
		if self.root is None:
			return True
		self.test_height(self.root)

	def test_height(self,node):
		if node is None:
			return -1
		h = max(self.test_height(node.left)+1,self.test_height(node.right)+1)
		node.pair = h
		return h