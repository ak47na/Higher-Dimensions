import Ownership
import Edge
import Sample
import createTable
import File
import Human
import readSNA_measure
import EdgeTypeDetails
from scipy.stats import spearmanr
import Issue
from networkx import *
import Settings
import SNAMeasures

class ContributionNetwork:
    def setProject(self):
        self.project = Settings.getProjectList()
        self.projectID = Settings.getProjectID()
    def setIssueType(self):
        # issueType in {pos-release, pre-release}
        self.issueType = Settings.getIssueType()

    def __init__(self):
        self.Adj = {}
        self.nrEdges = 0
        self.edgeList = []
        self.LayerPerm = EdgeTypeDetails.getLayerPerm()
        # C, F, R, I

        # Initialize the lists with the indexes of nodes within each type.
        self.humanNodes = []
        self.humansNodes = []
        self.issueNodes = []
        self.fileNodes = []
        self.humanRoles = 8
        self.humanLayers = 6
        for i in range(self.humanRoles):
            self.humanNodes.append([])
        self.nrNodes = 0
        self.nrIssues = 0
        self.Label = {}
        self.dict = {}
        self.i_R = {}
        self.usernames = {}
        self.issueDict = {}
        # self.fileIssues contains the nodes of the issues
        self.fileIssues = {}
        # dict with self.nrFileIssues[x] = the number of issues of nod x;
        self.nrFileIssues = {}
        self.reviewDict = {}
        self.reviewID = {}  # dict with commits as keys and their value represent the review they belong to
        self.commitDict = {}
        self.fileDict = {}
        self.files = []
        self.Edges = {}

    def addEdge_util(crtEdge):
        global nrEdges
        if crtEdge in self.Edges:
            self.Edges[crtEdge] += 1
            return 0
        else:
            nrEdges += 1
            edgeList.append(crtEdge)
            if not (crtEdge.nod1 in Adj):
                Adj[crtEdge.nod1] = []
            Adj[crtEdge.nod1].append((crtEdge.nod2, crtEdge.layer2))
            self.Edges[crtEdge] = 1
            return 1

    def addEdge(nod1, l1, nod2, l2, col):
        # if col != 1 and col != 14:
        #     return 0
        l1 = LayerPerm[l1]
        l2 = LayerPerm[l2]
        if col == 1 or col == 15:
            return addEdge_util(Edge.Edge(nod1, l1, nod2, l2, col))

        return max(addEdge_util(Edge.Edge(nod1, l1, nod2, l2, col)),
                   addEdge_util(Edge.Edge(nod2, l2, nod1, l1, col)))

    def openFiles(self):
        # Human Names files
        self.files = []
        Type = ['C', 'R', 'R', 'R', 'A', 'R', 'i_R', 'i_A', 'i_C']
        self.files.append(open("Data\\CommitterAuthorFiles.txt", "r"))
        self.files.append(open("Data\\OwnerNames2020.txt", "r"))
        self.files.append(open("Data\\UploaderNames2020.txt", "r"))
        self.files.append(open("Data\\CommentRevNames2020.txt", "r"))
        self.files.append(open("Data\\ApproverNames2020.txt", "r"))
        self.files.append(open("Data\\AuthorNames2020.txt", "r"))
        self.files.append(open("Data\\ReporterNames2020B.txt", "rb"))
        self.files.append(open("Data\\AssigneeNames2020B.txt", "rb"))
        self.files.append(open("Data\\CCedNames2020B.txt", "rb"))
        # File dependencies self.files
        depFile = []
        depFile.append(open("Data\\FileDep.txt", "r"))
        depFile.append(open("Data\\ClassDep.txt", "r"))
        # Event/Edge self.files
        reviewFile = open("Data\\ReviewEdges2020.txt", "r")
        rc2BugEdge = open("Data\\RevMsg2BugEdge.txt", "r")

    def addFile(crtFile, nrFiles):
        global nrNodes
        nrFiles += 1
        nrNodes += 1
        self.Label[nrNodes] = (crtFile, 'File')
        self.fileNoes.append(nrNodes)
        self.fileDict[crtFile] = nrNodes
        self.fileIssues[nrNodes] = {}
        self.nrFileIssues[nrNodes] = 0
        self.files.append(File.File(nrFiles, crtFile, 0, 0, 0, 0))
        return nrFiles

    class MyChange:
        def __init__(self, nodeVal_, index_, hash_id_):
            self.nodeVal = nodeVal_
            self.index = index_
            self.hash_id = hash_id_
            self.self.fileNoes = []

        def addFile(self, fileNode):
            self.self.fileNoes.append(fileNode)

    def readNameUsername():
        # name/\username from Bugzilla
        f = open("Data\\emailName2020B.txt", "rb")
        while (True):
            crtL = f.readline().decode('utf-8')
            if not crtL:
                break
            lst = crtL.split('/\\')
            Len = len(lst)
            name = Ownership.purifyName(lst[0])
            if name in self.dict:
                self.usernames[lst[-1][:-1]] = name
                self.dict[name].setUserName(lst[-1][:-1])
        f.close()

    def getHumanTable():
        cols = ['Committer', 'reviewOwner', 'patchUploader', 'reviewer', 'patchApprover', 'patchAuthor',
                'issueReporter', 'issueAssignee', 'issueCC']
        vals = []
        for r in range(self.humanRoles):
            vals.append([len(self.humanNodes[r])])
        createTable2(cols[:-1], vals)

    def addHuman(name, nrHumans, fNr):
        global nrNodes
        if not (name in self.dict):
            nrHumans += 1
            nrNodes += 1
            self.Label[nrNodes] = (name, Type[fNr])
            self.humansNodes.append(nrNodes)
            self.dict[name] = Human.Human(name, nrNodes, nrHumans)
        if self.dict[name].isFile[fNr] == False:
            self.humanNodes[fNr].append(self.dict[name].index)
        self.dict[name].isFile[fNr] = True
        self.dict[name].setRole(Human.Role(fNr))
        self.dict[name].setSite(fNr)
        return nrHumans

    def addReview(review_id, nrReviews):
        global nrNodes
        if not review_id in self.reviewDict:
            nrReviews += 1
            nrNodes += 1
            self.Label[nrNodes] = (str(review_id), 'Review')
            self.reviewDict[review_id] = MyChange(nrNodes, nrReviews, review_id)
        return nrReviews

    def addCommit(hash_id, nrCommits):
        if not (hash_id in self.commitDict):
            nrCommits += 1
            self.commitDict[hash_id] = MyChange(-1, nrCommits, hash_id)
        return nrCommits

    def readCommits(self, nrHumans, nrCommits, nrFiles):
        fileList = []
        global nrNodes
        commit_hash = 0
        while (True):
            crtL = self.files[0].readline()
            if not crtL:
                break
            if (crtL == '' or crtL == '\n'):
                continue
            # committer/\\author/\\commitHash
            Lst = crtL.split('/\\')
            if not (('.' in Lst[0]) or ('/' in Lst[0]) or ('\\' in Lst[0])):
                Lst = crtL.split('/\\')
                committerName = Ownership.purifyName(Lst[0])
                authorName = Ownership.purifyName(Lst[1])
                nrHumans = addHuman(committerName, nrHumans, 0)
                nrHumans = addHuman(authorName, nrHumans, 5)
                commitId = Lst[2][:-1]
                commit_hash = commitId
                nrCommits = addCommit(commitId, nrCommits)
                if authorName != committerName:
                    # add edge committer->author as cross layer edge
                    addEdge(self.dict[committerName].index, 1, self.dict[authorName].index, 3, 2)
                fileList = []
            else:
                crtFile = crtL.rsplit('.', 1)[0].replace("/", '.')
                if not (crtFile in self.fileDict):
                    nrFiles = addFile(crtFile, nrFiles)
                self.commitDict[commit_hash].addFile(self.fileDict[crtFile])
                if len(fileList) > 0:
                    L = Settings.getLayer2('file', 'fileC')
                    addEdge(self.fileDict[crtFile], L, self.fileDict[fileList[len(fileList) - 1]], L, 3)
                # self.Edges from commits to self.files:
                addEdge(self.dict[authorName].index, 1, self.fileDict[crtFile], 1, 4)
                if authorName != committerName:
                    addEdge(self.dict[committerName].index, 1, self.fileDict[crtFile], 1, 4)
                # for fileName in fileList:
                # nrEdges['file2fileCommit'] += addEdge(self.fileDict[crtFile], 10, self.fileDict[fileName], 10)
                # add undirected edge between co-committed self.files
                # addEdge(self.fileDict[crtFile], 12, self.fileDict[fileName], 12)
                # addEdge(self.fileDict[fileName], 12, self.fileDict[crtFile], 12)
                # change to L, L?

                fileList.append(crtFile)
            self.files[0].close()
        return nrHumans, nrCommits, nrFiles

    def readHumanF(fNr, nrHumans):
        while (True):
            # names in Bugzilla are read from binary self.files
            if fNr >= 6 and fNr <= 8:
                crtL = self.files[fNr].readline().decode('utf-8')
            else:
                crtL = self.files[fNr].readline()

            if not crtL:
                break
            if '/\\' in crtL:  # name/\email/\index
                name = Ownership.purifyName(crtL.split('/\\')[0])
                nrHumans = addHuman(name, nrHumans, fNr)
            else:  # name email index
                lst = crtL.split()
                Len = len(lst)
                name = ''
                for i in range(Len - 1):
                    name = name + lst[i]
                name = Ownership.purifyName(name)
                nrHumans = addHuman(name, nrHumans, fNr)

        return nrHumans

    def processReviewEdges(reviewEdges, L):
        edge4Review = {}
        for key in reviewEdges:
            revId = self.reviewID[key]
            humanEdges = reviewEdges[key]
            if not (revId in edge4Review):
                edge4Review[revId] = {}
            for edge in humanEdges:
                edge4Review[revId][edge[1]] = True
            for edge in edge4Review[revId]:
                addEdge(self.dict[edge].index, L, self.reviewDict[revId].nodeVal, L, 16)

    def readReviews():
        global nrReviews
        reviewEdges = {}
        while True:
            crtL = reviewFile.readline()
            if not crtL:
                break
            lst = crtL.split('/\\')
            if lst[0] == 'CommentEdge' or lst[0] == 'PCommentEdge':
                name1 = Ownership.purifyName(lst[1])
                name2 = Ownership.purifyName(lst[2][:-1])
                L = Settings.getLayer2('reviewer', 'reviewOwner')
                if lst[0] == 'CommentEdge':
                    addEdge(self.dict[name2].index, L, self.dict[name1].index, L, 8)
                else:
                    addEdge(self.dict[name2].index, L, self.dict[name1].index, L, 8)
            elif lst[0] == 'Review2Commit':
                reviewId = lst[1]
                nrReviews = addReview(reviewId, nrReviews)
                commitId = lst[2].replace('\n', '')
                if (commitId in self.reviewID) and (self.reviewID[commitId] != reviewId):
                    exit()
                self.reviewID[commitId] = reviewId
            else:
                commitId = lst[1]
                name = Ownership.purifyName(lst[2][:-1])
                # reviewEdges[commitId] = edges that relate to commitId s.t edges between the review coresp to commitId can be linked with the humans
                if not (commitId in reviewEdges):
                    reviewEdges[commitId] = []
                reviewEdges[commitId].append((lst[0], name))
                if commitId in self.commitDict:
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
                    L = Settings.getLayer2(layer, 'file')
                    # link humans to the self.files of the commit
                    if name in self.dict:
                        self.fileNoes = self.commitDict[commitId].self.fileNoes
                        for fileNode in self.fileNoes:
                            addEdge(self.dict[name].index, L, fileNode, L, 10)
        processReviewEdges(reviewEdges, 3)
        reviewFile.close()

    def readReviewComments(nrReviews):
        revFileComm = open("Data\\ReviewFilesFromComments.txt", "r")
        while (True):
            crtL = revFileComm.readline()
            if not crtL:
                break
            lst = crtL[:-1].split("/\\")
            reviewId = lst[4]
            if not (reviewId in self.reviewDict):
                nrReviews = addReview(reviewId, nrReviews)
            name1 = Ownership.purifyName(lst[2])
            name2 = Ownership.purifyName(lst[3])

            nod1 = self.dict[name1].index
            nod2 = self.dict[name2].index
            L = Settings.getLayer2('reviewer', 'reviewOwner')
            if name1 != name2:
                addEdge(nod2, L, nod1, L, 8)
            fileList = lst[1].rsplit('.', -1)[:-1]
            fileName = ''
            for x in fileList:
                fileName += x
                fileName += '.'
            fileName = fileName.replace('/', '.')[:-1]
            if fileName in self.fileDict:
                self.reviewDict[reviewId].addFile(self.fileDict[fileName])
                # edge between reviewOwner and file on Review layer from comment
                addEdge(nod1, 3, self.fileDict[fileName], 3, 11)
        return nrReviews

    def getIssues():
        g = open("BugDex2020.txt", "w")
        for key in self.issueDict:
            g.write(str(key) + '/\\')
        g.close()

    def addIssue(issue):
        global nrNodes
        self.nrIssues += 1
        nrNodes += 1
        self.Label[nrNodes] = (issue.name, 'Issue')
        self.issueNodes.append(nrNodes)
        self.issueDict[issue.name] = nrNodes

    def readIssueEdges():
        global nrNodes
        # HumanRole/\name/username/\bugID
        issueEdgesFile = open("Data\\IssueEdges2020B.txt", "rb")
        while True:
            crtL = issueEdgesFile.readline().decode('utf-8')
            if not crtL:
                break
            if crtL == '':
                continue
            lst = crtL.split('/\\')
            if (lst[0][0] != 'C'):
                name = Ownership.purifyName(lst[1])

                if not (lst[-1][:-1] in self.issueDict):  # issue was not fixed
                    continue

                if not (name in self.dict):
                    print(name, lst[1])
                    continue
                layer = 'issueReporter'
                col = 5
                if lst[0][0] == 'A':
                    layer = 'issueAssignee'
                    col = 6
                else:
                    self.dict[name].isReporter = True
                L = Settings.getLayer2(layer, 'issue')
                addEdge(self.dict[name].index, L, self.issueDict[lst[-1][:-1]], L, col)
            else:
                uname = lst[1]
                if uname in self.usernames:
                    name = self.usernames[uname]
                    # ToDo add CCassignee edges
        issueEdgesFile.close()
        return self.nrIssues

    def readIssues():
        global nrNodes
        # bugID/\version/\creation_ts/\delta_ts/\status/\resolution
        issueFile = open("Data\\BugDetails.txt")
        while True:
            crtL = issueFile.readline()
            if not crtL:
                break
            lst = crtL.split('/\\')
            a = lst[2].split(' ', 1)
            a[1] = a[1].replace(' ', '')
            if len(a) != 2:
                exit()
            lst[2] = Ownership.getTime(a[0], a[1])
            a = lst[3].split(' ', 1)
            a[1] = a[1].replace(' ', '')
            lst[3] = Ownership.getTime(a[0], a[1])
            if len(a) != 2:
                exit()
            if len(lst) != 6:
                exit()
            lst[5] = lst[5][:-1]  # ignore '\n'
            issue = Issue.Issue(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], self.project[self.projectID])

            if issue.getType() == self.issueType and (lst[5] == 'FIXED' or lst[5] == 'WORKSFORME'):
                if not (issue.name in self.issueDict):
                    self.nrIssues = addIssue(issue)
                    issue.setIndex(self.nrIssues)
                    self.i_R[nrNodes] = {}
            # in case only fixed issues must be added =>
            # if ("CLOSED" in status_i) or ("RESOLVED" in status_i) or ("VERIFIED" in status_i) or ("FIXED" in status_i):

        issueFile.close()
        self.nrIssues = readIssueEdges()
        return self.nrIssues

    def readIssueComments():
        # comments to Bugs:
        issueFile = open("Data\\comments2020.txt")
        while True:
            crtL = issueFile.readline()
            if not crtL:
                break
            bug = crtL[:-1]
            crtL = issueFile.readline()
            while crtL and crtL != 'EOB1':
                lst = crtL.split('/\\')
                if bug in self.issueDict and lst[0] in self.usernames:
                    self.i_R[self.issueDict[bug]][self.usernames[lst[0]]] = True
                    # all commenters are issueReporters
                crtL = issueFile.readline()
            crtL = issueFile.readline()
            while crtL and crtL != 'EOB2':
                lst = crtL.split('/\\')
                if bug in self.issueDict and lst[0] in self.usernames:
                    # all commenters are issueReporters
                    self.i_R[self.issueDict[bug]][self.usernames[lst[0]]] = True
                crtL = issueFile.readline()
        addIrEdges()
        issueFile.close()

    def addIssueDependency(fName):
        # b_1/\b_2 <=> b_2 is in b_1's list of "depends_on" in Bugzilla
        f = open(fName, "r")
        while True:
            crtL = f.readline()[:-1]
            if not crtL:
                break
            lst = crtL.split('/\\')
            if len(lst) != 2:
                exit()
            crtL = f.readline()[1:-1].split(', ')
            L = Settings.getLayer2('issue', 'issue')
            if (lst[0] in self.issueDict):
                i1 = self.issueDict[lst[0]]
                for elem in crtL:
                    if elem in self.issueDict:
                        i2 = self.issueDict[elem]
                        addEdge(i1, L, i2, L, 15)

    def processReview(crtL):
        reviewId = crtL[1]
        issueID = crtL[2][:-1]
        L = Settings.getLayer2('file', 'issue')
        if reviewId in self.reviewDict and issueID in self.issueDict:
            addEdge(self.reviewDict[reviewId].nodeVal, 3, self.issueDict[issueID], 4, 17)
            self.fileNoes = self.reviewDict[reviewId].self.fileNoes
            for fileNode in self.fileNoes:
                self.fileIssues[fileNode][self.issueDict[issueID]] = True
                self.nrFileIssues[fileNode] += addEdge(fileNode, L, self.issueDict[issueID], L, 12)

    def processCommit(crtL):
        commitID = crtL[1]
        issueID = crtL[2][:-1]
        L = Settings.getLayer2('file', 'issue')
        if commitID in self.commitDict and issueID in self.issueDict:
            self.fileNoes = self.commitDict[commitID].self.fileNoes
            for fileNode in self.fileNoes:
                self.fileIssues[fileNode][self.issueDict[issueID]] = True
                self.nrFileIssues[fileNode] += addEdge(fileNode, L, self.issueDict[issueID], L, 12)

    def readI2CSeeAlso():
        # type changeID bugID
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
        layer = Settings.getLayer2('issueReporter', 'issueReporter')
        for key in self.i_R:
            crtDict = self.i_R[key]
            for i_r1 in crtDict:
                nod1 = self.dict[i_r1].index
                for i_r2 in crtDict:
                    if i_r1 != i_r2:
                        addEdge(nod1, layer, self.dict[i_r2].index, layer, 7)

    def addDepEdge(f):
        while True:
            crtL = f.readline()
            if not crtL:
                break
            lst = crtL.split()
            if lst[1] in self.fileDict and lst[2] in self.fileDict:
                L = Settings.getLayer2('file', 'file')
                addEdge(self.fileDict[lst[1]], L, self.fileDict[lst[2]], L, 1)

    def readOwnershipFile(ownershipDict):
        # fileName/\nrCommits
        # author_name/\self.author_date/\author_timezone/\added/\removed/\complexity
        ownershipFile = open("Data\\ownership.txt")
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
            lst = crtL.split('/\\')
            compName = lst[0].replace('/', '.')
            compName = compName.rsplit('.', 1)[0]
            if not (compName in self.fileDict):
                for i in range(int(lst[1])):
                    nxtL = ownershipFile.readline()
                continue
            obj = Ownership.Ownership(compName)
            nrFiles += 1
            for i in range(int(lst[1])):
                nxtL = ownershipFile.readline().split('/\\')
                lineLen = len(nxtL)
                if lineLen == 0:
                    continue
                obj.addModif(Ownership.getModifFromLine(nxtL, lineLen))

            allCommitters = obj.authorDex[0]
            jarList = []

            L = Settings.getLayer2('committer', 'committer')
            A = Settings.getLayer2('committer', 'author')
            if self.fileDict[obj.name] in posInFiles:
                sAll = obj.sumAdd[0] + obj.sumRem[0]
            else:
                sAll = 0
            for c1 in allCommitters:
                nrCommitters += 1
                cp = (100 * obj.authorDex[0][c1].nrCommits / obj.nrCommits[0])
                # change to cp > 50 for only major edges
                if cp <= 50:
                    addEdge(self.dict[c1].index, 1, self.fileDict[obj.name], 1, 14)
                valuesC.append(cp)
                if sAll != 0:
                    if obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem >= sAll:
                        lp = 100
                    else:
                        lp = (100 * (obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem) / sAll)
                    valuesL.append(lp)
                for c2 in allCommitters:
                    if c1 != c2:
                        if self.dict[c1].isRole[0] and self.dict[c2].isRole[0]:
                            addEdge(self.dict[c1].index, L, self.dict[c2].index, L, 13)
                        elif self.dict[c2].isRole[0] or self.dict[c1].isRole[0]:
                            addEdge(self.dict[c1].index, L, self.dict[c2].index, A, 2)

            ownershipTuple = obj.nrCommitsOwner(0)
            ownershipDict[self.fileDict[obj.name]] = (ownershipTuple[0], obj.nrCommitsPercentage(0))
            m1, m2 = obj.getMeasures(0)

            X += m1
            Y += m2

        ownershipFile.close()
        return ownershipDict

    def readDataForHumans(self):
        nrHumans, nrCommits, nrFiles = readCommits(0, 0, 0)
        for fileId in range(1, self.humanRoles):
            nrHumans = readHumanF(fileId, nrHumans)
            self.files[fileId].close()
        readNameUsername()
        nrReviews = readReviewComments(0)
        readReviews()

    def readAndUpdateDataForIssues(self):
        self.nrIssues = readIssues()
        readIssue2Change()
        readI2CSeeAlso()
        readIssueComments()
        addIssueDependency("Data\\BugDep.txt")

    def readDataForFiles(self):
        for fileId in range(len(depFile)):
            addDepEdge(depFile[fileId])
            depFile[fileId].close()
        self.files, posInFiles = File.readFileMeasures(self.fileDict, "Data\\codeMeasures2020.txt")
    def readAndUpdateDataForOwnership(self):
        ownershipDict = {}
        ownershipDict = readOwnershipFile(ownershipDict)

    def getSNAMeasure(name):
        if name == 'Betweenness Centrality':
            return betweenness_centrality(self.ownershipGraph)
        if name == 'Closeness Centrality':
            return closeness_centrality(self.ownershipGraph)
        if name == 'Degree Centrality':
            return degree_centrality(self.ownershipGraph)
        if name == 'Effective Size':
            return effective_size(self.ownershipGraph)
        if name == 'Constraint':
            return constraint(self.ownershipGraph)
        if name == 'Reachability':
            return None
        if name == 'Effective Size':
            return monoplex.getEffectiveSize()
        if name == 'Constraint':
            return None

    def getSNAResult(name):
        fileValues = []
        self.nrIssuesList = []
        values = getSNAMeasure(name)

        for fileN in self.fileDict:
            nod = self.fileDict[fileN]
            if not (nod in Nodes):
                continue
            self.nrIssuesList.append(self.nrFileIssues[nod])
            if values == None:
                fileValues.append(local_reaching_centrality(self.ownershipGraph, nod))
            else:
                fileValues.append(values[nod])
        w, p = spearmanr(fileValues, self.nrIssuesList)
        print(measure, w, p)

    def createMonoplex(self):
        self.Nodes = []
        self.ownershipGraph = networkx.DiGraph()
        for e in self.Edges:
            if self.Edges[e] > 0 and (e.color == 1 or e.color == 14):
                self.ownershipGraph.add_edge(e.nod1, e.nod2, w=self.Edges[e])
        Nodes = list(self.ownershipGraph.nodes)
        self.monoplex = SNAMeasures.Monoplex(self.ownershipGraph, True, "w")

    def getResultsFromSNAMeasures(self, measures):
        for measure in measures:
            SNAMeasures.getSNAResult(measure)

    # measures1 = ['Degree Centrality', 'Betweenness Centrality', 'Closeness Centrality', 'Reachability']
    # measures2 = ['Effective Size', 'Constraint']

network = ContributionNetwork()
network.createMonoplex()
