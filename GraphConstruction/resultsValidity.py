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
        t2 = go.Figure(data=[go.Table(header=dict(values=t2ColumnNames),
                                      cells=dict(values=t2Data))
                             ])
        t2.show()

def plotTFComparisonTable(tTimes, tRows):
    columnNames = ['time interval', 'TF@B / All TF', 'MLN:TF@B@CLD / ALL TF', '#edges@B', '#edges @B@CLD']
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


def runResults():
    print('Running results...')
    for (t, delta_t) in timeIntWithResults:
        monoplexNetwork = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'monoplex', False)
        MLNNetwork = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'MLN', False)
        crtResult = monoplexNetwork.crtResult['monoplex']
        tfCountAll1 = monoplexNetwork.getAllTFs()
        tfCountAll2 = MLNNetwork.getAllTFs()
        assert tfCountAll1 == tfCountAll2
        tfRapMonoplex = []
        tfRapMLN = []
        for i in range(2):
            tfRapMonoplex.append(round(monoplexNetwork.tfCount['monoplex'][i] / tfCountAll1[i], 6))
            tfRapMLN.append(round(MLNNetwork.tfCount['MLN'][i] / tfCountAll1[i], 6))
        tCompRows[0].append(tfRapMonoplex)
        tCompRows[1].append(tfRapMLN)
        tCompRows[2].append(monoplexNetwork.getMonoplexEdgeCount())
        tCompRows[3].append(monoplexNetwork.getMLNEdgeCount())
        print(delta_t)

        if (delta_t in transitiveFaultRate_paperRes):
            projectId = 0
            for projResult in transitiveFaultRate_paperRes[delta_t]:
                t1Times.append(t)
                # Add paper name.
                t1Rows[0].append(paperProjects[projectId])
                #meanRes = getMeanResults(monoplexNetwork)
                meanRes = crtResult[0]
                for i in range(2):
                    # Compare both the optimistic and pessimistic models.
                    t1Rows[1 + i * 3].append(projResult[i])
                    t1Rows[2 + i * 3].append(meanRes[i])
                    t1Rows[3 + i * 3].append(Settings.dissimilarity(meanRes[i], projResult[i]))
                projectId += 1
                #Only check results for first project, i.e. Apache
                break

        if (delta_t in twoPathCorrelations_paperRes):
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
                    t2Rows[i][3].append(crtResult[i + 1][0])
                    t2Rows[i][4].append(crtResult[i + 1][1])
                    # Dissimilarity between paper result and our result.
                    t2Rows[i][5].append(Settings.dissimilarity(crtResult[i + 1][0], projResult[0]))
                projectId += 1
                #Only check for first project, i.e Apache
                break

paperProjects = ['Apache', 'MySQL', 'Perl']
print('Running')
t1Times = []
t1Rows = [[] for k in range(7)]
tCompRows = [[] for k in range(4)]

t2Times = []
t2Rows = [[[] for i in range(6)], [[] for j in range(6)]]
if __name__ == "__main__":
    runResults()
    plotTFComparisonTable(t1Times, tCompRows)
    # plotTable1(t1Times, t1Rows)
    # plotTable2(t2Times, t2Rows)
