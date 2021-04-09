from datetime import timedelta
import warnings
from dateutil.parser import parse
import tzInfo

MIN_YEAR = 1995
MAX_YEAR = 2005
invalidCh = ['\\', '/', '+', '!', '{', '}', '(', ')', ':', '[', ']']
warnings.filterwarnings("error")
peopleDict = {}

def writePeople(f4):
    for person in peopleDict:
        f4.write(person + '\n')
    f4.close()
#Removes any occurence of an invalid ch (from invalidCh) from the name.
def purify(name):
  newName = ''
  for ch in name:
    if not(ch in invalidCh):
      newName += ch
  return newName

#Return the name and emailUsername from the From input. Format: name/\emailUsername.
def getNameAndEmail(From):
    From = From.replace('\n', '')
    if '<' in From:
        From = From.rsplit('<', 1)
    elif '(' in From:
        From = From.split('(')
        assert ((')' in From[1]) and ('@' in From[0]))
        assert (From[1][-1] == ')')
        aux = From[0]
        From[0] = From[1]
        From[1] = aux
    elif ', ' in From:
        print(From)
        exit(0)
    else:
        From = ['', From]
    assert (len(From) == 2)
    From[0] = From[0].replace('\'', '')
    From[0] = From[0].replace('\"', '')
    From[0] = purify(From[0])
    From[0] = From[0].split('@')[0]
    From[0] = From[0].split('<')[0]
    From[1] = From[1].split('<')[0]
    return From[0] + '/\\' + From[1].split('@')[0]

f = open('D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\msgDetailsRawFull.txt', 'r', encoding="utf-8")
msgDict = {}
msgIds = {}
nrM = 0
nonUniqueMsgIds = 0
badCnt = 0
badRepliesFormat = 0
badMsgId = 0

#Read all lines from the file containing all message details.
tzInfo = tzInfo.getTZInfo()
noRepliedToCnt = 0
firstChange = True
while True:
    # The line contains information of current msg in format msgID/\repliedtoID/\name+email/\date
    crtLine = f.readline()
    if not crtLine:
        break
    assert (len(crtLine.split('/\\')) == 4)

    crtLine = crtLine.replace('\n', '')
    crtLine = crtLine.split('/\\')

    if not (crtLine[0][0] == '<' and crtLine[0][-1] == '>'):
        badMsgId += 1
        continue
    assert (crtLine[0][0] == '<' and crtLine[0][-1] == '>')
    msgId = crtLine[0]
    if len(crtLine[1]) == 0:
        noRepliedToCnt += 1

    msgRepliedTo = crtLine[1].split('>', 1)[0] + '>'
    if not '<' in crtLine[1]:
        if len(crtLine[1]) > 0:
            #print(crtLine[1].split(' of ')[-1])
            badRepliesFormat += 1
    name = getNameAndEmail(crtLine[2])
    if not(name in peopleDict):
        peopleDict[name] = True

    date = crtLine[3]

    isMET_DST = False
    if 'MET DST' in date or 'METDST' in date:
        date = date.replace('(MET DST)', '(MET)').replace('(METDST)', '(MET)')
        isMET_DST = True
    # Uncomment this lines to fix INVALID DATE ERRORS IN THE DATASET
    # date = date.replace('+48000', '+0000 (GMT)').replace('-3200 (PST)', '+0000 (GMT)')
    # date = date.replace('-70100 (EST)', '+0000 (GMT)').replace('+73900 (EST)', '+0000 (GMT)')
    # date = date.replace('+4100 (MST)', '+0000 (GMT)')

    date = date.replace('(Est)', '(EST)')
    date = date.replace('(Eastern Standard Time)', '(EST)')
    date = date.replace('(Pacific Daylight Time)', '(PDT)')
    date = date.replace('(Eastern Daylight Time)', '(EDT)')
    date = date.replace('(Pacific Standard Time)', '(PST)')
    date = date.replace('(AUS Eastern Daylight Time)', '(AEDT)')
    date = date.replace('((MEZ) - Mitteleurop. Sommerzeit)', '(MEZ)')
    if msgId in msgDict:
        nonUniqueMsgIds += 1
    else:
        try:
            # if '(' in date and ')' in date:
            #     date = date.split('(')[0]
            dt = parse(date, tzinfos=tzInfo)
            sec = 0
            if isMET_DST:
                sec -= 3600
            utcdate = dt + timedelta(seconds=sec)

            if utcdate.year < MIN_YEAR or utcdate.year > MAX_YEAR:
                print('Inappropriate date', date)
                continue
            msgDict[msgId] = (name, msgRepliedTo, utcdate.timestamp())
            if not msgId in msgIds:
                nrM += 1
                msgIds[msgId] = nrM
        except Warning:
            badCnt += 1
            #print(date, 'is a wrongly formatted date')
        except Exception:
            badCnt += 1
            #print(date, 'bad dates')

f2 = open("D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\apacheMsgDetails.txt", "w", encoding="utf-8")
f3 = open("D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\apacheMsgEdges.txt", "w", encoding="utf-8")
f4 = open("D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\apachePeople.txt", "w", encoding="utf-8")

writePeople(f4)
print(noRepliedToCnt, badRepliesFormat, badCnt, badMsgId, nrM, nonUniqueMsgIds)

msgWithReply = {}
msgWithReplyCount = 0
badReplyCnt = 0
badReplyMsg = {}
noReplyMsg = {}
print('Msg ids', len(msgIds))
for msgId in msgDict:
    f2.write(str(msgIds[msgId]) + '/\\' + msgDict[msgId][0] + '/\\' + str(msgDict[msgId][2]) + '\n')
    if msgDict[msgId][1] != '' and msgDict[msgId][1] in msgDict:
        if not (msgIds[msgDict[msgId][1]] in msgWithReply):
            msgWithReplyCount += 1
            msgWithReply[msgIds[msgDict[msgId][1]]] = msgWithReplyCount
        f3.write(str(msgIds[msgId]) + '/\\' + str(msgIds[msgDict[msgId][1]]) + '\n')
    # else:
    #     if len(msgDict[msgId][1]) > 1 or (len(msgDict[msgId][1]) == 1 and msgDict[msgId][1][0] != '>'):
    #         #print(msgDict[msgId][1])
    #         if not (msgIds[msgId] in badReplyMsg):
    #             badReplyCnt += 1
    #             badReplyMsg[msgIds[msgId]] = badReplyCnt

for msgId in msgDict:
    if msgDict[msgId][1] in msgDict:
        continue
    if msgDict[msgId][1] == '' or msgDict[msgId][1] == '>':
        continue
    if not (msgDict[msgId][1] in badReplyMsg):
        badReplyCnt += 1
        badReplyMsg[msgDict[msgId][1]] = badReplyCnt

print(badReplyCnt, msgWithReplyCount, len(msgDict))
noReplyMsgCount = 0
for msgId in msgIds:
    if (not(msgIds[msgId] in msgWithReply)) and (not(msgId in badReplyMsg)):
        noReplyMsgCount += 1

print(noReplyMsgCount, noReplyMsgCount + msgWithReplyCount, noReplyMsgCount + len(badReplyMsg) + msgWithReplyCount)
f2.close()
f3.close()
f.close()