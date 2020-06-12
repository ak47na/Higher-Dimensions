from OwnershipP import *
from Edge import *
from Sample import *
import datetime
from MyFile import *
from MyHuman import *

from scipy.stats import wilcoxon

nrLayers = 4

Adj = {}
nrEdges = 0
edgeList = []
LayerPerm = [0, 2, 4, 3, 1]


# C, F, R, I
def getLayer2(t1, t2):
    if t1 == 'committer' and t2 == 'author':
        return 3
    if t1 == 'committer' or t2 == 'committer':
        return 1
    if t1 == 'fileC' or t2 == 'fileC':
        return 1
    if t1 == 'file' and t2 == 'file':
        return 2
    if t1 == 'issueReporter' or t2 == 'issueReporter':
        return 3
    L1 = getLayer(t1)
    L2 = getLayer(t2)
    if L1 == 2 or L1 == 3 or L2 == 3 or L2 == 2:
        return 3
    if t1 == 'issueAssignee' and t2 == 'issue':
        return 4
    if t1 == 'file' and t2 == 'issue':
        return 4
    if t1 == 'issue' and t2 == 'issue':
        return 4
    # In case a pair is omitted
    print(t1, t2)
    exit()


def getLayer(type):
    if type == 'committer':
        return 1
    if type == 'reviewOwner' or type == 'author' or type == 'reviewer' or type == 'patchUploader':
        return 2
    if type == 'approver':
        return 3
    if type == 'issueReporter':
        return 4
    if type == 'issueAssignee':
        return 5
    if type == 'file':
        return 6
    if type == 'issue':
        return 7
    if type == 'ownership':
        return 8


humanNodes = []
humansNodes = []
issueNodes = []
fileNodes = []
humanRoles = 8
humanLayers = 6
# humanNodes, issueNodes, fileNodes are arrays that represent indexes of nodes within each type
for i in range(humanRoles):
    humanNodes.append([])
nrNodes = 0
nrIssues = 0
Label = {}
dict = {}
i_R = {}
usernames = {}
issueDict = {}
fileIssues = {}
nrFileIssues = {}
reviewDict = {}
reviewID = {}  # dict with commits as keys and their value represent the review they belong to
commitDict = {}
fileDict = {}
files = []
Edges = {}


def addEdge(nod1, l1, nod2, l2, col):
    global nrEdges
    l1 = LayerPerm[l1]
    l2 = LayerPerm[l2]
    crtEdge = myEdge(nod1, l1, nod2, l2, col)
    if crtEdge in Edges:
        Edges[crtEdge] += 1
        return 0
    else:
        nrEdges += 1
        edgeList.append(crtEdge)
        if not (nod1 in Adj):
            Adj[nod1] = []
        if not (nod2 in Adj):
            Adj[nod2] = []
        Adj[nod1].append((nod2, l2))
        Adj[nod2].append((nod1, l1))
        Edges[crtEdge] = 1
        return 1


# Human Names files
files = []
files.append(open("\\CommitterAuthorFiles.txt", "r"))
files.append(open("\\OwnerNames2020.txt", "r"))
files.append(open("\\UploaderNames2020.txt", "r"))
files.append(open("\\CommentRevNames2020.txt", "r"))
files.append(open("\\ApproverNames2020.txt", "r"))
files.append(open("\\AuthorNames2020.txt", "r"))
files.append(open("\\ReporterNames2020B.txt", "rb"))
files.append(open("\\AssigneeNames2020B.txt", "rb"))
files.append(open("\\CCedNames2020B.txt", "rb"))
# File dependencies files
depFile = []
depFile.append(open("\\FileDep.txt", "r"))
depFile.append(open("\\ClassDep.txt", "r"))
# Event/Edge files
reviewFile = open("\\ReviewEdges2020.txt", "r")
rc2BugEdge = open("\\RevMsg2BugEdge.txt", "r")


def addMyFile(crtFile, nrFiles):
    global nrNodes
    nrFiles += 1
    nrNodes += 1
    Label[nrNodes] = crtFile
    fileNodes.append(nrNodes)
    fileDict[crtFile] = nrNodes
    fileIssues[nrNodes] = {}
    nrFileIssues[nrNodes] = 0
    files.append(MyFile(nrFiles, crtFile, 0, 0, 0))
    return nrFiles

class MyChange:
    def __init__(self, nodeVal_, index_, hash_id_):
        self.nodeVal = nodeVal_
        self.index = index_
        self.hash_id = hash_id_
        self.fileNodes = []
    def addFile(self, fileNode):
        self.fileNodes.append(fileNode)


def readNameUsername():
    f = open("\\emailName2020B.txt", "rb")
    while (True):
        crtL = f.readline().decode('utf-8')
        if not crtL:
            break
        lst = crtL.split('/\\')
        Len = len(lst)
        name = purifyName(lst[0])
        if name in dict:
            usernames[lst[-1][:-1]] = name
            dict[name].setUserName(lst[-1][:-1])
    f.close()

def addHuman(name, nrHumans, fNr):
    global nrNodes
    if not (name in dict):
        nrHumans += 1
        nrNodes += 1
        Label[nrNodes] = name
        humanNodes[fNr].append(nrNodes)
        humansNodes.append(nrNodes)
        dict[name] = MyHuman(name, nrNodes, nrHumans)

    dict[name].setRole(Role(fNr))
    dict[name].setSite(fNr)
    return nrHumans


def addReview(review_id, nrReviews):
    global nrNodes
    if not review_id in reviewDict:
        nrReviews += 1
        nrNodes += 1
        Label[nrNodes] = 'R' + str(review_id)
        reviewDict[review_id] = MyChange(nrNodes, nrReviews, review_id)
    return nrReviews
def addCommit(hash_id, nrCommits):
    if not (hash_id in commitDict):
        nrCommits += 1
        commitDict[hash_id] = MyChange(-1, nrCommits, hash_id)
    return nrCommits
def readCommits(nrHumans, nrCommits, nrFiles):
    fileList = []
    global nrNodes
    commit_hash = 0
    while (True):
        crtL = files[0].readline()
        if not crtL:
            break
        if (crtL == '' or crtL == '\n'):
            continue
        # committer/\\author/\\commitHash
        Lst = crtL.split('/\\')
        if not (('.' in Lst[0]) or ('/' in Lst[0]) or ('\\' in Lst[0])):
            Lst = crtL.split('/\\')
            committerName = purifyName(Lst[0])
            authorName = purifyName(Lst[1])
            nrHumans = addHuman(committerName, nrHumans, 0)
            nrHumans = addHuman(authorName, nrHumans, 5)
            commitId = Lst[2][:-1]
            commit_hash = commitId
            nrCommits = addCommit(commitId, nrCommits)
            if authorName != committerName:
                # add edge committer->author
                L = getLayer2('committer', 'author')
                addEdge(dict[committerName].index, 1, dict[authorName].index, L, 2)
            fileList = []
        else:
            crtFile = crtL.rsplit('.', 1)[0].replace("/", '.')
            if not (crtFile in fileDict):
                nrFiles = addMyFile(crtFile, nrFiles)
            commitDict[commit_hash].addFile(fileDict[crtFile])
            if len(fileList) > 0:
                L = getLayer2('file', 'fileC')
                addEdge(fileDict[crtFile], L, fileDict[fileList[len(fileList) - 1]], L, 3)
            # for fileName in fileList:
            # nrEdges['file2fileCommit'] += addEdge(fileDict[crtFile], 10, fileDict[fileName], 10)
            # add undirected edge between co-committed files
            # addEdge(fileDict[crtFile], 12, fileDict[fileName], 12)
            # addEdge(fileDict[fileName], 12, fileDict[crtFile], 12)
            # change to L, L?

            fileList.append(crtFile)
    files[0].close()
    return nrHumans, nrCommits, nrFiles
def readHumanF(fNr, nrHumans):
    while (True):
        # names in Bugzilla are read from binary files
        if fNr >= 6 and fNr <= 8:
            crtL = files[fNr].readline().decode('utf-8')
        else:
            crtL = files[fNr].readline()

        if not crtL:
            break
        if '/\\' in crtL:  # name/\email/\index
            name = purifyName(crtL.split('/\\')[0])
            nrHumans = addHuman(name, nrHumans, fNr)
        else:  # name email index
            lst = crtL.split()
            Len = len(lst)
            name = ''
            for i in range(Len - 1):
                name = name + lst[i]
            name = purifyName(name)
            nrHumans = addHuman(name, nrHumans, fNr)

    return nrHumans
def processReviewEdges(reviewEdges, L):
    edge4Review = {}
    for key in reviewEdges:
        revId = reviewID[key]
        humanEdges = reviewEdges[key]
        if not (revId in edge4Review):
            edge4Review[revId] = {}
        for edge in humanEdges:
            edge4Review[revId][edge[1]] = True
        for edge in edge4Review[revId]:
            addEdge(dict[edge].index, L, reviewDict[revId].nodeVal, L, 16)
def readReviews():
    global nrReviews
    reviewEdges = {}
    while True:
        crtL = reviewFile.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        if lst[0] == 'CommentEdge' or lst[0] == 'PCommentEdge':
            name1 = purifyName(lst[1])
            name2 = purifyName(lst[2][:-1])
            L = getLayer2('reviewer', 'reviewOwner')
            if lst[0] == 'CommentEdge':
                addEdge(dict[name2].index, L, dict[name1].index, L, 8)
            else:
                addEdge(dict[name2].index, L, dict[name1].index, L, 8)
        elif lst[0] == 'Review2Commit':
            reviewId = lst[1]
            if not (reviewId in reviewDict):
                addReview(reviewId, nrReviews)
                nrReviews += 1
            commitId = lst[2].replace('\n', '')
            if (commitId in reviewID) and (reviewID[commitId] != reviewId):
                exit()
            reviewID[commitId] = reviewId
        else:
            commitId = lst[1]
            name = purifyName(lst[2][:-1])
            if not (commitId in reviewEdges):
                reviewEdges[commitId] = []
            reviewEdges[commitId].append((lst[0], name))
            if commitId in commitDict:
                layer = 'patchUploader'
                col = 5
                if lst[0] == 'OwnerEdge':
                    layer = 'reviewOwner'
                    col = 6
                elif lst[0] == 'AuthorEdge':
                    layer = 'author'
                    col = 7
                elif lst[0] == 'ApprovalEdge':
                    layer = 'approver'
                    col = 8
                elif lst[0] != 'UploaderEdge':
                    print(lst)
                    exit()
                L = getLayer2(layer, 'file')
                if name in dict:
                    fileNodes = commitDict[commitId].fileNodes
                    for fileNode in fileNodes:
                        addEdge(dict[name].index, L, fileNode, L, 10)
    processReviewEdges(reviewEdges, 3)
    reviewFile.close()
def readReviewComments(nrReviews):
    revFileComm = open("\\ReviewFilesFromComments.txt", "r")
    while (True):
        crtL = revFileComm.readline()
        if not crtL:
            break
        lst = crtL[:-1].split("/\\")
        reviewId = lst[4]
        if not (reviewId in reviewDict):
            nrReviews = addReview(reviewId, nrReviews)
        name1 = purifyName(lst[2])
        name2 = purifyName(lst[3])

        nod1 = dict[name1].index
        nod2 = dict[name2].index
        L = getLayer2('reviewer', 'reviewOwner')
        if name1 != name2:
            addEdge(nod2, L, nod1, L, 8)
        fileList = lst[1].rsplit('.', -1)[:-1]
        fileName = ''
        for x in fileList:
            fileName += x
            fileName += '.'
        fileName = fileName.replace('/', '.')[:-1]
        if fileName in fileDict:
            reviewDict[reviewId].addFile(fileDict[fileName])
            # edge between reviewOwner and file on Review layer
            addEdge(nod1, 3, fileDict[fileName], 3, 11)
    return nrReviews

def getIssues():
    g = open("BugDex2020.txt", "w")
    for key in issueDict:
        g.write(str(key) + '/\\')
    g.close()

def addIssue(issue, nrIssues):
    global nrNodes
    nrIssues += 1
    nrNodes += 1
    Label[nrNodes] = issue
    issueNodes.append(nrNodes)
    issueDict[issue] = nrNodes
    return nrIssues
def readIssueEdges(nrIssues):
    global nrNodes
    issueEdgesFile = open("\\IssueEdges2020B.txt", "rb")
    while True:
        crtL = issueEdgesFile.readline().decode('utf-8')
        if not crtL:
            break
        if crtL == '':
            continue
        lst = crtL.split('/\\')
        if (lst[0][0] != 'C'):
            name = purifyName(lst[1])

            if not (lst[-1][:-1] in issueDict): #issue was not fixed
                continue
            if not (name in dict):
                print(name, lst[1])
                continue
            layer = 'issueReporter'
            col = 1
            if lst[0][0] == 'A':
                layer = 'issueAssignee'
                col = 2
            else:
                dict[name].isReporter = True
            L = getLayer2(layer, 'issue')
            addEdge(dict[name].index, L, issueDict[lst[-1][:-1]], L, 6)
        else:
            uname = lst[1]
            if uname in usernames:
                name = usernames[uname]
                # ToDo add CCassignee edges
    issueEdgesFile.close()
    return nrIssues
def readIssues(nrIssues):
    global nrNodes
    issueFile = open("\\BugStatus2020.txt")

    while True:
        crtL = issueFile.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        status_i = lst[1][:-1]
        # in case only fixed issues must be added =>
        # if ("CLOSED" in status_i) or ("RESOLVED" in status_i) or ("VERIFIED" in status_i) or ("FIXED" in status_i):
        if not (lst[0] in issueDict):
            nrIssues = addIssue(lst[0], nrIssues)
            i_R[nrNodes] = {}
    issueFile.close()
    nrIssues = readIssueEdges(nrIssues)
    return nrIssues

def readIssueComments():
    issueFile = open("\\comments2020.txt")
    while True:
        crtL = issueFile.readline()
        if not crtL:
            break
        bug = crtL[:-1]
        crtL = issueFile.readline()
        while crtL and crtL != 'EOB1':
            lst = crtL.split('/\\')
            if bug in issueDict and lst[0] in usernames:
                i_R[issueDict[bug]][usernames[lst[0]]] = True
                # all commenters are issueReporters
            crtL = issueFile.readline()
        crtL = issueFile.readline()
        while crtL and crtL != 'EOB2':
            lst = crtL.split('/\\')
            if bug in issueDict and lst[0] in usernames:
                # all commenters are issueReporters
                i_R[issueDict[bug]][usernames[lst[0]]] = True
            crtL = issueFile.readline()
    addIrEdges()
    issueFile.close()
def addIssueDependency(fName):
    f = open(fName, "r")
    while True:
        crtL = f.readline()[:-1]
        if not crtL:
            break
        lst = crtL.split('/\\')
        if len(lst) != 2:
            print(lst)
            exit()
        crtL = f.readline()[1:-1].split(', ')
        L = getLayer2('issue', 'issue')
        if (lst[0] in issueDict):
            i1 = issueDict[lst[0]]
            for elem in crtL:
                if elem in issueDict:
                    i2 = issueDict[elem]
                    addEdge(i1, L, i2, L, 15)
def processReview(crtL):
    reviewID = crtL[1]
    issueID = crtL[2][:-1]
    L = getLayer2('file', 'issue')
    if reviewID in reviewDict and issueID in issueDict:
        fileNodes = reviewDict[reviewID].fileNodes
        for fileNode in fileNodes:
            fileIssues[fileNode][issueDict[issueID]] = True
            nrFileIssues[fileNode] += addEdge(fileNode, L, issueDict[issueID], L, 12)
def processCommit(crtL):
    commitID = crtL[1]
    issueID = crtL[2][:-1]
    L = getLayer2('file', 'issue')
    if commitID in commitDict and issueID in issueDict:
        fileNodes = commitDict[commitID].fileNodes
        for fileNode in fileNodes:
            fileIssues[fileNode][issueDict[issueID]] = True
            nrFileIssues[fileNode] += addEdge(fileNode, L, issueDict[issueID], L, 12)
def readI2CSeeAlso():
    bugEdgeFile = open("\\BugEdges.txt", "r")
    while (True):
        crtL = bugEdgeFile.readline()
        if not crtL:
            break
        if crtL == '\n':
            continue
        crtL = crtL.split(' ')
        if crtL[0] == 'ReviewEdge':
            processReview(crtL)
        else:
            processCommit(crtL)
    bugEdgeFile.close()
def readIssue2Change():
    while (True):
        crtL = rc2BugEdge.readline()
        if not crtL:
            break
        if crtL == '\n':
            continue
        crtL = crtL.split(' ')
        if crtL[0] == 'Review2Bug':
            processReview(crtL)
        # else:
        #     processCommit(crtL)
def addIrEdges():
    layer = getLayer2('issueReporter', 'issueReporter')
    for key in i_R:
        crtDict = i_R[key]
        for i_r1 in crtDict:
            nod1 = dict[i_r1].index
            for i_r2 in crtDict:
                if i_r1 != i_r2:
                    addEdge(nod1, layer, dict[i_r2].index, layer, 7)


def addDepEdge(f):
    while True:
        crtL = f.readline()
        if not crtL:
            break
        lst = crtL.split()
        if lst[1] in fileDict and lst[2] in fileDict:
            # addEdge(fileDict[lst[1]], getLayer('file'), fileDict[lst[2]], getLayer('file'), 0)
            L = getLayer2('file', 'file')
            addEdge(fileDict[lst[1]], L, fileDict[lst[2]], L, 1)
def readOwnershipFile(ownershipDict):
    ownershipFile = open("\\OwnershipFile.txt")
    minP = 100.0
    avg = 0.0
    nrFiles = 0
    nrCommitters = 0
    X = 0
    Y = 0
    values = []
    Values = []
    while (True):
        crtL = ownershipFile.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        compName = lst[0].replace('/', '.')
        compName = compName.rsplit('.', 1)[0]
        if not (compName in fileDict):
            for i in range(int(lst[1])):
                nxtL = ownershipFile.readline()
            continue
        obj = Ownership(compName)
        nrFiles += 1
        for i in range(int(lst[1])):
            nxtL = ownershipFile.readline().split('/\\')
            lineLen = len(nxtL)
            if lineLen == 0:
                continue
            obj.addModif(getModifFromLine(nxtL, lineLen))

        allCommitters = obj.authorDex[0]

        L = getLayer2('committer', 'committer')
        A = getLayer2('committer', 'author')
        for c1 in allCommitters:
            addEdge(dict[c1].index, 1, fileDict[obj.name], 1, 4)
            nrCommitters += 1
            cp = (100 * obj.authorDex[0][c1].nrCommits / obj.nrCommits[0])

            if cp < 100:
                values.append(cp)
            avg += cp
            minP = min(minP, cp)
            for c2 in allCommitters:
                if c1 != c2:
                    if dict[c1].isRole[0] and dict[c2].isRole[0]:
                        addEdge(dict[c1].index, L, dict[c2].index, L, 13)
                    elif dict[c2].isRole[0] or dict[c1].isRole[0]:
                        addEdge(dict[c1].index, L, dict[c2].index, A, 2)
        ownershipTuple = obj.nrCommitsOwner(0)
        ownershipDict[fileDict[obj.name]] = (ownershipTuple[0], obj.nrCommitsPercentage(0))
        m1, m2 = obj.getMeasures(0)
        m3 = m1 + m2
        X += m1
        Y += m2
        if obj.nrCommitsPercentage(0) < 100:
            Values.append(obj.nrCommitsPercentage(0))
        if ownershipTuple[0] in dict:
            addEdge(dict[ownershipTuple[0]].index, 1, fileDict[obj.name], 1, 14)


    ownershipFile.close()
    return ownershipDict


def checkFilesIssues():
    buggy = 0
    nonBuggy = 0
    buggyList = []
    unBuggyFile = []
    for key in fileDict:
        if nrFileIssues[fileDict[key]] != 0:
            buggy += 1
            if fileDict[key] in ownershipDict:
                buggyList.append(fileDict[key])
        else:
            nonBuggy += 1
            unBuggyFile.append(fileDict[key])


nrHumans, nrCommits, nrFiles = readCommits(0, 0, 0)

for fileId in range(1, humanRoles):
    nrHumans = readHumanF(fileId, nrHumans)
    files[fileId].close()
readNameUsername()

nrReviews = readReviewComments(0)
readReviews()

nrIssues = readIssues(0)
readIssue2Change()
readI2CSeeAlso()
readIssueComments()
getIssues()
addIssueDependency("\\BugDep.txt")
files = readFileMeasures(fileDict, "\\codeMeasures2020.txt")
for fileId in range(len(depFile)):
    addDepEdge(depFile[fileId])
    depFile[fileId].close()
ownershipDict = {}
ownershipDict = readOwnershipFile(ownershipDict)

print(nrNodes, nrReviews + nrIssues + nrHumans + nrFiles)
# checkFilesIssues()
nodes, sampledEdges = sampleNodesFromEdges(edgeList, 400)
# sampledEdges = sampleEdgesPerLayer(nrLayers, edgeList, 370)
s = Sample(nrLayers, nodes, sampledEdges, Label)
s.addAliasEdges()
createLayoutFile("\\muxViz-master\\data\\graph1\\layoutFile.txt", s.getNrNodes(), False)
s.createEdgesFile("\\muxViz-master\\data\\graph1\\EdgeFile.txt")
s.createColoredEdges("\\muxViz-master\\data\\graph1\\ExternalEdgeFile.txt")
print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())
