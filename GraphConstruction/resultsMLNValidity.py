import reproValidity
import mailID
import Settings
import parameters
import plotly.graph_objects as go

# the number of seconds in a year
Y = 3600 * 24 * 365

# timeInt = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
#            ('30 days', 3600 * 24 * 30), ('1 year', Y), ('2 years', Y * 2),
#            ('5 years', Y * 5), ('10 years', Y * 10), ('20 years', Y * 20)]
timeIntWithResults = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
                      ('30 days', 3600 * 24 * 30), ('1 year', Y), ('2 years', 2 * Y),
                      ('5 years', 5 * Y), ('10 years', 10 * Y), ('20 years', Y * 20)]

t1Times = []

def plotTableOPBounds(t1Times, t1Rows):
    t1Data = [t1Times]
    t1ColumnNames = ['time interval', 'TFR lowerbound for MLN', 'TFR lowerbound',
                     'TFR upperbound for MLN', 'TFR upperbound', 'L/U for MLN', 'L/U for monoplex']
    for col in t1Rows:
        t1Data.append(col)
    t1 = go.Figure(data=[go.Table(header=dict(values=t1ColumnNames),
                                  cells=dict(values=t1Data))
                         ])
    t1.show()

mailID.init()
msgDetailsFilePath = "Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)
t1Rows = [[] for k in range(6)]
parameters.setLayerDistance(1)

# Computes using InfoFlowNetwork class, the upper&lower bounds for the TFR for the MLN and the
# monoplex, and displays a table that compares them.
def getResults():
    for (t, delta_t) in timeIntWithResults:
        t1Times.append(t)
        MLN = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'MLN')
        MLNcrtResult = MLN.crtResult['MLN']
        cleCount = len(MLN.crossLayerEdges)
        t1Rows[0].append(MLNcrtResult[0][0])
        t1Rows[2].append(MLNcrtResult[0][1])
        t1Rows[4].append(MLNcrtResult[0][0] / MLNcrtResult[0][1])
        monoplex = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'monoplex')
        crtResult = monoplex.crtResult['monoplex']
        assert(cleCount == len(monoplex.crossLayerEdges))
        t1Rows[1].append(crtResult[0][0])
        t1Rows[3].append(crtResult[0][1])
        t1Rows[5].append(crtResult[0][0] / crtResult[0][1])
        assert(monoplex.nrGraphs == MLN.nrGraphs)
        # Compare OP bounds for all interval networks for MLN with monoplex.
        diff = [0]
        for netw in range(1, monoplex.nrGraphs + 1):
            diffNetw = []
            for i in range(2):
                diffNetw.append(MLN.TFperNetw['MLN'][netw][i] - monoplex.TFperNetw['monoplex'][netw][i])
            diff.append(diffNetw)
        print('For time ', t, ' and delta_t ', delta_t, ' diff array is ', diff)

    plotTableOPBounds(t1Times, t1Rows)

def plotTableSpcases(t2Times, t2Rows):
    t2Data = [t2Times]
    t2ColumnNames = ['time interval']
    for i in range(5):
        t2ColumnNames.append('case' + str(i) + ' restricted')
        t2ColumnNames.append('case' + str(i))

    for col in t2Rows:
        t2Data.append(col)
    t2 = go.Figure(data=[go.Table(header=dict(values=t2ColumnNames),
                                  cells=dict(values=t2Data))
                         ])
    t2.show()

def getSpCasesCount(id, layerD, t2Rows):
    parameters.setLayerDistance(layerD)
    netw = 0
    for (t, delta_t) in timeIntWithResults:
        flowNetw = reproValidity.getSpecialCases(t, delta_t, minTime, maxTime, msgDict)
        for i in range(5):
            t2Rows[id + i * 2].append(flowNetw.case[i])
        if id == 0:
            t2Times.append(t)

# Counts the number of special cases and display table.
def getSpecialCasesResults():
    getSpCasesCount(0, 1, t2Rows)
    getSpCasesCount(1, 10000000000, t2Rows)
    plotTableSpcases(t2Times, t2Rows)


t2Times = []
t2Rows = [[] for elem in range(11)]
getResults()

