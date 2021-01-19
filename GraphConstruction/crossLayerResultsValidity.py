import reproValidity
import mailID
import matplotlib.pyplot as plt

# the number of seconds in a year
Y = 3600 * 24 * 365
LIM = 1000000000

mailID.init()
msgDetailsFilePath = "Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

def plotGraph(startTimeSec, endTimeSec, step):
    cleCount = []
    deltaT = []
    minCLE = LIM
    maxCLE = 0

    for delta_t in range(startTimeSec,endTimeSec, step):
        t = str(delta_t) + 'seconds'
        infoFlowNetwork = reproValidity.createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
        crossLayerEdgesCount = len(infoFlowNetwork.crossLayerEdges)
        cleCount.append(crossLayerEdgesCount)
        deltaT.append(delta_t)
        minCLE = min(minCLE, crossLayerEdgesCount)
        maxCLE = max(maxCLE, crossLayerEdgesCount)
        #print("The number of cross-layer edge for ", delta_t, "is ", crossLayerEdgesCount)

    plt.plot(deltaT, cleCount, 'ro')
    plt.axis([startTimeSec, endTimeSec, minCLE, maxCLE])
    plt.xlabel('number of seconds')
    plt.ylabel('number of cross-layer edges')
    plt.show()

plotGraph(60, 3600 * 24, 10)
plotGraph(3600 * 24, 3600 * 30 * 24, 3600)
plotGraph(3600 * 30 * 24, Y, 3600 * 24)
plotGraph(Y, Y * 10, 3600 * 24 * 30)
plotGraph(Y * 10, Y * 20, 3600 * 24 * 30 * 2)