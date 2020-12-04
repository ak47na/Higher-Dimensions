import reproValidity
import mailID
import Settings

# the number of seconds in a year
Y = 3600 * 24 * 365

def similarity(actual, expected):
    diff = abs(actual - expected)
    return (diff / expected) * 100

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

transitiveFaultRateFile = open('Data\\transitiveFaultRate.txt', 'w')
twoPathCorrelationsFile = open('Data\\twoPathCorrelations.txt', 'w')
for (t, delta_t) in timeIntWithResults:
    crtResult = reproValidity.getValues(t, delta_t, minTime, maxTime, msgDict)

    if (delta_t in transitiveFaultRate):
        transitiveFaultRateFile.write('For ' + t + ':\n')
        # transitiveFaultRateFile.write('lower bound: ', + crtResult[0][0] + ' upper bound: ' + crtResult[0][1] + '\m')
        transitiveFaultRateFile.write('The similarity for lower-upper bounds of transitive fault rate is\n')
        for projResult in transitiveFaultRate[delta_t]:
            for i in range(2):
                transitiveFaultRateFile.write(str(crtResult[0][i]) + ' ' + str(projResult[i]) + ' ' +
                                              str(similarity(crtResult[0][i], projResult[i])) + '\n')

    if (delta_t in twoPathCorrelations):
        twoPathCorrelationsFile.write('For ' + t + ':\n')
        for projResult in twoPathCorrelations[delta_t]:
            twoPathCorrelationsFile.write('Similarity for 2path correlations:\n')
            for i in range(2):
                twoPathCorrelationsFile.write(str(crtResult[i + 1][0]) + ' ' + str(projResult[0]) + ' ' + str(similarity(crtResult[i + 1][0], projResult[0])) + ' ')
            twoPathCorrelationsFile.write('\n')

transitiveFaultRateFile.close()
twoPathCorrelationsFile.close()