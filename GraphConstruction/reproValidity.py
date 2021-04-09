import mailID
import mailClusters
import parameters
import unicodedata

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
    emptyFullName = open("emptyFullNames.txt", "wb")
    invalidDates =  open("invalidDates.txt", "wb")
    notfoundNames =  open("notFoundNames.txt", "wb")
    notFoundDict = {}
    emptyDict = {}
    msgDict = {}
    # read the file with the details of all messages in format :
    # msgKey/\senderName/\senderEmail/\date(%Y-%m-%d %H:%M:%S)
    detailsFile = open(filePath, "r", encoding='utf8')
    # Initialise time borders.
    minTime = datetime.now().timestamp()
    maxTime = 0
    while True:
        crtLine = detailsFile.readline()
        crtLine = unicodedata.normalize('NFD', crtLine).encode('ascii', 'ignore').decode('ascii')
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '').lower()
        # msgKey/\name/\email/\date
        lst = crtLine.split('/\\')
        # lst[1] = lst[1].split('<')[0]
        # lst[2] = lst[2].split('<')[0]
        assert not ('@' in lst[2])
        assert not ('@' in lst[1])
        # lst[1] = lst[1].split('@')[0]
        if 'MAILER-DAEMON' in lst[2]:
            continue
        assert len(lst) == 4
        # increment the number of messages
        # nrM += 1
        first_i, last_i, full_i = mailClusters.purifyName(lst[1])
        msgEmail = mailClusters.purifyEmail(lst[2].replace(' ', ''))
        if msgEmail == '':
            msgEmail = full_i
        if full_i == '':
            full_i = msgEmail
            if not(msgEmail in emptyDict):
                emptyDict[msgEmail] = True
                emptyFullName.write(full_i.encode("utf-8"))
                emptyFullName.write('\n'.encode("utf-8"))
        try:
            if not '-' in lst[3]:
                lst[3] = str(datetime.fromtimestamp(int(float(lst[3]))))
        except:
            invalidDates.write(lst[3].encode("utf-8"))
            invalidDates.write('\n'.encode("utf-8"))
            continue
        msgDate = datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        # store the message with key lst[0]
        if len(full_i) == 0:
            full_i = msgEmail
        elif len(msgEmail) == 0:
            msgEmail = full_i
        try:
            identity = mailID.getIdentity(msgEmail+full_i)
            msgDict[lst[0]] = (identity, msgDate)
            minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
        except:
            try:
                identity = mailID.getIdentity(msgEmail)
                msgDict[lst[0]] = (identity, msgDate)
                minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
            except:
                try:
                    identity = mailID.getIdentity(full_i)
                    msgDict[lst[0]] = (identity, msgDate)
                    minTime, maxTime = updateTimeBorders(minTime, maxTime, msgDate.timestamp())
                except:
                    msgEmailAndName = msgEmail + full_i + '/\\' + msgEmail + full_i
                    if msgEmailAndName in notFoundDict:
                        continue
                    notFoundDict[msgEmailAndName] = True
                    notfoundNames.write(msgEmailAndName.encode("utf-8"))
                    notfoundNames.write('\n'.encode("utf-8"))


    detailsFile.close()
    emptyFullName.close()
    invalidDates.close()
    notfoundNames.close()
    return minTime, maxTime, msgDict

'''
    Method that creates all information flow networks such that the number of seconds for each 
    network is delta_t.
'''
import correlationValidity
def createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict, useGT = False):
    infoFlowNetwork = correlationValidity.OrderInfoFlowNetwork(msgDict, delta_t, t, minTime, useGT)
    msgEdgesFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgEdges.txt'#"Data\\msgEdges.txt"
    nrNodes = infoFlowNetwork.readMsgEdges(0, msgEdgesFilePath)
    return infoFlowNetwork

import advMultilayeredNetwork
def createAdvInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = advMultilayeredNetwork.AdvMultilayeredNetwork(msgDict, delta_t, t, minTime)
    msgEdgesFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgEdges.txt'#"Data\\msgEdges.txt"
    nrNodes = infoFlowNetwork.readMsgEdges(0, msgEdgesFilePath)
    return infoFlowNetwork
'''
    Method that computes the number of transitive faults and the Spearman correlation of
    the 2-path rankings between the (aggregate) network with transitive faults and the one without.
'''
def getValues(t, delta_t, minTime, maxTime, msgDict, netwType, useGT = False):
    print('Creating network')
    infoFlowNetwork = createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict, useGT)
    # infoFlowNetwork.printNetworkDetails()
    infoFlowNetwork.getTransitiveFault(netwType)
    #infoFlowNetwork.getTFAggregate(netwType)
    #infoFlowNetwork.printNetwork2paths(netwType)
    #infoFlowNetwork.computeUpperLowerAggregateNetwork(netwType)

    #infoFlowNetwork.getRanginkCorrelationAggregate(netwType)
    if netwType == 'MLN':
        print("The MLN network for", t, "has (inLayer, restrCrossLayer, sum)", infoFlowNetwork.getMLNEdgeCount(), " edges")
        print("The MLN network for", t, "has", len(infoFlowNetwork.crossLayerEdges), "cross-layer edges")
    # if netwType == 'MLN':
    #     print("The MLN network for ", t, " has ", infoFlowNetwork.getMLNEdgeCount(), " edges")
    #     print("And it has CLE ", len(infoFlowNetwork.crossLayerEdges))
    # print(nrNodes, infoFlowNetwork.nrEdges)
    if netwType == 'monoplex':
        print("The number of edges is ", infoFlowNetwork.getEdgeCount())
        print('The u and l are ', infoFlowNetwork.crtResult[netwType][0])
    # else:
    #     print("The MLN network for ", t, " has ", infoFlowNetwork.getMLNEdgeCount(), " edges")
    #     print("The monoplex network for ", t, " has ", infoFlowNetwork.getEdgeCount(), " edges")
    return infoFlowNetwork

def getSpecialCases(t, delta_t, minTime, maxTime, msgDict):
    infoFlowNetwork = createAdvInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
    infoFlowNetwork.countSpCases()
    # print('Count of special cases for MLN with delta_t ', t)
    # for i in range(5):
    #     print('Case', i, infoFlowNetwork.case[i])
    return infoFlowNetwork




