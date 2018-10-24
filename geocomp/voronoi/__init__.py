# -*- coding: utf-8 -*-

"""Algoritmos para o Problema do Fecho Convexo:

Dado um conjunto de pontos, determinar o seu fecho convexo.

Algoritmos disponiveis:
- Graham
- Embrulho Para Presente
- Quick Hull
- Incremental Probabilistico
- Merge Hull
- Um algoritmo otimo proposto por Chan
- Um algoritmo otimo proposto por Bhattacharya e Sen

algoritmo otimo = executa em tempo O(n lg(h)), n = numero de pontos, 
                                               h = numero de arestas no fecho
"""
from . import DelaunayVoronoi

# cada entrada deve ter:
#  [ 'nome-do-modulo', 'nome-da-funcao', 'nome do algoritmo' ]
children = [ 
	[ 'DelaunayVoronoi', 'fortune', 'Fortune+Delaunay' ]
]

#children = algorithms

#__all__ = [ 'graham', 'gift' ]
__all__ = [a[0] for a in children]
