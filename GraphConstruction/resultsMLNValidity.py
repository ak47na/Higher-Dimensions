import reproValidity
import mailID
import Settings
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

for (t, delta_t) in timeIntWithResults:
    MLNcrtResult = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'MLN')
    t1Times.append(t)
    t1Rows[0].append(MLNcrtResult[0][0])
    t1Rows[2].append(MLNcrtResult[0][1])
    crtResult, cleCount = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict, 'monoplex')
    t1Rows[1].append(crtResult[0][0])
    t1Rows[3].append(crtResult[0][1])
    t1Rows[4].append(MLNcrtResult[0][0] / MLNcrtResult[0][1])
    t1Rows[5].append(crtResult[0][0] / crtResult[0][1])

plotTableOPBounds(t1Times, t1Rows)