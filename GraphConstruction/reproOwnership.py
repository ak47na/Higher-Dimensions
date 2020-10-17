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


class Change:
    def __init__(self, nodeVal_, index_):
        self.nodeVal = nodeVal_
        self.index = index_
        self.fileNoes = []

    def addFile(self, fileNode):
        self.fileNoes.append(fileNode)

class ContributionNetwork:
    '''
        Sets the Eclipse project from projectList whose data will be used for creating the network.
    '''
    def setProject(self):
        self.projectList = Settings.getProjectList()
        self.projectID = Settings.getProjectID()

    '''
        Sets the type of issues the network will consider.
    '''
    def setIssueType(self):
        # issueType in {pos-release, pre-release}
        self.issueType = Settings.getIssueType()

    '''
        
    '''
    def __init__(self, nrHumanSubRoles_):
        # Initialize the lists with the indexes of nodes within each type.
        ### why used?????
        self.humansNodes = []
        self.humanNodes = []
        self.issueNodes = []
        self.fileNodes = []
        self.nrNodes = 0
        self.nrIssues = 0
        self.nrHumanSubRoles = nrHumanSubRoles_
        # Initialize the adjacency list of nodes, the list of edges and the number of edges.
        self.Adj = {}
        self.nrEdges = 0
        self.edgeList = []
        self.Edges = {}
        # C, F, R, I
        # The permutation represnts the order in which layers will be displayed.
        self.LayerPerm = EdgeTypeDetails.getLayerPerm()

        for i in range(self.nrHumanSubRoles):
            self.humanNodes.append([])
        self.Label = {}
        self.humanDict = {}
        self.i_R = {}
        # For user with name A and username B, self.nameOfUsername[B] = A.
        self.nameOfUsername = {}
        # self.issueDict = dictionary with issue names as keys and their corresponding node index
        # as values.
        self.issueDict = {}
        self.networkFiles = []
        # self.fileIssues contains for each file node, the nodes of issues related to that file.
        # self.fileIssues[fileNode] = {issueNode1 : True, issueNode2 : True, ... }
        self.fileIssues = {}
        # self.nrFileIssues[x] = the number of issues of file nod x.
        self.nrFileIssues = {}
        # self.reviewDict[reviewIndex] = Change object with the index of the review and the node
        # of the review in the network.
        self.reviewDict = {}
        # reviewIdForCommit[commitHash] = reviewId if commitHash was committed in reviewId.
        self.reviewIdForCommit = {}  # dict with commits as keys and their value represent the review they belong to
        # commitDict[commitHash] = Change object that has the index as the index of the commit.
        self.commitDict = {}
        self.nrCommits = 0
        #fileDict[fileName] = the index of the file node in the network.
        self.fileDict = {}
        
    def addEdge_util(self, crtEdge):
        if crtEdge in self.Edges:
            self.Edges[crtEdge] += 1
            return 0
        else:
            self.nrEdges += 1
            self.edgeList.append(crtEdge)
            if not (crtEdge.nod1 in self.Adj):
                self.Adj[crtEdge.nod1] = []
            self.Adj[crtEdge.nod1].append((crtEdge.nod2, crtEdge.layer2))
            self.Edges[crtEdge] = 1
            return 1

    def addEdge(self, nod1, l1, nod2, l2, col):
        l1 = self.LayerPerm[l1]
        l2 = self.LayerPerm[l2]
        if col == 1 or col == 15:
            return self.addEdge_util(Edge.Edge(nod1, l1, nod2, l2, col))
        return max(self.addEdge_util(Edge.Edge(nod1, l1, nod2, l2, col)),
                   self.addEdge_util(Edge.Edge(nod2, l2, nod1, l1, col)))

    def getHumanRolesFiles(self):
        # Human Names files
        humanRoleFiles = []
        self.Type = ['C', 'R', 'R', 'R', 'A', 'R', 'i_R', 'i_A', 'i_C']
        humanRoleFiles.append(open("Data\\CommitterAuthorFiles.txt", "r"))
        humanRoleFiles.append(open("Data\\OwnerNames2020.txt", "r"))
        humanRoleFiles.append(open("Data\\UploaderNames2020.txt", "r"))
        humanRoleFiles.append(open("Data\\CommentRevNames2020.txt", "r"))
        humanRoleFiles.append(open("Data\\ApproverNames2020.txt", "r"))
        humanRoleFiles.append(open("Data\\AuthorNames2020.txt", "r"))
        humanRoleFiles.append(open("Data\\ReporterNames2020B.txt", "rb"))
        humanRoleFiles.append(open("Data\\AssigneeNames2020B.txt", "rb"))
        humanRoleFiles.append(open("Data\\CCedNames2020B.txt", "rb"))
        return humanRoleFiles

    def addFile(self, crtFile):
        if (crtFile in self.fileDict):
            # The file was already added.
            return
        nrFiles = len(self.fileDict)
        self.nrNodes += 1
        self.Label[self.nrNodes] = (crtFile, 'File')
        self.fileNodes.append(self.nrNodes)
        self.fileDict[crtFile] = self.nrNodes
        self.fileIssues[self.nrNodes] = {}
        self.nrFileIssues[self.nrNodes] = 0
        self.networkFiles.append(File.File(nrFiles, crtFile, 0, 0, 0, 0))

    def readNameUsername(self):
        # name/\username from Bugzilla
        f = open("Data\\emailName2020B.txt", "rb")
        while (True):
            crtLine = f.readline().decode('utf-8')
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            Len = len(lst)
            name = Ownership.purifyName(lst[0])
            if name in self.humanDict:
                self.nameOfUsername[lst[-1][:-1]] = name
                self.humanDict[name].setUserName(lst[-1][:-1])
        f.close()

    def getHumanTable():
        cols = ['Committer', 'reviewOwner', 'patchUploader', 'reviewer', 'patchApprover', 'patchAuthor',
                'issueReporter', 'issueAssignee', 'issueCC']
        vals = []
        for r in range(self.nrHumanSubRoles):
            vals.append([len(self.humanNodes[r])])
        createTable2(cols[:-1], vals)

    def addHuman(self, name, fileId):
        if not (name in self.humanDict):
            self.nrNodes += 1
            self.Label[self.nrNodes] = (name, self.Type[fileId])
            self.humansNodes.append(self.nrNodes)
            self.humanDict[name] = Human.Human(name, self.nrNodes, len(self.humanDict))
        if self.humanDict[name].isFile[fileId] == False:
            self.humanNodes[fileId].append(self.humanDict[name].index)
        self.humanDict[name].isFile[fileId] = True
        self.humanDict[name].setRole(Human.Role(fileId))
        self.humanDict[name].setSite(fileId)

    def addReview(review_id, nrReviews):
        global nrNodes
        if not review_id in self.reviewDict:
            nrReviews += 1
            nrNodes += 1
            self.Label[nrNodes] = (str(review_id), 'Review')
            self.reviewDict[review_id] = Change(nrNodes, nrReviews)
        return nrReviews

    def addCommit(self, hashValue):
        if not (hashValue in self.commitDict):
            self.nrCommits += 1
            self.commitDict[hashValue] = Change(-1, self.nrCommits)

    def readCommits(self, commitDataFile):
        fileListForCrtCommit = []
        crtCommitHash = 0
        committerName = ''
        authorName = ''
        while (True):
            crtLine = commitDataFile.readline()
            if not crtLine:
                break
            if (crtLine == '' or crtLine == '\n'):
                continue
            lst = crtLine.split('/\\')
            if not (('.' in lst[0]) or ('/' in lst[0]) or ('\\' in lst[0])):
                # committer/\\author/\\commitHash
                assert len(lst) == 3
                committerName = Ownership.purifyName(lst[0])
                authorName = Ownership.purifyName(lst[1])
                self.addHuman(committerName, 0)
                self.addHuman(authorName, 5)
                commitHash = lst[2][:-1]
                crtCommitHash = commitHash
                self.addCommit(commitHash)
                if authorName != committerName:
                    # add edge committer->author as cross layer edge
                    self.addEdge(self.humanDict[committerName].index, 1, self.humanDict[authorName].index, 3, 2)
                fileListForCrtCommit = []
            else:
                crtFile = crtLine.rsplit('.', 1)[0].replace("/", '.')
                if not (crtFile in self.fileDict):
                    self.addFile(crtFile)
                self.commitDict[crtCommitHash].addFile(self.fileDict[crtFile])
                if len(fileListForCrtCommit) > 0:
                    L = Settings.getLayer2('file', 'fileC')
                    self.addEdge(self.fileDict[crtFile], L, self.fileDict[fileListForCrtCommit[-1]], L, 3)
                # Add edge from author of file to file.
                self.addEdge(self.humanDict[authorName].index, 1, self.fileDict[crtFile], 1, 4)
                if authorName != committerName:
                    # Add edge from committer of file to file.
                    self.addEdge(self.humanDict[committerName].index, 1, self.fileDict[crtFile], 1, 4)
                # for fileName in fileList:
                # nrEdges['file2fileCommit'] += addEdge(self.fileDict[crtFile], 10, self.fileDict[fileName], 10)
                # add undirected edge between co-committed self.files
                # addEdge(self.fileDict[crtFile], 12, self.fileDict[fileName], 12)
                # addEdge(self.fileDict[fileName], 12, self.fileDict[crtFile], 12)
                # change to L, L?
                fileListForCrtCommit.append(crtFile)
        commitDataFile.close()

    def readHumanRoleFile(self, humanRoleFile, fileId):
        while (True):
            # names in Bugzilla are read from binary files
            if fileId >= 6 and fileId <= 8:
                crtLineine = humanRoleFile.readline().decode('utf-8')
            else:
                crtLineine = humanRoleFile.readline()
            if not crtLineine:
                break
            # name/\email/\index
            name = Ownership.purifyName(crtLineine.split('/\\')[0])
            self.addHuman(name, fileId)
        humanRoleFile.close()

    def processReviewEdges(reviewEdges, L):
        edge4Review = {}
        for key in reviewEdges:
            revId = self.reviewIdForCommit[key]
            humanEdges = reviewEdges[key]
            if not (revId in edge4Review):
                edge4Review[revId] = {}
            for edge in humanEdges:
                edge4Review[revId][edge[1]] = True
            for edge in edge4Review[revId]:
                addEdge(self.humanDict[edge].index, L, self.reviewDict[revId].nodeVal, L, 16)

    def readReviews():
        global nrReviews
        reviewEdges = {}
        reviewFile = open("Data\\ReviewEdges2020.txt", "r")
        while True:
            crtLine = reviewFile.readline()
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            if lst[0] == 'CommentEdge' or lst[0] == 'PCommentEdge':
                name1 = Ownership.purifyName(lst[1])
                name2 = Ownership.purifyName(lst[2][:-1])
                L = Settings.getLayer2('reviewer', 'reviewOwner')
                if lst[0] == 'CommentEdge':
                    addEdge(self.humanDict[name2].index, L, self.humanDict[name1].index, L, 8)
                else:
                    addEdge(self.humanDict[name2].index, L, self.humanDict[name1].index, L, 8)
            elif lst[0] == 'Review2Commit':
                reviewId = lst[1]
                nrReviews = addReview(reviewId, nrReviews)
                commitId = lst[2].replace('\n', '')
                if (commitId in self.reviewIdForCommit) and (self.reviewIdForCommit[commitId] != reviewId):
                    exit()
                self.reviewIdForCommit[commitId] = reviewId
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
                    if name in self.humanDict:
                        self.fileNoes = self.commitDict[commitId].self.fileNoes
                        for fileNode in self.fileNoes:
                            addEdge(self.humanDict[name].index, L, fileNode, L, 10)
        processReviewEdges(reviewEdges, 3)
        reviewFile.close()

    def readReviewComments():
        revFileComm = open("Data\\ReviewFilesFromComments.txt", "r")
        while (True):
            crtLine = revFileComm.readline()
            if not crtLine:
                break
            lst = crtLine[:-1].split("/\\")
            reviewId = lst[4]
            if not (reviewId in self.reviewDict):
                nrReviews = addReview(reviewId, nrReviews)
            name1 = Ownership.purifyName(lst[2])
            name2 = Ownership.purifyName(lst[3])

            nod1 = self.humanDict[name1].index
            nod2 = self.humanDict[name2].index
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
        self.nrIssues += 1
        self.nrNodes += 1
        self.Label[self.nrNodes] = (issue.name, 'Issue')
        self.issueNodes.append(self.nrNodes)
        self.issueDict[issue.name] = self.nrNodes

    def readIssueEdges():
        global nrNodes
        # HumanRole/\name/username/\bugID
        issueEdgesFile = open("Data\\IssueEdges2020B.txt", "rb")
        while True:
            crtLine = issueEdgesFile.readline().decode('utf-8')
            if not crtLine:
                break
            if crtLine == '':
                continue
            lst = crtLine.split('/\\')
            if (lst[0][0] != 'C'):
                name = Ownership.purifyName(lst[1])

                if not (lst[-1][:-1] in self.issueDict):  # issue was not fixed
                    continue

                if not (name in self.humanDict):
                    print(name, lst[1])
                    continue
                layer = 'issueReporter'
                col = 5
                if lst[0][0] == 'A':
                    layer = 'issueAssignee'
                    col = 6
                else:
                    self.humanDict[name].isReporter = True
                L = Settings.getLayer2(layer, 'issue')
                addEdge(self.humanDict[name].index, L, self.issueDict[lst[-1][:-1]], L, col)
            else:
                uname = lst[1]
                if uname in self.nameOfUsername:
                    name = self.nameOfUsername[uname]
                    # ToDo add CCassignee edges
        issueEdgesFile.close()
        return self.nrIssues

    def readIssues():
        global nrNodes
        # bugID/\version/\creation_ts/\delta_ts/\status/\resolution
        issueFile = open("Data\\BugDetails.txt")
        while True:
            crtLine = issueFile.readline()
            if not crtLine:
                break
            lst = crtLine.split('/\\')
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
            issue = Issue.Issue(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], self.projectList[self.projectID])

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
            crtLine = issueFile.readline()
            if not crtLine:
                break
            bug = crtLine[:-1]
            crtLine = issueFile.readline()
            while crtLine and crtLine != 'EOB1':
                lst = crtLine.split('/\\')
                if bug in self.issueDict and lst[0] in self.nameOfUsername:
                    self.i_R[self.issueDict[bug]][self.nameOfUsername[lst[0]]] = True
                    # all commenters are issueReporters
                crtLine = issueFile.readline()
            crtLine = issueFile.readline()
            while crtLine and crtLine != 'EOB2':
                lst = crtLine.split('/\\')
                if bug in self.issueDict and lst[0] in self.nameOfUsername:
                    # all commenters are issueReporters
                    self.i_R[self.issueDict[bug]][self.nameOfUsername[lst[0]]] = True
                crtLine = issueFile.readline()
        addIrEdges()
        issueFile.close()

    def addIssueDependency(fName):
        # b_1/\b_2 <=> b_2 is in b_1's list of "depends_on" in Bugzilla
        f = open(fName, "r")
        while True:
            crtLine = f.readline()[:-1]
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            if len(lst) != 2:
                exit()
            crtLine = f.readline()[1:-1].split(', ')
            L = Settings.getLayer2('issue', 'issue')
            if (lst[0] in self.issueDict):
                i1 = self.issueDict[lst[0]]
                for elem in crtLine:
                    if elem in self.issueDict:
                        i2 = self.issueDict[elem]
                        addEdge(i1, L, i2, L, 15)

    def processReview(crtLine):
        reviewId = crtLine[1]
        issueID = crtLine[2][:-1]
        L = Settings.getLayer2('file', 'issue')
        if reviewId in self.reviewDict and issueID in self.issueDict:
            addEdge(self.reviewDict[reviewId].nodeVal, 3, self.issueDict[issueID], 4, 17)
            self.fileNoes = self.reviewDict[reviewId].self.fileNoes
            for fileNode in self.fileNoes:
                self.fileIssues[fileNode][self.issueDict[issueID]] = True
                self.nrFileIssues[fileNode] += addEdge(fileNode, L, self.issueDict[issueID], L, 12)

    def processCommit(crtLine):
        commitID = crtLine[1]
        issueID = crtLine[2][:-1]
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
            crtLine = bugEdgeFile.readline()
            if not crtLine:
                break
            if crtLine == '\n':
                continue
            crtLine = crtLine.split(' ')
            if crtLine[0] == 'ReviewEdge':
                processReview(crtLine)
            else:
                processCommit(crtLine)
        bugEdgeFile.close()

    def readIssue2Change():
        # type changeID bugID
        rc2BugEdge = open("Data\\RevMsg2BugEdge.txt", "r")
        while (True):
            crtLine = rc2BugEdge.readline()
            if not crtLine:
                break
            if crtLine == '\n':
                continue
            crtLine = crtLine.split(' ')
            if crtLine[0] == 'Review2Bug':
                processReview(crtLine)
            else:
                processCommit(crtLine)
        rc2BugEdge.close()

    def addIrEdges():
        layer = Settings.getLayer2('issueReporter', 'issueReporter')
        for key in self.i_R:
            crtDict = self.i_R[key]
            for i_r1 in crtDict:
                nod1 = self.humanDict[i_r1].index
                for i_r2 in crtDict:
                    if i_r1 != i_r2:
                        addEdge(nod1, layer, self.humanDict[i_r2].index, layer, 7)

    def addDepEdge(f):
        while True:
            crtLine = f.readline()
            if not crtLine:
                break
            lst = crtLine.split()
            if lst[1] in self.fileDict and lst[2] in self.fileDict:
                L = Settings.getLayer2('file', 'file')
                addEdge(self.fileDict[lst[1]], L, self.fileDict[lst[2]], L, 1)

    def readOwnershipFile():
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
            crtLine = ownershipFile.readline()
            if not crtLine:
                break
            lst = crtLine.split('/\\')
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
                    addEdge(self.humanDict[c1].index, 1, self.fileDict[obj.name], 1, 14)
                valuesC.append(cp)
                if sAll != 0:
                    if obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem >= sAll:
                        lp = 100
                    else:
                        lp = (100 * (obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem) / sAll)
                    valuesL.append(lp)
                for c2 in allCommitters:
                    if c1 != c2:
                        if self.humanDict[c1].isRole[0] and self.humanDict[c2].isRole[0]:
                            addEdge(self.humanDict[c1].index, L, self.humanDict[c2].index, L, 13)
                        elif self.humanDict[c2].isRole[0] or self.humanDict[c1].isRole[0]:
                            addEdge(self.humanDict[c1].index, L, self.humanDict[c2].index, A, 2)

            ownershipTuple = obj.nrCommitsOwner(0)
            self.ownershipDict[self.fileDict[obj.name]] = (ownershipTuple[0], obj.nrCommitsPercentage(0))
            m1, m2 = obj.getMeasures(0)
            X += m1
            Y += m2

        ownershipFile.close()

    def readDataForHumans(self):
        humanRolesFiles = self.getHumanRolesFiles()
        self.readCommits(humanRolesFiles[0])
        for fileId in range(1, self.nrHumanSubRoles):
            self.readHumanRoleFile(humanRolesFiles[fileId], fileId)
        self.readNameUsername()
        nrReviews = readReviewComments(0)
        readReviews()

    def readAndUpdateDataForIssues(self):
        self.nrIssues = readIssues()
        readIssue2Change()
        readI2CSeeAlso()
        readIssueComments()
        addIssueDependency("Data\\BugDep.txt")

    def readDataForFiles(self):
        # File dependencies files
        depFile = []
        depFile.append(open("Data\\FileDep.txt", "r"))
        depFile.append(open("Data\\ClassDep.txt", "r"))
        for fileId in range(len(depFile)):
            addDepEdge(depFile[fileId])
            depFile[fileId].close()
        self.files, posInFiles = File.readFileMeasures(self.fileDict, "Data\\codeMeasures2020.txt")

    def readAndUpdateDataForOwnership(self):
        self.ownershipDict = {}
        readOwnershipFile(self)

    def getSNAMeasure(self, name):
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
            return self.monoplex.getEffectiveSize()
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

network = ContributionNetwork(8)
network.readDataForHumans()
network.createMonoplex()
