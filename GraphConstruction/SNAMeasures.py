from networkx import*
from queue import Queue

from networkx.algorithms.structuralholes import mutual_weight, normalized_mutual_weight

'''

a Monoplex object extends the functionality of a networkx graph:
-> implements effective size for directed networks
-> implements reachability 
-> implements hierarchy(ij) = (Cij / (C/N))
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

    def addEdge(self, weight, u, v):
        self.Adj[u][v] = True
        self.wSum[u] += weight

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

    def getNeighbourhood(self, u):
        Q = Queue(maxsize=0)
        Q.put(u)
        self.N[u] = {}
        self.N[u][u] = False
        while (not (Q.empty())):
            nod = Q.get()
            for adj in self.Adj[nod]:
                if not (adj in self.N[u]):
                    self.N[u][adj] = True
                    Q.put(adj)

    def precomputeNeighbourhood(self):
        self.maxMw = {}
        self.Mw = {}
        self.Pw = {}
        for u in self.nodes:
            if not(u in self.N):
                self.maxMw[u] = 0
                self.Mw[u] = {}
                self.Pw[u] = {}
                self.getNeighbourhood(u)
    def precomputeMutualWeights(self):
        for u in self.nodes:
            for v in self.N[u]:
                self.Mw[u][v] = mutual_weight(self.G, u, v, weight = self.weightStr)
                if self.Mw[u][v] == 0:
                    self.Pw[u][v] = 0
                else:
                    self.Pw[u][v] = normalized_mutual_weight(self.G, u, v, weight=self.weightStr)
                self.maxMw[u] = max(self.maxMw[u], self.Mw[u][v])
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
            self.Hierarchy[u] = sum / sizeN #toDo - find formula for Hierarchy
        return self.Hierarchy
