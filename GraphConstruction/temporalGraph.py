import mailID
from datetime import datetime
# from datetime import timedelta

msgDict = {}
nrNodes = 0
humanDict = {}
timeDict = []
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
    detailsFile = open("\\msgDetails.txt", "r")
    while True:
        crtL = detailsFile.readline()
        if not crtL:
            break
        #msgKey/\name/\email/\date
        lst = crtL.split('/\\')
        if len(lst) != 4:
            print(lst)
            exit()
        msgEmail = lst[2].replace(' ', '')
        msgEmail = mailID.removeStrings(msgEmail.replace('\n', '')).replace(' ', '')
        msgDate = datetime.strptime(lst[3], '%d %b %Y %H:%M:%S')
        msgDict[lst[0]] = (msgEmail, msgDate)
    detailsFile.close()

def readMsgEdges():
    edgeFile = open("\\msgEdges.txt", "r")
    while True:
        crtL = edgeFile.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        if len(lst) != 2:
            print(lst)
            exit()
        addEdge(lst[0], lst[1])
    edgeFile.close()

def normTime():
    timeList = []
    for t in timeDict:
        timeList.append(t)
    timeList = sorted(timeList)
    T = len(timeList)
    for i in range(T):
        timeDict[timeList[i]] = i + 1

def printEdges():
    edgeOut = open("\\temporalEdges.txt")
    for edge in edges:
        edgeOut.write(str(edge[0]) + ' ' + str(timeDict[edge[2]]) + ' ' + str(edge[1]) + ' ' + str(timeDict[edge[2]]) + '\n')
    edgeOut.close()

mailID.init()
readMsgDetails()
readMsgEdges()
normTime()
printEdges()
