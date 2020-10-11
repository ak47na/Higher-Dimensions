import mailID
from datetime import datetime
from datetime import timedelta
from networkx import *
from scipy.stats import spearmanr
from math import *
class InformationFlowNetwork:
    def __init__(self, msgDict):
        self.humanDict = {}
        self.Label = {}
        self.minT = {}
        self.maxT = {}
        # Adj[graphIndex][node] = the adjacency list of node in the graphIndex-th graph.
        self.Adj = {}
        # msgDict[msgKey] = (sender, time)
        self.msgDict = msgDict
        # timeDict[timeInterval] = the index of the network with messages sent in timeInterval
        # timeInterval = integer
        self.timeDict = {}
        # tGraphs = List of the networkX multiDiGraphs for each time time interval, i.e
        # TGraphs[index] = the graph for timeInterval with timeDict[timeInterval] = index.
        self.tGraphs = [0]
        # nr2paths[t][network][node] = the number of 2-paths of node in network
        # if t == 0, then the count includes transitive faults
        #    t == 1, then the count excludes transitive faults with optimistic model
        #    t == 2, then the count excludes transitive faults with pessimistic model
        self.nr2paths = [{}, {}, {}]
        # nr2p[t][node] = the number of 2-paths of node in aggregate network, i.e
        #               = sum(network in networks, nr2p[t][network][node])
        self.nr2p = [{}, {}, {}]

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

    '''
        Adds an edge between the sender of message u and the sender of message v. delta_t represents the
        number of seconds aggregated into one time interval.
        Returns the current number of graphs of messages spanning delta_t seconds, the number of human
        nodes across all networks.
    '''
    def addEdge(self, u, v, delta_t, nrGraphs, nrNodes, minTime):
        # u is a reply to v, a is the sender of u, b is the sender of v.
        a = self.msgDict[u][0]
        b = self.msgDict[v][0]
        nrNodes = self.addHuman(a, nrNodes)
        nrNodes = self.addHuman(b, nrNodes)
        if a == b:
            return nrGraphs, nrNodes
        A = self.humanDict[a]
        B = self.humanDict[b]
        # Compute the index of the network which contains the point in time when message v was sent.
        tIntervalId = trunc((self.msgDict[v][1].timestamp() - minTime) / delta_t)
        if not (tIntervalId in self.timeDict):
            nrGraphs += 1
            self.Adj[nrGraphs] = {}
            self.minT[nrGraphs] = {}
            self.maxT[nrGraphs] = {}
            self.tGraphs.append(networkx.MultiDiGraph())
            self.timeDict[tIntervalId] = nrGraphs

        T = self.timeDict[tIntervalId]
        # Update the minimum and maximum time for a conversation from person A to person B.
        # The value is necessary for computing transitive faults.
        if not ((A, B) in self.minT[T]):
            self.minT[T][(A, B)] = self.msgDict[v][1].timestamp()
            self.maxT[T][(A, B)] = self.msgDict[v][1].timestamp()
        else:
            self.minT[T][(A, B)], self.maxT[T][(A, B)] = updateTimeBorders(self.minT[T][(A, B)],
                                                                                self.maxT[T][(A, B)],
                                                                                self.msgDict[v][1].timestamp())
        # Add an edge in the T-th MultiDiGraph from the node representing human a to the node
        # representing human b.
        self.tGraphs[T].add_edge(self.humanDict[a], self.humanDict[b], time=self.msgDict[v][1])
        if not (A in self.Adj[T]):
            self.Adj[T][A] = []
        self.Adj[T][A].append(B)
        return nrGraphs, nrNodes

    '''
        Reads the file with messages' relations and adds a directed edge from the reply to the message.
    '''

    def readMsgEdges(self, delta_t, nrGraphs, nrNodes, minTime):
        errors = 0
        invalidMsg = {}
        # file with each line containing two string numbers u v representing that message with key v is
        # a reply to message with key u.
        edgeFile = open("Data\\msgEdges.txt", "r")

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
            if lst[0] in self.msgDict and lst[1] in self.msgDict:
                nrGraphs, nrNodes = self.addEdge(lst[1], lst[0], delta_t, nrGraphs, nrNodes, minTime)
        edgeFile.close()
        return nrGraphs, nrNodes

    '''
        Computes the number of 2-paths(with or without transitive faults) for each node. The number of
        seconds aggregated in each network is delta_t.
        Transitive fault = "a directed path of length exactly two where the time label on the first edge
        is later than the time label on the second edge along the path, i.e. a directed 2-path with
        decreasing edge time stamps."
    '''

    def getTransitiveFault(self, delta_t, nrGraphs):
        upperBound = 0
        lowerBound = 1
        Y = 3600 * 24 * 365
        for netw in range(1, nrGraphs + 1):
            N = self.tGraphs[netw].number_of_nodes()
            transFaultSum = [0, 0]
            # 0 = with transitive faults,
            # 1 = without transitive faults(optimistic model)
            # 2 = without transitive faults(pessimistic model)
            self.nr2paths[0][netw] = {}
            self.nr2paths[1][netw] = {}
            self.nr2paths[2][netw] = {}
            for a in self.Adj[netw]:
                self.nr2paths[0][netw][a] = 0
                self.nr2paths[1][netw][a] = 0
                self.nr2paths[2][netw][a] = 0
                # optimisticCount - "lower bound on the transitive fault rate.
                # whenever we see b->c following a->b, we indicate no transitive faults for the 2-path
                # a->b->c, regardless of if there is an edge b->c prior to the edge a->b(which in
                # isolation would represent a transitive fault)."
                optimisticCount = 0
                # pessimisticCount - "upper bound on the fault rate. Here, whenever we see an edge a->b
                # after an edge b->c, we label the 2-path a->b->c as a transitive fault regardless of
                # what other edges between a, b and c exist in the same time interval."
                pesimisticCount = 0
                for b in self.Adj[netw][a]:
                    if not (b in self.Adj[netw]):
                        # Ignore a's neighbours with out-degree = 0.
                        continue
                    for c in self.Adj[netw][b]:
                        # Count the 2-path : a->b->c
                        self.nr2paths[0][netw][a] += 1
                        self.nr2paths[1][netw][a] += 1
                        self.nr2paths[2][netw][a] += 1
                        # If there is no edge a->b with time smaller than an edge b->c, then a->b->c is
                        # a transitive-fault.
                        if self.minT[netw][(a, b)] > self.maxT[netw][(b, c)]:
                            optimisticCount += 1
                            self.nr2paths[1][netw][a] -= 1
                        # If there is an edge a->b with time bigger than b->c, then a->b->c is a
                        # transitive fault in the pessimistic model.
                        if self.maxT[netw][(a, b)] > self.minT[netw][(b, c)]:
                            pesimisticCount += 1
                            self.nr2paths[2][netw][a] -= 1
                if self.nr2paths[0][netw][a] == 0:
                    # When computing the transitive fault rate, ignore the nodes without 2-paths.
                    continue
                transFaultSum[0] += (optimisticCount / self.nr2paths[0][netw][a])
                transFaultSum[1] += (pesimisticCount / self.nr2paths[0][netw][a])
            # The network transitive fault rate is the sum of the node transitive fault rates over all
            # nodes, divided by the number of nodes in the network.
            transFaultSum[0] /= N
            transFaultSum[1] /= N
            upperBound = max(max(transFaultSum[0], transFaultSum[1]), upperBound)
            lowerBound = min(min(transFaultSum[0], transFaultSum[1]), lowerBound)

        print('For delta_t ', delta_t / Y, 'years', lowerBound, upperBound)

    '''
        Returns the list of nodes in the netw-th network, sorted in increasing order by the number of
        2-paths for each node. id represents the type of network (0 = without transitive faults, 
        1 = with optimistic transitive faults, 2 =  with pessimistic transitive faults.)
    '''

    def getNodesOrder(self, id, netw):
        centralityList = []
        for nod in self.nr2paths[id][netw]:
            centralityList.append((self.nr2paths[id][netw][nod], nod))
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
        return order

    '''
        For the current delta_t time interval, compute the number of 2-paths for each node in the
        aggregate network as the sum of the number of 2-paths of the node in each network.
    '''
    def compute2PathsAggregateNetwork(self, nrGraphs):
        for netw in range(1, nrGraphs + 1):
            for nod in self.nr2paths[0][netw]:
                if not (nod in self.nr2p[0]):
                    for i in range(3):
                        self.nr2p[0][nod] = 0
                        self.nr2p[1][nod] = 0
                        self.nr2p[2][nod] = 0
                for i in range(3):
                    self.nr2p[i][nod] += self.nr2paths[i][netw][nod]

    def getRanginkCorrelation(self, nrGraphs):
        Order = [[], [], []]
        for netw in range(1, nrGraphs + 1):
            order = []
            for i in range(3):
                order.append(self.getNodesOrder(i, netw))
                for x in order[i]:
                    Order[i].append(x)
        w, p = spearmanr(Order[0], Order[1])
        print(w, p)
        w, p = spearmanr(Order[0], Order[2])
        print(w, p)

    '''
        Returns the Spearman rank correlation value between the 2-path ranking of the nodes in the
        network with transitive faults with the 2-path ranking of the nodes in the network without 
        transitive faults.
    '''

    def getRanginkCorrelationAggregate(self, nrGraphs):
        self.compute2PathsAggregateNetwork(nrGraphs)
        order = []
        for i in range(3):
            order.append(self.getNodesOrderAggregate(i))
        w, p = spearmanr(order[0], order[1])
        print(w, p)
        w, p = spearmanr(order[0], order[2])
        print(w, p)

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
def readMsgDetails():
    msgDict = {}
    nrM = 0
    # read the file with the details of all messages in format :
    # msgKey/\senderName/\senderEmail/\date(%Y-%m-%d %H:%M:%S)
    detailsFile = open("Data\\msgDetails.txt", "r")
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
        nrM += 1
        msgEmail = mailID.purifyEmail(lst[2].replace(' ', ''))
        msgDate = datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        # store the message with key lst[0]
        msgDict[lst[0]] = (msgEmail, msgDate)
        minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
    detailsFile.close()
    return minTime, maxTime, msgDict

'''
    Method that creates all information flow networks such that the number of seconds for each 
    network is delta_t, computes the number of transitive faults and the Spearman correlation of
    the 2-path rankings between the (aggregate) network with transitive faults and the one without.
'''
def getValues(delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = InformationFlowNetwork(msgDict)
    nrGraphs, nrNodes = infoFlowNetwork.readMsgEdges(delta_t, 0, 0, minTime)
    infoFlowNetwork.getTransitiveFault(delta_t, nrGraphs)
    infoFlowNetwork.getRanginkCorrelationAggregate(nrGraphs)
