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
                      ('30 days', 3600 * 24 * 30), ('1 year', Y), ('20 years', Y * 20)]

mailID.init()
msgDetailsFilePath = "Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

transitiveFaultRate = Settings.getPaper7UpperLowerTransitiveFaultRate()
twoPathCorrelations = Settings.getPaper7TwoPathCorrelations()

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

paperProjects = ['Apache', 'MySQL', 'Perl']

t1Times = []
t1Rows = [[] for k in range(7)]

t2ColumnNames = ['time interval', 'project', '2path correlation', 'pval', 'repro 2path correlation', 'repro pval', 'dissimilarity']
t2Times = []
t2Rows = [[[] for i in range(6)], [[] for j in range(6)]]

for (t, delta_t) in timeIntWithResults:
    crtResult, crossLayerEdgesCount = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict)
    print("The number of cross-layer edge for ", t, "is ", crossLayerEdgesCount)
    if (delta_t in transitiveFaultRate):
        projectId = 0
        for projResult in transitiveFaultRate[delta_t]:
            t1Times.append(t)
            t1Rows[0].append(paperProjects[projectId])
            for i in range(2):
                t1Rows[1 + i * 3].append(projResult[i])
                t1Rows[2 + i * 3].append(crtResult[0][i])
                t1Rows[3 + i * 3].append(Settings.dissimilarity(crtResult[0][i], projResult[i]))
            projectId += 1

    if (delta_t in twoPathCorrelations):
        projectId = 0
        for projResult in twoPathCorrelations[delta_t]:
            t2Times.append(t)
            for i in range(2):
                t2Rows[i][0].append(paperProjects[projectId])
                t2Rows[i][1].append(projResult[0])
                t2Rows[i][2].append(projResult[1])
                t2Rows[i][3].append(crtResult[i + 1][0])
                t2Rows[i][4].append(crtResult[i + 1][1])
                t2Rows[i][5].append(Settings.dissimilarity(crtResult[i + 1][0], projResult[0]))
            projectId += 1

plotTable1(t1Times, t1Rows)
for i in range(2):
    t2Data = [t2Times]
    for col in t2Rows[i]:
        t2Data.append(col)
    t2 = go.Figure(data=[go.Table(header=dict(values=t2ColumnNames),
                                  cells=dict(values=t2Data))
                         ])
    t2.show()
