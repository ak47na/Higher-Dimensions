import reproValidity
import mailID
import Settings
import plotly.graph_objects as go

# the number of seconds in a year
Y = 3600 * 24 * 365

timeInt = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
           ('30 days', 3600 * 24 * 30), ('1 year', Y), ('2 years', Y * 2),
           ('5 years', Y * 5), ('10 years', Y * 10), ('20 years', Y * 20)]
timeIntWithResults = [('1 hour', 3600), ('1 day', 3600 * 24), ('5 days', 3600 * 24 * 5),
                      ('30 days', 3600 * 24 * 30), ('1 year', Y), ('5 years', Y * 5)]

mailID.fullInit()

msgDetailsFilePath = 'D:\AKwork2020-2021\Higher-Dimensions\ApacheData\\apacheMsgDetails.txt'
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
        crtResult = monoplexNetwork.crtResult['monoplex']
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

paperProjects = ['Apache', 'MySQL', 'Perl']

t1Times = []
t1Rows = [[] for k in range(7)]


t2Times = []
t2Rows = [[[] for i in range(6)], [[] for j in range(6)]]

runResults()

plotTable1(t1Times, t1Rows)
plotTable2(t2Times, t2Rows)
