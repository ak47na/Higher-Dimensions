import mailID
from datetime import datetime
import Sample
# from datetime import timedelta


Adj = {}
msgDict = {}
nrNodes = 0
nrLayers = 0
humanDict = {}
timeDict = {}
nodeLayers = []
Edges = []

edges = []
def addHuman(name):
    global nrNodes
    if not (name in humanDict):
        nrNodes += 1
        humanDict[name] = nrNodes
        Adj[nrNodes] = []

# u is a reply to v, a is the sender of u, b is the sender of v
def addEdge(u, v):
    a = msgDict[u][0]
    b = msgDict[v][0]
    addHuman(a)
    addHuman(b)
    if not (msgDict[u][1] in timeDict):
        timeDict[msgDict[u][1]] = True
    edges.append((humanDict[a], humanDict[b], msgDict[u][1]))

def readMsgDetails():
    nrM = 0
    detailsFile = open("\\TxtDataInUse\\msgDetails.txt", "r")
    while True:
        crtL = detailsFile.readline()
        if not crtL:
            break
        crtL = crtL.replace('\n', '')
        #msgKey/\name/\email/\date
        lst = crtL.split('/\\')
        if len(lst) != 4:
            print(lst)
            exit()
        nrM += 1
        msgEmail = lst[2].replace(' ', '')
        msgEmail = mailID.removeStrings(msgEmail.replace('\n', '')).replace(' ', '')
        msgDate = datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        msgDict[lst[0]] = (msgEmail, msgDate)
    detailsFile.close()
    print(nrM)

def readMsgEdges():
    errors = 0
    invalidMsg = {}
    edgeFile = open("\\TxtDataInUse\\msgEdges.txt", "r")
    while True:
        crtL = edgeFile.readline()
        if not crtL:
            break
        crtL = crtL.replace('\n', '')
        lst = crtL.split(' ')
        if len(lst) != 2:
            print(lst)
            exit()
        if not (lst[0] in msgDict) and not (lst[0] in invalidMsg):
            invalidMsg[lst[0]] = True
            errors += 1
        if not (lst[1] in msgDict) and not (lst[1] in invalidMsg):
            invalidMsg[lst[1]] = True
            errors += 1
        if lst[0] in msgDict and lst[1] in msgDict:
            addEdge(lst[1], lst[0])
    edgeFile.close()
    print(errors)

def normTime():
    global nrLayers
    timeList = []
    for t in timeDict:
        timeList.append(t)
    timeList = sorted(timeList)

    nrLayers = len(timeList)
    for i in range(nrLayers):
        timeDict[timeList[i]] = i + 1

def getEdges():
    from Edge import myEdge
    for edge in edges:
        Edges.append(myEdge(edge[0], timeDict[edge[2]], edge[1], timeDict[edge[2]], 0))
        Adj[edge[0]].append((edge[1], timeDict[edge[2]]))

mailID.init()
readMsgDetails()
readMsgEdges()
normTime()
getEdges()
nodes = []
nodeSample = Sample.sampleOfNodes(nrNodes, 40)
for node in nodeSample:
    nodes.append((node, Adj[node]))
s = Sample.Sample(nrLayers, Sample.sampleFromNodes(nodes), Edges)
print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())
s.addOrdinalAliasEdges()
print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())
s.createEdgesFile("\\temporalEdges.txt")
Sample.createLayoutFile("\\muxViz-master\\data\\temporalGraph\\B.txt", s.getNrNodes(), False)
Sample.createLayoutFile("\\muxViz-master\\data\\temporalGraph\\C.txt", s.getNrLayers(), True)
