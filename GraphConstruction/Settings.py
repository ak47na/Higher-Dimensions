from datetime import datetime
from datetime import timedelta
import datetime as dt

projectID = 0
networkType = "Major"
issueType = "post-release"
projectName = 'jdt'
timeInterval = timedelta(hours = 1)
measureCorrelation = {}
reproMeasureCorrelation = {}
measureNames = ['Degree Centrality', 'Closeness Centrality', 'Betweenness Centrality', 'Reachability', 'Effective Size']


def dissimilarity(actual, expected):
    diff = abs(actual - expected)
    return (diff / expected) * 100

def setNetworkType(networkType_):
    global networkType
    networkType = networkType_

def setIssueType(issueType_):
    global issueType
    issueType = issueType_

def initMeasureCorrelation():
    for measure in measureNames:
        measureCorrelation[measure] = {}
        reproMeasureCorrelation[measure] = {}
        for Itype in ['pre-release', 'post-release']:
            measureCorrelation[measure][Itype] = {}
            reproMeasureCorrelation[measure][Itype] = {}
            for Ntype in ['Minor', 'Major']:
                measureCorrelation[measure][Itype][Ntype] = {}
                reproMeasureCorrelation[measure][Itype][Ntype] = {}

def getReproMeasureCorrelation():
    return reproMeasureCorrelation
def getMeasureNames():
    return measureNames

def getMeasureCorrelation(measureName):
    return measureCorrelation[measureName][issueType][networkType]
def getMeasureCorrelation(measureName, networkType_):
    return measureCorrelation[measureName][issueType][networkType_]
def getMeasureCorrelation(measureName, issueType_, networkType_):
    return measureCorrelation[measureName][issueType_][networkType_]

def getPastPaperResult():
    initMeasureCorrelation()
    measureCorrelation['Degree Centrality']['pre-release']['Minor'] = (0.861, 0.931)
    measureCorrelation['Degree Centrality']['pre-release']['Major'] = (0.909, 0.797)
    measureCorrelation['Degree Centrality']['post-release']['Minor'] = (0.668, 0.269)
    measureCorrelation['Degree Centrality']['post-release']['Major'] = (0.599, 0.319)

    measureCorrelation['Closeness Centrality']['pre-release']['Minor'] = (0.624, 0.737)
    measureCorrelation['Closeness Centrality']['pre-release']['Major'] = (-0.098, 0.167)
    measureCorrelation['Closeness Centrality']['post-release']['Minor'] = (0.602, 0.130)
    measureCorrelation['Closeness Centrality']['post-release']['Major'] = (0.107, 0.013)

    measureCorrelation['Reachability']['pre-release']['Minor'] = (0.647, 0.747)
    measureCorrelation['Reachability']['pre-release']['Major'] = (-0.091, 0.176)
    measureCorrelation['Reachability']['post-release']['Minor'] = (0.618, 0.135)
    measureCorrelation['Reachability']['post-release']['Major'] = (0.199, 0.018)

    measureCorrelation['Betweenness Centrality']['pre-release']['Minor'] = (0.703, 0.748)
    measureCorrelation['Betweenness Centrality']['pre-release']['Major'] = (0.146, 0.285)
    measureCorrelation['Betweenness Centrality']['post-release']['Minor'] = (0.601 , 0.289)
    measureCorrelation['Betweenness Centrality']['post-release']['Major'] = (0.132 , 0.154)

    measureCorrelation['Effective Size']['pre-release']['Minor'] = (0.775, 0.884)
    measureCorrelation['Effective Size']['pre-release']['Major'] = (0.311, 0.391)
    measureCorrelation['Effective Size']['post-release']['Minor'] = (0.649 , 0.223)
    measureCorrelation['Effective Size']['post-release']['Major'] = (0.286 , 0.196)

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

def getPaper7TwoPathCorrelations():
    results = {}
    oneDay = 3600 * 24
    results[oneDay] = [(0.67, 0.01), (0.52, 0.22), (0.74, 0.01)]
    results[oneDay * 5] = [(0.71, 0.01), (0.63, 0.01), (0.77, 0.0001)]
    results[oneDay * 365] = [(0.82, 0.0001), (0.73, 0.0001), (0.86, 0.0001)]
    return results

def getPaper7UpperLowerTransitiveFaultRate():
    results = {}
    oneHour = 3600
    oneDay = oneHour * 24
    results[oneHour] = [(0.48, 0.55), (0.38, 0.43), (0.45, 0.52)]
    results[oneDay] = [(0.43, 0.55), (0.41, 0.53), (0.44, 0.55)]
    results[oneDay * 30] = [(0.21, 0.50), (0.38, 0.51), (0.27, 0.51)]
    results[oneDay * 365] = [(0.11, 0.49), (0.37, 0.50), (0.17, 0.50)]
    results[oneDay * 365 * 20] = [(0.15, 0.50), (0.41, 0.51), (0.17, 0.51)]
    return results