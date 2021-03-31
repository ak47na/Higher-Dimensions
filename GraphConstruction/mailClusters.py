#program to get the clusters of email addresses
import editdistance
# import pylcs
from pyjarowinkler.distance import get_jaro_distance
import re
nameLim = [[-4, 0.70], [-3, 0.80], [0, 0.95]]
emailLim = [[-4, 0.70], [-3, 0.80], [0, 0.95]]
lim = 10
# emailNamesFile = "GraphConstruction/Data/emailName2020B.txt" #File with email names for eclipse
emailNamesFile = 'D:\\AKwork2020-2021\\Higher-Dimensions\\ApacheData\\nameAndEmailUsername.txt'
#File with names and emails in format name/\email
nameEmails = open(emailNamesFile, 'r')
emailsOfFullName = {}

#removeStr = ['eclipse', 'jdt', 'admin', 'support', '.']
invalidCh = ['\\', '/', '+', '!', '{', '}', '(', ')', ':', '[', ']']
removeStr = ['admin', 'support', '.', 'apache', 'mail', 'list']

def removeSpecialStringsFromString():
    pass

def purifyEmail(name):
    return removeStrings(name.replace(' ', '').replace('\n', '')).lower()
#
# def isLetter(a):
#   return (ord(a) <= ord('z') and ord(a) >= ord('a')) or (ord(a) <= ord('Z') and ord(a) >= ord('A'))
def removeStrings(name):
    for removeS in removeStr:
        name = name.replace(removeS, '')
    newName = ''
    nameLen = len(name)
    while nameLen > 0 and name[nameLen - 1] == ' ':
        name = name[:-1]
        nameLen -= 1
    for i in range(nameLen):
        if not(name[i] in invalidCh):
            newName += name[i]
    return newName

def purifyName(name):
    name = removeStrings(name)
    name = name.strip()
    NameList = re.split(' |\t', name)
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

'''
    Returns True if:
    1. the similarity[type] of the full name of p1 and the full name of p2 is >= nameLim[type] OR
    2. (the similarity[type] of one of the names of p1 and one of the names of p2 is >= nameLim[type] AND
       the similarity[type] of the last name of p1 and the last name of p2 is >= nameLim[type])  OR
'''
def nameSimilarity(name1, name2, type, l):
    firstN1 = name1['first']
    firstN2 = name2['first']
    if len(firstN1) == 0 or len(firstN2) == 0:
        return False
    simF = -lim
    for n1 in firstN1:
        for n2 in firstN2:
            if len(n1) > 2 and len(n2) > 2:
                simF = max(simF, stringSimilarity(n1, n2, type))

    simL = stringSimilarity(name1['last'], name2['last'], type)
    fullSim = stringSimilarity(name1['full'], name2['full'], type)
    nameSim = max(min(simF, simL), fullSim)
    #print('Name similarity for ', name1, name2, 'is', nameSim, simL, simF, fullSim)
    return nameSim >= nameLim[l][type]

'''
    Returns True if:
    1. the emails of p1 and p2 have similarity[type] >= emailLim[l][type] OR
    2. the last name of p1 has length >= 2 AND 
      2.1 all names of p1 are present in the email of p2 OR
      2.2 the first letter of the one name and the last name of p1 are present in the email of p2 OR
      2.3 the first letter of the last name and one name with length >= 2 are present in the email of p2
'''
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
    #print('Email similarity for ', p1, p2, 'is', sim)
    return sim >= emailLim[l][type]

def equalPairs(p1, p2):
    if (p1[1] == p2[1]):
        return True
    if (p1[0]['full'] == p2[0]['full']):
        return True
    return False

'''
    Returns True if the (name, email) pairs p1 and p2 have high similarity.
'''
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

def root(par, x):
    if par[x] == x:
        return x
    par[x] = root(par, par[x])
    return par[x]

def joinRoots(par, rx, ry):
    if rx == ry:
        return
    if rx > ry:
        par[rx] = ry
    else:
        par[ry] = rx

pairs = []

def readNames(f):
    while True:
        crtL = f.readline().encode("utf-8", 'ignore').decode("utf-8", 'ignore')
        if not crtL:
            break
        if crtL == '\n':
            continue
        lst = crtL.split('/\\')
        if lst[0] == '':
            lst[0] = lst[1]
        lst[0] = lst[0].split('<')[0]
        lst[1] = lst[1].split('<')[0]
        assert len(lst) == 2

        email_i = purifyEmail(lst[1]).lower()
        first_i, last_i, full_i = purifyName(lst[0])
        name_i = {'first': first_i, 'last': last_i, 'full': full_i.lower()}
        if name_i['full'] == '':
            name_i = {'first': email_i, 'last': '', 'full': email_i}

        if email_i == '':
            email_i = name_i['full']

        if name_i['full'] in emailsOfFullName:
            emailsOfFullName[name_i['full']].append(email_i)
        else:
            emailsOfFullName[name_i['full']] = [email_i]
        pairs.append((name_i, email_i))
    f.close()
    return pairs

def getEmailsOfFullName():
    return emailsOfFullName

readNames(nameEmails)
N = len(pairs)
# name_i1 = {'first': 'thom', 'last': 'thom', 'full': 'thom'}
# name_i2 = {'first': 'ben', 'last': 'ben', 'full': 'ben'}
# p1 =(name_i1, 'thom')
# p2 =(name_i2, 'ben')
# print(similarPairs(p1, p2))
# exit()

def createClusters(par):
    print('creating clusters')
    for i in range(N):
        par.append(i)

    for i in range(N):
        for j in range(i + 1, N):
            if equalPairs(pairs[i], pairs[j]):
                joinRoots(par, root(par, i), root(par, j))

    nrC = 0
    print(N)
    for i in range(N):
        if root(par, i) == i:
            nrC += 1
            cluster = [i]
            for j in range(i + 1, N):
                if root(par, j) == i:
                    cluster.append(j)
            clusterSize = len(cluster)
            if clusterSize > 1:
                filePath = "D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\Data\\clustersApache\\cluster"
                if clusterSize > 2:
                    filePath += '_'
                f = open(filePath + str(nrC) + ".txt", "wb")
                for j in cluster:
                    f.write((str(pairs[j][0]) + '/\\' + str(pairs[j][1]) + '\n').encode())
                f.close()

par = []
createClusters(par)