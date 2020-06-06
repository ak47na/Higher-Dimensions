import mailID
from datetime import datetime
import Sample
# from datetime import timedelta

msgDict = {}
nrNodes = 0
nrLayers = 0
humanDict = {}
timeDict = {}

edges = []
def addHuman(name):
    global nrNodes
    if not (name in humanDict):
        nrNodes += 1
        humanDict[name] = nrNodes
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
    detailsFile = open("\\msgDetails.txt", "r")
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
            addEdge(lst[0], lst[1])
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

def printEdges():
    edgeOut = open("\\temporalEdges.txt", "w")
    for edge in edges:
        edgeOut.write(str(edge[0]) + ' ' + str(timeDict[edge[2]]) + ' ' + str(edge[1]) + ' ' + str(timeDict[edge[2]]) + '\n')
    edgeOut.close()


mailID.init()
readMsgDetails()
readMsgEdges()
normTime()
printEdges()
Sample.createLayoutFile("\\muxViz-master\\data\\temporalGraph\\B.txt", nrNodes, False)
Sample.createLayoutFile("\\muxViz-master\\data\\temporalGraph\\C.txt", nrLayers, True)
