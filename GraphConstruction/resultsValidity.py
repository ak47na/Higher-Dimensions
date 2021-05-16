import reproValidity
import mailID
import Settings
import plotly.graph_objects as go
import parameters

# the number of seconds in a year
Y = 3600 * 24 * 365

parameters.setLayerDistance(1)

timeInt = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
           ('30 days', 3600 * 24 * 30), ('1 year', Y), ('2 years', Y * 2),
           ('5 years', Y * 5), ('10 years', Y * 10), ('20 years', Y * 20)]
# timeIntWithResults = [('11 years', 11 * Y)]
timeIntWithResults = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
                     ('30 days', 3600 * 24 * 30), ('1 year', Y), ('10 years', Y * 10), ('11 years', 11 * Y)]

mailID.cachedInit()

msgDetailsFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheMsgDetails.txt'
#"Data\\msgDetails.txt"
#Create the dictionary of messages and get the min,max times of messages.
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

transitiveFaultRate_paperRes = Settings.getPaper7UpperLowerTransitiveFaultRate()
twoPathCorrelations_paperRes = Settings.getPaper7TwoPathCorrelations()

def plotTable1(t1Times, t1Rows):
    t1Data = [t1Times]
    t1ColumnNames = ['time interval', 'project', 'TFR lowerbound', 'repro lowerbound', 'dissimilarity',
                     'TFR upperbound',
                     'repro upperbound', 'dissimilarity']
    for col in t1Rows:
        t1Data.append(col)
    t1 = go.Figure(data=[go.Table(header=dict(values=t1ColumnNames),
                                  cells=dict(values=t1Data))
                         ])
    t1.show()

def plotTable2(t2Times, t2Rows):
    t2ColumnNames = ['time interval', 'project', '2path correlation', 'pval', 'repro 2path correlation', 'repro pval',
                     'dissimilarity']
    for i in range(2):
        t2Data = [t2Times]
        for col in t2Rows[i]:
            t2Data.append(col)
        modelType = 'O'
        if i:
            modelType = 'P'
        t2ColumnNames[4] = 'repro 2path@' + modelType + ' correlation'
        t2 = go.Figure(data=[go.Table(header=dict(values=t2ColumnNames),
                                      cells=dict(values=t2Data))
                             ])
        t2.show()

def plotTwoPathVsTF(tTimes, tRows):
    columnNames = ['time interval', '2P@B', '2P@MLN@CLD']

    tData = [tTimes]
    for col in tRows:
        tData.append(col)
    t = go.Figure(data=[go.Table(header=dict(values=columnNames),
                                 cells=dict(values=tData))
                        ])
    t.show()

def plotTFComparisonTable(tTimes, tRows):
    columnNames = ['time interval', 'TF@B_O / All TF_O', 'TF@B_P / All TF_P',
                   'TF@MLN@CLD_O / All TF_O', 'TF@MLN@CLD / All TF_P', '#edges@B', '#edges @MLN@CLD', 'edge addition']
    tData = [tTimes]
    for col in tRows:
        tData.append(col)
    t = go.Figure(data=[go.Table(header=dict(values=columnNames),
                                      cells=dict(values=tData))
                             ])
    t.show()

def getMeanResults(monoplex):
    res = [[], []]
    resSum = [0, 0]

    for netw in range(1, monoplex.nrGraphs + 1):
        for i in range(2):
            crtDiff = monoplex.TFperNetw['monoplex'][netw][i]
            res[i].append(crtDiff)
            resSum[i] += crtDiff
    resSum[0] = round(resSum[0] / monoplex.nrGraphs, 4)
    resSum[1] = round(resSum[1] / monoplex.nrGraphs, 4)
    return resSum

def updateTwoPathTable(monoplexNetwork, MLNNetwork):
    twoPathRows[0].append(len(monoplexNetwork.twoPaths['monoplex']))
    twoPathRows[1].append(len(MLNNetwork.twoPaths['MLN']))

def updateMLNMonoplexCompTable(monoplexNetwork, MLNNetwork):
    tfCountAll = monoplexNetwork.getAllTFs()
    # MLN and monoplex should have the same number of Transitive faults under "ground truth".
    assert tfCountAll == MLNNetwork.getAllTFs()
    tfRapMonoplex = []
    tfRapMLN = []
    for i in range(2):
        tfRapMonoplex.append(round(monoplexNetwork.tfCount['monoplex'][i] / tfCountAll[1], 6))
        tfRapMLN.append(round(MLNNetwork.tfCount['MLN'][i] / tfCountAll[1], 6))
    tCompRows[0].append(tfRapMonoplex[0])
    tCompRows[1].append(tfRapMonoplex[1])
    tCompRows[2].append(tfRapMLN[0])
    tCompRows[3].append(tfRapMLN[1])
    tCompRows[4].append(monoplexNetwork.getMonoplexEdgeCount())
    MLNEdgeCount = MLNNetwork.getMLNEdgeCount()
    tCompRows[5].append(MLNEdgeCount[2])
    tCompRows[6].append(round((MLNEdgeCount[2] - MLNEdgeCount[0]) / MLNEdgeCount[0], 6))

def updateMonoplexCorrTable(t, delta_t, res):
    projectId = 0
    for projResult in twoPathCorrelations_paperRes[delta_t]:
        t2Times.append(t)
        for i in range(2):
            # Add project name.
            t2Rows[i][0].append(paperProjects[projectId])
            # Correlation from paper.
            t2Rows[i][1].append(projResult[0])
            # P-value
            t2Rows[i][2].append(projResult[1])
            t2Rows[i][3].append(res[i + 1][0])
            t2Rows[i][4].append(round(res[i + 1][1], 6))
            # Dissimilarity between paper result and our result.
            t2Rows[i][5].append(Settings.dissimilarity(res[i + 1][0], projResult[0]))
        projectId += 1
        # Only check for first project, i.e Apache
        break
def updateTFRTable(t, delta_t, res):
    projectId = 0
    for projResult in transitiveFaultRate_paperRes[delta_t]:
        t1Times.append(t)
        # Add paper name.
        t1Rows[0].append(paperProjects[projectId])
        for i in range(2):
            # Compare both the optimistic and pessimistic models.
            t1Rows[1 + i * 3].append(projResult[i])
            t1Rows[2 + i * 3].append(round(res[i], 6))
            t1Rows[3 + i * 3].append(Settings.dissimilarity(res[i], projResult[i]))
        projectId += 1
        # Only check results for first project, i.e. Apache
        break

def runResults():
    print('Running results...')
    for (t, delta_t) in timeIntWithResults:
        tTotalTimes.append(t)
        monoplexNetwork = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'monoplex', False)
        MLNNetwork = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'MLN', False)
        monoplexNetwork.getTFRAggregatedBuckets('monoplex')
        updateTwoPathTable(monoplexNetwork, MLNNetwork)
        updateMLNMonoplexCompTable(monoplexNetwork, MLNNetwork)
        if (delta_t in transitiveFaultRate_paperRes):
            res = monoplexNetwork.getTFRWithinAndAccross()
            # res = getMeanResults(monoplexNetwork) # mean upper and lower bounds
            # monoplexNetwork.crtResult['monoplex'][0] # upper and lower bounds
            # res = monoplexNetwork.crtResultAgg['monoplex'] # aggregate 2P&TF upper and lower bounds
            # res = monoplexNetwork.aggregCrtRes #aggregate network upper and lower bounds
            updateTFRTable(t, delta_t, res)
        if (delta_t in twoPathCorrelations_paperRes):
            updateMonoplexCorrTable(t, delta_t, monoplexNetwork.crtResult['monoplex'])

paperProjects = ['Apache', 'MySQL', 'Perl']
print('Running')
t1Times = []
t1Rows = [[] for k1 in range(7)]
tCompRows = [[] for k2 in range(7)]
twoPathRows = [[] for k3 in range(2)]
tTotalTimes = []
t2Times = []
t2Rows = [[[] for i in range(6)], [[] for j in range(6)]]
if __name__ == "__main__":
    runResults()
    plotTwoPathVsTF(tTotalTimes, twoPathRows)
    plotTFComparisonTable(tTotalTimes, tCompRows)
    plotTable1(t1Times, t1Rows)
    plotTable2(t2Times, t2Rows)
