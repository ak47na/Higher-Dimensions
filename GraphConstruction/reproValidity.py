import mailID
import parameters

from datetime import datetime
from networkx import *
from scipy.stats import spearmanr
from math import *
# Note: t0 < t1 <=> t0 happened before t1

'''
    Updates the minimum and maximum number of seconds with t.
'''
def updateTimeBorders(minTime, maxTime, t):
    minTime = min(minTime, t)
    maxTime = max(maxTime, t)
    return minTime, maxTime

'''
    Reads the message details from file and updates the messages dictionary to store for each 
    message key, the email of the sender and the date of the message as a tuple.
'''
def readMsgDetails(filePath):
    msgDict = {}
    # read the file with the details of all messages in format :
    # msgKey/\senderName/\senderEmail/\date(%Y-%m-%d %H:%M:%S)
    detailsFile = open(filePath, "r")
    # Initialise time borders.
    minTime = datetime.now().timestamp()
    maxTime = 0
    while True:
        crtLine = detailsFile.readline()
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '')
        # msgKey/\name/\email/\date
        lst = crtLine.split('/\\')
        assert len(lst) == 4
        # increment the number of messages
        # nrM += 1
        msgEmail = mailID.purifyEmail(lst[2].replace(' ', ''))
        msgDate = datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        # store the message with key lst[0]
        msgDict[lst[0]] = (msgEmail, msgDate)
        minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
    detailsFile.close()
    return minTime, maxTime, msgDict

'''
    Method that creates all information flow networks such that the number of seconds for each 
    network is delta_t.
'''
import correlationValidity
def createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = correlationValidity.OrderInfoFlowNetwork(msgDict, delta_t, t, minTime)
    msgEdgesFilePath = "Data\\msgEdges.txt"
    nrNodes = infoFlowNetwork.readMsgEdges(0, msgEdgesFilePath)
    return infoFlowNetwork

import advMultilayeredNetwork
def createAdvInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = advMultilayeredNetwork.AdvMultilayeredNetwork(msgDict, delta_t, t, minTime)
    msgEdgesFilePath = "Data\\msgEdges.txt"
    nrNodes = infoFlowNetwork.readMsgEdges(0, msgEdgesFilePath)
    return infoFlowNetwork
'''
    Method that computes the number of transitive faults and the Spearman correlation of
    the 2-path rankings between the (aggregate) network with transitive faults and the one without.
'''
def getValues(t, delta_t, minTime, maxTime, msgDict, netwType):
    infoFlowNetwork = createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
    infoFlowNetwork.getTransitiveFault(netwType)
    # print(nrNodes, infoFlowNetwork.nrEdges)
    if netwType == 'monoplex':
        infoFlowNetwork.getRanginkCorrelationAggregate()
        print("The number of edges is ", infoFlowNetwork.nrEdges)
        return infoFlowNetwork.crtResult[netwType], len(infoFlowNetwork.crossLayerEdges)
    else:
        print("The MLN network for ", t, " has ", infoFlowNetwork.getMLNEdgeCount(), " edges")
        print("The monoplex network for ", t, " has ", infoFlowNetwork.getEdgeCount(), " edges")
        return infoFlowNetwork.crtResult[netwType]

def getSpecialCases(t, delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = createAdvInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
    infoFlowNetwork.countSpCases()
    # print('Count of special cases for MLN with delta_t ', t)
    # for i in range(5):
    #     print('Case', i, infoFlowNetwork.case[i])
    return infoFlowNetwork




