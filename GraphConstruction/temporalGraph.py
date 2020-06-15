import mailID
from datetime import datetime
import Sample
# from datetime import timedelta

Label = {}
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
    name = mailID.getIdentity(name)
    global nrNodes
    if not (name in humanDict):
        nrNodes += 1
        Label[nrNodes] = name
        humanDict[name] = nrNodes
        Adj[nrNodes] = []

# u is a reply to v, a is the sender of u, b is the sender of v
def addEdge(u, v):
    a = msgDict[u][0]
    b = msgDict[v][0]
    addHuman(a)
    addHuman(b)
    if a == b:
        return
    if not (msgDict[v][1] in timeDict):
        timeDict[msgDict[v][1]] = True

    edges.append((humanDict[a], humanDict[b], msgDict[v][1]))

def readMsgDetails():
    nrM = 0
    detailsFile = open("\\msgDetails.txt", "r")
    while True:
        crtL = detailsFile.readline()
        if not crtL:
            break
        crtL = crtL.replace('\n', '')
        #msgKey/\name/\email/\date
        lst = crtL.split('/\\')
        if len(lst) != 4:
            exit()
        nrM += 1
        msgEmail = lst[2].replace(' ', '')
        msgEmail = mailID.purifyEmail(mailID.removeStrings(msgEmail.replace('\n', '')))
        msgDate = datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        msgDict[lst[0]] = (msgEmail, msgDate)
    detailsFile.close()
    print(nrM)

def readMsgEdges():
    errors = 0
    invalidMsg = {}
    edgeFile = open("\\msgEdges.txt", "r")
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

def normTime():
    global nrLayers
    timeList = []
    yearDict = {}
    for t in timeDict:
        timeList.append(t)
        yearDict[t.year] = True
    timeList = sorted(timeList)

    nrLayers = len(timeList)
    #print(timeList[0].year, timeList[nrLayers - 1])

    for i in range(nrLayers):
        timeDict[timeList[i]] = i
    #nrLayers = timeDict[timeList[nrLayers - 1]]


def getEdges():
    from Edge import myEdge
    for edge in edges:
            Edges.append(myEdge(edge[0], timeDict[edge[2]], edge[1], timeDict[edge[2]], 1))
            Adj[edge[0]].append((edge[1], timeDict[edge[2]]))

mailID.init()
readMsgDetails()
readMsgEdges()
normTime()
getEdges()
nodes, sampleEdges = Sample.sampleNodesFromEdges(Edges, 1)

s = Sample.Sample(nrLayers, nodes, sampleEdges, Label)
print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())
s.addOrdinalAliasEdges()
print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())
s.createEdgesFile("\\muxViz-master\\data\\temporalGraph\\temporalEdges.txt")
Sample.createLayoutFile("\\muxViz-master\\data\\temporalGraph\\B.txt", s.getNrNodes(), False)
# Sample.createLayoutFile("D:\\Ak_work2019-2020\\muxViz-master\\data\\temporalGraph\\C.txt", s.getNrLayers(), True)
