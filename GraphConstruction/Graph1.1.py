# Edge-coloured multigraph with L = {C, R, A, i_R, i_A, F, I, O}, O = {F + I + C}
from OwnershipP import *
from Edge import *
from Sample import *
import datetime

from scipy.stats import wilcoxon
nrLayers = 4
Adj = {}
nrEdges = 0
edgeList = []
#C, F, R, I
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

Roles = ['committer', 'reviewOwner', 'patchUploader', 'reviewer', 'patchApprover', 'patchAuthor', 'issueReporter', 'issueAssignee', 'issueCC']

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
commitDict = {}
fileDict = {}
Edges = {}



def addEdge(nod1, l1, nod2, l2, col):
    global nrEdges
    crtEdge = myEdge(nod1, l1, nod2, l2, col)
    if crtEdge in Edges:
        Edges[crtEdge] += 1
        return 0
    else:
        nrEdges += 1
        edgeList.append(crtEdge)
        if not(nod1 in Adj):
            Adj[nod1] = []
        if not(nod2 in Adj):
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
issueFile = open("\\IssueEdges2020B.txt", "rb")
rc2BugEdge = open("\\RevMsg2BugEdge.txt", "r")


def Site(layer):
    if layer == 0 or layer == 5:
        return 0
    if layer <= 4 and layer >= 1:
        return 1
    return 2
class MyChange:
    def __init__(self, index_, hash_id_):
        self.index = index_
        self.hash_id = hash_id_
        self.fileNodes = []
    def addFile(self, fileNode):
        self.fileNodes.append(fileNode)

class MyHuman:
    def __init__(self, name_, index_, human_index):
        self.name = name_
        self.humanId = human_index
        self.email = None
        self.username = None
        self.isRole = [False] * 7
        self.index = index_
        self.site = 0
        # self.commits.append(commit)
    def setUserName(self, username_):
        self.username = username_
    def setRole(self, nr):
        self.isRole[nr] = True
    def setSite(self, fNr):
        self.site = Site(fNr)

def isLetter(a):
    return (ord(a) <= ord('z') and ord(a) >= ord('a'))
def purifyName(name):
    nameLen = len(name)
    newName = ''
    for i in range(nameLen):
        crtSymbol = name[i].lower()
        if isLetter(crtSymbol):
            newName += crtSymbol
    return newName

def readNameUsername():
    f = open("\\emailName2020B.txt", "rb")
    while (True):
        crtL = f.readline().decode('utf-8')
        if not crtL:
            break
        lst = crtL.split('/\\')
        Len = len(lst)
        name = purifyName(lst[0].replace(' ', ''))
        if name in dict:
            usernames[lst[-1][:-1]] = name
            dict[name].setUserName(lst[-1][:-1])
        # else:
        #     print(name, lst[-1][:-1])
    f.close()

def Role(x):
    if x < 3:
        return x
    if x == 5:
        return 2
    return x - 1

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
    if not review_id in reviewDict:
        nrReviews += 1
        reviewDict[review_id] = MyChange(nrReviews, review_id)
    return nrReviews

def addCommit(hash_id, nrCommits):
    if not (hash_id in commitDict):
        nrCommits += 1
        commitDict[hash_id] = MyChange(nrCommits, hash_id)
    return nrCommits

def addDepEdge(f):
    while True:
        crtL = f.readline()
        if not crtL:
            break
        lst = crtL.split()
        if lst[1] in fileDict and lst[2] in fileDict:
            #addEdge(fileDict[lst[1]], getLayer('file'), fileDict[lst[2]], getLayer('file'), 0)
            L = getLayer2('file', 'file')
            addEdge(fileDict[lst[1]], L, fileDict[lst[2]], L, 1)


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
            committerName = purifyName(Lst[0].replace(' ', ''))
            authorName = purifyName(Lst[1].replace(' ', ''))
            nrHumans = addHuman(committerName, nrHumans, 0)
            nrHumans = addHuman(authorName, nrHumans, 5)
            commitId = Lst[2][:-1]
            commit_hash = commitId
            nrCommits = addCommit(commitId, nrCommits)
            if authorName != committerName:
                # add edge author->committer
                L = getLayer2('committer', 'author')
                addEdge(dict[committerName].index, 1, dict[authorName].index, L, 2)
            fileList = []
        else:
            crtFile = crtL.rsplit('.', 1)[0].replace("/", '.')
            if not (crtFile in fileDict):
                nrFiles += 1
                nrNodes += 1
                Label[nrNodes] = crtFile
                fileNodes.append(nrNodes)
                fileDict[crtFile] = nrNodes
                fileIssues[nrNodes] = {}
                nrFileIssues[nrNodes] = 0
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
            if authorName in dict:
                L = getLayer2('author', 'file')
                addEdge(dict[authorName].index, L, fileDict[crtFile], 1, 4)
            if committerName in dict:
                L = getLayer2('committer', 'file')
                addEdge(dict[committerName].index, L, fileDict[crtFile], L, 5)
            fileList.append(crtFile)
    files[0].close()
    return nrHumans, nrCommits, nrFiles


def readF(fNr, nrHumans):
    while (True):
        # names in Bugzilla are read from binary files
        if fNr >= 6 and fNr <= 8:
            crtL = files[fNr].readline().decode('utf-8')
        else:
            crtL = files[fNr].readline()

        if not crtL:
            break
        if '/\\' in crtL:  # name/\index
            name = purifyName(crtL.split('/\\')[0].replace(' ', ''))
            nrHumans = addHuman(name, nrHumans, fNr)
        else:  # name index
            lst = crtL.split()
            Len = len(lst)
            name = ''
            for i in range(Len - 1):
                name = name + lst[i]
            name = purifyName(name)
            nrHumans = addHuman(name, nrHumans, fNr)

    return nrHumans

def readIssues(nrIssues):
    global nrNodes
    while True:
        crtL = issueFile.readline().decode('utf-8')
        if not crtL:
            break
        if crtL == '':
            continue
        lst = crtL.split('/\\')
        Len = len(lst)
        # there is an Assignee/Reporter edge
        if (lst[0][0] != 'C'):
            name = purifyName(lst[1].replace(' ', ''))
            if not (lst[-1] in issueDict):
                nrIssues += 1
                nrNodes += 1
                Label[nrNodes] = lst[-1]
                issueNodes.append(nrNodes)
                issueDict[lst[-1][:-1]] = nrNodes
                i_R[nrNodes] = {}
            if not (name in dict):
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
                #ToDo add CCassignee edges
    issueFile.close()
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
def addIrEdges():
    layer = getLayer2('issueReporter', 'issueReporter')
    for key in i_R:
        crtDict = i_R[key]
        for i_r1 in crtDict:
            nod1 = dict[i_r1].index
            for i_r2 in crtDict:
                if i_r1 != i_r2:
                    addEdge(nod1, layer, dict[i_r2].index, layer, 7)

def readReviews():
    while True:
        crtL = reviewFile.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        if lst[0] == 'CommentEdge' or lst[0] == 'PCommentEdge':
            name1 = purifyName(lst[1].replace(' ', ''))
            name2 = purifyName(lst[2][:-1].replace(' ', ''))
            L = getLayer2('reviewer', 'reviewOwner')
            if lst[0] == 'CommentEdge':
                addEdge(dict[name2].index, L, dict[name1].index, L, 8)
            else:
                addEdge(dict[name2].index, L, dict[name1].index, L, 8)
        else:
            commitId = lst[1]
            if commitId in commitDict:
                name = purifyName(lst[2][:-1].replace(' ', ''))
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
                L = getLayer2(layer, 'file')
                if name in dict:
                    fileNodes = commitDict[commitId].fileNodes
                    for fileNode in fileNodes:
                        addEdge(dict[name].index, L, fileNode, L, 10)

    reviewFile.close()
def readReviewComments(nrReviews):
    revFileComm = open("\\ReviewFilesFromComments.txt", "r")
    while (True):
        crtL = revFileComm.readline()
        if not crtL:
            break
        lst = crtL[:-1].split("/\\")
        reviewId = lst[4]
        if not(reviewId in reviewDict):
            nrReviews = addReview(reviewId, nrReviews)
        name1 = purifyName(lst[2].replace(' ', ''))
        name2 = purifyName(lst[3].replace(' ', ''))

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

def readOwnershipFile(ownershipDict):
    ownershipFile = open("\\OwnershipFile.txt")
    minP = 100.0
    avg = 0.0
    cnt = 0
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
            for c2 in allCommitters:
                if c1 != c2:
                    if dict[c1].isRole[0] and dict[c2].isRole[0]:
                        addEdge(dict[c1].index, L, dict[c2].index, L, 13)
                    addEdge(dict[c1].index, A, dict[c2].index, L, 2)

        ownershipTuple = obj.nrCommitsOwner(0)
        ownershipDict[fileDict[obj.name]] = (ownershipTuple[0], obj.nrCommitsPercentage(0))
        minP = min(minP, obj.nrCommitsPercentage(0))
        avg += obj.nrCommitsPercentage(0)
        cnt += 1
        #print(obj.nrCommitsPercentage(0))
        if ownershipTuple[0] in dict:
            addEdge(dict[ownershipTuple[0]].index, 1, fileDict[obj.name], 1, 14)
            # print(compName, ' ', ownershipTuple)

    ownershipFile.close()
    #print(minP, avg / cnt)
    return ownershipDict

def checkFilesIssues():
    buggy = 0
    nonBuggy = 0
    buggyList = []
    filePair = []
    unBuggyFile = []
    for key in fileDict:
        if nrFileIssues[fileDict[key]] != 0:
            buggy += 1
            # buggyList.append((fileDict[key], Adj[fileDict[key]]))
            if fileDict[key] in ownershipDict:
                buggyList.append(fileDict[key])
        else:
            nonBuggy += 1
            # filePair.append((fileDict[key], Adj[fileDict[key]]))
            unBuggyFile.append(fileDict[key])

    from scipy.stats import randint as sp_randint
    unfBuggy = sorted(sp_randint.rvs(0, len(buggyList), size=8, random_state=1))
    # buggyFilePairs = []
    buggyFiles = []
    for i in unfBuggy:
        buggyFiles.append(buggyList[i])
        # if buggyList[i] in ownershipDict:
        #     print(ownershipDict[buggyList[i]], nrFileIssues[buggyList[i]])
    #print(buggy, nonBuggy)
    sampleEfile = open("\\muxViz-master\\data\\graph1\\edgeFile.txt", 'w')
    crtSample = Sample(8, sampleNetFromNodes(buggyFiles, Adj), Edges)
    crtSample.addAliasEdges()
    sampleEfile.write(crtSample.getEdgesString())
    sampleEfile.close()
    return crtSample.getNrNodes()

nrHumans, nrCommits, nrFiles = readCommits(0, 0, 0)
for fileId in range(1, humanRoles):
    nrHumans = readF(fileId, nrHumans)
    files[fileId].close()


nrReviews = readReviewComments(0)

readNameUsername()
readReviews()
nrIssues = readIssues(0)
readIssue2Change()
readI2CSeeAlso()
for fileId in range(len(depFile)):
    addDepEdge(depFile[fileId])
    depFile[fileId].close()

readIssueComments()
ownershipDict = {}
ownershipDict = readOwnershipFile(ownershipDict)

def sampleNodes():
    sampleNodes = []
    humanSample = getSample(0, len(humansNodes), 5)
    fileSample = getSample(0, len(fileNodes), 11)
    issueSample = getSample(0, len(issueNodes), 46)
    for i in humanSample:
        sampleNodes.append(humansNodes[i])
    for i in fileSample:
        sampleNodes.append(fileNodes[i])
    for i in issueSample:
        sampleNodes.append(issueNodes[i])
    samplePair = []
    for x in sampleNodes:
        if not (x in Adj):
            Adj[x] = []
        samplePair.append((x, Adj[x]))
    return Sample(nrLayers, sampleNodes, Edges)


checkFilesIssues()
#nodes, sampledEdges = sampleNodesFromEdges(edgeList, 40)
sampledEdges = sampleEdgesPerLayer(nrLayers, edgeList, 370)
print(len(sampledEdges), nrLayers)
nodes = getNodesFromEdgeSample(sampledEdges)
s = Sample(nrLayers, nodes, sampledEdges)
s.addAliasEdges()
createLayoutFile("\\muxViz-master\\data\\graph1\\layoutFile.txt", s.getNrNodes(), False)
#createLayoutFile
s.createEdgesFile("\\muxViz-master\\data\\graph1\\EdgeFile.txt")
s.createColoredEdges("\\muxViz-master\\data\\graph1\\ExternalEdgeFile.txt")
print(s.getLayers())

print(nrHumans, nrCommits, nrIssues, nrFiles)
print(nrNodes, nrHumans + nrIssues + nrFiles)
print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())
