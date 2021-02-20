import reproValidity
import mailID
import parameters
import matplotlib.pyplot as plt

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
        lst = crtLine.split(' ')
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
    return replyTimes

def compReplyTimesHist(replyTimes, x):
    plt.hist(replyTimes,
             color='blue', edgecolor='black', bins=100)
    plt.title('Histogram for Eclipse ', size=10)
    plt.xlabel('Time(hours)', size=10)
    plt.ylabel('count', size=10)
    plt.tight_layout()
    plt.show()
    # plt.savefig('D:\AKwork2020-2021\Higher-Dimensions\\first' + str(x) + 'HReplyTimeHist.png')

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


mailID.init()
msgDetailsFilePath = "Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

msgEdgesFilePath = "Data\\msgEdges.txt"
replyTimes = sorted(getReplyTimesFromMsgEdges(msgEdgesFilePath, msgDict))

for x in range(100, 1 + int(replyTimes[-1]), 100):
    smallRempyTimes = getSmallerThanXReplyTimes(replyTimes, x)
    print(((len(replyTimes) - len(smallRempyTimes)) / len(replyTimes)) * 100)
# compReplyTimesHist(replyTimes)
# compReplyTimesHist(smallRempyTimes, 100)