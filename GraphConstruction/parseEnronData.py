import pandas as pd
import email
from dateutil.parser import parse
import tzInfo

def write100Df(df):
    filePath100 = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\\emails100.csv'
    colNames = df.columns
    unqSubj = {}
    unqSubjRe = {}
    data = {}
    cnt = 0
    replCount = 0
    nonUnqSubj = 0
    for index, row in df.iterrows():
        cnt += 1
        messageList = row[colNames[1]].split('\n')
        for ln in messageList:
            lnList = ln.split(': ', 1)
            if (len(lnList) != 2):
                #print(lnList)
                continue
            if cnt <= 100:
                if (lnList[0] in data):
                    data[lnList[0]].append(lnList[-1])
                else:
                    data[lnList[0]] = [lnList[-1]]
            if (lnList[0] == 'Subject'):
                if lnList[-1] in unqSubj:
                    nonUnqSubj += 1
                    unqSubj[lnList[-1]] += 1
                else:
                    unqSubj[lnList[-1]] = 1
                unqSubj[lnList[-1]] += 1
                if ('re:' in lnList[-1][:3].lower()):
                    replCount += 1
                    if lnList[-1][3:] in unqSubjRe:
                        unqSubjRe[lnList[-1][3:]] += 1
                    else:
                        unqSubjRe[lnList[-1][3:]] = 1

    print(replCount, cnt)
    fSubj = open('subjects.txt', 'w')
    for subj in unqSubj:
        fSubj.write(str(subj) + '/\\' + str(unqSubj[subj]) + '\n')
    fSubjRe = open('re_subjects.txt', 'w')
    for subj in unqSubjRe:
        fSubjRe.write(str(subj) + '/\\' + str(unqSubjRe[subj]) + '\n')
    print(nonUnqSubj, len(unqSubj), len(unqSubjRe))
    fSubj.close()
    fSubjRe.close()
    df100 = pd.DataFrame({k:pd.Series(v[:100]) for k,v in data.items()})
    #df100.to_csv(filePath100)

def getEnronDf():
    filePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\\emails.csv'
    df = pd.read_csv(filePath)
    #write100Df(df)
    return df

def createDetailsDataFrame(df, filePath, filePath100):
    colNames = df.columns
    dfColumns = []
    data = {}
    for index, row in df.iterrows():
        message = row[colNames[1]]
        e = email.message_from_string(message)
        if dfColumns == []:
            dfColumns = e.keys()
            for column in dfColumns:
                data[column] = []
        for column in dfColumns:
            data[column].append(e.get(column))
    df100 = pd.DataFrame({k: pd.Series(v[:100]) for k, v in data.items()})
    dfFull = pd.DataFrame({k: pd.Series(v) for k, v in data.items()})
    #df100.to_csv(filePath100)
    #dfFull.to_csv(filePath)
    return dfFull, df100

def addSubject(subj, unqSubjects, msgKey, email):
    if subj:
        subj = subj.lstrip()
    if subj in unqSubjects:
        unqSubjects[subj].append((email, msgKey))
    else:
        unqSubjects[subj] = [(email, msgKey)]

def customEncoding(txt):
    if txt:
        return txt.encode('ascii', 'ignore').decode('ascii')
    return txt

def writeReplies(replies):
    filePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\EnronData\\enronReplies.txt'
    f = open(filePath, 'w')
    for time in replies:
        f.write(str(time) + ', ')

def readEnronAuthors():
    filePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\enronAliasesGambit.csv'
    df = pd.read_csv(filePath)
    filePath100 = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\EnronData\enronAliases100.csv'
    df.head(100).to_csv(filePath100)

def createMsgDetailsFile(df, filePath, edgesFilePath):
    replyTimes = []
    replyCount = 0
    tzInfos = tzInfo.getTZInfo()
    f = open(filePath, 'w')
    edgesF = open(edgesFilePath, 'w')
    invalidRowCount = 0
    delim = '/\\'
    unqSubjects = {}
    unqReSubjects = {}
    invalidRe = 0
    countNoRe = 0
    countManyRe = 0
    msgTimestamp = {}
    for index, row in df.iterrows():
        email = row['From']
        msgKey = row['Message-ID']
        subj = row['Subject']
        date = customEncoding(row['Date'])
        addSubject(subj, unqSubjects, msgKey, email)
        dateObj = parse(date, tzinfos=tzInfos)
        dateTimestamp = dateObj.timestamp()
        msgTimestamp[msgKey] = dateTimestamp

    for index, row in df.iterrows():
        date = customEncoding(row['Date'])
        email = customEncoding(row['From'])
        msgKey = customEncoding(row['Message-ID'])
        name = customEncoding(row['X-From'])
        subj = customEncoding(row['Subject'])
        toList = customEncoding(row['To'])

        if ('re:' in subj[:3].lower()):
            # the message is a reply
            reSubject = subj[3:].lstrip()
            replyCount += 1
            if not (reSubject in unqSubjects):
                invalidRe += 1
            else:
                cntPoss = 0
                repliedToKey = ''
                for res in unqSubjects[reSubject]:
                    if (toList and (res[0] in toList)):
                        cntPoss += 1
                        repliedToKey = res[1]
                if cntPoss == 0:
                    countNoRe += 1
                if cntPoss > 1:
                    print('Many re', subj, email, toList)
                    countManyRe += 1
                if cntPoss == 1:
                    replyTimes.append(abs(msgTimestamp[repliedToKey] - msgTimestamp[msgKey]))
                    edgesF.write(str(repliedToKey) + '/\\' + str(msgKey) + '\n')

        if date == '' or email == '' or msgKey == '' or name == '':
            invalidRowCount += 1
        else:
            f.write(str(msgKey) + delim + str(name) + delim)
            f.write(str(email) + delim + str(dateTimestamp) + '\n')
    writeReplies(replyTimes)
    print(replyCount, countManyRe, countNoRe, invalidRe, invalidRowCount)

readEnronAuthors()
pathPref = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\EnronData'
enronDf = getEnronDf()
dfFull, df100 = createDetailsDataFrame(enronDf, 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\EnronData\enronDetails.csv',
                       'D:\AKwork2021\HigherDimensions\Higher-Dimensions\emails100.csv')
createMsgDetailsFile(dfFull, pathPref + '\\enronMsgDetails.txt', pathPref + '\\enronMsgEdges.txt')