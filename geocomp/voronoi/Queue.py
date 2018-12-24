from heapq import *
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point


class Ponto:
	
	def __init__(self, x, y, isPonto = True, leaf = None, center = None):
		self.x = x
		self.y = y
		self.isPonto = isPonto
		self.leaf = leaf
		self.center = center

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y and self.isPonto == other.isPonto

	def __ne__(self, other):
		return not (self == other)

	def __lt__(self, other):
		if self.y < other.y or self.x < other.x or (self.isPonto and not other.isPonto):
			return True
		return False

	def __gt__(self, other):
		return not self < other


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
		self.n = 0
		self.fila = []
		self.isIn = {}

	def put(self, item, key):
		if (-key.x, -key.y) in self.isIn:
			if type(self.isIn[(-key.x, -key.y)][-1]) is bool and self.isIn[(-key.x, -key.y)][2].isPonto:
				return
			else:
				self.n+=1
				inv = [-item.y, -item.x, item, True]
				if type(self.isIn[(-key.x, -key.y)][-1]) is bool:
					self.isIn[(-key.x, -key.y)] = [self.isIn[(-key.x, -key.y)], inv]
				else:
					self.isIn[(-key.x, -key.y)].append(inv)
				heappush(self.fila, inv)
				return
		self.n += 1
		inv = [-item.y, -item.x, item, True]
		self.isIn[(-key.x, -key.y)] = inv
		heappush(self.fila, inv)

	def take(self, key):
		if (-key.x, -key.y) not in self.isIn:
			return
		taken = self.isIn.pop((-key.x, -key.y))
		if type(taken[-1]) is bool:
			taken[-1] = False
		else:
			taken[0][-1] = False
			aux = []
			for i in range(1, len(taken)):
				aux.append(taken[i])
			if len(aux) == 1:
				self.isIn[(-key.x, -key.y)] = aux[0]
			else:
				self.isIn[(-key.x, -key.y)] = aux
		self.n -= 1

	def takeHighest(self):
		while self.fila:
			item = heappop(self.fila)
			key = item[2]
			if item[-1]:
				self.n -= 1
				if type(self.isIn[(-key.x, -key.y)][-1]) is bool:
					del self.isIn[(-key.x, -key.y)]
				else:
					aux = []
					for i in range(1, len(self.isIn[(-key.x, -key.y)])):
						aux.append(self.isIn[(-key.x, -key.y)][i])
					if len(aux) == 1:
						self.isIn[(-key.x, -key.y)] = aux[0]
					else:
						self.isIn[(-key.x, -key.y)] = aux
				return key
