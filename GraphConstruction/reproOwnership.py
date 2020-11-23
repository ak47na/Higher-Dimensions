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

'''
    Class that represents a code change using its node value in the ContributionNetwork (if it's a
    node or -1 otw) and its index in the set of code changes of its type(commit/review).
    Each change object stores a list with the names of the files it modified.
'''
class Change:
    def __init__(self, nodeVal_, index_):
        self.nodeVal = nodeVal_
        self.index = index_
        self.modifiedFiles = []

    def addFile(self, fileNode):
        self.modifiedFiles.append(fileNode)

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
        ### why used?????
        self.setProject()
        self.setIssueType()
        # Initialize the lists with the indexes of graph nodes within each type.
        # humansNodes = list of graph nodes of that represent humans.
        self.humansNodes = []
        # humanNodes[humanRole] = list of graph nodes of humans that have the role humanRole.
        self.humanNodes = []
        # issueNodes = list of graph nodes that represent issues.
        self.issueNodes = []
        # fileNodes = list of graph nodes that represent files.
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
        # The permutation represents the order in which layers will be displayed.
        self.LayerPerm = EdgeTypeDetails.getLayerPerm()

        for i in range(self.nrHumanSubRoles):
            self.humanNodes.append([])
        self.Label = {}
        self.humanDict = {}
        self.i_R = {}
        # For user with name A and username B, self.nameOfUsername[B] = A.
        self.nameOfUsername = {}
        # self.issueDict = dictionary with issue names as keys and their corresponding graph node
        #  index as values.
        self.issueDict = {}
        # list of File objects corresponding to all the files in the ContributionNetwork.
        self.networkFiles = []
        # self.fileIssues contains for each file node, the nodes of issues related to that file.
        # self.fileIssues[fileNode] = {issueNode1 : True, issueNode2 : True, ... }
        self.fileIssues = {}
        # self.reviewDict[reviewId] = Change object with the index of the review in the set of
        # reviews and the node of the review in the network.
        self.reviewDict = {}
        # reviewIdForCommit[commitHash] = reviewId if commitHash was committed in reviewId:
        # dict with commits as keys and their value represent the review they belong to
        self.reviewIdForCommit = {}
        # commitDict[commitHash] = Change object that has the index as the index of the commit.
        self.commitDict = {}
        # fileDict[fileName] = the graph node of the file with fileName in the network.
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
        self.networkFiles.append(File.File(nrFiles, crtFile, 0, 0, 0, 0))

    def readNameUsername(self):
        # name/\username from Bugzilla
        f = open("Data\\emailName2020B.txt", "rb")
        while (True):
            crtLine = f.readline().decode('utf-8')
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            assert len(lst) == 2
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

    def addHuman(self, name, roleId):
        if not (name in self.humanDict):
            self.nrNodes += 1
            self.Label[self.nrNodes] = (name, self.Type[roleId])
            self.humanDict[name] = Human.Human(name, self.nrNodes, len(self.humanDict))
            self.humansNodes.append(self.humanDict[name].index)
        if self.humanDict[name].isFile[roleId] == False:
            self.humanNodes[roleId].append(self.humanDict[name].index)
        self.humanDict[name].isFile[roleId] = True
        self.humanDict[name].setRole(Human.Role(roleId))
        self.humanDict[name].setSite(roleId)

    def addReview(self, reviewNumber):
        if not reviewNumber in self.reviewDict:
            self.nrNodes += 1
            self.Label[self.nrNodes] = (str(reviewNumber), 'Review')
            self.reviewDict[reviewNumber] = Change(self.nrNodes, len(self.reviewDict))

    def addCommit(self, hashValue):
        if not (hashValue in self.commitDict):
            self.commitDict[hashValue] = Change(-1, len(self.commitDict))

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
                fileListForCrtCommit.append(crtFile)
        commitDataFile.close()

    def readHumanRoleFile(self, humanRoleFile, fileId):
        while (True):
            # names in Bugzilla are read from binary files
            if fileId >= 6 and fileId <= 8:
                crtLine = humanRoleFile.readline().decode('utf-8')
            else:
                crtLine = humanRoleFile.readline()
            if not crtLine:
                break
            # name/\email/\index
            lst = crtLine.split('/\\')
            assert len(lst) == 3 - (fileId >= 6 and fileId <= 8)
            name = Ownership.purifyName(lst[0])
            self.addHuman(name, fileId)
        humanRoleFile.close()

    def processReviewEdges(self, reviewEdges, L):
        edge4Review = {}
        for commitHash in reviewEdges:
            revId = self.reviewIdForCommit[commitHash]
            humanEdges = reviewEdges[commitHash]
            if not (revId in edge4Review):
                edge4Review[revId] = {}
            for edge in humanEdges:
                edge4Review[revId][edge[1]] = True
            for humanName in edge4Review[revId]:
                self.addEdge(self.humanDict[humanName].index, L, self.reviewDict[revId].nodeVal, L, 16)

    def readReviews(self):
        reviewEdges = {}
        reviewFile = open("Data\\ReviewEdges2020.txt", "r")
        while True:
            crtLine = reviewFile.readline()
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            assert len(lst) == 3
            if lst[0] == 'CommentEdge' or lst[0] == 'PCommentEdge':
                # The format of current line is "edgeType/\ownerName/\commenterName".
                name1 = Ownership.purifyName(lst[1])
                name2 = Ownership.purifyName(lst[2][:-1])
                L = Settings.getLayer2('reviewer', 'reviewOwner')
                self.addEdge(self.humanDict[name2].index, L, self.humanDict[name1].index, L, 8)
            elif lst[0] == 'Review2Commit':
                # The format of current line is "edgeType/\reviewNumber/\commitHash".
                reviewNumber = lst[1]
                self.addReview(reviewNumber)
                commitHash = lst[2].replace('\n', '')
                # If the commit belongs to multiple reviews, then data is invalid.
                assert (not((commitHash in self.reviewIdForCommit) and
                            (self.reviewIdForCommit[commitHash] != reviewNumber)))
                self.reviewIdForCommit[commitHash] = reviewNumber
            else:
                # The format of current line is "edgeType/\commitHash/\developerName", where
                # edgeType in {AuthorEdge, UploaderEdge, ApprovalEdge, OwnerEdge}
                commitHash = lst[1]
                developerName = Ownership.purifyName(lst[2][:-1])
                # reviewEdges[commitHash] = edges that relate to commitHash s.t edges between the 
                # review corresponding to commitHash can be linked with the humans in one pass.
                if not (commitHash in reviewEdges):
                    reviewEdges[commitHash] = []
                reviewEdges[commitHash].append((lst[0], developerName))
                if commitHash in self.commitDict:
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
                    else:
                        assert lst[0] == 'UploaderEdge'
                        
                    L = Settings.getLayer2(layer, 'file')
                    # link humans to the files of the commit
                    if developerName in self.humanDict:
                        for fileNode in self.commitDict[commitHash].modifiedFiles:
                            self.addEdge(self.humanDict[developerName].index, L, fileNode, L, 10)
        self.processReviewEdges(reviewEdges, 3)
        reviewFile.close()

    def readReviewComments(self):
        # File with review, commit, file and developer data from comments in format:
        # relationType/\\fileName/\\ownerName/\\commenterName/\\reviewNumber/\\commitHash
        revFileComm = open("Data\\ReviewFilesFromComments.txt", "r")
        while (True):
            crtLine = revFileComm.readline()
            if not crtLine:
                break
            lst = crtLine[:-1].split("/\\")
            assert len(lst) == 6
            reviewNumber = lst[4]
            self.addReview(reviewNumber)
            ownerName = Ownership.purifyName(lst[2])
            commenterName = Ownership.purifyName(lst[3])

            node1 = self.humanDict[ownerName].index
            node2 = self.humanDict[commenterName].index
            L = Settings.getLayer2('reviewer', 'reviewOwner')
            if ownerName != commenterName:
                # Add edge from commenter to owner.
                self.addEdge(node2, L, node1, L, 8)
            if not('.' in lst[1]):
                # All files should contain at least one '.' from the file type.
                continue
            fileName = (lst[1].rsplit('.', 1)[0]).replace('/', '.')[:-1]
            if fileName in self.fileDict:
                self.reviewDict[reviewNumber].addFile(self.fileDict[fileName])
                #Add edge between reviewOwner and file on Review layer.
                self.addEdge(node1, 3, self.fileDict[fileName], 3, 11)

    def writeIssuesFile(self):
        g = open("BugDex2020.txt", "w")
        for key in self.issueDict:
            g.write(str(key) + '/\\')
        g.close()

    def addIssue(self, issue):
        self.nrIssues += 1
        self.nrNodes += 1
        self.Label[self.nrNodes] = (issue.name, 'Issue')
        self.issueNodes.append(self.nrNodes)
        self.issueDict[issue.name] = self.nrNodes

    def readIssueEdges(self):
        # Each line of file contains data for an issue in format HumanRole/\name/username/\bugID.
        issueEdgesFile = open("Data\\IssueEdges2020B.txt", "rb")
        while True:
            crtLine = issueEdgesFile.readline().decode('utf-8')
            if not crtLine:
                break
            if crtLine == '':
                continue
            lst = crtLine.split('/\\')
            assert(len(lst) == 3)
            if (lst[0][0] != 'C'):
                # Ignore "CC-Assignees".
                name = Ownership.purifyName(lst[1])
                bugId = lst[-1][:-1]
                if not (bugId in self.issueDict):
                    # issue was not fixed
                    continue
                # All humans must have been introduced previously.
                assert (name in self.humanDict)
                layer = 'issueReporter'
                col = 5
                if lst[0][0] == 'A':
                    layer = 'issueAssignee'
                    col = 6
                else:
                    assert lst[0][0] == 'R'
                    self.humanDict[name].isReporter = True
                L = Settings.getLayer2(layer, 'issue')
                self.addEdge(self.humanDict[name].index, L, self.issueDict[bugId], L, col)
            else:
                uname = lst[1]
                if uname in self.nameOfUsername:
                    name = self.nameOfUsername[uname]
                    # ToDo add CCassignee edges
        issueEdgesFile.close()
        return self.nrIssues

    def readIssues(self):
        # Each line of file contains issue data in format:
        # bugID/\version/\creation_ts/\delta_ts/\status/\resolution.
        issueFile = open("Data\\BugDetails.txt")
        while True:
            crtLine = issueFile.readline()
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            assert(len(lst) == 6)
            dateTime = lst[2].split(' ', 1)
            dateTime[1] = dateTime[1].replace(' ', '')
            assert len(dateTime) == 2
            lst[2] = Ownership.getTime(dateTime[0], dateTime[1])
            dateTime = lst[3].split(' ', 1)
            dateTime[1] = dateTime[1].replace(' ', '')
            lst[3] = Ownership.getTime(dateTime[0], dateTime[1])
            assert len(dateTime) == 2

            lst[5] = lst[5][:-1]  # ignore '\n'
            issue = Issue.Issue(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], self.projectList[self.projectID])

            if issue.getType() == self.issueType and (lst[5] == 'FIXED' or lst[5] == 'WORKSFORME'):
                if not (issue.name in self.issueDict):
                    self.addIssue(issue)
                    issue.setIndex(self.nrIssues)
                    self.i_R[self.nrNodes] = {}
                # only fixed issues must be added =>
            # if ("CLOSED" in status_i) or ("RESOLVED" in status_i) or ("VERIFIED" in status_i) or ("FIXED" in status_i):

        issueFile.close()


    def readIssueComments(self):
        # comments to Bugs:
        issueFile = open("Data\\comments2020.txt")
        while True:
            crtLine = issueFile.readline()
            if not crtLine:
                break
            bug = crtLine[:-1]
            crtLine = issueFile.readline()
            while crtLine and crtLine != 'EOB1\n':
                # Format of comments of type 1 ['who']['name']/\\['bug_when']['__text__'].
                lst = crtLine.split('/\\')
                assert(len(lst) == 2)
                if bug in self.issueDict and lst[0] in self.nameOfUsername:
                    self.i_R[self.issueDict[bug]][self.nameOfUsername[lst[0]]] = True
                    # all commenters are issueReporters
                crtLine = issueFile.readline()
            crtLine = issueFile.readline()
            while crtLine and crtLine != 'EOB2\n':
                # Format of comments of type 2 ['Who']/\\['When']/\\['Added']/\\['Removed'].
                lst = crtLine.split('/\\')
                assert(len(lst) == 4)
                if bug in self.issueDict and lst[0] in self.nameOfUsername:
                    # all commenters are issueReporters
                    self.i_R[self.issueDict[bug]][self.nameOfUsername[lst[0]]] = True
                crtLine = issueFile.readline()
        self.addIrEdges()
        issueFile.close()

    def addIssueDependency(self, fName):
        # b_1/\[b_2, ..] <=> b_2 is in b_1's list of "depends_on" in Bugzilla
        f = open(fName, "r")
        while True:
            crtLine = f.readline()[:-1]
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            assert len(lst) == 2
            issueList = lst[1][1:-1].split(', ')
            L = Settings.getLayer2('issue', 'issue')
            if (lst[0] in self.issueDict):
                i1 = self.issueDict[lst[0]]
                for elem in issueList:
                    if elem in self.issueDict:
                        i2 = self.issueDict[elem]
                        self.addEdge(i1, L, i2, L, 15)

    def processReview(self, crtLine):
        reviewId = crtLine[1]
        issueID = crtLine[2][:-1]

        L = Settings.getLayer2('file', 'issue')
        if reviewId in self.reviewDict and issueID in self.issueDict:
            self.addEdge(self.reviewDict[reviewId].nodeVal, 3, self.issueDict[issueID], 4, 17)
            self.fileNodes = self.reviewDict[reviewId].modifiedFiles
            for fileNode in self.fileNodes:
                self.fileIssues[fileNode][self.issueDict[issueID]] = True
                self.addEdge(fileNode, L, self.issueDict[issueID], L, 12)

    def processCommit(self, crtLine):
        commitID = crtLine[1]
        issueID = crtLine[2][:-1]
        L = Settings.getLayer2('file', 'issue')
        if commitID in self.commitDict and issueID in self.issueDict:
            self.fileNodes = self.commitDict[commitID].modifiedFiles
            for fileNode in self.fileNodes:
                # add issueID to the issues of fileNode
                self.fileIssues[fileNode][self.issueDict[issueID]] = True
                self.addEdge(fileNode, L, self.issueDict[issueID], L, 12)

    def readI2CSeeAlso(self):
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
                self.processReview(crtLine)
            elif crtLine[0] == 'CommitEdge':
                self.processCommit(crtLine)
            else:
                print("error")
                exit(0)
        bugEdgeFile.close()

    def readIssue2Change(self):
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
                self.processReview(crtLine)
            else:
                self.processCommit(crtLine)
        rc2BugEdge.close()

    def addIrEdges(self):
        layer = Settings.getLayer2('issueReporter', 'issueReporter')
        for key in self.i_R:
            crtDict = self.i_R[key]
            # i_r1 and i_r2 are 2 distinct reporters of issue i_R.
            for i_r1 in crtDict:
                nod1 = self.humanDict[i_r1].index
                for i_r2 in crtDict:
                    if i_r1 != i_r2:
                        nod2 = self.humanDict[i_r2].index
                        self.addEdge(nod1, layer, nod2, layer, 7)

    def addDepEdgeFromFile(self, f):
        while True:
            crtLine = f.readline()
            if not crtLine:
                break
            lst = crtLine.split()
            if lst[1] in self.fileDict and lst[2] in self.fileDict:
                L = Settings.getLayer2('file', 'file')
                self.addEdge(self.fileDict[lst[1]], L, self.fileDict[lst[2]], L, 1)

    def readOwnershipFile(self):
        # For each modified file in the repository, the format is as follows:
        # fileName/\nrCommits
        # author_name/\self.author_date/\author_timezone/\added/\removed/\complexity
        # Note: author_date = '%Y-%m-%d %H:%M:%S'
        ownershipFile = open("Data\\ownership.txt")
        valuesC = []
        valuesL = []
        self.ownershipDict = {}
        while (True):
            # Read the line with file details, then read nrCommits lines with commit details.
            crtLine = ownershipFile.readline()
            if not crtLine:
                break
            lst = crtLine.split('/\\')
            # Format the file names to contain '.' instead of '/'
            compName = lst[0].replace('/', '.')
            # Remove the file type (i.e "dir.file.java" -> "dir.file").
            compName = compName.rsplit('.', 1)[0]
            if not (compName in self.fileDict):
                # Ignore modified files that are not in the Contribution Network.
                for i in range(int(lst[1])):
                    ownershipFile.readline()
                continue
            obj = Ownership.Ownership(compName)

            for i in range(int(lst[1])):
                nxtLine = ownershipFile.readline().split('/\\')
                lineLen = len(nxtLine)
                if lineLen == 0:
                    continue
                obj.addModif(Ownership.getModifFromLine(nxtLine))

            allCommitters = obj.authorDex[0]
            L = Settings.getLayer2('committer', 'committer')
            A = Settings.getLayer2('committer', 'author')
            nrChangedLines = 0
            if self.fileDict[obj.name] in self.posInFiles:
                nrChangedLines = obj.sumAdd[0] + obj.sumRem[0]

            for c1 in allCommitters:
                cp = (100 * obj.authorDex[0][c1].nrCommits / obj.nrCommits[0])
                # Add only minor edges. Change to cp > 50 for only major edges.
                if cp <= 50:
                    self.addEdge(self.humanDict[c1].index, 1, self.fileDict[obj.name], 1, 14)
                valuesC.append(cp)
                if nrChangedLines != 0:
                    c1ChangedLines = obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem
                    assert (c1ChangedLines <= nrChangedLines)
                    if c1ChangedLines == nrChangedLines:
                        lp = 100
                    else:
                        lp = (100 * (obj.authorDex[0][c1].sumAdd + obj.authorDex[0][c1].sumRem) / nrChangedLines)
                    valuesL.append(lp)
                for c2 in allCommitters:
                    if c1 != c2:
                        if self.humanDict[c1].isRole[0] and self.humanDict[c2].isRole[0]:
                            # Add committer to committer edge.
                            self.addEdge(self.humanDict[c1].index, L, self.humanDict[c2].index, L, 13)
                        elif self.humanDict[c2].isRole[0] or self.humanDict[c1].isRole[0]:
                            # Add committer to author edge.
                            self.addEdge(self.humanDict[c1].index, L, self.humanDict[c2].index, A, 2)

            # Tuple(name, nrCommits) for obj file where name is the name of the committer with
            # the highest number of the commits to obj.
            ownershipTuple = obj.nrCommitsOwner(0)
            self.ownershipDict[self.fileDict[obj.name]] = (ownershipTuple[0], obj.nrCommitsPercentage(0))

        ownershipFile.close()

    def readDataForHumans(self):
        humanRolesFiles = self.getHumanRolesFiles()
        self.readCommits(humanRolesFiles[0])
        for fileId in range(1, self.nrHumanSubRoles):
            self.readHumanRoleFile(humanRolesFiles[fileId], fileId)
        self.readNameUsername()
        self.readReviewComments()
        self.readReviews()

    def readAndUpdateDataForIssues(self):
        self.readIssues()
        self.readIssueEdges()
        self.readIssue2Change()
        self.readI2CSeeAlso()
        self.readIssueComments()
        self.addIssueDependency("Data\\BugDep.txt")

    def readDataForFiles(self):
        # File dependencies files
        depFile = []
        depFile.append(open("Data\\FileDep.txt", "r"))
        depFile.append(open("Data\\ClassDep.txt", "r"))
        for fileId in range(len(depFile)):
            self.addDepEdgeFromFile(depFile[fileId])
            depFile[fileId].close()
        self.files, self.posInFiles = File.readFileMeasures(self.fileDict, "Data\\codeMeasures2020.txt")

    def readAndUpdateDataForOwnership(self):
        self.ownershipDict = {}
        self.readOwnershipFile()

    def getSNAMeasure(self, name):
        if name == 'Betweenness Centrality':
            return betweenness_centrality(self.ownershipGraph)
        if name == 'Closeness Centrality':
            return closeness_centrality(self.ownershipGraph)
        if name == 'Degree Centrality':
            return degree_centrality(self.ownershipGraph)
        if name == 'Effective Size':
            return self.monoplex.computeEffectiveSizeFormula()
        if name == 'Constraint':
            return self.monoplex.computeConstraint()
        if name == 'Reachability':
            return self.monoplex.computeReachability()

    def getSNAResult(self, name):
        fileValues = []
        self.nrIssuesList = []
        values = self.getSNAMeasure(name)

        for fileN in self.fileDict:
            nod = self.fileDict[fileN]
            if not (nod in self.Nodes):
                #Ignore deleted files.
                continue
            self.nrIssuesList.append(len(self.fileIssues[nod]))
            fileValues.append(values[nod])
        w, p = spearmanr(fileValues, self.nrIssuesList)
        print(name, w, p)

    def createMonoplex(self, edgeList):
        self.ownershipGraph = networkx.DiGraph()
        for e in edgeList:
            if edgeList[e] > 0 and (e.color == 1 or e.color == 14):
                self.ownershipGraph.add_edge(e.nod1, e.nod2, w=edgeList[e])
        self.Nodes = list(self.ownershipGraph.nodes)
        self.monoplex = SNAMeasures.Monoplex(self.ownershipGraph, True, "w")

    def getResultsFromSNAMeasures(self, measures):
        for measure in measures:
            self.getSNAResult(measure)

    # Measures: ['Degree Centrality', 'Betweenness Centrality', 'Closeness Centrality',
    # 'Reachability', 'Effective Size', 'Constraint']

network = ContributionNetwork(8)
network.readDataForHumans()
network.readDataForFiles()
network.readReviewComments()
network.readReviews()
network.readAndUpdateDataForIssues()
network.readOwnershipFile()

network.createMonoplex(Edge.getEdgeSample(Edge.filterEdges(network.Edges, [1, 14]), 10))
network.getResultsFromSNAMeasures(['Degree Centrality', 'Betweenness Centrality', 'Closeness Centrality',
                                   'Reachability', 'Effective Size', 'Constraint'])
