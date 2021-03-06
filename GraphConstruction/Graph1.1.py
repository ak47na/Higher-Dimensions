from OwnershipP import *
from Edge import *
from SNAMeasures import Monoplex
from Sample import *
from createTable import *
from MyFile import *
from MyHuman import *
from EdgeTypeDetails import *
from scipy.stats import spearmanr
from Issue import *
from Settings import *

from scipy.stats import wilcoxon

nrLayers = 4


project = getProjectList()
projectID = getProjectID()
networkType = getNetworkType()
issueType = getIssueType()
Adj = {}
nrEdges = 0
edgeList = []
#[0, 2, 4, 3, 1]

LayerPerm = getLayerPerm()
# C, F, R, I

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
#dict with nrFileIssues[x] = the number of issues of nod x; fileIssues contains the nodes of the issues
nrFileIssues = {}
reviewDict = {}
reviewID = {}  # dict with commits as keys and their value represent the review they belong to
commitDict = {}
fileDict = {}
files = []
Edges = {}


def addEdge_util(crtEdge):
    global nrEdges
    if crtEdge in Edges:
        Edges[crtEdge] += 1
        return 0
    else:
        nrEdges += 1
        edgeList.append(crtEdge)
        if not (crtEdge.nod1 in Adj):
            Adj[crtEdge.nod1] = []
        Adj[crtEdge.nod1].append((crtEdge.nod2, crtEdge.layer2))
        Edges[crtEdge] = 1
        return 1
def addEdge(nod1, l1, nod2, l2, col):
    l1 = LayerPerm[l1]
    l2 = LayerPerm[l2]
    #dependency edges between files (col == 1) or issues (col = 5) are directed
    if col == 1 or col == 15:
        return addEdge_util(myEdge(nod1, l1, nod2, l2, col))

    return max(addEdge_util(myEdge(nod1, l1, nod2, l2, col)),
               addEdge_util(myEdge(nod2, l2, nod1, l1, col)))


# Human Names files
files = []
Type = ['C', 'R', 'R', 'R', 'A', 'R', 'i_R', 'i_A', 'i_C']
files.append(open("Data\\CommitterAuthorFiles.txt", "r"))
files.append(open("Data\\OwnerNames2020.txt", "r"))
files.append(open("Data\\UploaderNames2020.txt", "r"))
files.append(open("Data\\CommentRevNames2020.txt", "r"))
files.append(open("Data\\ApproverNames2020.txt", "r"))
files.append(open("Data\\AuthorNames2020.txt", "r"))
files.append(open("Data\\ReporterNames2020B.txt", "rb"))
files.append(open("Data\\AssigneeNames2020B.txt", "rb"))
files.append(open("Data\\CCedNames2020B.txt", "rb"))
# File dependencies files
depFile = []
depFile.append(open("Data\\Data\\FileDep.txt", "r"))
depFile.append(open("Data\\Data\\ClassDep.txt", "r"))
# Event/Edge files
reviewFile = open("Data\\ReviewEdges2020.txt", "r")
rc2BugEdge = open("Data\\RevMsg2BugEdge.txt", "r")


def addMyFile(crtFile, nrFiles):
    global nrNodes
    nrFiles += 1
    nrNodes += 1
    Label[nrNodes] = (crtFile, 'File')
    fileNodes.append(nrNodes)
    fileDict[crtFile] = nrNodes
    fileIssues[nrNodes] = {}
    nrFileIssues[nrNodes] = 0
    files.append(MyFile(nrFiles, crtFile, 0, 0, 0, 0))
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
    #name/\username from Bugzilla
    f = open("Data\\emailName2020B.txt", "rb")
    while (True):
        crtL = f.readline().decode('utf-8')
        if not crtL:
            break
        lst = crtL.split('/Data\\')
        Len = len(lst)
        name = purifyName(lst[0])
        if name in dict:
            usernames[lst[-1][:-1]] = name
            dict[name].setUserName(lst[-1][:-1])
    f.close()
def getHumanTable():
    cols = ['Committer', 'reviewOwner', 'patchUploader', 'reviewer', 'patchApprover', 'patchAuthor',
                  'issueReporter', 'issueAssignee', 'issueCC']
    vals = []
    for r in range(humanRoles):
        vals.append([len(humanNodes[r])])
    createTable2(cols[:-1], vals)

def addHuman(name, nrHumans, fNr):
    global nrNodes
    if not (name in dict):
        nrHumans += 1
        nrNodes += 1
        Label[nrNodes] = (name, Type[fNr])
        humansNodes.append(nrNodes)
        dict[name] = MyHuman(name, nrNodes, nrHumans)
    if dict[name].isFile[fNr] == False:
        humanNodes[fNr].append(dict[name].index)
    dict[name].isFile[fNr] = True
    dict[name].setRole(Role(fNr))
    dict[name].setSite(fNr)
    return nrHumans

def addReview(review_id, nrReviews):
    global nrNodes
    if not review_id in reviewDict:
        nrReviews += 1
        nrNodes += 1
        Label[nrNodes] = (str(review_id), 'Review')
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
        # committer/Data\\author/Data\\commitHash
        Lst = crtL.split('/Data\\')
        if not (('.' in Lst[0]) or ('/' in Lst[0]) or ('Data\\' in Lst[0])):
            Lst = crtL.split('/Data\\')
            committerName = purifyName(Lst[0])
            authorName = purifyName(Lst[1])
            nrHumans = addHuman(committerName, nrHumans, 0)
            nrHumans = addHuman(authorName, nrHumans, 5)
            commitId = Lst[2][:-1]
            commit_hash = commitId
            nrCommits = addCommit(commitId, nrCommits)
            if authorName != committerName:
                # add edge committer->author as cross layer edge
                addEdge(dict[committerName].index, 1, dict[authorName].index, 3, 2)
            fileList = []
        else:
            crtFile = crtL.rsplit('.', 1)[0].replace("/", '.')
            if not (crtFile in fileDict):
                nrFiles = addMyFile(crtFile, nrFiles)
            commitDict[commit_hash].addFile(fileDict[crtFile])
            if len(fileList) > 0:
                L = getLayer2('file', 'fileC')
                addEdge(fileDict[crtFile], L, fileDict[fileList[len(fileList) - 1]], L, 3)
            # Edges from commits to files:
            addEdge(dict[authorName].index, 1, fileDict[crtFile], 1, 4)
            if authorName != committerName:
                addEdge(dict[committerName].index, 1, fileDict[crtFile], 1, 4)

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
        if '/Data\\' in crtL:  # name/\email/\index
            name = purifyName(crtL.split('/Data\\')[0])
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
        lst = crtL.split('/Data\\')
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
            nrReviews = addReview(reviewId, nrReviews)
            commitId = lst[2].replace('\n', '')
            if (commitId in reviewID) and (reviewID[commitId] != reviewId):
                exit()
            reviewID[commitId] = reviewId
        else:
            commitId = lst[1]
            name = purifyName(lst[2][:-1])
            #reviewEdges[commitId] = edges that relate to commitId s.t edges between the review coresp to commitId can be linked with the humans
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
                    exit()
                L = getLayer2(layer, 'file')
                #link humans to the files of the commit
                if name in dict:
                    fileNodes = commitDict[commitId].fileNodes
                    for fileNode in fileNodes:
                        addEdge(dict[name].index, L, fileNode, L, 10)
    processReviewEdges(reviewEdges, 3)
    reviewFile.close()
def readReviewComments(nrReviews):
    revFileComm = open("Data\\ReviewFilesFromComments.txt", "r")
    while (True):
        crtL = revFileComm.readline()
        if not crtL:
            break
        lst = crtL[:-1].split("/Data\\")
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
            # edge between reviewOwner and file on Review layer from comment
            addEdge(nod1, 3, fileDict[fileName], 3, 11)
    return nrReviews

def getIssues():
    g = open("BugDex2020.txt", "w")
    for key in issueDict:
        g.write(str(key) + '/Data\\')
    g.close()

def addIssue(issue, nrIssues, projectID):
    global nrNodes
    nrIssues += 1
    nrNodes += 1
    Label[nrNodes] = (issue.name, 'Issue')
    issueNodes.append(nrNodes)
    issueDict[issue.name] = nrNodes
    return nrIssues

def readIssueEdges(nrIssues):
    global nrNodes
    #HumanRole/\name/username/\bugID
    issueEdgesFile = open("Data\\IssueEdges2020B.txt", "rb")
    while True:
        crtL = issueEdgesFile.readline().decode('utf-8')
        if not crtL:
            break
        if crtL == '':
            continue
        lst = crtL.split('/Data\\')
        if (lst[0][0] != 'C'):
            name = purifyName(lst[1])

            if not (lst[-1][:-1] in issueDict): #issue was not fixed
                continue

            if not (name in dict):
                print(name, lst[1])
                continue
            layer = 'issueReporter'
            col = 5
            if lst[0][0] == 'A':
                layer = 'issueAssignee'
                col = 6
            else:
                dict[name].isReporter = True
            L = getLayer2(layer, 'issue')
            addEdge(dict[name].index, L, issueDict[lst[-1][:-1]], L, col)
        else:
            uname = lst[1]
            if uname in usernames:
                name = usernames[uname]
                # ToDo add CCassignee edges
    issueEdgesFile.close()
    return nrIssues
def readIssues(nrIssues, projectID):
    global nrNodes
    #bugID/\version/\creation_ts/\delta_ts/\status/\resolution
    issueFile = open("Data\\BugDetails.txt")
    while True:
        crtL = issueFile.readline()
        if not crtL:
            break
        lst = crtL.split('/Data\\')
        a = lst[2].split(' ', 1)
        a[1] = a[1].replace(' ', '')
        if len(a) != 2:
            exit()
        lst[2] = getTime(a[0], a[1])
        a = lst[3].split(' ', 1)
        a[1] = a[1].replace(' ', '')
        lst[3] = getTime(a[0], a[1])
        if len(a) != 2:
            exit()
        if len(lst) != 6:
            print('Error\n')
            exit()
        lst[5] = lst[5][:-1] #ignore '\n'
        issue = Issue(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], project[projectID])

        if issue.getType() == issueType:
            if not (issue.name in issueDict):
                nrIssues = addIssue(issue, nrIssues, projectID)
                issue.setIndex(nrIssues)
                i_R[nrNodes] = {}


    issueFile.close()
    nrIssues = readIssueEdges(nrIssues)
    return nrIssues

def readIssueComments():
    #comments to Bugs:
    issueFile = open("Data\\comments2020.txt")
    while True:
        crtL = issueFile.readline()
        if not crtL:
            break
        bug = crtL[:-1]
        crtL = issueFile.readline()
        while crtL and crtL != 'EOB1':
            lst = crtL.split('/Data\\')
            if bug in issueDict and lst[0] in usernames:
                i_R[issueDict[bug]][usernames[lst[0]]] = True
                # all commenters are issueReporters
            crtL = issueFile.readline()
        crtL = issueFile.readline()
        while crtL and crtL != 'EOB2':
            lst = crtL.split('/Data\\')
            if bug in issueDict and lst[0] in usernames:
                # all commenters are issueReporters
                i_R[issueDict[bug]][usernames[lst[0]]] = True
            crtL = issueFile.readline()
    addIrEdges()
    issueFile.close()
def addIssueDependency(fName):
    #b_1/\b_2 <=> b_2 is in b_1's list of "depends_on" in Bugzilla
    f = open(fName, "r")
    while True:
        crtL = f.readline()[:-1]
        if not crtL:
            break
        lst = crtL.split('/Data\\')
        if len(lst) != 2:
            print(lst, '*')
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
    reviewId = crtL[1]
    issueID = crtL[2][:-1]
    L = getLayer2('file', 'issue')
    if reviewId in reviewDict and issueID in issueDict:
        addEdge(reviewDict[reviewId].nodeVal, 3, issueDict[issueID], 4, 17)
        fileNodes = reviewDict[reviewId].fileNodes
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
    #type changeID bugID
    bugEdgeFile = open("Data\\BugEdges.txt", "r")
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
    # type changeID bugID
    while (True):
        crtL = rc2BugEdge.readline()
        if not crtL:
            break
        if crtL == '\n':
            continue
        crtL = crtL.split(' ')
        if crtL[0] == 'Review2Bug':
            processReview(crtL)
        else:
            processCommit(crtL)
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
            L = getLayer2('file', 'file')
            addEdge(fileDict[lst[1]], L, fileDict[lst[2]], L, 1)
def readOwnershipFile(ownershipDict):
    #fileName/\nrCommits
    #author_name/\self.author_date/\author_timezone/\added/\removed/\complexity
    ownershipFile = open("Data\\Data\\OwnershipFile.txt")
    nrFiles = 0
    nrCommitters = 0
    X = 0
    Y = 0
    valuesC = []
    valuesL = []
    while (True):
        crtL = ownershipFile.readline()
        if not crtL:
            break
        lst = crtL.split('/Data\\')
        compName = lst[0].replace('/', '.')
        compName = compName.rsplit('.', 1)[0]
        if not (compName in fileDict):
            for i in range(int(lst[1])):
                nxtL = ownershipFile.readline()
            continue
        obj = Ownership(compName)
        nrFiles += 1
        for i in range(int(lst[1])):
            nxtL = ownershipFile.readline().split('/Data\\')
            lineLen = len(nxtL)
            if lineLen == 0:
                continue
            obj.addModif(getModifFromLine(nxtL, lineLen))

        allCommitters = obj.authorDex[0]

        L = getLayer2('committer', 'committer')
        A = getLayer2('committer', 'author')
        if fileDict[obj.name] in posInFiles:
            sAll = obj.sumAdd[0] + obj.sumRem[0]
        else:
            sAll = 0
        for c1 in allCommitters:
            nrCommitters += 1
            cp = (100 * obj.authorDex[0][c1].nrCommits / obj.nrCommits[0])
            if (cp <= 50 and networkType != "Major") or (cp > 50 and networkType != "Minor"):
                addEdge(dict[c1].index, 1, fileDict[obj.name], 1, 14)
            valuesC.append(cp)
            if sAll != 0:
                if obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem >= sAll:
                    lp = 100
                else:
                    lp = (100 * (obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem) / sAll)
                valuesL.append(lp)
            for c2 in allCommitters:
                if c1 != c2:
                    if dict[c1].isRole[0] and dict[c2].isRole[0]:
                        addEdge(dict[c1].index, L, dict[c2].index, L, 13)
                    elif dict[c2].isRole[0] or dict[c1].isRole[0]:
                        addEdge(dict[c1].index, L, dict[c2].index, A, 2)

        ownershipTuple = obj.nrCommitsOwner(0)
        ownershipDict[fileDict[obj.name]] = (ownershipTuple[0], obj.nrCommitsPercentage(0))
    ownershipFile.close()
    return ownershipDict

nrHumans, nrCommits, nrFiles = readCommits(0, 0, 0)

for fileId in range(1, humanRoles):
    nrHumans = readHumanF(fileId, nrHumans)
    files[fileId].close()
readNameUsername()

nrReviews = readReviewComments(0)
readReviews()

nrIssues = readIssues(0, projectID)

readIssue2Change()
readI2CSeeAlso()
readIssueComments()
getIssues()

addIssueDependency("Data\\BugDep.txt")

for fileId in range(len(depFile)):
    addDepEdge(depFile[fileId])
    depFile[fileId].close()
files, posInFiles = readFileMeasures(fileDict, "Data\\codeMeasures2020.txt")
ownershipDict = {}
ownershipDict = readOwnershipFile(ownershipDict)

def createSample():
    nodes = list(range(1, nrNodes + 1))
    s = Sample(nrLayers, nodes, Edges, Label, True)
    s.addAliasEdges()
    createLayoutFile("Data\\muxViz-masterData\\dataData\\graph1Data\\layoutFile.txt", s.getNrNodes(), False)
    s.createEdgesFile("Data\\muxViz-masterData\\dataData\\graph1Data\\EdgeFile.txt")
    s.createColoredEdges("Data\\muxViz-masterData\\dataData\\graph1Data\\ExternalEdgeFile.txt")
    print(s.getNrNodes(), s.getNrEdges(), s.getNrLayers())

    return s

def getSNAMeasure(name):
    if name == 'Betweenness Centrality':
        return betweenness_centrality(Graph_o)
    if name == 'Closeness Centrality':
        return closeness_centrality(Graph_o)
    if name == 'Degree Centrality':
        return degree_centrality(Graph_o)
    if name == 'Effective Size':
        return effective_size(Graph_o)
    if name == 'Constraint':
        return constraint(Graph_o)
    if name == 'Reachability':
        return None
    if name == 'Effective Size':
        return monoplex.getEffectiveSize()
    if name == 'Hierarchy':
        return monoplex.getHierarhy()
def getSNAResult(name):
    fileValues = []
    nrIssuesList = []
    values = getSNAMeasure(name)

    for fileN in fileDict:
        nod = fileDict[fileN]
        if not(nod in Nodes):
            continue
        nrIssuesList.append(nrFileIssues[nod])
        if values == None:
            fileValues.append(local_reaching_centrality(Graph_o, nod))
        else:
            fileValues.append(values[nod])

    w, p = spearmanr(fileValues, nrIssuesList)
    print(measure, w, p)

def createMonoplex(layer):
    for e in Edges:
        if Edges[e] > 0 and (e.layer1 == layer and e.layer2 == layer):
            Graph_o.add_edge(e.nod1, e.nod2, w = Edges[e])
    global Nodes
    Nodes = list(Graph_o.nodes)



Nodes = []
Graph_o = networkx.DiGraph()

measures1 = ['Degree Centrality', 'Betweenness Centrality', 'Closeness Centrality', 'Reachability']
measures2 = ['Hierarchy', 'Effective Size']

for layer in range(1, nrLayers + 1)
    Graph_o = networkx.DiGraph()
    createMonoplex(layer)
    monoplex = Monoplex(Graph_o, True, "w")
    for measure in measures2:
        getSNAResult(measure)
