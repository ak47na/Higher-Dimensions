from networkx import*
from queue import Queue

from networkx.algorithms.structuralholes import mutual_weight, normalized_mutual_weight

'''
    A Monoplex object extends the functionality of a networkx graph:
    -> implements effective size for directed networks
    -> implements reachability: reachability(i) = the number of nodes that can be reached from i.
    -> implements hierarchy(ij) = (Cij / (C/N))
    https://www.jstor.org/stable/pdf/10.1086/421787.pdf?refreqid=excelsior%3Aac83f85bfac62c3d4d8c762408b02ef2
    page 15/52 or 362
    https://www.researchgate.net/publication/281206574_Structural_Holes?enrichId=rgreq-c51b445fe2f7cc6ae1b0ba53d4df5994-XXX&enrichSource=Y292ZXJQYWdlOzI4MTIwNjU3NDtBUzoyNjU5ODAyNTc1MDExODRAMTQ0MDQyNjA0MzYzNg%3D%3D&el=1_x_3&_esc=publicationCoverPdf
'''
class Monoplex:
    def __init__(self, G, isDirected_, weightStr_):
        self.G = G
        self.isDirected = isDirected_
        self.nodes = list(G.nodes)
        if weightStr_ == None:
            self.Edges = list(G.edges)
        else:
            self.Edges = list(G.edges.data(weightStr_))
        self.weightStr = weightStr_
        self.wSum = {}
        self.N = {}
        self.Adj = {}
        self.getAdjList()
        self.Constr = constraint(self.G)
        self.precomputeNeighbourhood()
        self.precomputeMutualWeights()

    '''
        Adds an directed edge from node u to v with weight.
    '''
    def addEdge(self, weight, u, v):
        self.Adj[u][v] = True
        self.wSum[u] += weight

    '''
        Computes the adjacency matrix as a dictionary of dictionaries for each node u, i.e. 
        Adj[u][v] = True iff there is a directed edge from node u to node v.
    '''
    def getAdjList(self):
        for u in self.nodes:
            self.Adj[u] = {}
            self.wSum[u] = 0
        for e in self.Edges:
            weight = 1
            if self.weightStr != None:
                weight = e[2]
            self.addEdge(weight, e[0], e[1])
            if not(self.isDirected):
                self.addEdge(weight, e[1], e[0])

    '''
        Computes the neighbourhood for node u. 
        TODO: check if the neighbourhood of a node u in a directed graph includes nodes v such that
        there is at least one edge v->u but no edge u->v.
    '''
    def getNeighbourhood(self, u):
        self.N[u] = {}
        self.N[u][u] = False
        for adj in self.Adj[u]:
            self.N[u][adj] = True
        for v in self.nodes:
            if (u in self.Adj[v] and self.Adj[v][u] == True):
                self.N[u][v] = True

    '''
        Computes the neighbourhood of all nodes in the graph.
    '''
    def precomputeNeighbourhood(self):
        self.maxMw = {}
        self.Mw = {}
        self.Pw = {}
        for u in self.nodes:
            if not(u in self.N):
                self.getNeighbourhood(u)

    '''
        Computes the mutual weight (self.Mw[][]) and the normalised mutual wight (self.Pw[][]) for
        each pair of adjacent nodes in the network.
    '''
    def precomputeMutualWeights(self):

        for u in self.nodes:
            # self.maxMw[u] = the maximum mutual weight of u with all its neighbours.
            self.maxMw[u] = 0
            self.Mw[u] = {}
            # self.Mw[u][v] = "the sum of the weights of the edge from `u` to `v` and the edge from
            # `v` to `u` in `G`."
            self.Pw[u] = {}
            # self.Pw[u][v] = "normalized mutual weight of the edges from `u` to `v` with respect to
            # the mutual weights of the neighbors of `u` in `G`."
            for v in self.N[u]:
                self.Mw[u][v] = mutual_weight(self.G, u, v, weight = self.weightStr)
                if self.Mw[u][v] == 0:
                    self.Pw[u][v] = 0
                else:
                    self.Pw[u][v] = normalized_mutual_weight(self.G, u, v, weight=self.weightStr)
                self.maxMw[u] = max(self.maxMw[u], self.Mw[u][v])

    '''
        Returns a dictionary with the effective size value of each node in the network.
    '''
    def getEffectiveSize(self):
        value = {}
        for u in self.nodes:
            value[u] = 0
            for v in self.N[u]:
                if v == u:
                    continue
                value[u] += 1
                for w in self.N[v]:
                    Puw = self.Pw[u][w]
                    if self.maxMw[v] == 0:
                        Mvw = 0
                    else:
                        Mvw = self.Mw[v][w] / self.maxMw[v]
                    value[u] -= Puw * Mvw
        return value

    '''
        Returns a dictionary with the hierarchy value of each node in the network.
        TODO - find formula for Hierarchy.
    '''
    def getHierarhy(self):
        self.H = {}
        self.Hierarchy = {}
        for u in self.nodes:
            self.H[u] = {}
            C = self.Constr[u]
            sizeN = 0
            sum = 0
            for v in self.N[u]:
                sizeN += 1
                self.H[u][v] = local_constraint(self.G, u, v)
            for v in self.H[u]:
                self.H[u][v] = self.H[u][v] * sizeN / C
                sum += self.H[u][v]
            self.Hierarchy[u] = sum / sizeN
        return self.Hierarchy
