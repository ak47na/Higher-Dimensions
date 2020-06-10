from Edge import myEdge
from queue import Queue
import random

colorSet = ['', 'brown', 'firebrick1', 'coral', 'goldenrod1', 'greenyellow', 'darkolivegreen3', 'lightblue',
            'darkturquoise', 'midnightblue', 'hotpink4', 'mediumpurple', 'gray3', 'chocolate', 'yellow1']


def getSample(x, y, nrNodesSample):
    nodeIds = random.sample(range(x, y), nrNodesSample)
    return nodeIds

def sampleEdgesPerLayer(nrLayers, edgeList, divBy):
    edgeIdx = []
    for i in range(nrLayers):
        edgeIdx.append([])
    nrEdges = len(edgeList)
    for i in range(nrEdges):
        if edgeList[i].layer1 == edgeList[i].layer2:
            edgeIdx[edgeList[i].layer1 - 1].append(i)
    edges = []
    for i in range(nrLayers):
        nrEdges_i = len(edgeIdx[i])
        sample = getSample(0, nrEdges_i - 1, nrEdges_i // divBy)
        for j in sample:
            edges.append(edgeList[edgeIdx[i][j]])
    return edges

def sampleNodesFromEdges(edgeList, divBy):
    nrEdges = len(edgeList)
    edgeSample = getSample(0, nrEdges, nrEdges // divBy)
    nodeDict = {}
    nodes = []
    edges = []
    for i in edgeSample:
        if not(edgeList[i].nod1 in nodeDict):
            nodeDict[edgeList[i].nod1] = True
            nodes.append(edgeList[i].nod1)
        if not(edgeList[i].nod2 in nodeDict):
            nodeDict[edgeList[i].nod2] = True
            nodes.append(edgeList[i].nod2)
        edges.append(edgeList[i])
    return nodes, edges

def getNodesFromEdgeSample(edges):
    nodeDict = {}
    nodes = []
    for e in edges:
        if not (e.nod1 in nodeDict):
            nodeDict[e.nod1] = True
            nodes.append(e.nod1)
        if not (e.nod2 in nodeDict):
            nodeDict[e.nod2] = True
            nodes.append(e.nod2)
    return nodes

def createLayoutFile(fileName, nr, isLayer):
    f = open(fileName, "w")
    add = 0
    if isLayer:
        f.write("layerID layerLabel\n")
    else:
        f.write("nodeID nodeLabel\n")
    for i in range(nr):
        f.write(str(i + 1) + ' ' + str(i + 1) + '\n')
    f.close()

#returns the list of all nodes that are adjacent to at least one node in nodes_
def sampleFromNodes(nodes_):
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
# return network of nodes_ using BFS
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
    def __init__(self, nrLayers_, nodes_, edges_, labels_):
        self.nrNodes = 0
        self.nrEdges = 0
        self.usedNodes = {}
        self.realNodes = [0]
        self.NLtuples = {}
        self.labels = labels_
        self.normNodes(nodes_)
        self.normLayers(edges_)
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
    def getNrEdges(self):
        return self.nrEdges
    def getNrLayers(self):
        return self.nrLayers
    def getLayers(self):
        realLayers = []
        for x in self.layers:
            realLayers.append(x)
        return realLayers

    def addEdge(self, e):
        if e in self.edges:
            self.edges[e] += 1
        else:
            self.edges[e] = 1
            self.NLtuples[e.nod1][e.layer1] = True
            self.NLtuples[e.nod2][e.layer2] = True
            self.nrEdges += 1
    def addLayer(self, layer):
        if layer in self.layersDict:
            return
        self.nrLayers += 1
        self.layersDict[layer] = True
        self.layers.append(layer)
    def normLayers(self, edges_):
        self.layersDict = {}
        self.layers = []
        self.nrLayers = 0
        for edge in edges_:
            if (edge.nod1 in self.usedNodes) and (edge.nod2 in self.usedNodes):
                self.addLayer(edge.layer1)
                self.addLayer(edge.layer2)
        self.layers = sorted(self.layers)
        for i in range(self.nrLayers):
            self.layersDict[self.layers[i]] = i + 1
    def normEdges(self, edges_):
        self.edges = {}
        for edge in edges_:
            if (edge.nod1 in self.usedNodes) and (edge.nod2 in self.usedNodes):
                self.addEdge(myEdge(self.usedNodes[edge.nod1], self.layersDict[edge.layer1],
                                    self.usedNodes[edge.nod2], self.layersDict[edge.layer2], edge.color))

    def addOrdinalAliasEdges(self):
        for nod in self.usedNodes:
            x = self.usedNodes[nod]
            layers_x = []
            for l1 in self.NLtuples[x]:
                layers_x.append(l1)
            layers_x = sorted(layers_x)
            nrL = len(layers_x)
            for i in range(nrL - 1):
                self.addEdge(myEdge(x, layers_x[i], x, layers_x[i + 1], 9))


    def addAliasEdges(self):
        for nod in self.usedNodes:
            x = self.usedNodes[nod]
            for l1 in self.NLtuples[x]:
                for l2 in self.NLtuples[x]:
                    if l1 != l2:
                        self.addEdge(myEdge(x, l1, x, l2, 9))

    def getEdgesString(self):
        edgeStr = ''
        for edge in self.edges:
            edgeStr += str(edge.ToString() + ' ' + str(self.edges[edge]) + '\n')
        return edgeStr

    def createEdgesFile(self, fileName1):
        f = open(fileName1, "w")
        f.write(self.getEdgesString())
        f.close()
    def createColoredEdges(self, fileName):
        f = open(fileName, "w")
        f.write("nodeID.from layerID.from nodeID.to layerID.to color size\n")
        for edge in self.edges:
            f.write(edge.ToString() + ' ' + colorSet[edge.color] + ' 3\n')
        f.close()
    def printCountOfEdgeTypes(self, Layer):
        edgeTypes = {}
        for e in self.edges:
            if not ((e.layer1, e.layer2) in edgeTypes):
                edgeTypes[(e.layer1, e.layer2)] = 1
            else:
                edgeTypes[(e.layer1, e.layer2)] += 1
        edgeTypesList = []
        for key in edgeTypes:
            edgeTypesList.append(key)
        edgeTypesList = sorted(edgeTypesList)
        for key in edgeTypesList:
            print(Layer[key[0]], 'x', Layer[key[1]], '=', edgeTypes[key])
