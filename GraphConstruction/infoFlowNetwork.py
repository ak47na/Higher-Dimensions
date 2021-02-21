import mailID
import parameters

from datetime import datetime
from networkx import *
from scipy.stats import spearmanr
from math import *

'''
    Updates the minimum and maximum number of seconds with t.
'''
def updateTimeBorders(minTime, maxTime, t):
    minTime = min(minTime, t)
    maxTime = max(maxTime, t)
    return minTime, maxTime

def getMinMax(timePair, t):
    return (min(timePair[0], t), max(timePair[1], t))

class InformationFlowNetwork:
    def __init__(self, msgDict, delta_t, t, minTime, useGT = False):
        self.minTime = minTime
        self.nrEdges = 0
        self.replyDict = {}
        self.humanDict = {}
        self.Label = {}
        # minT[graphIndex][(A, B)] = min time t in graphIndex s.t there was a message from B to A at t.
        self.minT = {}
        self.maxT = {}
        #inLayer[graphIndex][A][B] = (minT, maxT)
        #crossLayerIn[graphIndex][A][B] = (minT, maxT)
        #crossLayerOut[graphIndex][A][B] = minT
        self.netwNodes = {}
        self.inLayer = {}
        self.crossLayerIn = {}
        self.crossLayerOut = {}
        # Adj[graphIndex][node] = the adjacency list of node in the graphIndex-th graph.
        self.Adj = {}
        # msgDict[msgKey] = (sender, time)
        self.msgDict = msgDict
        # timeDict[timeInterval] = the index of the network(graphIndex) with messages sent in timeInterval
        # timeInterval = integer
        self.timeDict = {}
        # timeDict[timeInterval] = the index of the network(graphIndex) with messages sent in timeInterval
        # timeInterval = integer
        self.crossLayerEdges = []
        # tGraphs = List of the networkX multiDiGraphs for each time time interval, i.e
        # TGraphs[graphIndex] =the graph for timeInterval with timeDict[timeInterval] = graphIndex.
        self.tGraphs = [0]
        # nr2paths[t][graphIndex][node] = the number of 2-paths of node in network
        # if t == 0, then the count includes transitive faults
        #    t == 1, then the count excludes transitive faults with optimistic model
        #    t == 2, then the count excludes transitive faults with pessimistic model
        self.nr2paths = {'MLN': [{}, {}, {}], 'monoplex' : [{}, {}, {}]}

        # nr2p[t][node] = the number of 2-paths of node in aggregate network, i.e
        #               = sum(network in networks, nr2p[t][network][node])
        self.nr2p = {'MLN': [{}, {}, {}], 'monoplex' : [{}, {}, {}]}
        self.nrGraphs = 0
        self.delta_t = delta_t
        self.analysedT = t
        self.TFperNetw = {"monoplex" : {}, "MLN": {}}
        self.crtResult = {"monoplex" : [(0, 0), (0, 0), (0, 0)], "MLN": [(0, 0), (0, 0), (0, 0)]}
        self.meanRes = {}
        if useGT:
            parameters.setLayerDistance(1 + (parameters.T - 1) // delta_t)

    '''
        Add the human with name to humanDict and as a graph node with index nrNodes + 1 and label
        name.
    '''
    def addHuman(self, name, nrNodes):
        name = mailID.getIdentity(name)
        if not (name in self.humanDict):
            nrNodes += 1
            self.Label[nrNodes] = name
            self.humanDict[name] = nrNodes
        return nrNodes

    def getTimeRange(self, timestmp):
        return trunc((timestmp - self.minTime) / self.delta_t)

    def createTGraphForT(self, tIntervalId):
        self.nrGraphs += 1
        self.Adj[self.nrGraphs] = {}
        self.minT[self.nrGraphs] = {}
        self.maxT[self.nrGraphs] = {}
        self.tGraphs.append(networkx.MultiDiGraph())
        self.netwNodes[self.nrGraphs] = {}
        self.timeDict[tIntervalId] = self.nrGraphs
        self.inLayer[self.nrGraphs] = {}
        self.crossLayerIn[self.nrGraphs] = {}
        self.crossLayerOut[self.nrGraphs] = {}

    def addNodeToNetw(self, A, netw):
        self.netwNodes[netw][A] = True

    '''
        Adds an edge between the sender of message v and the sender of message u. delta_t represents the
        number of seconds aggregated into one time interval.
        Returns the number of human nodes across all networks.
    '''
    def addEdge(self, u, v, nrNodes):
        # u is a reply to v, b is the sender of u, a is the sender of v.
        if (self.msgDict[u][1].timestamp() < self.msgDict[v][1].timestamp()):
            u, v = v, u
        timeU = self.msgDict[u][1].timestamp()
        timeV = self.msgDict[v][1].timestamp()
        assert (timeU >= timeV)
        if ((u, v) in self.replyDict):
            # The reply u to message v was already processed.
            return nrNodes

        self.replyDict[(u, v)] = True
        b = self.msgDict[u][0]
        a = self.msgDict[v][0]
        nrNodes = self.addHuman(a, nrNodes)
        nrNodes = self.addHuman(b, nrNodes)
        if a == b:
            # Do not include self replies
            return nrNodes
        self.nrEdges += 1
        A = self.humanDict[a]
        B = self.humanDict[b]
        # Compute the TIME index of the network which contains the point in time when message u was sent.
        tIntervalIdU = self.getTimeRange(timeU)
        # Compute the TIME index of the network which contains the point in time when message v was sent.
        tIntervalIdV = self.getTimeRange(timeV)
        assert tIntervalIdV <= tIntervalIdU

        if tIntervalIdU - tIntervalIdV > parameters.kLayer:
            # Ignore cross edges for layer distance > kLayer.
            return nrNodes

        if not (tIntervalIdU in self.timeDict):
            # Create the graph for tIntervalIdU
            self.createTGraphForT(tIntervalIdU)
        if not (tIntervalIdV in self.timeDict):
            # Create the graph for tIntervalIdV
            self.createTGraphForT(tIntervalIdV)

        self.addNodeToNetw(A, self.timeDict[tIntervalIdU])
        self.addNodeToNetw(A, self.timeDict[tIntervalIdV])
        self.addNodeToNetw(B, self.timeDict[tIntervalIdU])
        self.addNodeToNetw(B, self.timeDict[tIntervalIdV])

        T = self.timeDict[tIntervalIdU]
        if tIntervalIdU != tIntervalIdV:
            self.crossLayerEdges.append(((A, timeV), (B, timeU)))
            Tv = self.timeDict[tIntervalIdV]
            # Add cross-layer edge outgoing from A.
            if (not A in self.crossLayerOut[Tv]):
                self.crossLayerOut[Tv][A] = {}
            if (not B in self.crossLayerOut[Tv][A]):
                self.crossLayerOut[Tv][A][B] = (timeU, timeU)
            else:
                self.crossLayerOut[Tv][A][B] = getMinMax(self.crossLayerOut[Tv][A][B], timeU)
            # Add cross-layer edge ingoing to B.
            if (not B in self.crossLayerIn[T]):
                self.crossLayerIn[T][B] = {}
            if (not A in self.crossLayerIn[T][B]):
                self.crossLayerIn[T][B][A] = (timeU, timeU)
            else:
                self.crossLayerIn[T][B][A] = getMinMax(self.crossLayerIn[T][B][A], timeU)
        else:
            if not(A in self.inLayer[T]):
                self.inLayer[T][A] = {}
            if not(B in self.inLayer[T][A]):
                self.inLayer[T][A][B] = (timeU, timeU)
            else:
                self.inLayer[T][A][B] = getMinMax(self.inLayer[T][A][B], timeU)
        # Update the minimum and maximum time for a conversation from person A to person B.
        # The value is necessary for computing transitive faults.
        if not ((A, B) in self.minT[T]):
            self.minT[T][(A, B)] = timeU
            self.maxT[T][(A, B)] = timeU
        else:
            self.minT[T][(A, B)], self.maxT[T][(A, B)] = updateTimeBorders(self.minT[T][(A, B)],
                                                                                self.maxT[T][(A, B)],
                                                                                timeU)
        # Add an edge in the T-th MultiDiGraph from the node representing human a to the node
        # representing human b.
        # Comment this if-statement if CLE should be considered parallel edges in CP network
        if tIntervalIdU != tIntervalIdV:
            return nrNodes

        if not (A in self.Adj[T]):
            self.Adj[T][A] = {}
        if not (B in self.Adj[T][A]):
            self.tGraphs[T].add_edge(self.humanDict[a], self.humanDict[b], time=self.msgDict[u][1])
            self.Adj[T][A][B] = self.msgDict[u][1]
        return nrNodes

    '''
        Reads the file with messages' relations and adds a directed edge from the reply to the message.
    '''

    def readMsgEdges(self, nrNodes, filePath):
        errors = 0
        invalidMsg = {}
        # file with each line containing two string numbers u v representing that message with key u is
        # a reply to message with key v.
        edgeFile = open(filePath, "r")

        while True:
            crtLine = edgeFile.readline()
            if not crtLine:
                break
            crtLine = crtLine.replace('\n', '')
            lst = crtLine.split(' ')
            assert len(lst) == 2
            if not (lst[0] in self.msgDict) and not (lst[0] in invalidMsg):
                invalidMsg[lst[0]] = True
                errors += 1
            if not (lst[1] in self.msgDict) and not (lst[1] in invalidMsg):
                invalidMsg[lst[1]] = True
                errors += 1
            if (lst[0] in self.msgDict) and (lst[1] in self.msgDict):
                nrNodes = self.addEdge(lst[1], lst[0], nrNodes)
        edgeFile.close()
        return nrNodes

    def getTFaultMonoplex(self, a, b, c, netw, netwType, optimisticCount, pesimisticCount):
        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
        # a transitive-fault.
        if self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1]:
            optimisticCount += 1
            self.nr2paths[netwType][1][netw][a] -= 1
        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
        # transitive fault in the pessimistic model.
        if self.inLayer[netw][a][b][1] > self.inLayer[netw][b][c][0]:
            pesimisticCount += 1
            self.nr2paths[netwType][2][netw][a] -= 1
        return optimisticCount, pesimisticCount

    def getTFaultMonoplexLimitingPrevReply(self, a, b, c, netw, netwType, optimisticCount, pesimisticCount):
        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
        # a transitive-fault.
        if self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1]:
            if self.inLayer[netw][a][b][0] - self.inLayer[netw][b][c][1] <= parameters.T:
                # Only consider 2paths where the distance between replies is <= T
                optimisticCount += 1
            self.nr2paths[netwType][1][netw][a] -= 1
        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
        # transitive fault in the pessimistic model.
        if self.inLayer[netw][a][b][1] > self.inLayer[netw][b][c][0]:
            d = min(abs(self.inLayer[netw][a][b][1] - self.inLayer[netw][b][c][0]),
                    abs(self.inLayer[netw][a][b][1] - self.inLayer[netw][b][c][1]),
                    abs(self.inLayer[netw][a][b][0] - self.inLayer[netw][b][c][0]),
                    abs(self.inLayer[netw][a][b][0] - self.inLayer[netw][b][c][1]))
            if d <= parameters.T:
                pesimisticCount += 1
            self.nr2paths[netwType][2][netw][a] -= 1
        return optimisticCount, pesimisticCount

    def getTFaultMonoplexV2(self, a, b, c, netw, netwType, optimisticCount, pesimisticCount):
        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
        # a transitive-fault.
        if self.minT[netw][(a, b)] > self.maxT[netw][(b, c)]:
            optimisticCount += 1
            self.nr2paths[netwType][1][netw][a] -= 1
        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
        # transitive fault in the pessimistic model.
        if self.maxT[netw][(a, b)] > self.minT[netw][(b, c)]:
            pesimisticCount += 1
            self.nr2paths[netwType][2][netw][a] -= 1
        return optimisticCount, pesimisticCount

    def getTFaultMLN(self, a, b, c, netw, netwType, optimisticCount, pesimisticCount):
        cleAdowntoB = b in self.crossLayerIn[netw] and a in self.crossLayerIn[netw][b]
        cleAtoBup = a in self.crossLayerOut[netw] and b in self.crossLayerOut[netw][a]
        cleBtoupC = b in self.crossLayerOut[netw] and c in self.crossLayerOut[netw][b]
        cleBdowntoC = c in self.crossLayerIn[netw] and b in self.crossLayerIn[netw][c]

        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
        # a transitive-fault.
        if (self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1]) and (not (cleAdowntoB or cleBtoupC)):
            optimisticCount += 1
            self.nr2paths[netwType][1][netw][a] -= 1
        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
        # transitive fault in the pessimistic model.
        if self.inLayer[netw][a][b][1] > self.inLayer[netw][b][c][0] or cleBdowntoC or cleAtoBup:
            pesimisticCount += 1
            self.nr2paths[netwType][2][netw][a] -= 1
        return optimisticCount, pesimisticCount

    def addCLEPathAB(self, netw, netwType, a, b):
        assert netwType == 'MLN'
        if b in self.crossLayerOut[netw]:
            for c in self.crossLayerOut[netw][b]:
                if not (b in self.inLayer[netw] and c in self.inLayer[netw][b]):
                    # Cross-edges b->c where there is also an in-layer edge b->c are treated in getTFaultMLN.
                    assert (self.crossLayerOut[netw][b][c][0] > self.inLayer[netw][a][b][1])
                    for ty in range(3):
                        self.nr2paths[netwType][ty][netw][a] += 1

    def addCLEPathA(self, netw, netwType, a, optimisticCount, pesimisticCount):
        for b in self.crossLayerOut[netw][a]:
            for id in range(0, 2):
                if id == 1 and self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b][0])] \
                        == self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b][1])]:
                    continue
                netwb = self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b][id])]
                if not (b in self.inLayer[netwb]):
                    # Ignore bs with no inLayer edge b->c
                    continue
                if not (a in self.inLayer[netwb] and b in self.inLayer[netwb][a]):
                    for c in self.inLayer[netwb][b]:
                        for ty in range(3):
                            self.nr2paths[netwType][ty][netw][a] += 1
                        # Cross-edges c->a where there is also an in-layer edge c->a are treated in getTFaultMLN.
                        if self.crossLayerOut[netw][a][b][0] > self.inLayer[netwb][b][c][1]:
                            optimisticCount += 1
                            self.nr2paths[netwType][1][netw][a] -= 1
                        if self.crossLayerOut[netw][a][b][1] > self.inLayer[netwb][b][c][0]:
                            pesimisticCount += 1
                            self.nr2paths[netwType][2][netw][a] -= 1

        return optimisticCount, pesimisticCount

    def initTFRForNode(self, netw, netwType, a):
        self.nr2paths[netwType][0][netw][a] = 0
        self.nr2paths[netwType][1][netw][a] = 0
        self.nr2paths[netwType][2][netw][a] = 0
        optimisticCount = 0
        pesimisticCount = 0
        return optimisticCount, pesimisticCount

    def addTFRForNode(self, netw, netwType, transFaultSum, a, optimisticCount, pesimisticCount):
        if self.nr2paths[netwType][0][netw][a] == 0:
            # When computing the transitive fault rate, ignore the nodes without 2-paths.
            return transFaultSum
        transFaultSum[0] += (optimisticCount / self.nr2paths[netwType][0][netw][a])
        transFaultSum[1] += (pesimisticCount / self.nr2paths[netwType][0][netw][a])
        return transFaultSum

    '''
        Computes the number of 2-paths(with or without transitive faults) for each node. The number of
        seconds aggregated in each network is delta_t.
        Transitive fault = "a directed path of length exactly two where the time label on the first edge
        is later than the time label on the second edge along the path, i.e. a directed 2-path with
        decreasing edge time stamps."
    '''
    def getTransitiveFault(self, netwType):
        upperBound = 0
        lowerBound = 1
        for netw in range(1, self.nrGraphs + 1):
            N = len(self.netwNodes[netw])
            if N == 0:
                self.TFperNetw[netwType][netw] = [0, 0]
                continue
            transFaultSum = [0, 0]
            # 0 = with transitive faults,
            # 1 = without transitive faults(optimistic model)
            # 2 = without transitive faults(pessimistic model)
            self.nr2paths[netwType][0][netw] = {}
            self.nr2paths[netwType][1][netw] = {}
            self.nr2paths[netwType][2][netw] = {}
            if netwType == 'MLN':
                for a in self.crossLayerOut[netw]:
                    if not (a in self.inLayer[netw]):
                        optimisticCount, pesimisticCount = self.initTFRForNode(netw, netwType, a)
                        N += 1
                        optimisticCount, pesimisticCount = self.addCLEPathA(netw, netwType, a, optimisticCount, pesimisticCount)
                        transFaultSum = self.addTFRForNode(netw, netwType, transFaultSum, a, optimisticCount, pesimisticCount)

            netwEdges = self.inLayer[netw]
            # Uncomment this part if the CP network adds CLE as inLayer parallel edges.
            # if (netwType == "MLN"):
            #     netwEdges = self.inLayer[netw]
            # else:
            #     netwEdges = self.Adj[netw]
            for a in netwEdges:
                self.nr2paths[netwType][0][netw][a] = 0
                self.nr2paths[netwType][1][netw][a] = 0
                self.nr2paths[netwType][2][netw][a] = 0
                optimisticCount = 0
                pesimisticCount = 0
                for b in netwEdges[a]:
                    if netwType == 'MLN':
                        self.addCLEPathAB(netw, netwType, a, b)

                    if not (b in netwEdges):
                        # Ignore a's neighbours with out-degree = 0.
                        continue
                    for c in netwEdges[b]:
                        # Count the 2-path : a->b->c
                        self.nr2paths[netwType][0][netw][a] += 1
                        self.nr2paths[netwType][1][netw][a] += 1
                        self.nr2paths[netwType][2][netw][a] += 1
                        if netwType == 'MLN':
                            optimisticCount, pesimisticCount = \
                                self.getTFaultMLN(a, b, c, netw, netwType, optimisticCount, pesimisticCount)
                        else:
                            optimisticCount, pesimisticCount = \
                                self.getTFaultMonoplex(a, b, c, netw, netwType, optimisticCount, pesimisticCount)
                transFaultSum = self.addTFRForNode(netw, netwType, transFaultSum, a, optimisticCount, pesimisticCount)

            self.TFperNetw[netwType][netw] = (transFaultSum[0], transFaultSum[1])
            # The network transitive fault rate is the sum of the node transitive fault rates over all
            # nodes, divided by the number of nodes in the network.
            transFaultSum[0] /= N
            transFaultSum[1] /= N

            # optimistic model should have at most pessimistic model transitive faults.
            assert transFaultSum[0] <= transFaultSum[1]

            upperBound = max(transFaultSum[1], upperBound)
            lowerBound = min(transFaultSum[0], lowerBound)

        self.crtResult[netwType][0] = (lowerBound, upperBound)

    def getMLNEdgeCount(self):
        inLayerEdgeCount = self.getMonoplexEdgeCount()
        crossLayerEdgeCount = 0
        for netw in range(1, self.nrGraphs + 1):
            for a in self.crossLayerIn[netw]:
                for b in self.crossLayerIn[netw][a]:
                    crossLayerEdgeCount += 1
                    if self.crossLayerIn[netw][a][b][0] != self.crossLayerIn[netw][a][b][1]:
                        crossLayerEdgeCount += 1
            for a in self.crossLayerOut[netw]:
                for b in self.crossLayerOut[netw][a]:
                    for id in range(2):
                        if id == 1 and self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b][0])] \
                                == self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b][1])]:
                            continue
                        netwb = self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b][id])]
                        if b in self.crossLayerIn[netwb]:
                            if self.crossLayerIn[netwb][b][a][0] != self.crossLayerOut[netw][a][b][id] and \
                                    self.crossLayerIn[netwb][b][a][1] != self.crossLayerOut[netw][a][b][id]:
                                crossLayerEdgeCount += 1

        return (inLayerEdgeCount, crossLayerEdgeCount, crossLayerEdgeCount + inLayerEdgeCount)

    def getMonoplexEdgeCount(self):
        inLayerEdgeCount = 0
        for netw in range(1, self.nrGraphs + 1):
            for a in self.inLayer[netw]:
                inLayerEdgeCount += len(self.inLayer[netw][a])
                for b in self.inLayer[netw][a]:
                    if (self.inLayer[netw][a][b][0] != self.inLayer[netw][a][b][1]):
                        inLayerEdgeCount += 1
        return inLayerEdgeCount

    def getTFSum(self, netwType):
        res = [0, 0]
        for netw in range(1, self.nrGraphs + 1):
            for modelId in range(2):
                res[modelId] += self.TFperNetw[netwType][netw][modelId]
        return res



    def getEdgeCount(self):
        edgeCount = 0
        for netw in range(1, self.nrGraphs + 1):
            for a in self.Adj[netw]:
                for b in self.Adj[netw][a]:
                    edgeCount += 1
                    if (self.minT[netw][(a, b)] != self.maxT[netw][(a, b)]):
                        edgeCount += 1
        return edgeCount
