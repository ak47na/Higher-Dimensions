import mailID
from datetime import datetime
from networkx import *
from scipy.stats import spearmanr
from math import *
# Note: t0 < t1 <=> t0 happened before t1

def getMinMax(timePair, t):
    return (min(timePair[0], t), max(timePair[1], t))

class InformationFlowNetwork:
    def __init__(self, msgDict, delta_t, t, minTime):
        self.minTime = minTime
        self.nrEdges = 0
        self.replyDict = {}
        self.humanDict = {}
        self.Label = {}
        # minT[graphIndex][(A, B)] = min time t in graphIndex s.t there was a message from B to A at t.
        self.minT = {}
        self.maxT = {}
        #inLayer[graphIndex][A][B] = (minT, maxT)
        #crossLayerIn[graphIndex][A][B] = maxL
        #crossLayerOut[graphIndex][A][B] = minL
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
        self.nr2p = [{}, {}, {}]
        self.nrGraphs = 0
        self.delta_t = delta_t
        self.analysedT = t
        self.crtResult = {"monoplex" : [(0, 0), (0, 0), (0, 0)], "MLN": [(0, 0), (0, 0), (0, 0)]}

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
        self.timeDict[tIntervalId] = self.nrGraphs
        self.inLayer[self.nrGraphs] = {}
        self.crossLayerIn[self.nrGraphs] = {}
        self.crossLayerOut[self.nrGraphs] = {}

    '''
        Adds an edge between the sender of message v and the sender of message u. delta_t represents the
        number of seconds aggregated into one time interval.
        Returns the number of human nodes across all networks.
    '''
    def addEdge(self, u, v, nrNodes):
        # u is a reply to v, b is the sender of u, a is the sender of v.
        if (self.msgDict[u][1].timestamp() < self.msgDict[v][1].timestamp()):
            u, v = v, u
        assert (self.msgDict[u][1].timestamp() >= self.msgDict[v][1].timestamp())
        if ((u, v) in self.replyDict):
            # The reply u to message v was already processed.
            return nrNodes

        self.replyDict[(u, v)] = True
        b = self.msgDict[u][0]
        timeU = self.msgDict[u][1].timestamp()
        timeV = self.msgDict[v][1].timestamp()
        a = self.msgDict[v][0]
        nrNodes = self.addHuman(a, nrNodes)
        nrNodes = self.addHuman(b, nrNodes)
        if a == b:
            return nrNodes
        A = self.humanDict[a]
        B = self.humanDict[b]
        # Compute the index of the network which contains the point in time when message u was sent.
        tIntervalIdU = self.getTimeRange(timeU)
        tIntervalIdV = self.getTimeRange(timeV)


        if not (tIntervalIdU in self.timeDict):
            # Create the graph for tIntervalIdU
            self.createTGraphForT(tIntervalIdU)
        if not (tIntervalIdV in self.timeDict):
            # Create the graph for tIntervalIdV
            self.createTGraphForT(tIntervalIdV)

        T = self.timeDict[tIntervalIdU]
        if tIntervalIdU != tIntervalIdV:
            self.crossLayerEdges.append(((A, timeV), (B, timeU)))
            Tv = self.timeDict[tIntervalIdV]
            # Add cross-layer edge outgoing from A
            if (not A in self.crossLayerOut[Tv]):
                self.crossLayerOut[Tv][A] = {}
            if (not B in self.crossLayerOut[Tv][A]):
                self.crossLayerOut[Tv][A][B] = timeU
            else:
                self.crossLayerOut[Tv][A][B] = min(self.crossLayerOut[Tv][A][B], timeU)
            #Add cross-layer edge ingoing to B
            if (not B in self.crossLayerIn[T]):
                self.crossLayerIn[T][B] = {}
            if (not A in self.crossLayerIn[T][B]):
                self.crossLayerIn[T][B][A] = timeV
            else:
                self.crossLayerIn[T][B][A] = max(self.crossLayerIn[T][B][A], timeV)
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
        if not (A in self.Adj[T]):
            self.Adj[T][A] = {}
        if not (B in self.Adj[T][A]):
            self.tGraphs[T].add_edge(self.humanDict[a], self.humanDict[b], time=self.msgDict[u][1])
            self.Adj[T][A][B] = self.msgDict[u][1]
            self.nrEdges += 1
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
        if self.inLayer[netw][a][b][1] > self.inLayer[netw][b][c][0] or cleBdowntoC:
            pesimisticCount += 1
            self.nr2paths[netwType][2][netw][a] -= 1
        return optimisticCount, pesimisticCount

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
            if netwType == 'MLN':
                N = len(self.inLayer[netw])
            else:
                N = self.tGraphs[netw].number_of_nodes()
            if N == 0:
                continue
            transFaultSum = [0, 0]
            # 0 = with transitive faults,
            # 1 = without transitive faults(optimistic model)
            # 2 = without transitive faults(pessimistic model)
            self.nr2paths[netwType][0][netw] = {}
            self.nr2paths[netwType][1][netw] = {}
            self.nr2paths[netwType][2][netw] = {}
            if (netwType == "MLN"):
                netwEdges = self.inLayer[netw]
            else:
                netwEdges = self.Adj[netw]
            for a in netwEdges:
                self.nr2paths[netwType][0][netw][a] = 0
                self.nr2paths[netwType][1][netw][a] = 0
                self.nr2paths[netwType][2][netw][a] = 0
                optimisticCount = 0
                pesimisticCount = 0
                for b in netwEdges[a]:
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
                if self.nr2paths[netwType][0][netw][a] == 0:
                    # When computing the transitive fault rate, ignore the nodes without 2-paths.
                    continue
                transFaultSum[0] += (optimisticCount / self.nr2paths[netwType][0][netw][a])
                transFaultSum[1] += (pesimisticCount / self.nr2paths[netwType][0][netw][a])
            # The network transitive fault rate is the sum of the node transitive fault rates over all
            # nodes, divided by the number of nodes in the network.
            transFaultSum[0] /= N
            transFaultSum[1] /= N
            # optimistic model should have at most pessimistic model transitive faults.
            assert transFaultSum[0] <= transFaultSum[1]
            upperBound = max(transFaultSum[1], upperBound)
            lowerBound = min(transFaultSum[0], lowerBound)

        self.crtResult[netwType][0] = (lowerBound, upperBound)

    '''
        Returns the list of nodes in the netw-th network, sorted in increasing order by the number of
        2-paths for each node. id represents the type of network (0 = without transitive faults, 
        1 = with optimistic transitive faults, 2 =  with pessimistic transitive faults.)
    '''

    def getNodesOrder(self, id, netw):
        netwType = 'monoplex'
        centralityList = []
        for nod in self.nr2paths[netwType][id][netw]:
            centralityList.append((self.nr2paths[netwType][id][netw][nod], nod))
        centralityList = sorted(centralityList)
        order = []
        for p in centralityList:
            order.append(p[1])
        return order

    '''
        Returns the list of nodes in the aggregate network, sorted in increasing order by the number of
        2-paths for each node. id represents the type of network (0 = without transitive faults, 
        1 = with optimistic transitive faults, 2 =  with pessimistic transitive faults.)
    '''
    def getNodesOrderAggregate(self, id):
        centralityList = []
        for nod in self.nr2p[id]:
            centralityList.append((self.nr2p[id][nod], nod))
        centralityList = sorted(centralityList)
        order = []
        for p in centralityList:
            order.append(p[1])
            if len(order) > 1:
                assert(self.nr2p[id][order[-1]] >= self.nr2p[id][order[-2]])

        return order

    '''
        For the current delta_t time interval, compute the number of 2-paths for each node in the
        aggregate network as the sum of the number of 2-paths of the node in each network.
    '''
    def compute2PathsAggregateNetwork(self):
        netwType = 'monoplex'
        for netw in range(1, self.nrGraphs + 1):
            if not(netw in self.nr2paths[netwType][0]):
                continue
            for nod in self.nr2paths[netwType][0][netw]:
                if not (nod in self.nr2p[0]):
                    for i in range(3):
                        self.nr2p[0][nod] = 0
                        self.nr2p[1][nod] = 0
                        self.nr2p[2][nod] = 0
                for i in range(3):
                    self.nr2p[i][nod] += self.nr2paths[netwType][i][netw][nod]

    def getRanginkCorrelation(self):
        netwType = 'monoplex'
        Order = [[], [], []]
        for netw in range(1, self.nrGraphs + 1):
            order = []
            for i in range(3):
                order.append(self.getNodesOrder(i, netw))
                for x in order[i]:
                    Order[i].append(x)
        w, p = spearmanr(Order[0], Order[1])
        self.crtResult[netwType][1] = (w, p)
        #print(w, p)
        w, p = spearmanr(Order[0], Order[2])
        #print(w, p)
        self.crtResult[netwType][2] = (w, p)

    '''
        Returns the Spearman rank correlation value between the 2-path ranking of the nodes in the
        network with transitive faults with the 2-path ranking of the nodes in the network without 
        transitive faults.
    '''

    def getRanginkCorrelationAggregate(self):
        netwType = 'monoplex'
        self.compute2PathsAggregateNetwork()
        order = []
        for i in range(3):
            order.append(self.getNodesOrderAggregate(i))
        w, p = spearmanr(order[0], order[1])
        self.crtResult[netwType][1] = (w, p)
        #print(w, p)
        w, p = spearmanr(order[0], order[2])
        self.crtResult[netwType][2] = (w, p)
        #print(w, p)

    def getMLNEdgeCount(self):
        inLayerEdgeCount = 0
        crossLayerEdgeCount = 0
        for netw in range(1, self.nrGraphs + 1):
            for a in self.inLayer[netw]:
                inLayerEdgeCount += len(self.inLayer[netw][a])
                for b in self.inLayer[netw][a]:
                    if (self.inLayer[netw][a][b][0] != self.inLayer[netw][a][b][1]):
                        inLayerEdgeCount += 1
            for a in self.crossLayerOut[netw]:
                crossLayerEdgeCount += len(self.crossLayerOut[netw][a])
                for b in self.crossLayerOut[netw][a]:
                    netwb = self.timeDict[self.getTimeRange(self.crossLayerOut[netw][a][b])]
                    if b in self.crossLayerIn[netwb]:
                        if (self.timeDict[self.getTimeRange(self.crossLayerIn[netwb][b][a])] != netw):
                            crossLayerEdgeCount += 1

        return (inLayerEdgeCount, crossLayerEdgeCount, crossLayerEdgeCount + inLayerEdgeCount)

    def getEdgeCount(self):
        edgeCount = 0
        for netw in range(1, self.nrGraphs + 1):
            for a in self.Adj[netw]:
                for b in self.Adj[netw][a]:
                    edgeCount += 1
                    if (self.minT[netw][(a, b)] != self.maxT[netw][(a, b)]):
                        edgeCount += 1
        return edgeCount


'''
    Updates the minimum and maximum number of seconds with t.
'''
def updateTimeBorders(minTime, maxTime, t):
    minTime = min(minTime, t)
    maxTime = max(maxTime, t)
    return minTime, maxTime

'''
    Reads the message details from file and updates the messages dictionary to store for each 
    message key, the email of the sender and the date of the message as a tuple.
'''
def readMsgDetails(filePath):
    msgDict = {}
    # read the file with the details of all messages in format :
    # msgKey/\senderName/\senderEmail/\date(%Y-%m-%d %H:%M:%S)
    detailsFile = open(filePath, "r")
    # Initialise time borders.
    minTime = datetime.now().timestamp()
    maxTime = 0
    while True:
        crtLine = detailsFile.readline()
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '')
        # msgKey/\name/\email/\date
        lst = crtLine.split('/\\')
        assert len(lst) == 4
        # increment the number of messages
        # nrM += 1
        msgEmail = mailID.purifyEmail(lst[2].replace(' ', ''))
        msgDate = datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        # store the message with key lst[0]
        msgDict[lst[0]] = (msgEmail, msgDate)
        minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
    detailsFile.close()
    return minTime, maxTime, msgDict

'''
    Method that creates all information flow networks such that the number of seconds for each 
    network is delta_t.
'''
def createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = InformationFlowNetwork(msgDict, delta_t, t, minTime)
    msgEdgesFilePath = "Data\\msgEdges.txt"
    nrNodes = infoFlowNetwork.readMsgEdges(0, msgEdgesFilePath)
    return infoFlowNetwork

'''
    Method that computes the number of transitive faults and the Spearman correlation of
    the 2-path rankings between the (aggregate) network with transitive faults and the one without.
'''
def getValues(t, delta_t, minTime, maxTime, msgDict, netwType):
    infoFlowNetwork = createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
    infoFlowNetwork.getTransitiveFault(netwType)
    # print(nrNodes, infoFlowNetwork.nrEdges)
    if netwType == 'monoplex':
        infoFlowNetwork.getRanginkCorrelationAggregate()
        print("The number of edges is ", infoFlowNetwork.nrEdges)
        return infoFlowNetwork.crtResult[netwType], len(infoFlowNetwork.crossLayerEdges)
    else:
        print("The MLN network for ", t, " has ", infoFlowNetwork.getMLNEdgeCount(), " edges")
        print("The monoplex network for ", t, " has ", infoFlowNetwork.getEdgeCount(), " edges")
        return infoFlowNetwork.crtResult[netwType]


