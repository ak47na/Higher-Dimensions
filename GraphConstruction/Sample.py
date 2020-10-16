import Edge
from queue import Queue
import random
from EdgeTypeDetails import *
from createTable import *

from networkx import *

colorSet = ['', 'brown', 'firebrick1', 'coral', 'goldenrod1', 'greenyellow', 'darkolivegreen3', 'lightblue',
            'darkturquoise', 'midnightblue', 'hotpink4', 'mediumpurple', 'gray3', 'chocolate', 'yellow1', 'c14', 'c15', 'c16']

# returns a uniform list of length nrNodesSample with values in range [x, y]
def getSample(x, y, nrNodesSample):
    nodeIds = random.sample(range(x, y), nrNodesSample)
    return nodeIds

# returns a list of edges uniformly selected from each layer
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

# returns 2 lists: nodes = set of used nodes within edges,
# edges = set of edges sampled uniformly
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

# returns a list with nodes with degree > 0 given a list of edges
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
    def __init__(self, nrLayers_, nodes_, edges_, labels_, normalize_):
        self.nrNodes = 0
        self.nrEdges = 0
        self.nrLayers = nrLayers_
        self.deg = {}
        self.normalize = normalize_
        self.usedNodes = {}
        self.realNodes = [0]
        self.NLtuples = {}
        self.labels = labels_
        self.normNodes(nodes_)
        self.normLayers(edges_)
        self.Graph = self.createNXGraph()
        self.normEdges(edges_)
    ''' if normalize is True, 
        then usedNodes will be a dictionary with keys = values = nodes in input graph
        else usedNodes will be a dictionary with keys = nodes in input graph,
                                                        values = normalized nodes
        realNodes = dictionary where
        realNodes[x] = y <=> x is a node in Sample graph and y is a node in value graph
    '''
    def normNodes(self, nodes):
        nodes = sorted(nodes)
        if not (self.normalize):
            self.nrNodes = len(nodes)
        for node in nodes:
            if not (node in self.usedNodes):
                self.deg[node] = 0
                if not(self.normalize):
                    self.usedNodes[node] = node
                else:
                    self.nrNodes += 1
                    self.usedNodes[node] = self.nrNodes
                self.NLtuples[self.usedNodes[node]] = {}
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

    def addEdge(self, e, weight):
        if e in self.edges:
            self.edges[e] += weight
        else:
            self.edges[e] = weight
            self.NLtuples[e.nod1][e.layer1] = True
            self.NLtuples[e.nod2][e.layer2] = True
            self.nrEdges += 1
        self.Graph.add_edge((e.nod1, e.layer1), (e.nod2, e.layer2), weight=self.edges[e])
    def addLayer(self, layer):
        if layer in self.layersDict:
            return
        self.nrLayers += 1
        self.layersDict[layer] = True
        self.layers.append(layer)

    ''' creates the list of layers = self.layers with nonempty layers and
        self.layersDict, the dictionary with keys = actual value of the layer 
                                           values = the value of layer in Sample graph
    '''
    def normLayers(self, edges_):
        if not(self.normalize):
            self.layers = list(range(1, self.nrLayers))
            for l in self.layers:
                self.layersDict[l] = l
            return
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
    '''
    creates a dictionary with keys = edges with nodes from self.usedNodes
                              values = weight of the edge
    '''
    def normEdges(self, edges_):
        self.edges = {}
        for edge in edges_:
            if (edge.nod1 in self.usedNodes) and (edge.nod2 in self.usedNodes):
                if not(edge.nod1 in self.deg):
                    self.deg[edge.nod1] = 0
                if not(edge.nod2 in self.deg):
                    self.deg[edge.nod2] = 0
                weight = edges_[edge]
                self.deg[edge.nod1] += weight
                self.deg[edge.nod2] += weight
                self.addEdge(myEdge(self.usedNodes[edge.nod1], self.layersDict[edge.layer1],
                                    self.usedNodes[edge.nod2], self.layersDict[edge.layer2], edge.color),
                             edges_[edge])

    def addOrdinalAliasEdges(self):
        for nod in self.usedNodes:
            x = self.usedNodes[nod]
            layers_x = []
            for l1 in self.NLtuples[x]:
                layers_x.append(l1)
            layers_x = sorted(layers_x)
            nrL = len(layers_x)
            for i in range(nrL - 1):
                self.deg[self.realNodes[x]] += 1
                self.deg[self.realNodes[x]] += 1
                self.addEdge(myEdge(x, layers_x[i], x, layers_x[i + 1], 9), 1)

    def addAliasEdges(self):
        for nod in self.usedNodes:
            x = self.usedNodes[nod]
            for l1 in self.NLtuples[x]:
                for l2 in self.NLtuples[x]:
                    if l1 != l2:
                        self.deg[self.realNodes[x]] += 1
                        self.deg[self.realNodes[x]] += 1
                        self.addEdge(myEdge(x, l1, x, l2, 9), 1)

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
    '''
    returns a dict with keys = types of nodes,
                        values = list with the number of nodes of type in each layer
    '''
    def getCountOfNodesPerLayer(self):
        count = {}
        for node in self.usedNodes:
            nodeType = self.labels[node][1]
            if not (nodeType in count):
                count[nodeType] = [0] * self.nrLayers
            for layer in self.NLtuples[self.usedNodes[node]]:
                count[nodeType][layer - 1] += 1
        return count
    # prints the number of edges for each pair of layers
    def printCountOfEdgeTypes(self):
        Layer = getLayerName()
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
    '''
    creates a table with the number of edges of each type within each layer
    edgeData[layerID] = list with the edges within layer layerID
    '''
    def getEdgeTypeData(self):
        edgeTypeDetails = getEdgeTypeDetails()
        edgeData = []
        for i in range(self.nrLayers + 1):
            edgeData.append([])
        crossLayer = {}
        for e in self.edges:
            type = e.color
            if type == 9:
                continue
            if isinstance(edgeTypeDetails[type][0], int):
                edgeData[edgeTypeDetails[type][0]].append((edgeTypeDetails[type][1], edgeTypeDetails[type][2]))
            # else:
            #     crossLayer[edgeTypeDetails[type][0]][edgeTypeDetails[type][1]] += 1
        layerName = getLayerName()
        for i in range(1, 5):
            createLayerTable(layerName[i], edgeData[i])
    # creates a NXMuliDiGraph from the Sample where nodes are node-layer tuples
    def createNXGraph(self):
        G = networkx.MultiDiGraph()
        for node in self.usedNodes:
            u = self.usedNodes[node]
            for l in self.NLtuples[u]:
                if self.NLtuples[u][l] == True:
                    G.add_node((u, l))
        return G
    def getDegreeCentrality(self):
        return degree_centrality(self.Graph)
    def getWeightedDegreeCentrality(self):
        weightedDC = {}
        for node in self.usedNodes:
            weightedDC[self.usedNodes[node]] = self.deg[node]
        return weightedDC
    def getBetweennessCentrality(self):
        return betweenness_centrality(self.Graph, None)
    def getClosenessCentrality(self):
        return closeness_centrality(self.Graph)
