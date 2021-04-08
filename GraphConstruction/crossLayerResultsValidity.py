from math import trunc

import reproValidity
import mailID
import matplotlib.pyplot as plt

# the number of seconds in a year
Y = 3600 * 24 * 365
LIM = 1000000000

mailID.cachedInit()
msgDetailsFilePath = "Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

def plotGraphForRelevantCLE(startTimeSec, endTimeSec, step):
    cleCount = []
    deltaT = []
    minCLE = LIM
    maxCLE = 0
    for delta_t in range(startTimeSec, endTimeSec, step):
        t = str(delta_t) + 'seconds'
        infoFlowNetwork = reproValidity.createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
        edgesCount = infoFlowNetwork.getMLNEdgeCount()
        crossLayerEdgesCount = edgesCount[1]
        cleCount.append(crossLayerEdgesCount)
        deltaT.append(delta_t)
        minCLE = min(minCLE, crossLayerEdgesCount)
        maxCLE = max(maxCLE, crossLayerEdgesCount)
        print("The number of relevant cross-layer edges for ", delta_t, "is ", crossLayerEdgesCount)

    plt.plot(deltaT, cleCount, 'ro')
    plt.axis([startTimeSec, endTimeSec, minCLE, maxCLE])
    plt.xlabel('number of seconds')
    plt.ylabel('number of cross-layer edges')
    fileName = 'R_CLE_Count' + str(step) + '.png'
    plt.savefig('D:\AKwork2020-2021\Higher-Dimensions\CLE Visualizations\RelevantCLECount_Plots\\' + fileName)
    plt.show()

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
        print("The number of cross-layer edges for ", delta_t, "is ", crossLayerEdgesCount)

    plt.plot(deltaT, cleCount, 'ro')
    plt.axis([startTimeSec, endTimeSec, minCLE, maxCLE])
    plt.xlabel('number of seconds')
    plt.ylabel('number of cross-layer edges')
    fileName = 'CLE_Count' + str(step) + '.png'
    plt.savefig('D:\AKwork2020-2021\Higher-Dimensions\CLE Visualizations\CLECount_Plots\\' + fileName)
    plt.show()

def plotCLEGraphs():
    plotGraph(60, 3600 * 24, 10)
    plotGraph(3600 * 24, 3600 * 30 * 24, 3600)
    plotGraph(3600 * 30 * 24, Y, 3600 * 24)
    plotGraph(Y, Y * 10, 3600 * 24 * 30)
    plotGraph(Y * 10, Y * 20, 3600 * 24 * 30 * 2)

def plotRelevantCLEGraphs():
    plotGraphForRelevantCLE(60, 3600 * 24, 10)
    plotGraphForRelevantCLE(3600 * 24, 3600 * 30 * 24, 3600)
    plotGraphForRelevantCLE(3600 * 30 * 24, Y, 3600 * 24)
    plotGraphForRelevantCLE(Y, Y * 10, 3600 * 24 * 30)
    plotGraphForRelevantCLE(Y * 10, Y * 20, 3600 * 24 * 30 * 2)

def createHistogramForTime(t, timeDist):
    for i, binsCount in enumerate([25, 50, 75, 100]):
        # Set up the plot
        ax = plt.subplot(2, 2, i + 1)
        # Draw the plot
        ax.hist(timeDist, bins=binsCount,
                color='blue', edgecolor='black')
        # Title and labels
        ax.set_title('Histogram for ' + t +' with BinCount = %d' % binsCount, size=6)
        ax.set_xlabel('Time (seconds)', size=10)
        ax.set_ylabel('CLE', size=10)

    plt.tight_layout()
    plt.show()

def createBasicHistogramForTime(t, timeDist):
    plt.hist(timeDist,
            color='blue', edgecolor='black')
    plt.title('Histogram for ' + t, size=10)
    plt.xlabel('Time (seconds)', size=10)
    plt.ylabel('CLE', size=10)
    plt.tight_layout()
    plt.show()

def createBasicHistogramForLayer(t, layerDist):
    plt.hist(layerDist,
            color='blue', edgecolor='black')
    plt.title('Histogram for ' + t, size=10)
    plt.xlabel('Layer distance', size=10)
    plt.ylabel('CLE', size=10)
    plt.tight_layout()
    plt.show()

def creteHistogramsWithDistanceForCLE():
    times = [3600, 3600 * 24, 3600 * 24 * 30, Y, Y * 2, Y * 3]
    for delta_t in times:
        t = str(delta_t) + 'seconds'
        infoFlowNetwork = reproValidity.createInfoFlowNetwork(t, delta_t, minTime, maxTime, msgDict)
        crossLayerEdges = infoFlowNetwork.crossLayerEdges
        timeDist = []
        layerDist = []
        for edge in crossLayerEdges:
            if delta_t == 3600:
                print(delta_t, edge)
            timeDist.append(edge[0][1] - edge[1][1])
            t1 = trunc((edge[0][1] - minTime) / delta_t)
            t2 = trunc((edge[1][1] - minTime) / delta_t)
            assert t1 < t2
            layerDist.append(t2 - t1)
        #createBasicHistogramForTime(t, timeDist)
        #createHistogramForTime(t, timeDist)
        createBasicHistogramForLayer(t, layerDist)

#creteHistogramsWithDistanceForCLE()
#plotCLEGraphs()
plotRelevantCLEGraphs()