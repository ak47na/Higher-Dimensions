import mailID
from datetime import datetime
from datetime import timedelta
from networkx import *
from scipy.stats import spearmanr
from math import *

nrNodes = 0
nrLayers = 0
humanDict = {}

def initData():
    global minT, maxT, minTime, maxTime, Label, Adj, msgDict, nrNodes, nrLayers
    global timeDict, nodeLayers, Edges, tGraphs, nrGraphs, edges
    minT = {}
    maxT = {}

    minTime = datetime.now().timestamp()
    maxTime = 0

    Label = {}
    Adj = {}
    msgDict = {}

    timeDict = {}
    nodeLayers = []
    Edges = {}
    tGraphs = [0]
    nrGraphs = 0
    edges = []



def addHuman(name):
    name = mailID.getIdentity(name)
    global nrNodes
    if not (name in humanDict):
        nrNodes += 1
        Label[nrNodes] = name
        humanDict[name] = nrNodes


# u is a reply to v, a is the sender of u, b is the sender of v
def addEdge(u, v, delta_t):
    global nrGraphs
    a = msgDict[u][0]
    b = msgDict[v][0]
    addHuman(a)
    addHuman(b)
    if a == b:
        return
    A = humanDict[a]
    B = humanDict[b]
    tIntervalId = trunc((msgDict[v][1].timestamp() - minTime) / delta_t)
    if not (tIntervalId in timeDict):
        nrGraphs += 1
        Adj[nrGraphs] = {}
        minT[nrGraphs] = {}
        maxT[nrGraphs] = {}
        tGraphs.append(networkx.MultiDiGraph())
        timeDict[tIntervalId] = nrGraphs

    T = timeDict[tIntervalId]
    if not ((A, B) in minT[T]):
        minT[T][(A, B)] = msgDict[v][1].timestamp()
        maxT[T][(A, B)] = msgDict[v][1].timestamp()
    else:
        minT[T][(A, B)], maxT[T][(A, B)] = updateTimeBorders(minT[T][(A, B)], maxT[T][(A, B)],
                                                             msgDict[v][1].timestamp())
    tGraphs[T].add_edge(humanDict[a], humanDict[b], time=msgDict[v][1])
    if not (A in Adj[T]):
        Adj[T][A] = []
    Adj[T][A].append(B)


def updateTimeBorders(minTime, maxTime, t):
    minTime = min(minTime, t)
    maxTime = max(maxTime, t)
    return minTime, maxTime

'''
    Reads the message details from file and updates the messages dictionary to store for each 
    message key, the email of the sender and the date of the message as a tuple.
'''
def readMsgDetails():
    global minTime, maxTime
    nrM = 0
    # read the file with the details of all messages in format :
    # msgKey/\senderName/\senderEmail/\date(%Y-%m-%d %H:%M:%S)
    detailsFile = open("Data\\msgDetails.txt", "r")
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
        msgDict[lst[0]] = (msgEmail, msgDate)
        minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
    detailsFile.close()

def readMsgEdges(delta_t):
    errors = 0
    invalidMsg = {}
    edgeFile = open("Data\\msgEdges.txt", "r")

    while True:
        crtLine = edgeFile.readline()
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '')
        lst = crtLine.split(' ')
        assert len(lst) == 2
        if not (lst[0] in msgDict) and not (lst[0] in invalidMsg):
            invalidMsg[lst[0]] = True
            errors += 1
        if not (lst[1] in msgDict) and not (lst[1] in invalidMsg):
            invalidMsg[lst[1]] = True
            errors += 1
        if lst[0] in msgDict and lst[1] in msgDict:
            addEdge(lst[1], lst[0], delta_t)
    edgeFile.close()

nr2paths = [{}, {}, {}]

def getTransitiveFault(delta_t):
    upperBound = 0
    lowerBound = 1
    Y = 3600 * 24 * 30 * 12
    for netw in range(1, nrGraphs + 1):
        N = tGraphs[netw].number_of_nodes()
        transFaultSum = [0, 0]
        #0 = with transitive faults, 1 & 2 without
        nr2paths[0][netw] = {}
        nr2paths[1][netw] = {}
        nr2paths[2][netw] = {}
        for a in Adj[netw]:
            nr2paths[0][netw][a] = 0
            nr2paths[1][netw][a] = 0
            nr2paths[2][netw][a] = 0
            optimisticCount = 0
            pesimisticCount = 0
            for b in Adj[netw][a]:
                if not (b in Adj[netw]):
                    continue
                for c in Adj[netw][b]:
                    nr2paths[0][netw][a] += 1
                    nr2paths[1][netw][a] += 1
                    nr2paths[2][netw][a] += 1
                    if minT[netw][(a, b)] > maxT[netw][(b, c)]:
                        optimisticCount += 1
                        nr2paths[1][netw][a] -= 1
                    if maxT[netw][(a, b)] > minT[netw][(b, c)]:
                        pesimisticCount += 1
                        nr2paths[2][netw][a] -= 1
            if nr2paths[0][netw][a] == 0:
                continue
            transFaultSum[0] += (optimisticCount / nr2paths[0][netw][a])
            transFaultSum[1] += (pesimisticCount / nr2paths[0][netw][a])
        transFaultSum[0] /= N
        transFaultSum[1] /= N
        upperBound = max(max(transFaultSum[0], transFaultSum[1]), upperBound)
        lowerBound = min(min(transFaultSum[0], transFaultSum[1]), lowerBound)

    print('For delta_t ', delta_t / Y, 'years', lowerBound, upperBound)

def getNodesOrder(id, netw):
    centralityList = []
    for nod in nr2paths[id][netw]:
        centralityList.append((nr2paths[id][netw][nod], nod))
    centralityList = sorted(centralityList)
    order = []
    for p in centralityList:
        order.append(p[1])
    return order

def getNodesOrderAggregate(id):
    centralityList = []
    for nod in nr2p[id]:
        centralityList.append((nr2p[id][nod], nod))
    centralityList = sorted(centralityList)
    order = []
    for p in centralityList:
        order.append(p[1])
    return order

nr2p = [{}, {}, {}]

def AggregateNetwork():
    for netw in range(1, nrGraphs + 1):
        for nod in nr2paths[0][netw]:
            if not (nod in nr2p[0]):
                for i in range(3):
                    nr2p[0][nod] = 0
                    nr2p[1][nod] = 0
                    nr2p[2][nod] = 0
            for i in range(3):
                nr2p[i][nod] += nr2paths[i][netw][nod]

def getRanginkCorrelation():
    #order1 = order of nodes without transitive faults
    #order2 = order of nodes with transitive faults
    Order = [[], [], []]
    for netw in range(1, nrGraphs + 1):
        order = []
        for i in range(3):
            order.append(getNodesOrder(i, netw))
            for x in order[i]:
                Order[i].append(x)
    w, p = spearmanr(Order[0], Order[1])
    print(w, p)
    w, p = spearmanr(Order[0], Order[2])
    print(w, p)

def getRanginkCorrelationAggregate():
    AggregateNetwork()
    order = []
    for i in range(3):
        order.append(getNodesOrderAggregate(i))
    w, p = spearmanr(order[0], order[1])
    print(w, p)
    w, p = spearmanr(order[0], order[2])
    print(w, p)

mailID.init()

def getValues(delta_t):
    initData()
    readMsgDetails()
    readMsgEdges(delta_t)
    getTransitiveFault(delta_t)
    getRanginkCorrelationAggregate()
