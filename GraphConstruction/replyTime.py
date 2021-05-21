import reproValidity
import mailID
import parameters
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def getInfoFlowNetwork(t, delta_t):
    parameters.setLayerDistance(1)
    mailID.cachedInit()
    msgDetailsFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgDetails.txt'
    # "Data\\msgDetails.txt"
    # Create the dictionary of messages and get the min,max times of messages.
    minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)
    monoplexNetwork = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'monoplex', False)
    return monoplexNetwork

def getTimeBetweenMsgs(msgDict, u, v):
    return abs(msgDict[u][1].timestamp() - msgDict[v][1].timestamp()) / (3600)

def getReplyTimesFromMsgEdges(filePath, msgDict):
    errors = 0
    invalidMsg = {}
    # file with each line containing two string numbers u v representing that message with key u is
    # a reply to message with key v.
    edgeFile = open(filePath, "r")
    replyTimes = []
    while True:
        crtLine = edgeFile.readline()
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '')
        if (not '/\\' in crtLine):
            lst = crtLine.split()
        else:
            lst = crtLine.split('/\\')

        assert len(lst) == 2
        if not (lst[0] in msgDict) and not (lst[0] in invalidMsg):
            invalidMsg[lst[0]] = True
            errors += 1
        if not (lst[1] in msgDict) and not (lst[1] in invalidMsg):
            invalidMsg[lst[1]] = True
            errors += 1
        if (lst[0] in msgDict) and (lst[1] in msgDict):
            replyTimes.append(getTimeBetweenMsgs(msgDict, lst[1], lst[0]))
    edgeFile.close()
    assert errors == 0
    return replyTimes

def compReplyTimesHist(replyTimes, filePath, x):
    binWidth = 2.5
    binVals = [0]
    for i in range(40):
        binVals.append(binWidth + binVals[-1])

    plt.hist(replyTimes, bins=binVals,
             color='blue', edgecolor='black')
    plt.title('Histogram for Apache ', size=3)
    plt.xlabel('Time(hours)', size=3)

    # if x < 15:
    #     countVals = x
    # countVals = 10
    # for i in range(countVals + 1):
    #     vals.append(round((i / countVals) * x, 2))
    vals = []
    for i in range(0, 21):
        vals.append(round(binVals[i * 2]))
    plt.xticks(vals, vals)
    plt.ylabel('count', size=10)
    plt.tight_layout()
    #plt.show()
    plt.savefig(filePath)
    plt.close()

def compReplyTimesHists(replyTimes):
    for i, binsCount in enumerate([50, 75, 100, 125]):
        # Set up the plot
        ax = plt.subplot(2, 2, i + 1)
        # Draw the plot
        ax.hist(replyTimes, bins=binsCount,
                color='blue', edgecolor='black')
        # Title and labels
        ax.set_title('Reply time hist with BinCount = %d' % binsCount, size=6)
        ax.set_xlabel('Time(seconds)', size=10)
        ax.set_ylabel('count', size=10)

    plt.tight_layout()
    plt.show()

def getSmallerThanXReplyTimes(replyTimes, x):
    res = []
    for t in replyTimes:
        if t < x:
            res.append(t)
    return res

def getIQR(arr):
    n = len(arr)
    n4 = n // 4
    Q1 = 0
    Q3 = 0
    if n % 4 == 0:
        Q1 = 0.5 * (arr[n4 - 1] + arr[n4])
        Q3 = 0.5 * (arr[n - n4] + arr[n - n4 - 1])
    else:
        Q1 = arr[n4]
        Q3 = arr[n - n4 - 1]
    return Q1, Q3, Q3 - Q1

def getMeanAndStdev(arr):
    n = len(arr)
    mean = sum(arr) / n
    var = 0
    for x in arr:
        var += (x - mean) ** 2
    var /= n
    stdev = math.sqrt(var)
    return mean, stdev

def getStats(arr):
    arr = sorted(arr)
    mean, stdev = getMeanAndStdev(arr)
    Q1, Q3, iqr = getIQR(arr)
    print(mean, stdev, Q1, Q3, iqr)
    print(getPropFromFirstXH(arr, mean + stdev), getPropFromFirstXH(arr, mean + iqr))
    return mean + iqr

def getPropFromFirstXH(arr, x):
    n = len(arr)
    cntSmaller = 0
    for i in arr:
        if i <= x:
            cntSmaller += 1
    return (cntSmaller / n) * 100

def plotCDF(data):
    x = np.sort(data)
    # get the cdf values of y
    maxVal = data[-1]
    x = x / float(maxVal)
    x = x * 100
    y = (np.arange(0, maxVal, 0.3434) / float(maxVal)) * 100
    y = y[0:len(data)]
    filePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\CDF.png'
    # plotting
    plt.xlabel('Percentage of (reply-sent) times')
    plt.ylabel('Percentage of messages')
    plt.plot(x, y)
    plt.savefig(filePath)

mailID.cachedInit()
msgDetailsFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgDetails.txt'#"Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

msgEdgesFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgEdges.txt'#"Data\\msgEdges.txt"

replyTimes = sorted(getReplyTimesFromMsgEdges(msgEdgesFilePath, msgDict))
monoplexNetwork = getInfoFlowNetwork('1 hour', 3600)
assert replyTimes == sorted(monoplexNetwork.allReplyTimes)
meanIQR = getStats(replyTimes)
N = len(replyTimes)
randIDx = random.sample(range(0, N), 100)
randReplT = []
print('Nr msg', N)
for i in randIDx:
    randReplT.append(replyTimes[i])

filePathTemplate = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\FixedBSzReplyTimesHistatMost'
timesList = [10, 20, meanIQR, 30, 40, 50, 60, 100]
firsXHistFilePaths = {}
for t in timesList:
    firsXHistFilePaths[t] = filePathTemplate + str(round(t)) + '.png'

sampleHistFilePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\sample100ReplyTimesHist.png'
for x in range(10, 1 + int(replyTimes[-1]), 10):
    smallRempyTimes = getSmallerThanXReplyTimes(replyTimes, x)
    # if x <= 100 and (x in timesList):
    #     compReplyTimesHist(smallRempyTimes, firsXHistFilePaths[x], x)
    if x <= 60 or x == 100:
        print('Percentage for reply times <= ' + str(x) + ' hours', ((len(smallRempyTimes)) / len(replyTimes)) * 100)


plotCDF(replyTimes)
#compReplyTimesHist(getSmallerThanXReplyTimes(replyTimes, meanIQR), firsXHistFilePaths[meanIQR], meanIQR)
#compReplyTimesHist(randReplT, sampleHistFilePath)
# print(replyTimes)
# compReplyTimesHist(smallRempyTimes, 100)
# compReplyTimesHist(randReplT)