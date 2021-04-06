import editdistance
import mailClusters

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
# # List of pairs (name, email) for all email addresses in the file.
# pairs = []

# humanID[email] = the index of human with email
humanID = {}
# fullNames[email] = the list of full names for the human with email
fullNames = {}
# email[fullName] = the email of person with fullName
email = {}

def getIdentity(name):
    return Identity[name]

def readNames():
    # File with developers' names and email in format Name1 Name2 .. LastName /\ email.
    # Name1, Name2, .., lastName can be empty.
    # todo: change file name and check if correct file.
    nameEmails = open("D:\AKwork2020-2021\Higher-Dimensions\ApacheData\\nameAndEmailUsername.txt", "r")
    return mailClusters.readNames(nameEmails)

'''
    Join every two names that are similar.
'''
def joinNames(pairs):
    par = []
    nrEmailAdd = len(pairs)
    for i in range(nrEmailAdd):
        par.append(i)
    print(nrEmailAdd)
    for i in range(nrEmailAdd):
        for j in range(i + 1, nrEmailAdd):
            if mailClusters.similarPairs(pairs[i], pairs[j]):
                mailClusters.joinRoots(par, mailClusters.root(par, i), mailClusters.root(par, j))
    return par

def createCheckedIdentities(filename):
    eqPeople = open(filename, 'r')
    while True:
        crtL = eqPeople.readline()
        if not crtL or crtL == '\n':
            break
        crtL = crtL.replace('\n', '')
        crtL = crtL.split('/\\')
        if crtL == ['']:
            break
        assert len(crtL) == 4
        alias1 = crtL[1] + crtL[0]
        alias2 = crtL[3] + crtL[2]
        if alias1 in Identity:
            print(alias1, alias2)
            assert not(alias2 in Identity)
            Identity[alias2] = Identity[alias1]
        elif alias2 in Identity:
            Identity[alias1] = Identity[alias2]
        else:
            Identity[alias1] = alias1
            Identity[alias2] = Identity[alias1]


'''
    For each component of joined names, update the details(Identity, fullName, humanID, email) for
    each pair (name, email). The pair is updated depending on whether or not all names correspond
    to the same person,.
'''
def createClusters(par, pairs):
    # List with the cluster ids of false positives (groups of email addresses that don't actually
    # correspond to the same person.
    fakeList = [8, 60, 77, 4, 47, 209, 57, 56, 38, 98, 126, 68, 83, 703, 44, 154, 402, 749, 85, 118]
    #364, 476, 1672, 168, 88, 1541, 79, 96, 1377, 779, 109, 162, 78]
    emailsOfFullName = mailClusters.getEmailsOfFullName()
    nrHumans = 0
    cluster = {}
    nrC = 0
    print("creating clusters in mailID")
    nrEmailAdd = len(pairs)
    for i in range(nrEmailAdd):
        if mailClusters.root(par, i) == i:
            cluster[i] = [i]
        else:
            cluster[mailClusters.root(par, i)].append(i)

    createCheckedIdentities('D:\AKwork2020-2021\Higher-Dimensions\GraphConstruction\Data\clustersApache\equalNames.txt')
    for i in range(nrEmailAdd):
        if mailClusters.root(par, i) == i:
            nrC += 1
            clusterSize = len(cluster[i])
            if clusterSize > 1 and (not (nrC in fakeList)):
                iFull = pairs[i][1] + pairs[i][0]['full']
                assert not(iFull in Identity)
                #Aliases in cluster correspond to same person.
                nrHumans += 1
                fullNames[nrHumans] = []

                for j in cluster[i]:
                    jFull = pairs[j][1] + pairs[j][0]['full']
                    if jFull in Identity:
                        if Identity[jFull] != pairs[i][1] + pairs[i][0]['full']:
                            print('Err', Identity[jFull], pairs[i][1] + pairs[i][0]['full'])

                    Identity[jFull] = pairs[i][1] + pairs[i][0]['full']
                    humanID[jFull] = nrHumans
                    fullNames[nrHumans].append(pairs[j][0]['full'])
                    email[pairs[j][0]['full']] = pairs[j][1]
            else:
                for j in cluster[i]:
                    jFull = pairs[j][1] + pairs[j][0]['full']
                    if jFull in Identity:
                        continue
                    if pairs[j][0]['full'] in email:
                        Identity[jFull] = Identity[emailsOfFullName[pairs[j][0]['full']][0] + pairs[j][0]['full']]
                        humanID[jFull] = humanID[Identity[jFull]]
                        print('Jfull is ', pairs[j][0]['full'], pairs[j][1], Identity[jFull])
                    else:
                        nrHumans += 1
                        Identity[jFull] = jFull
                        humanID[jFull] = nrHumans
                        fullNames[nrHumans] = [pairs[j][0]['full']]
                        email[pairs[j][0]['full']] = pairs[j][1]
    print('#humans is', nrHumans)

def cachedInit():
    f = open("D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\identityFile.txt", 'r')
    print('Reading identity file')
    nrHumans = 0
    global humanID
    while (True):
        crtLine = f.readline().encode("utf-8", 'ignore').decode("utf-8", 'ignore')
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '').lower()
        crtLine = crtLine.split('/\\')
        if crtLine == ['']:
            continue
        # if len(crtLine) != 2:
        #     print(crtLine)
        assert len(crtLine) == 2
        Identity[crtLine[0]] = crtLine[1]
        if not(crtLine[1] in humanID):
            nrHumans += 1
            humanID[crtLine[1]] = nrHumans
        humanID[crtLine[0]] = humanID[crtLine[1]]
    print('The number of humans is', nrHumans)
    print('Finished reading identities')

def createIdentityFile():
    identityFile = open("D:\\AKwork2020-2021\\Higher-Dimensions\\ApacheData\\identityFile.txt", 'w')
    for emailAndName in Identity:
        res2Write = emailAndName + '/\\' + Identity[emailAndName] + '\n'
        identityFile.write(res2Write.encode("utf-8", 'ignore').decode("utf-8", 'ignore'))
    identityFile.close()


def getEmailDict():
    return email
def getHumanIDs():
    return humanID
def getFullNames():
    return fullNames

def fullInit():
    print('Reading names')
    pairs = readNames()
    print('Joining names')
    par = joinNames(pairs)
    createClusters(par, pairs)
    createIdentityFile()
