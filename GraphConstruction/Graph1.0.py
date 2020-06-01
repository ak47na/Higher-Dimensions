# Edge-coloured multigraph with L = {C, R, A, i_R, i_A, F, I, O}, O = {F + I + C}
from OwnershipP import *
from Edge import *
from Sample import *
import datetime

from scipy.stats import wilcoxon

colorSet = ['brown', 'firebrick1', 'coral', 'goldenrod1', 'greenyellow', 'darkolivegreen3', 'lightblue',
            'darkturquoise', 'midnightblue', 'hotpink4', 'mediumpurple', 'gray3', 'chocolate', 'yellow1', 'c1', 'c2',
            'c3']

Adj = {}
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
    crtEdge = myEdge(nod1, l1, nod2, l2, col)
    if crtEdge in Edges:
        Edges[crtEdge] += 1
        return 0
    else:
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
depFile.append(open("\\\\FileDep.txt", "r"))
depFile.append(open("\\\\ClassDep.txt", "r"))
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
            addEdge(fileDict[lst[1]], getLayer('file'), fileDict[lst[2]], getLayer('file'), 0)

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
                addEdge(dict[committerName].index, getLayer('committer'), dict[authorName].index, getLayer('author'), 9)
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
                addEdge(fileDict[crtFile], getLayer('file'), fileDict[fileList[len(fileList) - 1]], getLayer('file'), 10)
            # for fileName in fileList:
            # nrEdges['file2fileCommit'] += addEdge(fileDict[crtFile], 10, fileDict[fileName], 10)
            # add undirected edge between co-committed files
            # addEdge(fileDict[crtFile], 12, fileDict[fileName], 12)
            # addEdge(fileDict[fileName], 12, fileDict[crtFile], 12)
            if authorName in dict:
                addEdge(dict[authorName].index, getLayer('author'), fileDict[crtFile], getLayer('file'), 11)

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
            layer = getLayer('issueReporter')
            col = 1
            if lst[0][0] == 'A':
                layer = getLayer('issueAssignee')
                col = 2
            else:
                dict[name].isReporter = True
            addEdge(dict[name].index, layer, issueDict[lst[-1][:-1]], getLayer('issue'), col)
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
    layer = getLayer('issueReporter')
    for key in i_R:
        crtDict = i_R[key]
        for i_r1 in crtDict:
            nod1 = dict[i_r1].index
            for i_r2 in crtDict:
                if i_r1 != i_r2:
                    addEdge(nod1, layer, dict[i_r2].index, layer, 0)

def readReviews():
    while True:
        crtL = reviewFile.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        if lst[0] == 'CommentEdge' or lst[0] == 'PCommentEdge':
            name1 = purifyName(lst[1].replace(' ', ''))
            name2 = purifyName(lst[2][:-1].replace(' ', ''))
            if lst[0] == 'CommentEdge':
                addEdge(dict[name2].index, getLayer('reviewer'), dict[name1].index, getLayer('reviewOwner'), 4)
            else:
                addEdge(dict[name2].index, getLayer('reviewer'), dict[name1].index, getLayer('reviewOwner'), 14)
        else:
            commitId = lst[1]
            if commitId in commitDict:
                name = purifyName(lst[2][:-1].replace(' ', ''))
                layer = getLayer('patchUploader')
                col = 5
                if lst[0] == 'OwnerEdge':
                    layer = getLayer('reviewOwner')
                    col = 6
                elif lst[0] == 'AuthorEdge':
                    layer = getLayer('author')
                    col = 7
                elif lst[0] == 'ApproverEdge':
                    layer = getLayer('approver')
                    col = 8
                if name in dict:
                    fileNodes = commitDict[commitId].fileNodes
                    for fileNode in fileNodes:
                        addEdge(dict[name].index, layer, fileNode, getLayer('file'), -1)

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
        if name1 != name2:
           addEdge(nod2, getLayer('reviewer'), nod1, getLayer('reviewOwner'), 4)
        fileList = lst[1].rsplit('.', -1)[:-1]
        fileName = ''
        for x in fileList:
            fileName += x
            fileName += '.'
        fileName = fileName.replace('/', '.')[:-1]
        if fileName in fileDict:
            reviewDict[reviewId].addFile(fileDict[fileName])
            addEdge(nod1, getLayer('reviewOwner'), fileDict[fileName], getLayer('file'), 12)
    return nrReviews

def processReview(crtL):
    reviewID = crtL[1]
    issueID = crtL[2][:-1]
    if reviewID in reviewDict and issueID in issueDict:
        fileNodes = reviewDict[reviewID].fileNodes
        for fileNode in fileNodes:
            fileIssues[fileNode][issueDict[issueID]] = True
            nrFileIssues[fileNode] += addEdge(fileNode, getLayer('file'), issueDict[issueID], getLayer('issue'), -1)

def processCommit(crtL):
    commitID = crtL[1]
    issueID = crtL[2][:-1]
    if commitID in commitDict and issueID in issueDict:
        fileNodes = commitDict[commitID].fileNodes
        for fileNode in fileNodes:
            fileIssues[fileNode][issueDict[issueID]] = True
            nrFileIssues[fileNode] += addEdge(fileNode, getLayer('file'), issueDict[issueID], getLayer('issue'), -1)

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

def readOwnershipFile():
    ownershipFile = open("\\\\OwnershipFile.txt")
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
        for c1 in allCommitters:
            for c2 in allCommitters:
                if c1 != c2:
                    if dict[c1].isRole[0] and dict[c2].isRole[0]:
                        addEdge(dict[c1].index, getLayer('committer'), dict[c2].index, getLayer('committer'), 0)
                    addEdge(dict[c1].index, getLayer('author'), dict[c2].index, getLayer('author'), 0)

        ownershipTuple = obj.sumAROwner(0)
        if ownershipTuple[0] in dict:
            addEdge(dict[ownershipTuple[0]].index, getLayer('ownership'), fileDict[obj.name], getLayer('ownership'), 13)
            # print(compName, ' ', ownershipTuple)

    ownershipFile.close()

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
            buggyList.append(fileDict[key])
        else:
            nonBuggy += 1
            # filePair.append((fileDict[key], Adj[fileDict[key]]))
            unBuggyFile.append(fileDict[key])

    from scipy.stats import randint as sp_randint
    unfBuggy = sorted(sp_randint.rvs(0, len(buggyList), size=8, random_state=0))
    # buggyFilePairs = []
    buggyFiles = []
    for i in unfBuggy:
        buggyFiles.append(buggyList[i])
    print(buggy, nonBuggy)
    sampleEfile = open("\\muxViz-master\\data\\graph1\\edgeFile.txt", 'w')
    crtSample = Sample(8, sampleNetFromNodes(buggyFiles, Adj), Edges)
    crtSample.addAliasEdges()
    sampleEfile.write(crtSample.getEdgesString())
    sampleEfile.close()
    return crtSample.getNrNodes()

def createLayoutFile(N):
    Layoutfile = open("\\muxViz-master\\data\\graph1\\layoutFile.txt", 'w')
    Layoutfile.write("NodeID NodeLabel\n")
    for i in range(N):
        Layoutfile.write(str(i + 1) + ' ' + str(i + 1) + '\n')
    Layoutfile.close()


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
readOwnershipFile()

createLayoutFile(checkFilesIssues())
edgeFile = open("\\EdgeFile.txt", "w")
weightedEdges = 0

for key in Edges:
    if key.layer2 != key.layer1:
        continue
    weightedEdges += 1
    edgeFile.write(str(key.nod1) + " " + str(key.layer1) + " "
                    + str(key.nod2) + " " + str(key.layer2) + " " + str(Edges[key]) + "\n")

print(nrHumans, nrCommits, nrIssues, nrFiles)
print(nrNodes, nrHumans + nrIssues + nrFiles)
print(weightedEdges)
edgeFile.close()
