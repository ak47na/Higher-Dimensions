from datetime import datetime
from datetime import timedelta
import datetime as dt

projectID = 0
networkType = "Major"
issueType = "post-release"
projectName = 'jdt'
timeInterval = timedelta(hours = 1)

def getProjectList():
    return ['JDT', 'Platform']
def getProjectID():
    return projectID
def getProjectName():
    return projectName
def getTimeInterval():
    return timeInterval

#'jdt/eclipse.jdt.core'
def getIssueType():
    return issueType
def getNetworkType():
    return networkType
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
