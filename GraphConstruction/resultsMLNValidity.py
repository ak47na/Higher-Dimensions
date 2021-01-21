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
                      ('30 days', 3600 * 24 * 30), ('1 year', Y), ('20 years', Y * 20)]

mailID.init()
msgDetailsFilePath = "Data\\msgDetails.txt"
minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)

for (t, delta_t) in timeIntWithResults:
    crtResult = reproValidity.getValuesForMLN(t, delta_t, minTime, maxTime, msgDict)
