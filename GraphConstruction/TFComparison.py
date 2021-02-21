import reproValidity
import mailID
import Settings
import parameters
import constants
import plotly.graph_objects as go

# the number of seconds in a year
Y = 3600 * 24 * 365

# timeInt = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
#            ('30 days', 3600 * 24 * 30), ('1 year', Y), ('2 years', Y * 2),
#            ('5 years', Y * 5), ('10 years', Y * 10), ('20 years', Y * 20)]
timeIntWithResults = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
                      ('30 days', 3600 * 24 * 30), ('1 year', Y), ('2 years', 2 * Y),
                      ('5 years', 5 * Y), ('10 years', 10 * Y), ('20 years', Y * 20)]

def addOPResult(tRows, indexes, res):
    i = 0
    for idx in indexes:
        tRows[idx].append(round(res[i], 4))
        i += 1
    return tRows

def dataSetUp():
    mailID.init()
    msgDetailsFilePath = "Data\\msgDetails.txt"
    return reproValidity.readMsgDetails(msgDetailsFilePath)


def plotTable(tTimes, tRows):
    tData = [tTimes]
    tColumnNames = ['time interval', 'TF_O under Bird', 'TF_P under Bird', '#edges',
                    'TF_O under adjacent', 'TF_P under adjacent', 'P gain', '#edges', 'edge % addition',
                     'TF_O under hist', 'TF_P under hist', 'P gain', '#edges',
                    'edge % addition']
    for col in tRows:
        tData.append(col)
    t = go.Figure(data=[go.Table(header=dict(values=tColumnNames),
                                 cells=dict(values=tData))
                        ])
    t.show()

def getResults():
    # tCorrRows = [[] for x in range(4)]
    tRows = [[] for x in range(13)]
    t1Times = []
    for (t, delta_t) in timeIntWithResults:
        t1Times.append(t)
        # Create the 3 networks
        parameters.setLayerDistance(1)
        adjMLN = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'MLN', False)
        parameters.setLayerDistance(1)
        MLN = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'MLN', True)
        parameters.setLayerDistance(1)
        monoplex = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'monoplex', False)
        # Add O/P TF for each network.
        tRows = addOPResult(tRows, [0, 1], monoplex.getTFSum('monoplex'))
        tRows = addOPResult(tRows, [3, 4], adjMLN.getTFSum('MLN'))
        tRows = addOPResult(tRows, [8, 9], MLN.getTFSum('MLN'))
        # Add P gain
        tRows[5].append(round((tRows[4][-1] - tRows[1][-1]) / tRows[1][-1], 4))
        tRows[10].append(round((tRows[9][-1] - tRows[1][-1]) / tRows[1][-1], 4))
        # Add the number of edges used by each network.
        monoplexEdgeCount = monoplex.getMonoplexEdgeCount()
        MLNEdgeCount = MLN.getMLNEdgeCount()
        adjMLNEdgeCount = adjMLN.getMLNEdgeCount()
        tRows[2].append((monoplexEdgeCount, round((monoplexEdgeCount / monoplex.nrEdges) * 100, 4)))
        tRows[6].append((adjMLNEdgeCount[2], round((adjMLNEdgeCount[2] / adjMLN.nrEdges) * 100, 4)))
        tRows[11].append((MLNEdgeCount[2], round((MLNEdgeCount[2] / MLN.nrEdges) * 100, 4)))
        # Add edge gain.
        tRows[7].append(round(tRows[6][-1][0] / tRows[2][-1][0], 4))
        tRows[12].append(round(tRows[11][-1][0] / tRows[2][-1][0], 4))
        assert (monoplex.nrEdges == MLN.nrEdges and MLN.nrEdges == adjMLN.nrEdges)
        assert (monoplexEdgeCount == MLNEdgeCount[0] and MLNEdgeCount[0] == adjMLNEdgeCount[0])

    plotTable(t1Times, tRows)

minTime, maxTime, msgDict = dataSetUp()
getResults()