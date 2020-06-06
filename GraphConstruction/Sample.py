from Edge import myEdge
from queue import Queue

def createLayoutFile(fileName, nr, isLayer):
    f = open(fileName, "w")
    if isLayer:
        f.write("layerID layerLabel\n")
    else:
        f.write("nodeID nodeLabel\n")
    for i in range(nr):
        f.write(str(i + 1) + ' ' + str(i + 1) + '\n')
    f.close()

#returns the list of all nodes that are adjacent to at least one node in nodes_
def sampleFromLayer(nodes_):
    allNodes = {}
    nodeList = []
    for nod in nodes_:
        if not (nod[0] in allNodes):
            allNodes[nod[0]] = True
            nodeList.append(nod[0])
        for adj in nod[1]:
            if not (adj[0] in allNodes):
                allNodes[adj[0]] = True
                nodeList.append(adj[0])

    return nodeList
# return the network of nodes_ using BFS
def sampleNetFromNodes(nodes_, Adj):
    allNodes = {}
    nodeList = []
    Q = Queue(maxsize = 0)
    for nod in nodes_:
        if not(nod in allNodes):
            allNodes[nod] = True
            nodeList.append(nod)
            Q.put(nod)
    while (not(Q.empty())):
        nod = Q.get()
        for adj in Adj[nod]:
            if not (adj[0] in allNodes):
                allNodes[adj[0]] = True
                nodeList.append(adj[0])
                Q.put(adj[0])
    return nodeList

class Sample:
    def __init__(self, nrLayers_, nodes_, edges_):
        self.nrLayers = nrLayers_
        self.nrNodes = 0
        self.nrEdges = 0
        self.usedNodes = {}
        self.realNodes = [0]
        self.NLtuples = {}
        self.normNodes(nodes_)
        self.normEdges(edges_)

    def normNodes(self, nodes):
        for node in nodes:
            if not (node in self.usedNodes):
                self.nrNodes += 1
                self.usedNodes[node] = self.nrNodes
                self.NLtuples[self.nrNodes] = {}
                self.realNodes.append(node)
    def getNrNodes(self):
        return self.nrNodes

    def addEdge(self, e):
        if e in self.edges:
            self.edges[e] += 1
        else:
            self.edges[e] = 1
            self.NLtuples[e.nod1][e.layer1] = True
            self.NLtuples[e.nod2][e.layer2] = True
            self.nrEdges += 1
    def normEdges(self, edges_):
        self.edges = {}
        for edge in edges_:
            if (edge.nod1 in self.usedNodes) and (edge.nod2 in self.usedNodes):
                self.addEdge(myEdge(self.usedNodes[edge.nod1], edge.layer1, self.usedNodes[edge.nod2], edge.layer2, 0))
    def addAliasEdges(self):
        for nod in self.usedNodes:
            x = self.usedNodes[nod]
            for l1 in self.NLtuples[x]:
                for l2 in self.NLtuples[x]:
                    if l1 != l2:
                        self.addEdge(myEdge(x, l1, x, l2, 0))
    def getEdgesString(self):
        edgeStr = ''
        for edge in self.edges:
            edgeStr += str(edge.ToString() + ' ' + str(self.edges[edge]) + '\n')
        return edgeStr
