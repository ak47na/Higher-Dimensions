from datetime import timedelta

from dateutil.parser import parse

invalidCh = ['\\', '/', '+', '!', '{', '}', '(', ')', ':', '[', ']']
def purify(name):
  newName = ''
  for ch in name:
    if not(ch in invalidCh):
      newName += ch
  return newName

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
    return From[0] + '/\\' + From[1].split('@')[0]

f = open('D:\AKwork2020-2021\Higher-Dimensions\ApacheData\msgDetailsRawFull.txt', 'r', encoding="utf-8")
msgDict = {}
msgIds = {}
nrM = 0
nonUniqueMsgIds = 0
badCnt = 0
badRepliesFormat = 0
badMsgId = 0
while True:
    # The line contains information of current msg in format msgID/\repliedtID/\name+email/\date
    crtLine = f.readline()
    if not crtLine:
        break
    if (len(crtLine.split('/\\')) < 4):
        print(crtLine, 'was incomplete')
        crtLine += f.readline()
        print(crtLine, 'now')

    crtLine = crtLine.replace('\n', '')
    crtLine = crtLine.split('/\\')

    if not (crtLine[0][0] == '<' and crtLine[0][-1] == '>'):
        badMsgId += 1
        continue
    assert (crtLine[0][0] == '<' and crtLine[0][-1] == '>')
    msgId = crtLine[0]

    msgRepliedTo = crtLine[1].split('>', 1)[0] + '>'
    if not '<' in crtLine[1]:
        badRepliesFormat += 1
    name = getNameAndEmail(crtLine[2])
    date = crtLine[3].replace('(MET DST)', '(MET)')
    # Uncomment this lines to fix INVALID DATE ERRORS IN THE DATASET
    # date = date.replace('+48000', '+0000 (GMT)').replace('-3200 (PST)', '+0000 (GMT)')
    # date = date.replace('-70100 (EST)', '+0000 (GMT)').replace('+73900 (EST)', '+0000 (GMT)')
    # date = date.replace('+4100 (MST)', '+0000 (GMT)')
    if len(crtLine) != 4:
        print(crtLine, len(crtLine))
    assert (len(crtLine) == 4)
    if msgId in msgDict:
        nonUniqueMsgIds += 1
    else:
        sec = 0
        try:
            dt = parse(date)
            if dt.tzinfo and dt.tzinfo.utcoffset(dt):
                sec = dt.utcoffset().total_seconds()

            utcdate = dt + timedelta(seconds=sec)
            msgDict[msgId] = (name, msgRepliedTo, utcdate.timestamp())
            nrM += 1
            msgIds[msgId] = nrM
        except:
            badCnt += 1
            # print(date, 'is a bad date')

f2 = open("D:\AKwork2020-2021\Higher-Dimensions\ApacheData\\apacheMsgDetails.txt", "w", encoding="utf-8")
f3 = open("D:\AKwork2020-2021\Higher-Dimensions\ApacheData\\apacheMsgEdges.txt", "w", encoding="utf-8")
print(badRepliesFormat, badCnt, badMsgId, nrM, nonUniqueMsgIds)

badReplyCnt = 0
for msgId in msgDict:
    f2.write(str(msgIds[msgId]) + '/\\' + msgDict[msgId][0] + '/\\' + str(msgDict[msgId][2]) + '\n')
    if msgDict[msgId][1] != '' and msgDict[msgId][1] in msgDict:
        f3.write(str(msgIds[msgId]) + '/\\' + str(msgIds[msgDict[msgId][1]]) + '\n')
    else:
        if len(msgDict[msgId][1]) > 1:
            badReplyCnt += 1

print(badReplyCnt)
f2.close()
f3.close()
