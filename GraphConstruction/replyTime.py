import reproValidity
import mailID
import parameters
import random
import math
import matplotlib.pyplot as plt
import numpy as np

def getInfoFlowNetwork(tStr, delta_t):
    parameters.setLayerDistance(1)
    mailID.cachedInit()
    msgDetailsFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgDetails.txt'
    # Create the dictionary of messages and get the min,max times of messages.
    minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)
    return reproValidity.getValues(tStr, delta_t, minTime, maxTime, msgDict, 'monoplex', False)

def plotHist(data, pltTitle, xLabel, filePath, **kwargs): # binVals, vals, yvals):
    if not('binVals' in kwargs):
        plt.hist(data, bins=100,
                 color='blue', edgecolor='black')
    else:
        plt.hist(data, bins=kwargs['binVals'],
             color='blue', edgecolor='black')
    plt.title(pltTitle, size=10)
    plt.xlabel(xLabel, size=10)
    if 'vals' in kwargs:
        plt.xticks(kwargs['vals'], kwargs['vals'])
    if 'yvals' in kwargs:
        plt.yticks(kwargs['yvals'], kwargs['yvals'])
    plt.ylabel('count', size=8)
    #plt.ticklabel_format(axis='both', style='plain')
    plt.tight_layout()
    plt.savefig(filePath)
    plt.clf()
def computeBasicHist(replyTimes, filePath):
    plotHist(replyTimes, 'Histogram for Apache ', 'Time(hours)', filePath)

def compReplyTimesHist(replyTimes, filePath):
    binWidth = 2.5
    binVals = [0]
    for i in range(40):
        binVals.append(binWidth + binVals[-1])
    vals = [round(binVals[i * 2]) for i in range(0, 21)]
    plotHist(replyTimes, 'Histogram for Apache ', 'Time(hours)', filePath, binVals=binVals, vals=vals)

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

def getSmallerThanXReplyTimes(replyTimes, X):
    return list(filter(lambda T: T < X, replyTimes))

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
    var = sum(map(lambda x: (x - mean) ** 2, arr)) / n
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
    cntSmaller = len(list(filter(lambda i: i <= x, arr)))
    return (cntSmaller / n) * 100

def plotCDF(data, filePath, xLabel, yLabel):
    x = np.sort(data)
    # get the cdf values of y
    maxVal = data[-1]
    x = (x / float(maxVal)) * 100
    y = (np.arange(0, maxVal, maxVal / len(data)) / float(maxVal)) * 100
    y = y[0:len(data)]
    # plotting
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.ticklabel_format(axis='both', style='plain')
    plt.plot(x, y)
    plt.savefig(filePath)
    plt.clf()

def plot2PathsHist(times2Paths):
    # print('Two paths times***', times2Paths)
    times2Paths[0] = sorted(times2Paths[0])
    times2Paths[1] = sorted(times2Paths[1])

    print('max vals', times2Paths[0][-1])
    filePath = ['D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\hist2PathsBC.png',
                'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\hist2PathsAC.png']

    for idx in range(2):
        for x in range(len(times2Paths[idx])):
            times2Paths[idx][x] /= 3600
        maxVal = max(times2Paths[idx])
        yticks = np.arange(0, maxVal, maxVal / 8)
        plotHist(times2Paths[idx], 'Histogram for Apache ', 'Time(hours)', filePath[idx], yvals=yticks)

def plot2PathsHistOP(times2Paths):
    times2Paths[0] = sorted(times2Paths[0])
    times2Paths[1] = sorted(times2Paths[1])
    print('max vals', times2Paths[0][-1])
    filePath = ['D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\hist2PathsO.png',
                'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\hist2PathsP.png']
    for idx in range(2):
        for x in range(len(times2Paths[idx])):
            times2Paths[idx][x] /= 3600
        maxVal = max(times2Paths[idx])
        yticks = np.arange(0, maxVal, maxVal / 8)
        plotHist(times2Paths[idx], 'Histogram for Apache ', 'Time(hours)', filePath[idx], yvals=yticks)

def readReplyTimes():
    filePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\EnronData\\enronReplies.txt'
    f = open(filePath, 'r')
    data = f.readline().split(', ')
    replyList = []
    for t in data:
        try:
            timeVal = float(t) / 3600
            replyList.append(timeVal)
        except:
            print(t, 'invalid timestamp')
    return replyList

def readOP2PathsTimes():
    filepath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\OP2paths.txt'
    f = open(filepath, 'r')
    parseFloat = lambda floatStr: float(floatStr)
    time2PathsO = f.readline().replace('\n', '').split(', ')
    time2PathsP = f.readline().replace('\n', '').split(', ')
    assert time2PathsO[-1] == ''
    assert time2PathsO[-1] == ''
    time2PathsO = sorted(map(parseFloat, time2PathsO[:-1]))
    time2PathsP = sorted(map(parseFloat, time2PathsP[:-1]))
    return time2PathsO, time2PathsP

def writeOP2PathsTimes(times2Paths):
    filepath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\OP2paths.txt'
    f = open(filepath, 'w')
    for idx in range(2):
        for x in range(len(times2Paths[idx])):
            f.write(str(times2Paths[idx][x]) + ', ')
        f.write('\n')
    f.close()

def plotRandomSample(replyTimes):
    N = len(replyTimes)
    randIDx = random.sample(range(0, N), 100)
    randReplT = []
    print('Nr msg', N)
    for i in randIDx:
        randReplT.append(replyTimes[i])
    sampleHistFilePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\EnronSample100ReplyTimesHist.png'
    compReplyTimesHist(randReplT, sampleHistFilePath)

def plot2PathData(monoplexNetwork):
    correct2Paths = monoplexNetwork.getAllCorrect2Paths()
    op2paths = monoplexNetwork.getOP2Paths_Greedy()
    writeOP2PathsTimes(op2paths)
    plot2PathsHistOP(op2paths)
    plot2PathsHist(correct2Paths)
    plotCDF(sorted(correct2Paths[0]), 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\CDF2P0.png',
            'Percentage of (replyB-replyC) times',
            'Percentage of 2-paths')
    plotCDF(sorted(correct2Paths[1]), 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\CDF2P1.png',
            'Percentage of (messageA-replyC) times',
            'Percentage of 2-paths')

def plotReplyData(allReplyTimes, filePathTemplate, project):
    filePathTemplate = filePathTemplate.replace('project', project)
    meanIQR = getStats(allReplyTimes)
    timesList = [10, 20, meanIQR, 30, 40, 50, 60, 100]
    firsXHistFilePaths = {}
    for t in timesList:
        firsXHistFilePaths[t] = filePathTemplate + str(round(t)) + '.png'
    for xi in range(10, 1 + int(allReplyTimes[-1]), 10):
        smallRempyTimes = getSmallerThanXReplyTimes(allReplyTimes, xi)
        if xi <= 100 and (xi in timesList):
            compReplyTimesHist(smallRempyTimes, firsXHistFilePaths[xi])
        if xi <= 60 or xi == 100:
            print('Percentage for reply times <= ' + str(xi) + ' hours',
                  ((len(smallRempyTimes)) / len(allReplyTimes)) * 100)
    plotCDF(allReplyTimes, 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\CDF_replies.png',
            'Percentage of (reply-sent) times',
            'Percentage of messages')

def getApacheReplyData(monoplexNetwork):
    return sorted(monoplexNetwork.allReplyTimes)

def getEnronRepliesTime():
    return readReplyTimes()

monoplexNetwork = getInfoFlowNetwork('1 hour', 3600)
filePathTemplate = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\project_FixedBSzReplyTimesHistatMost'
plotReplyData(getApacheReplyData(monoplexNetwork), filePathTemplate, 'Apache')
#computeBasicHist(enronRepliesTime, 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\enronHist.png')

# plotCDF(enronRepliesTime, 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\CDF_replies_enron.png',
#         'Percentage of (reply-sent) times',
#         'Percentage of messages')

# compReplyTimesHist(getSmallerThanXReplyTimes(replyTimes, meanIQR), firsXHistFilePaths[meanIQR], meanIQR)
# print(replyTimes)
# compReplyTimesHist(smallRempyTimes, 100)
# compReplyTimesHist(randReplT)
