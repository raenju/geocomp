
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point


class Ponto:
	
	def __init__(self, x, y, isPonto = True, leaf = None, center = None, isInf = False):
		self.x = x
		self.y = y
		self.isPonto = isPonto
		self.isInf = isInf
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
		self.arr = []
		self.len = -1

	def put(self, item, key):
		self.len += 1
		self.arr.append(None)
		self.findSpot(self.len, item)

	def findSpot(self, i, item):
		self.arr[i] = item
		half = int(i/2)
		while i>1 and self.arr[half].y < self.arr[i].y:
			aux = self.arr[half]
			self.arr[half] = self.arr[i]
			self.arr[i] = aux
			i = half

	def take(self, item):
		for i in self.arr:
			if i == item:
				taken = self.arr[i]
				self.arr[i] = self.arr[self.len]
				self.len -= 1
				self.heapify(i)
				return

	def takeHighest(self):
		if self.len == -1:
			return False
		M = self.arr[0]
		self.arr[0] = self.arr[self.len]
		self.len -= 1
		self.heapify(0)
		return M

	def heapify(self, i):
		l = 2*i
		r = l+1
		Largest = 0
		if l<=self.len and self.arr[l].y > self.arr[i].y:
			Largest = l
		else:
			Largest = i
		if r<=self.len and self.arr[r].y > Largest:
			Largest = r
		if Largest != i:
			aux = self.arr[Largest]
			self.arr[Largest] = self.arr[i]
			self.arr[i] = aux
			self.heapify(Largest)


	"""
	def __init__(self):
		self.root = None
		self.size = 0
		self.d = {}

	def put(self, item, key):
		if self.root is None:
			self.root = Node(item, key)
		else:
			self.putRec(item, key, self.root)

	def take(self, key):
		if self.root is None:
			return False
		if self.root.key == key:
			if self.root.hasRight() and self.root.hasLeft():
				r = self.root.right
				self.putRec(r.item, r.key, self.root.left)
				self.root = self.root.left
			elif self.root.hasLeft():
				self.root = self.root.left
			else:
				self.root = self.root.right
		else:
			self.takeRec(key, self.root)



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
		"""