import editdistance
# import pylcs
from pyjarowinkler.distance import get_jaro_distance
nameLim = [[-4, 0.60], [-3, 0.80], [-1, 0.95]]
emailLim = [[-4, 0.60], [-3, 0.80], [-1, 0.95]]
lim = 10

nameEmails = open("\\emailNames.txt")
removeStr = ['eclipse', 'jdt', 'admin', 'support', '.']
def isLetter(a):
  return (ord(a) <= ord('z') and ord(a) >= ord('a')) or (ord(a) <= ord('Z') and ord(a) >= ord('A'))

def removeStrings(name):
    for removeS in removeStr:
        name = name.replace(removeS, '')
    newName = ''
    nameLen = len(newName)
    nameLen = len(name)
    while nameLen > 0 and name[nameLen - 1] == ' ':
        name = name[:-1]
        nameLen -= 1
    for i in range(nameLen):
        if isLetter(name[i]) or name[i] == ' ':
            newName += name[i]
    return newName
def purifyName(name):
    if name[0] == ' ':
        name = name[1:]
    name = removeStrings(name)
    firstN = []

    NameList = name.split(' ')
    lastN = NameList[-1]
    firstN = NameList[:-1]
    if firstN == []:
        firstN.append(lastN)

    return firstN, lastN, name.replace(' ','')

def stringSimilarity(s1, s2, type):
    if type == 0:
        return -editdistance.eval(s1, s2)
    if s1 == '' or s2 == '':
        return -lim
    return get_jaro_distance(s1, s2)

def nameSimilarity(name1, name2, type, l):
    firstN1 = name1['first']
    firstN2 = name2['first']

    simF = -lim
    for n1 in firstN1:
        for n2 in firstN2:
            if len(n1) > 2 and len(n2) > 2:
                simF = max(simF, stringSimilarity(n1, n2, type))

    simL = stringSimilarity(name1['last'], name2['last'], type)
    fullSim = stringSimilarity(name1['full'], name2['full'], type)

    return max(min(simF, simL), fullSim) >= nameLim[l][type]

def emailsSimilarity(p1, p2, type, l):
    sim = stringSimilarity(p1[1], p2[1], type)

    if len(p1[0]['last']) <= 2:
        return sim >= emailLim[l][type]
    firsts = p1[0]['first']
    okF = False
    okFI = False
    okL = p1[0]['last'] in p2[1]
    okLI = p1[0]['last'][0] in p2[1]
    ok = False
    for first in firsts:
        if len(first) <= 2:
            continue
        ok = True
        if first in p2[1]:
            okF = True
            break
        if first[0] in p2[1]:
            okFI = True

    if ok and ((okF and okL) or (okF and okLI) or (okFI and okL)):
        return True
    return sim >= emailLim[l][type]

def similarPairs(p1, p2):
    if nameSimilarity(p1[0], p2[0], 0, 2) and nameSimilarity(p1[0], p2[0], 1, 2):
        return True
    if emailsSimilarity(p1, p2, 0, 2) and emailsSimilarity(p1, p2, 1, 2):
        return True
    for type in range(2):
        if (not nameSimilarity(p1[0], p2[0], type, 0)):
            return False
        if (not emailsSimilarity(p1, p2, type, 0)) and (not emailsSimilarity(p2, p1, type, 0)):
            return False
        if (not nameSimilarity(p1[0], p2[0], type, 1)) and (not emailsSimilarity(p1, p2, type, 1)) and (not emailsSimilarity(p2, p1, type, 1)):
            return False
    return True

def root(x):
    if par[x] == x:
        return x
    par[x] = root(par[x])
    return par[x]

def joinRoots(rx, ry):
    if rx == ry:
        return
    if rx > ry:
        par[rx] = ry
    else:
        par[ry] = rx

pairs = []

while True:
    crtL = nameEmails.readline()
    if not crtL:
        break
    lst = crtL.split('/\\')
    if lst[0] == '':
        continue
    if len(lst) != 2:
        print(lst)
        exit()

    email_i = lst[1].replace(' ', '')
    email_i = removeStrings(email_i.replace('\n', '')).replace(' ', '')
    first_i, last_i, full_i = purifyName(lst[0])
    name_i = {'first' : first_i, 'last': last_i, 'full': full_i}
    pairs.append((name_i, email_i))

N = len(pairs)

par = []
for i in range(N):
    par.append(i)
for i in range(N):
    for j in range(i + 1, N):
        if similarPairs(pairs[i], pairs[j]):
            joinRoots(root(i), root(j))
            p1 = pairs[i]
            p2 = pairs[j]

nrC = 0
print(N)
bad = 0
for i in range(N):
    if root(i) == i:
        nrC += 1
        cluster = [i]
        for j in range(i + 1, N):
            if root(j) == i:
                cluster.append(j)
        clusterSize = len(cluster)
        if clusterSize > 1:
            f = open("\\cluster" + str(nrC) + ".txt", "wb")
            for j in cluster:
                f.write((str(pairs[j][0]) + '/\\' + str(pairs[j][1]) + '\n').encode())
            f.close()
