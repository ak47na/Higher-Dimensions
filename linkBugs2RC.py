f = open("\\Bug2Gerrit.txt", "r")
bugEdgeFile = open("\\BugEdges.txt", "w")
issueLabel = {}

nrBugs = 0

def isDigit(ch):
    if (int(ord(ch)) <= int(ord('9')) and int(ord(ch)) >= int(ord('0'))):
        return True
    return False
while (True):
    crtL = f.readline()
    if not crtL:
        break
    lst = crtL.split(" ")

    nrBugs += 1
    seeAlso = f.readline().split(', ')
    a = len('https://git.eclipse.org/')
    for lnk in seeAlso:
        strLen = len(lnk)
        idx = a
        if ('https://git.eclipse.org/' in lnk) and not('commit' in lnk):
            while not isDigit(lnk[idx]):
                idx += 1
            reviewID = 0
            while idx < strLen and isDigit(lnk[idx]):
                reviewID = reviewID * 10 + int(lnk[idx])
                idx += 1
            bugEdgeFile.write('ReviewEdge ' + str(lst[0]) + ' ' + str(reviewID) + '\n')
        elif 'commit' in lnk:
            idx = 0
            while lnk[idx] != '=':
                idx += 1
            if lnk[idx] != '=':
                continue
            idx += 1
            bugEdgeFile.write('CommitEdge ' + str(lst[0]) + ' ')
            while lnk[idx] != '\'':
                bugEdgeFile.write(lnk[idx])
                idx += 1
            bugEdgeFile.write('\n')

f.close()
bugEdgeFile.close()
