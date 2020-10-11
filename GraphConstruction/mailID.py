import editdistance

from pyjarowinkler.distance import get_jaro_distance
nameLim = [[-4, 0.60], [-3, 0.80], [-1, 0.95]]
emailLim = [[-4, 0.60], [-3, 0.80], [-1, 0.95]]
lim = 10
# Dictionary used for determining the email address representative for each email address, i.e
# Identity[email2] = email1 iff email2 and email1 correspond to the same person and email1 appears
# before email2 in the file with email addresses.
Identity = {}
# List with the strings that must be removed from the email addresses.
removeStr = ['eclipse', 'jdt', 'admin', 'support', '.']
# List of pairs (name, email) for all email addresses in the file.
pairs = []

# humanID[email] = the index of human with email
humanID = {}
# fullNames[email] = the list of full names for the human with email
fullNames = {}
# email[fullName] = the email of person with fullName
email = {}

def isLetter(a):
  return (ord(a) <= ord('z') and ord(a) >= ord('a')) or (ord(a) <= ord('Z') and ord(a) >= ord('A'))

def getIdentity(name):
    return Identity[name]
def removeStrings(name):
    for removeS in removeStr:
        name = name.replace(removeS, '')
    newName = ''
    nameLen = len(name)
    # remove the spaces at the end of the name
    while nameLen > 0 and name[nameLen - 1] == ' ':
        name = name[:-1]
        nameLen -= 1
    for i in range(nameLen):
        if isLetter(name[i]) or name[i] == ' ':
            newName += name[i]
    return newName
def purifyEmail(name):
    return removeStrings(name.replace(' ', '').replace('\n', '')).lower()

def purifyName(name):
    # remove leading spaces from the beginning of the name
    while len(name) > 0 and name[0] == ' ':
        name = name[1:]
    name = removeStrings(name)
    firstN = []
    NameList = name.split(' ')
    lastN = NameList[-1]
    firstN = NameList[:-1]
    # todo: remember why the firstName contains lastName when no first name given
    if firstN == []:
        firstN.append(lastN)

    return firstN, lastN, name.replace(' ','').replace('\n', '')

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

    simF = -lim
    for n1 in firstN1:
        for n2 in firstN2:
            if len(n1) > 2 and len(n2) > 2:
                simF = max(simF, stringSimilarity(n1, n2, type))

    simL = stringSimilarity(name1['last'], name2['last'], type)
    fullSim = stringSimilarity(name1['full'], name2['full'], type)

    return max(min(simF, simL), fullSim) >= nameLim[l][type]

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
    return sim >= emailLim[l][type]

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

def readNames():
    # File with developers' names and email in format Name1 Name2 .. LastName /\ email.
    # Name1, Name2, .., lastName can be empty.
    # todo: change file name and check if correct file.
    nameEmails = open("Data\\emailName2020B.txt", "rb")
    while True:
        crtLine = nameEmails.readline().decode()
        if not crtLine:
            break
        lst = crtLine.split('/\\')
        # Ignore the lines where the name of the developer is not mentioned.
        if lst[0] == '':
            continue
        assert len(lst) == 2
        # remove spaces, newlines and fixed strings from the email.
        email_i = purifyEmail(lst[1])
        first_i, last_i, full_i = purifyName(lst[0])
        name_i = {'first': first_i, 'last': last_i, 'full': full_i}
        pairs.append((name_i, email_i))

'''
    Join every two names that are similar.
'''
def joinNames():
    par = []
    nrEmailAdd = len(pairs)
    for i in range(nrEmailAdd):
        par.append(i)
    for i in range(nrEmailAdd):
        for j in range(i + 1, nrEmailAdd):
            if similarPairs(pairs[i], pairs[j]):
                joinRoots(par, root(par, i), root(par, j))
    return par

'''
    For each component of joined names, update the details(Identity, fullName, humanID, email) for
    each pair (name, email). The pair is updated depending on whether or not all names correspond
    to the same person,.
'''
def createClusters(par):
    # List with the cluster ids of false positives (groups of email addresses that don't actually
    # correspond to the same person.
    fakeList = [132]  # [58, 121, 191]
    nrHumans = 0
    cluster = {}
    nrC = 0
    nrEmailAdd = len(pairs)
    for i in range(nrEmailAdd):
        if root(par, i) == i:
            cluster[i] = [i]
        else:
            cluster[root(par, i)].append(i)

    for i in range(nrEmailAdd):
        if root(par, i) == i:
            nrC += 1
            clusterSize = len(cluster[i])
            if clusterSize > 1 and (not (nrC in fakeList)):
                nrHumans += 1
                fullNames[nrHumans] = []
                for j in cluster[i]:
                    Identity[pairs[j][1]] = pairs[i][1]
                    humanID[pairs[j][1]] = nrHumans
                    fullNames[nrHumans].append(pairs[j][0]['full'])
                    email[pairs[j][0]['full']] = pairs[j][1]
            else:
                for j in cluster[i]:
                    nrHumans += 1
                    Identity[pairs[j][1]] = pairs[j][1]
                    humanID[pairs[j][1]] = nrHumans
                    fullNames[nrHumans] = [pairs[j][0]['full']]
                    email[pairs[j][0]['full']] = pairs[j][1]


def getEmailDict():
    return email
def getHumanIDs():
    return humanID
def getFullNames():
    return fullNames

def init():
    readNames()
    par = joinNames()
    createClusters(par)
