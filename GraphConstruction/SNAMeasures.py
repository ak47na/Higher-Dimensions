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
        self.Nbhd = {}
        self.Adj = {}
        self.getAdjList()
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
        self.Nbhd[u] = {}
        self.Nbhd[u][u] = False
        for adj in self.Adj[u]:
            self.Nbhd[u][adj] = True
        for v in self.nodes:
            if (u in self.Adj[v] and self.Adj[v][u] == True):
                self.Nbhd[u][v] = True

    '''
        Computes the neighbourhood of all nodes in the graph.
    '''
    def precomputeNeighbourhood(self):
        self.maxMw = {}
        self.Mw = {}
        self.Pw = {}
        for u in self.nodes:
            if not(u in self.Nbhd):
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
            for v in self.Nbhd[u]:
                self.Mw[u][v] = mutual_weight(self.G, u, v, weight = self.weightStr)
                if self.Mw[u][v] == 0:
                    self.Pw[u][v] = 0
                else:
                    self.Pw[u][v] = normalized_mutual_weight(self.G, u, v, weight=self.weightStr)
                self.maxMw[u] = max(self.maxMw[u], self.Mw[u][v])
    def computeConstraint(self):
        self.constraint = constraint(self.G)

    '''
        Returns a dictionary with the effective size value of each node in the network.
    '''
    def computeEffectiveSize(self):
        effectiveSize = {}
        for u in self.nodes:
            effectiveSize[u] = 0
            for v in self.Nbhd[u]:
                if v == u:
                    continue
                effectiveSize[u] += 1
                for w in self.Nbhd[v]:
                    Puw = self.Pw[u][w]
                    if self.maxMw[v] == 0:
                        Mvw = 0
                    else:
                        Mvw = self.Mw[v][w] / self.maxMw[v]
                    effectiveSize[u] -= Puw * Mvw
        return effectiveSize

    def computeReachabilityForNode(self, x):
        reach = {}
        N = len(self.nodes)
        reachableNodes = 0
        if (x in self.Adj[x]):
            # x has a self-loop, thus it is reachable from itself.
            reach[x] = True
            reachableNodes += 1
        # Run BFS with x as source node to get all nodes reachable from x.
        Q = Queue(maxsize=N)
        Q.put(x)
        while (not(Q.empty())):
            nod = Q.get()
            # loop through nod's neighbours
            for adj in self.Adj[nod]:
                if (not(adj in reach)) or (not(reach[adj])):
                    reach[adj] = True
                    Q.put(x)
                    reachableNodes += 1
        return reachableNodes


    def computeReachability(self):
        # reachability[x] = the number of nodes that can be reached from self.nodes[x].
        # reach[x][y] = True iff self.nodes[x] can reach self.nodes[y]
        # O(N * (N + M))
        N = len(self.nodes)
        reachability = {}
        for node in self.nodes:
            reachability[node] = self.computeReachabilityForNode(node)
        return reachability

    '''
        Returns a dictionary with the hierarchy value of each node in the network.
        Hierarchy (H) indicates the extent to which aggregate constraint on ego is concentrated
        in a single alter.
        It measures inequality in the distribution of constraints on a focal person across the other
        actors in its neighborhood.
        For node u, 
        C = sum of constraint (from an actor’s network) across all N relationships of an actor
        N = number of contacts in the actor’s network
        H[i] = )C[i][j] / (C/N)[
    '''
    def getHierarhy(self):
        H = {}
        Hierarchy = {}
        for u in self.nodes:
            H[u] = {}
            C = self.constraint[u]
            sizeNbhd = len(self.Nbhd[u])

            for v in self.Nbhd[u]:
                H[u][v] = local_constraint(self.G, u, v) * (sizeNbhd / C)
            # TODO compute hierarchy for u from formula using H[u][v].
        return Hierarchy