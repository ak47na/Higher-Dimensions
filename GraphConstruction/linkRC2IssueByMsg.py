filer = open("Data\\ReviewData.txt", "r")
filec = open("Data\\CommitEditedData.txt", "r")
testFile = open("Data\\test.txt", "w")
bugRCEdge = open("Data\\RevMsg2BugEdge.txt", "w")
nrRev = 0
nrRevWithBugs = 0

def isDigit(ch):
    if (int(ord(ch)) <= int(ord('9')) and int(ord(ch)) >= int(ord('0'))):
        return True
    return False
def getNumber(subj):
    idx = 0
    strLen = len(subj)
    while idx < strLen and (not(isDigit(subj[idx]))):
        idx += 1
    nr = 0
    while idx < strLen and isDigit(subj[idx]):
        nr = nr * 10 + int(subj[idx])
        idx += 1
    return nr

def readMessages(file, outFile, changeIndex, subjID, edgeType):
    nrMsg = 0
    nrMsgWithBugs = 0
    while (True):
        crtL = file.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        if len(lst) <= subjID:
            print(lst)
            continue

        nrMsg += 1
        subj = lst[subjID].lower()
        strLen = len(subj)

        ok = False
        nr = -1
        for i in range(0, strLen - 2):
            if subj[i] == 'b' and subj[i + 1] == 'u' and subj[i + 2] == 'g':
                nr = getNumber(subj[i + 3:-1])
                if nr != 0:
                    ok = True
                    break

        if ok:
            outFile.write(edgeType + lst[changeIndex] + ' ' + str(nr) + '\n')
            nrMsgWithBugs += 1

readMessages(filer, bugRCEdge, 1, 3, "Review2Bug ")
readMessages(filec, bugRCEdge, 0, 1, "Commit2Bug ")
bugRCEdge.close()
