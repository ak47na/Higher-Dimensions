from OwnershipP import *

humanLayers = 9
edgeTypes = 17
colorSet = ['brown', 'firebrick1', 'coral', 'goldenrod1', 'greenyellow', 'darkolivegreen3', 'lightblue',
            'darkturquoise', 'midnightblue', 'hotpink4', 'mediumpurple', 'gray3', 'chocolate', 'yellow1', 'c1', 'c2',
            'c3']

NameSymbols = {}
Label = {}
dict = {}
usernames = {}
humanNodes = []
issueNodes = []
commitNodes = []
fileNodes = []
# humanNodes, issueNodes, commitNodes, fileNodes are arrays that represent indexes of nodes within each type
for i in range(humanLayers):
    humanNodes.append([])
nrEdgesofCol = {}
for i in range(edgeTypes):
    nrEdgesofCol[i] = 0
nrNodes = 0
nrIssues = 0
issueDict = {}
commitDict = {}
fileDict = {}
Edges = {}
nrEdges = {}

nrEdges['Author2file'] = 0
nrEdges['Author2Commit'] = 0
nrEdges['Author2Committer'] = 0
nrEdges['file2file'] = 0
nrEdges['file2fileCommit'] = 0
nrEdges['Owner2Commenter'] = 0
nrEdges['Owner2Commit'] = 0
nrEdges['Approver2Commit'] = 0
nrEdges['Uploader2Commit'] = 0
nrEdges['Assignee2Issue'] = 0
nrEdges['Cced2Issue'] = 0
nrEdges['Reporter2Issue'] = 0
nrEdges['Owner2File'] = 0
nrEdges['SumAROwner2File'] = 0
nrEdges['Commit2Issue'] = 0
nrEdges['PatchOwner2Commenter'] = 0


class myEdge:
    def __init__(self, nod1_, layer1_, nod2_, layer2_, color_):
        self.nod1 = nod1_
        self.layer1 = layer1_
        self.nod2 = nod2_
        self.layer2 = layer2_
        self.color = color_

    def __lt__(self, other):
        if self.layer1 == other.layer1 and self.layer2 == other.layer2:
            if self.nod1 == other.nod1:
                return self.nod2 < other.nod2
            return self.nod1 < other.nod1
        if self.layer1 == other.layer1:
            return self.layer2 < other.layer2
        return self.layer1 < other.layer1

    def __hash__(self):
        return hash((self.nod1, self.layer1, self.nod2, self.layer2, self.color))

    def __eq__(self, other):
        return ((self.nod1, self.layer1, self.nod2, self.layer2, self.color) == (
        other.nod1, other.layer1, other.nod2, other.layer2, other.color))

    def __ne__(self, other):
        return not (self == other)


def addEdge(nod1, l1, nod2, l2, col):
    crtEdge = myEdge(nod1, l1, nod2, l2, col)
    if crtEdge in Edges:
        Edges[crtEdge] += 1
        return 0
    else:
        nrEdgesofCol[col] += 1
        Edges[crtEdge] = 1
        return 1


# Output files
edgeFile = open("D:\\Ak_work2019-2020\\muxViz-master\\data\\fullGraphV1\\edgeFile.txt", "w")
externalEdgeFile = open("D:\\Ak_work2019-2020\\muxViz-master\\data\\fullGraphV1\\externalEdgeFile.txt", "w")
layoutFile = open("D:\\Ak_work2019-2020\\muxViz-master\\data\\fullGraphV1\\layoutFile.txt", "w")
# Human Names files
files = []
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\CommitterAuthorFiles.txt", "r"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\OwnerNames2020.txt", "r"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\UploaderNames2020.txt", "r"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\CommentRevNames2020.txt", "r"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ApproverNames2020.txt", "r"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\AuthorNames2020.txt", "r"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ReporterNames2020B.txt", "rb"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\AssigneeNames2020B.txt", "rb"))
files.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\CCedNames2020B.txt", "rb"))
# File dependencies files
depFile = []
depFile.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\FileDep.txt", "r"))
depFile.append(open("D:\\Ak_work2019-2020\\HigherDimensions\\ClassDep.txt", "r"))
# Event/Edge files
reviewFile = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ReviewEdges2020.txt", "r")
issueFile = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\IssueEdges2020B.txt", "rb")
rc2BugEdge = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\RevMsg2BugEdge.txt", "r")


def addDepEdge(f):
    while True:
        crtL = f.readline()
        if not crtL:
            break
        lst = crtL.split()
        if lst[1] in fileDict and lst[2] in fileDict:
            nrEdges['file2file'] += addEdge(fileDict[lst[1]], 10, fileDict[lst[2]], 10, 0)


def readIssue2Change():
    while (True):
        crtL = rc2BugEdge.readline()
        if not crtL:
            break
        if crtL == '\n':
            continue
        crtL = crtL.split('/\\')
        if crtL[0] == 'Review2Bug':
            continue
        else:
            commitID = crtL[1]
            issueID = crtL[2][:-1]
            if commitID in commitDict and issueID in issueDict:
                nrEdges['Commit2Issue'] += addEdge(commitDict[commitID], 8, issueDict[issueID], 9, 15)


def Site(layer):
    if layer == 0 or layer == 5:
        return 0
    if layer <= 4 and layer >= 1:
        return 1
    return 2


class MyHuman:
    def __init__(self, name_, index_, human_index):
        self.name = name_
        self.humanId = human_index
        self.email = None
        self.username = None
        self.isCommitter = False
        self.isReviewOwner = False
        self.isUploader = False
        self.isReviewer = False
        self.isApprover = False
        self.isPatchAuthor = False
        self.isReporter = False
        self.isAssignee = False
        self.isCCed = False
        self.index = index_
        self.commits = []
        self.site = 0
        # self.commits.append(commit)

    def setUserName(self, username_):
        self.username = username_

    def setCommitter(self, TF):
        self.isCommitter = TF

    def setReviewOwner(self, TF):
        self.isReviewOwner = TF

    def setUploader(self, TF):
        self.isUploader = TF

    def setReviewer(self, TF):
        self.isReviewer = TF

    def setApprover(self, TF):
        self.isApprover = TF

    def setPatchAuthor(self, TF):
        self.isPatchAuthor = TF

    def setReporter(self, TF):
        self.isReporter = TF

    def setAssignee(self, TF):
        self.isAssignee = TF

    def setCCed(self, TF):
        self.isCCed = TF

    def setRole(self, nr):
        if nr == 8:
            self.setCCed(True)
        elif nr == 7:
            self.setAssignee(True)
        elif nr == 6:
            self.setReporter(True)
        elif nr == 5:
            self.setPatchAuthor(True)
        elif nr == 4:
            self.setApprover(True)
        elif nr == 3:
            self.setReviewer(True)
        elif nr == 2:
            self.setUploader(True)
        elif nr == 1:
            self.setReviewOwner(True)
        elif nr == 0:
            self.setCommitter(True)

    def setSite(self, fNr):
        self.site = Site(fNr)


def isLetter(a):
    return (ord(a) <= ord('z') and ord(a) >= ord('a'))


def purifyName(name):
    nameLen = len(name)
    newName = ''
    for i in range(nameLen):
        crtSymbol = name[i].lower()
        if not isLetter(crtSymbol):
            NameSymbols[crtSymbol] = name
        else:
            newName += crtSymbol
    return newName


def readNameUsername():
    f = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\emailName2020B.txt", "rb")
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
        else:
            print(name, lst[-1][:-1])
    f.close()


def addHuman(name, nrHumans, fNr):
    global nrNodes
    if not (name in dict):
        nrHumans += 1
        nrNodes += 1
        Label[nrNodes] = name
        humanNodes[fNr].append(nrNodes)
        dict[name] = MyHuman(name, nrNodes, nrHumans)

    dict[name].setRole(fNr)
    dict[name].setSite(fNr)
    return nrHumans


def addCommit(hash_id, nrCommits, fNr):
    global nrNodes
    if not (hash_id in commitDict):
        nrCommits += 1
        nrNodes += 1
        Label[nrNodes] = hash_id
        commitNodes.append(nrNodes)
        commitDict[hash_id] = nrNodes

    return nrCommits


def readCommits(nrHumans, nrCommits, nrFiles):
    fileList = []
    global nrNodes
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
            nrCommits = addCommit(commitId, nrCommits, 0)
            if authorName != committerName:
                # add edge author->committer
                nrEdges['Author2Commit'] += addEdge(dict[committerName].index, 1, dict[authorName].index, 5, 9)
            fileList = []
        else:
            crtFile = crtL.rsplit('.', 1)[0].replace("/", '.')
            if not (crtFile in fileDict):
                nrFiles += 1
                nrNodes += 1
                Label[nrNodes] = crtFile
                fileNodes.append(nrNodes)
                fileDict[crtFile] = nrNodes
            if len(fileList) > 0:
                addEdge(fileDict[crtFile], 10, fileDict[fileList[len(fileList) - 1]], 10, 10)
            # for fileName in fileList:
            # nrEdges['file2fileCommit'] += addEdge(fileDict[crtFile], 10, fileDict[fileName], 10)
            # add undirected edge between co-committed files
            # addEdge(fileDict[crtFile], 12, fileDict[fileName], 12)
            # addEdge(fileDict[fileName], 12, fileDict[crtFile], 12)
            # edgeFile.write(str(fileDict[crtFile]) + ' 12 ' + str(fileDict[fileName]) + ' 12\n')
            if authorName in dict:
                nrEdges['Author2file'] += addEdge(dict[authorName].index, 5, fileDict[crtFile], 10, 11)

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
                issueDict[lst[-1]] = nrNodes
            if not (name in dict):
                continue
            layer = 6
            col = 1
            if lst[0][0] == 'A':
                layer = 7
                col = 2
            else:
                dict[name].isReporter = True
            val = addEdge(dict[name].index, layer, issueDict[lst[-1]], 9, col)
            if val == 1:
                if layer == 7:
                    nrEdges['Assignee2Issue'] += 1
                else:
                    nrEdges['Reporter2Issue'] += 1
        else:
            uname = lst[1]
            if uname in usernames:
                name = usernames[uname]
                if (name in dict):
                    nrEdges['Cced2Issue'] += addEdge(dict[name].index, 10, issueDict[lst[-1]], 9, 16)
    issueFile.close()
    return nrIssues


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
                nrEdges['Owner2Commenter'] += addEdge(dict[name2].index, 3, dict[name1].index, 1, 4)
            else:
                nrEdges['PatchOwner2Commenter'] += addEdge(dict[name2].index, 3, dict[name1].index, 1, 14)
        else:
            commitId = lst[1]
            if commitId in commitDict:
                name = purifyName(lst[2][:-1].replace(' ', ''))
                # Committer
                layer = 0
                col = 5
                if lst[0] == 'OwnerEdge':
                    layer = 1
                    col = 6
                elif lst[0] == 'AuthorEdge':
                    layer = 5
                    col = 7
                elif lst[0] == 'ApproverEdge':
                    layer = 4
                    col = 8
                if name in dict:
                    val = addEdge(dict[name].index, layer, commitDict[commitId], 8, col)
                    if val == 1:
                        if layer == 1:
                            nrEdges['Owner2Commit'] += 1
                        elif layer == 5:
                            nrEdges['Author2Commit'] += 1
                        elif layer == 4:
                            nrEdges['Approver2Commit'] += 1
                        else:
                            nrEdges['Uploader2Commit'] += 1
    reviewFile.close()
def readReviewComments(nrHumans):
    revFileComm = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ReviewFilesFromComments.txt", "r")
    while (True):
        crtL = revFileComm.readline()
        if not crtL:
            break
        lst = crtL[:-1].split("/\\")
        name1 = purifyName(lst[2].replace(' ', ''))
        name2 = purifyName(lst[3].replace(' ', ''))

        nod1 = dict[name1].index
        nod2 = dict[name2].index
        if name1 != name2:
            nrEdges['Owner2Commenter'] += addEdge(nod2, 3, nod1, 2, 4)
        fileList = lst[1].rsplit('.', -1)[:-1]
        fileName = ''
        for x in fileList:
            fileName += x
            fileName += '.'
        fileName = fileName.replace('/', '.')[:-1]
        if fileName in fileDict:
            nrEdges['Owner2File'] += addEdge(nod1, 2, fileDict[fileName], 10, 12)

    return nrHumans
def readOwnershipFile():
    ownershipFile = open("D:\\Ak_work2019-2020\\HigherDimensions\\OwnershipFile.txt")
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

        ownershipTuple = obj.sumAROwner(0)
        if ownershipTuple[0] in dict:
            nrEdges['SumAROwner2File'] += addEdge(dict[ownershipTuple[0]], 1, fileDict[obj.name], 10, 13)
            # print(compName, ' ', ownershipTuple)

    ownershipFile.close()


edgesForNode = {}
nrHumans, nrCommits, nrFiles = readCommits(0, 0, 0)
for i in range(edgeTypes):
    edgesForNode[i] = 0
for fileId in range(1, humanLayers):
    nrHumans = readF(fileId, nrHumans)
    files[fileId].close()
nrHumans = readReviewComments(nrHumans)
readNameUsername()
readReviews()
nrIssues = readIssues(0)
for fileId in range(len(depFile)):
    addDepEdge(depFile[fileId])
    depFile[fileId].close()
readOwnershipFile()

externalEdgeFile.write("nodeID.from layerID.from nodeID.to layerID.to color size\n")
weightedEdges = 0
for key in Edges:
    nrEdgesofCol[key.color] += 1
    weightedEdges += 1
    externalEdgeFile.write(str(key.nod1) + " " + str(key.layer1) + " "
                           + str(key.nod2) + " " + str(key.layer2) + " " + str(colorSet[key.color]) + " " + "2\n")
    edgeFile.write(str(key.nod1) + " " + str(key.layer1) + " "
                   + str(key.nod2) + " " + str(key.layer2) + " " + str(Edges[key]) + "\n")

print(nrHumans, nrCommits, nrIssues, nrFiles)
print(nrNodes, nrHumans + nrCommits + nrIssues + nrFiles)
print(weightedEdges)


class Tuple:
    def __init__(self, name1_, name2_, d1_, d2_):
        self.name1 = name1_
        self.name2 = name2_
        self.d1 = d1_
        self.d2 = d2_

    def __lt__(self, other):
        if self.d1 == 0 and other.d1 == 0:
            return self.d2 < other.d2
        if self.d1 == 0:
            return False
        if other.d1 == 0:
            return True
        if self.d2 / self.d1 == other.d2 / other.d1:
            return self.d1 > other.d1
        return self.d2 / self.d1 < other.d2 / other.d1

    def __eq__(self, other):
        return (self.name1 == other.name1 and self.name2 == other.name2)


names = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\NameSim.txt", "w")
allNames = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\AllName.txt", "wb")

from pyjarowinkler.distance import get_jaro_distance
import editdistance


def getSimilarity1(name1, name2):
    jaro_score = get_jaro_distance(name1, name2)
    return jaro_score


def getSimilarity2(name1, name2):
    return editdistance.eval(name1, name2)


def checkIdentities():
    lst = []
    for name in dict:
        if 'jdt' in name or 'inbox' in name or dict[name].site > 5:
            continue
        crtSite = Site(dict[name].site)
        allNames.write((name + '\n').encode('utf-8'))
        for otherName in dict:
            if otherName == name or 'jdt' in otherName or 'inbox' in otherName or Site(dict[otherName].site) == crtSite:
                continue
            lst.append(Tuple(name, otherName, getSimilarity1(name, otherName), getSimilarity2(name, otherName)))
    lst = sorted(lst)
    for i in range(len(lst)):
        bstr = (lst[i].name1 + ' ' + dict[lst[i].name1].site + ' ' + lst[i].name2 + ' ' +
                dict[lst[i].name2].site + '\n').encode()
        names.write(bstr)
    names.close()
    allNames.close()


layoutFile.write("nodeID nodeLabel\n")
for i in range(1, nrNodes + 1):
    layoutFile.write(str(i) + ' ' + str(Label[i]) + '\n')

layoutFile.close()
edgeFile.close()
externalEdgeFile.close()

for key in nrEdges:
    print(key + " " + str(nrEdges[key]))
