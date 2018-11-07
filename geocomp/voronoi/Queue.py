
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point


class Ponto:
	
	def __init__(self, x, y, isPonto = True, leaf = None, center = None):
		self.x = x
		self.y = y
		self.isPonto = isPonto
		self.isInf = False
		self.leaf = leaf
		self.center = center

class Node:

	def __init__(self, item, key):
		self.item = item
		self.left = None
		self.right = None
		self.key = key

	def hasLeft(self):
		return self.left

	def hasRight(self):
		return self.right


class EventQueue:

	def __init__(self):
		self.root = None
		self.size = 0

	def put(self, item, key):
		if self.root is None:
			self.root = Node(item, key)
		else:
			self.putRec(item, key, self.root)

	def take(self, key):
		if self.root is None:
			return False
		else:
			self.takeRec(key, self.root)
			control.plot_disc (key.x, key.y, config.COLOR_PRIM, 6)
			print("ACÁ")



	def putRec(self, item, key, current):
		if key.y < current.key.y:
			if current.hasLeft():
				self.putRec(item, key, current.left)
			else:
				current.left = Node(item, key)
			return
		if key.y > current.key.y:
			if current.hasRight():
				self.putRec(item, key, current.right)
			else:
				current.right = Node(item, key)
			return
		if key.x < current.key.x:
			if current.hasLeft():
				self.putRec(item, key, current.left)
			else:
				current.left = Node(item, key)
		else:
			if current.hasRight():
				self.putRec(item, key, current.right)
			else:
				current.right = Node(item, key)

	def takeRec(self, key, current):
		if key.y < current.key.y:
			if current.hasLeft():
				if key == current.left.key:
					self.takeOut(current, current.left)
				else:
					self.takeRec(key, current.left)
			else:
				return False
			return
		if key.y > current.key.y:
			if current.hasRight():
				if key == current.right.key:
					self.takeOut(current, current.right)
				else:
					self.takeRec(key, current.right)
			else:
				return False
			return
		if key.x < current.key.x:
			if current.hasLeft():
				if key == current.left.key:
					self.takeOut(current, current.left)
				else:
					self.takeRec(key, current.left)
			else:
				return False
		else:
			if current.hasRight():
				if key == current.right.key:
					self.takeOut(current, current.right)
				else:
					self.takeRec(key, current.right)
			else:
				return False

	def takeOut(self, parent, taken):
		if taken.hasLeft() and taken.hasRight():
			aux = taken.right
			prev = taken
			while aux.hasLeft():
				prev = aux
				aux = aux.left
			if parent.left == taken:
				parent.left = aux
				prev.left = taken
				auxl = taken.left
				auxr = taken.right
				taken.left = aux.left
				taken.right = aux.right
				aux.left = auxl
				aux.right = auxr
				self.takeOut(prev, taken)
			if parent.right == taken:
				parent.right = aux
				prev.left = taken
				auxl = taken.left
				auxr = taken.right
				taken.left = aux.left
				taken.right = aux.right
				aux.left = auxl
				aux.right = auxr
				self.takeOut(prev, taken)
		else:
			if taken.hasLeft():
				if parent.left == taken:
					parent.left = taken.left
				if parent.right == taken:
					parent.right = taken.left
			else:
				if parent.left == taken:
					parent.left = taken.right
				if parent.right == taken:
					parent.right = taken.right
			
	def takeHighest(self):
		if self.root.hasRight():
			prox = None
			parent = self.root
			taken = self.root.right
			while taken.hasRight():
				parent = taken
				taken = taken.right
			if taken.hasLeft():
				prox = taken.left
			parent.right = prox
		else:
			taken = self.root
			self.root = self.root.left
		return taken.item

	def tp(self):
		if self.root is not None:
			self.tpr(self.root)

	def tpr(self,node):
		if node is None:
			return
		self.tpr(node.left)
		print(node.item.x,node.item.y)
		self.tpr(node.right)