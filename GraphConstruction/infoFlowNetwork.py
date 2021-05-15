import mailID
import parameters

from networkx import *
from math import *
import matplotlib.pyplot as plt

'''
    Updates the minimum and maximum number of seconds with the value of t.
'''
def updateTimeBorders(minTime, maxTime, t):
    minTime = min(minTime, t)
    maxTime = max(maxTime, t)
    return minTime, maxTime

def getMinMax(timePair, t):
    assert timePair[0] <= timePair[1]
    return (min(timePair[0], t), max(timePair[1], t))

class InformationFlowNetwork:
    def __init__(self, msgDict, delta_t, t, minTime, useGT = False):
        # self.allTimes=[(timeU_i, timeV_i)], timeU_i = time of reply sent to msg with time timeV_i
        # self.allTimes[1] = includes cross-bucket replies;
        # self.allTimes[0] = doesn't include cross bucket reply.
        self.allTimesBucket = [{}, {}]
        self.allTimes = [{}, {}]
        self.gtTP = {}
        self.gtTF = [{}, {}]
        # uniqueFaults[netwType][type] = dict with (2path, count) where 2path = transitive fault
        # and count is the occurence of that 2path as a transitive fault.
        self.uniqueFaults = {"monoplex" : [{}, {}], "MLN": [{}, {}]}
        self.minTime = minTime
        self.nrEdges = 0
        self.replyDict = {}
        self.humanDict = {}
        self.Label = {}
        # minT[graphIndex][(A, B)] = min time t in graphIndex s.t there was a message from B to A at t.
        self.minT = {}
        self.maxT = {}
        #minPair[A][B] = the minimum time t s.t. there is a reply from B to A at time t.
        self.minPair = {}
        self.maxPair = {}
        #inLayer[graphIndex][A][B] = (minT_AB, maxT_AB)
        #crossLayerIn[graphIndex][A][B] = (minT_AB, maxT_AB)
        #crossLayerOut[graphIndex][A][B] = minT
        self.netwNodes = {}
        self.inLayer = {}
        self.crossLayerIn = {}
        self.crossLayerOut = {}
        # msgDict[msgKey] = (sender, time)
        self.msgDict = msgDict
        # timeDict[timeInterval] = the index of the network(graphIndex) with messages sent in timeInterval
        # timeInterval = integer
        self.timeDict = {}

        # list with all cross-layer edges (A, timeV, B, timeU) where timeU is the time of reply
        # sent by B to message sent by A at timeV.
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
        #               = sum(netw in networks, nr2p[t][netw][node])
        self.nr2p = {'MLN': [{}, {}, {}], 'monoplex' : [{}, {}, {}]}

        self.nrGraphs = 0
        # The bucket width in seconds.
        self.delta_t = delta_t
        # String representation of bucket width used for print statements.
        self.analysedT = t
        # self.twoPaths[netwType] = dict with tuples (A, B, C) representing all 2paths.
        self.twoPaths = {"monoplex" : {}, "MLN": {}}
        # self.tfCount[netwType] = dict with tuples (A, B, C) representing transitive faults.
        # self.tfCount[netwType][0] ->optimistic; self.tfCount[netwType][0] ->pessimistic
        self.tfCount = {"monoplex" : [0, 0], "MLN": [0, 0]}
        self.TFperNetw = {"monoplex" : {}, "MLN": {}}
        self.crtResult = {"monoplex" : [(0, 0), (0, 0), (0, 0)], "MLN": [(0, 0), (0, 0), (0, 0)]}
        self.crtResultAgg = {"monoplex" : [], "MLN": []}
        if useGT:
            parameters.setLayerDistance(1 + (parameters.T - 1) // delta_t)
        else:
            parameters.setLayerDistance(1)

    '''
        Add the human with name to humanDict and increment nrNodes.
        Add name as a graph node with index nrNodes and label name.
    '''
    def addHuman(self, name, nrNodes):
        name = mailID.getIdentity(name)
        if not (name in self.humanDict):
            nrNodes += 1
            self.Label[nrNodes] = name
            self.humanDict[name] = nrNodes
        return nrNodes

    '''
        Return the bucket index of timestamp.
    '''
    def getTimeRange(self, timestamp):
        return trunc((timestamp - self.minTime) / self.delta_t)

    def createTGraphForT(self, tIntervalId):
        self.nrGraphs += 1
        self.minT[self.nrGraphs] = {}
        self.maxT[self.nrGraphs] = {}
        self.tGraphs.append(networkx.MultiDiGraph())
        self.netwNodes[self.nrGraphs] = {}
        self.timeDict[tIntervalId] = self.nrGraphs
        self.inLayer[self.nrGraphs] = {}
        self.crossLayerIn[self.nrGraphs] = {}
        self.crossLayerOut[self.nrGraphs] = {}
        self.allTimesBucket[0][tIntervalId] = {}
        self.allTimesBucket[1][tIntervalId] = {}

    def addNodeToNetw(self, A, netw):
        self.netwNodes[netw][A] = True

    def sortTimedData(self):
        for ty in range(2):
            for a in self.allTimes[ty]:
                for b in self.allTimes[ty][a]:
                    self.allTimes[ty][a][b].sort(key=lambda x: x[0])
            for bucket in self.allTimesBucket[ty]:
                for a in self.allTimesBucket[ty][bucket]:
                    for b in self.allTimesBucket[ty][bucket][a]:
                        self.allTimesBucket[ty][bucket][a][b].sort(key=lambda x: x[0])

    def addTimedEdge(self, A, B, timeU, timeV, bucket, ty):
        if not(A in self.allTimes[ty]):
            self.allTimes[ty][A] = {}
        if not(B in self.allTimes[ty][A]):
            self.allTimes[ty][A][B] = []
        self.allTimes[ty][A][B].append((timeU, timeV))
        if not(A in self.allTimesBucket[ty][bucket]):
            self.allTimesBucket[ty][bucket][A] = {}
        if not(B in self.allTimesBucket[ty][bucket][A]):
            self.allTimesBucket[ty][bucket][A][B] = []
        self.allTimesBucket[ty][bucket][A][B].append((timeU, timeV))


    '''
        Adds an edge between the sender of message v and the sender of message u. delta_t represents the
        number of seconds aggregated into one time interval.
        Returns the number of human nodes across all networks.
    '''
    def addEdge(self, u, v, nrNodes):
        if ((u, v) in self.replyDict):
            # The reply u to message v was already processed.
            return nrNodes
        # u is a reply to v, b is the sender of u, a is the sender of v.
        if (self.msgDict[u][1].timestamp() < self.msgDict[v][1].timestamp()):
            u, v = v, u
        timeU = self.msgDict[u][1].timestamp()
        timeV = self.msgDict[v][1].timestamp()
        assert (timeU >= timeV)
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
        self.addTimedEdge(A, B, timeU, timeV, tIntervalIdU, 1)

        if tIntervalIdU == tIntervalIdV:
            self.addTimedEdge(A, B, timeU, timeV, tIntervalIdU, 0)
        if not(A in self.minPair):
            self.minPair[A] = {}
        if not (B in self.minPair[A]):
            self.minPair[A][B] = timeU
        self.minPair[A][B] = min(self.minPair[A][B], timeU)
        if not (A in self.maxPair):
            self.maxPair[A] = {}
        if not (B in self.maxPair[A]):
            self.maxPair[A][B] = timeU
        self.maxPair[A][B] = max(self.maxPair[A][B], timeU)

        if tIntervalIdU - tIntervalIdV > parameters.kLayer:
            # Ignore cross edges for layer distance > kLayer.
            return nrNodes

        T = self.timeDict[tIntervalIdU]
        Tv = self.timeDict[tIntervalIdV]
        if tIntervalIdU != tIntervalIdV:
            self.crossLayerEdges.append(((A, timeV), (B, timeU)))
            # Add cross-layer edge outgoing from A.
            if (not A in self.crossLayerOut[Tv]):
                self.crossLayerOut[Tv][A] = {}
            if (not B in self.crossLayerOut[Tv][A]):
                self.crossLayerOut[Tv][A][B] = timeU
            else:
                self.crossLayerOut[Tv][A][B] = min(self.crossLayerOut[Tv][A][B], timeU)
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
                prev0 = self.inLayer[T][A][B][0]
                prev1 = self.inLayer[T][A][B][1]
                self.inLayer[T][A][B] = getMinMax(self.inLayer[T][A][B], timeU)
                if not(prev0 >= timeU or self.inLayer[T][A][B][0] <= timeU) or (not(prev1 <= timeU or self.inLayer[T][A][B][1] >= timeU)):
                    print(prev0, prev1, timeU)
                assert prev0 >= timeU or self.inLayer[T][A][B][0] <= timeU
                assert prev1 <= timeU or self.inLayer[T][A][B][1] >= timeU
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
        # Remove this if-statement if CLE should be considered parallel edges in CP network
        if tIntervalIdU != tIntervalIdV:
            return nrNodes
        # Note that edge self.humanDict[a], self.humanDict[b] can be added more than once.
        self.tGraphs[T].add_edge(self.humanDict[a], self.humanDict[b], time=self.msgDict[u][1])
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
            if '/\\' in crtLine:
                lst = crtLine.split('/\\')
            else:
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
        # For the apache dataset, there should be no errors.
        # assert errors == 0
        return nrNodes

    def getTFaultMonoplex(self, a, b, c, netw, netwType):
        tfTuple = (self.Label[a], self.Label[b], self.Label[c])
        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
        # a transitive-fault.
        if a == b or b == c or c == a:
            return
        if self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1]:
            self.addUniqueTfaults(netwType, tfTuple, 0)
            self.nr2paths[netwType][1][netw][b] -= 1
        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
        # transitive fault in the pessimistic model.
        if self.inLayer[netw][a][b][1] > self.inLayer[netw][b][c][0]:
            #print('Pessimistic fault', a, b, c, self.inLayer[netw][a][b], self.inLayer[netw][b][c])
            self.addUniqueTfaults(netwType, tfTuple, 1)
            self.nr2paths[netwType][2][netw][b] -= 1
        return

    def getTFaultMLN(self, a, b, c, netw, netwType):
        tfTuple = (self.Label[a], self.Label[b], self.Label[c])
        cleAdowntoB = b in self.crossLayerIn[netw] and a in self.crossLayerIn[netw][b]
        cleAtoBup = a in self.crossLayerOut[netw] and b in self.crossLayerOut[netw][a]
        cleBtoupC = b in self.crossLayerOut[netw] and c in self.crossLayerOut[netw][b]
        cleBdowntoC = c in self.crossLayerIn[netw] and b in self.crossLayerIn[netw][c]

        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
        # a transitive-fault.
        if (self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1]) and (not (cleAdowntoB or cleBtoupC)):
            self.addUniqueTfaults(netwType, tfTuple, 0)
            self.nr2paths[netwType][1][netw][b] -= 1
        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
        # transitive fault in the pessimistic model.
        if self.inLayer[netw][a][b][1] > self.inLayer[netw][b][c][0] or cleBdowntoC or cleAtoBup:
            self.addUniqueTfaults(netwType, tfTuple, 1)
            self.nr2paths[netwType][2][netw][b] -= 1
        return

    def addCLEPathAB(self, netw, netwType, a, b):
        assert netwType == 'MLN'
        if b in self.crossLayerOut[netw]:
            for c in self.crossLayerOut[netw][b]:
                if not (b in self.inLayer[netw] and c in self.inLayer[netw][b]):
                    self.addTwoPath((self.Label[a], self.Label[b], self.Label[c]), netwType)
                    # Cross-edges b->c where there is also an in-layer edge b->c are treated in getTFaultMLN.
                    assert (self.crossLayerOut[netw][b][c] > self.inLayer[netw][a][b][1])
                    for ty in range(3):
                        self.nr2paths[netwType][ty][netw][b] += 1

    def addCLEPathA(self, netw, netwType, a):
        for b in self.crossLayerOut[netw][a]:
            netwb = self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b])]
            if not (b in self.inLayer[netwb]):
                # Ignore bs with no inLayer edge b->c
                continue
            if not (a in self.inLayer[netwb] and b in self.inLayer[netwb][a]):
                for c in self.inLayer[netwb][b]:
                    for ty in range(3):
                        self.nr2paths[netwType][ty][netw][b] += 1
                    tfTuple = (self.Label[a], self.Label[b], self.Label[c])
                    # Cross-edges c->a where there is also an in-layer edge c->a are treated in getTFaultMLN.
                    if self.crossLayerOut[netw][a][b] > self.inLayer[netwb][b][c][1]:
                        self.addUniqueTfaults(netwType, tfTuple, 0)
                        self.nr2paths[netwType][1][netw][b] -= 1
                    if self.crossLayerOut[netw][a][b] > self.inLayer[netwb][b][c][0]:
                        self.addUniqueTfaults(netwType, tfTuple, 1)
                        self.nr2paths[netwType][2][netw][b] -= 1

    def addUniqueTfaults(self, netwType, tfTuple, type):
        if not (tfTuple in self.uniqueFaults[netwType][type]):
            self.uniqueFaults[netwType][type][tfTuple] = 1
            self.tfCount[netwType][type] += 1
        else:
            self.uniqueFaults[netwType][type][tfTuple] += 1

    def initTFRForNode(self, netw, netwType, a):
        self.nr2paths[netwType][0][netw][a] = 0
        self.nr2paths[netwType][1][netw][a] = 0
        self.nr2paths[netwType][2][netw][a] = 0

    def addTFRForNode(self, netw, netwType, transFaultSum, a):
        if self.nr2paths[netwType][0][netw][a] == 0:
            # When computing the transitive fault rate, ignore the nodes without 2-paths.
            return transFaultSum
        optimisticCount = self.nr2paths[netwType][0][netw][a] - self.nr2paths[netwType][1][netw][a]
        pesimisticCount = self.nr2paths[netwType][0][netw][a] - self.nr2paths[netwType][2][netw][a]
        transFaultSum[0] += (optimisticCount / self.nr2paths[netwType][0][netw][a])
        transFaultSum[1] += (pesimisticCount / self.nr2paths[netwType][0][netw][a])
        return transFaultSum

    def addTwoPath(self, twoPathTuple, netwType):
        self.twoPaths[netwType][twoPathTuple] = True

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
            # if netwType == 'MLN':
            #     for a in self.crossLayerOut[netw]:
            #         if not (a in self.inLayer[netw]):
            #             self.initTFRForNode(netw, netwType, a)
            #             self.addCLEPathA(netw, netwType, a)
            #             transFaultSum = self.addTFRForNode(netw, netwType, transFaultSum, a)

            netwEdges = self.inLayer[netw]
            # #Uncomment this part if the CP network adds CLE as inLayer parallel edges.
            # if (netwType == "MLN"):
            #     netwEdges = self.inLayer[netw]
            # else:
            #     netwEdges = self.Adj[netw]
            atLeastOne2Path = False
            has2Paths = 0
            for a in self.netwNodes[netw]:
                self.initTFRForNode(netw, netwType, a)
            for a in netwEdges:
                for b in netwEdges[a]:
                    if netwType == 'MLN':
                        self.addCLEPathAB(netw, netwType, a, b)
                    if not (b in netwEdges):
                        # Ignore a's neighbours with out-degree = 0.
                        continue
                    for c in netwEdges[b]:
                        # Count the 2-path : a->b->c
                        if a == b or b == c or c == a:
                            continue
                        atLeastOne2Path = True
                        twoPathTuple = (self.Label[a], self.Label[b], self.Label[c])
                        self.addTwoPath(twoPathTuple, netwType)
                        self.nr2paths[netwType][0][netw][b] += 1
                        self.nr2paths[netwType][1][netw][b] += 1
                        self.nr2paths[netwType][2][netw][b] += 1
                        if netwType == 'MLN':
                            self.getTFaultMLN(a, b, c, netw, netwType)
                        else:
                            self.getTFaultMonoplex(a, b, c, netw, netwType)
                if self.nr2paths[netwType][0][netw][a] > 0:
                    has2Paths += 1

            for a in self.nr2paths[netwType][0][netw]:
                transFaultSum = self.addTFRForNode(netw, netwType, transFaultSum, a)

            # The network transitive fault rate is the sum of the node transitive fault rates over all
            # nodes, divided by the number of nodes in the network.
            transFaultSum[0] /= N
            transFaultSum[1] /= N
            self.TFperNetw[netwType][netw] = (transFaultSum[0], transFaultSum[1])
            # optimistic model should have at most pessimistic model transitive faults.
            assert transFaultSum[0] <= transFaultSum[1]
            if atLeastOne2Path:
                upperBound = max(transFaultSum[1], upperBound)
                lowerBound = min(transFaultSum[0], lowerBound)

        self.crtResult[netwType][0] = (lowerBound, upperBound)

    # Returns the number of edges in the MLN network: (inLayer, outLayer, in + out)
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
                    netwb = self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b])]
                    if b in self.crossLayerIn[netwb]:
                        if self.crossLayerIn[netwb][b][a][0] != self.crossLayerOut[netw][a][b] and self.crossLayerIn[netwb][b][a][1] != self.crossLayerOut[netw][a][b]:
                            crossLayerEdgeCount += 1

        return (inLayerEdgeCount, crossLayerEdgeCount, crossLayerEdgeCount + inLayerEdgeCount)

    # Return the number of inLayer edges for the monoplex network.
    def getMonoplexEdgeCount(self):
        inLayerEdgeCount = 0
        for netw in range(1, self.nrGraphs + 1):
            for a in self.inLayer[netw]:
                inLayerEdgeCount += len(self.inLayer[netw][a])
                for b in self.inLayer[netw][a]:
                    if (self.inLayer[netw][a][b][0] != self.inLayer[netw][a][b][1]):
                        inLayerEdgeCount += 1
        return inLayerEdgeCount

    def getTfCount(self, netwType, tfType):
        if tfType == 'TF':
            return self.tfCount[netwType]
        else:
            res = [0, 0]
            for netw in range(1, self.nrGraphs + 1):
                for ty in range(2):
                    res[ty] += self.TFperNetw[netwType][netw][ty]
            return res

    # Use for GT
    def getAllTFs(self):
        tfSumAll = [0, 0]
        optimisticCount = {}
        pessimisticCount = {}
        nr2pathsC = {}
        for a in self.minPair:
            optimisticCount[a] = 0
            pessimisticCount[a] = 0
            nr2pathsC[a] = 0
        for a in self.minPair:
            for b in self.minPair[a]:
                if not (b in self.minPair) or a == b:
                    continue
                assert b in self.maxPair[a]
                for c in self.maxPair[b]:
                    if a == c or b == c:
                        continue
                    nr2pathsC[b] += 1
                    if self.minPair[a][b] > self.maxPair[b][c]:
                        optimisticCount[b] += 1
                        tfSumAll[0] += 1
                    if self.maxPair[a][b] > self.minPair[b][c]:
                        pessimisticCount[b] += 1
                        tfSumAll[1] += 1

        self.aggregCrtRes = [0, 0]
        for a in self.minPair:
            self.gtTP[a] = nr2pathsC[a]
            self.gtTF[0][a] = optimisticCount[a]
            self.gtTF[1][a] = pessimisticCount[a]
            if nr2pathsC[a] == 0:
                continue
            self.aggregCrtRes[0] += optimisticCount[a] / nr2pathsC[a]
            self.aggregCrtRes[1] += pessimisticCount[a] / nr2pathsC[a]
        self.aggregCrtRes[0] /= len(self.minPair)
        self.aggregCrtRes[1] /= len(self.minPair)
        return tfSumAll

    def getAggResNewDef(self, netwType):
        TFCount = [{}, {}]
        nr2Paths = {}
        nodes = {}
        for twoPathTuple in self.twoPaths[netwType]:
            for tupleNod in twoPathTuple:
                if not tupleNod in nodes:
                    nodes[tupleNod] = True
            if not twoPathTuple[1] in nr2Paths:
                TFCount[0][twoPathTuple[1]] = 0
                TFCount[1][twoPathTuple[1]] = 0
                nr2Paths[twoPathTuple[1]] = 0
            nr2Paths[twoPathTuple[1]] += 1
        for i in range(2):
            for fault in self.uniqueFaults[netwType][i]:
                TFCount[i][fault[1]] += 1
        bounds = [0, 0]
        for nod in nr2Paths:
            for i in range(2):
                if TFCount[i][nod] == nr2Paths[nod]:
                    bounds[i] += 1
                else:
                    bounds[i] += TFCount[i][nod] / (nr2Paths[nod] - TFCount[i][nod])
        for i in range(2):
            bounds[i] = bounds[i] / len(nr2Paths)
        self.crtResultAgg[netwType] = bounds
        # if self.delta_t == 3600:
        #     self.compute2PHist(self.getVals(nr2Paths, 50, True), 'small2P.png')
        #     self.compute2PHist(self.getVals(nr2Paths, 50, False), 'big2P.png')

    def getVals(self, nr2P, x, smallValues):
        vals = []
        for nod in nr2P:
            if smallValues and nr2P[nod] <= 50:
                vals.append(nr2P[nod])
            elif not(smallValues) and nr2P[nod] > 50:
                vals.append(nr2P[nod])
        return vals

    def compute2PHist(self, vals, fileName):
        if 'small' in fileName:
            xvalues = []
            yvalues = []
            for i in range(26):
                xvalues.append(i * 2)
            plt.xticks(xvalues, xvalues)
            for i in range(12):
                yvalues.append(i * 5)
            plt.yticks(yvalues, yvalues)

        plt.hist(vals, bins = 50,
                 color='blue', edgecolor='black')
        plt.title('Histogram for Apache ', size=8)
        plt.xlabel('Nr 2 paths (1h)', size=8)
        plt.ylabel('count', size=10)
        plt.tight_layout()
        #plt.show()
        plt.savefig(fileName)
        plt.close()

    def printNetwork2paths(self, netwType):
        for netw in range(1, self.nrGraphs + 1):
            for a in self.nr2paths[netwType][0][netw]:
                print('Nod ', a, 'has #2paths:', self.nr2paths[netwType][0][netw][a],
                      self.nr2paths[netwType][1][netw][a], self.nr2paths[netwType][2][netw][a])


