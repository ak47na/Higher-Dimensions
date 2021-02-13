import requests
from datetime import datetime
from datetime import timedelta

pref = 'https://www.eclipse.org/lists/jdt-dev/msg'
pageLinks = ['https://www.eclipse.org/lists/jdt-dev/threads.html']
defaultLink = 'https://www.eclipse.org/lists/jdt-dev/thrd'
# the good code
errorFile = open("errors.txt", "wb")
warningFile = open("warnings.txt", "wb")
edgeFile = open("emailMsgEdges.txt", "w")
detailsFile = open("emailDetails.txt", "wb")
namesFile = open("emailNames.txt", "wb")
emailOfName = {}

for i in range(2, 19):
    pageLinks.append(defaultLink + str(i) + '.html')


def getPageContent(pageLink):
    page = requests.get(pageLink)
    return page.content


from bs4 import BeautifulSoup, NavigableString, Tag

nrNodes = 0
msgDex = {}
msgDetails = {}
names = {}


def CheckPage(pageBody):
    global nrNodes
    allLists = pageBody.find_all('li')
    for lst in allLists:
        Link = lst.find('a')
        if Link and not ('href' in Link.attrs):
            continue
        if Link and ('msg' in Link['href']):
            msg = Link['name']
            if not (msg in msgDex):
                nrNodes += 1
                msgDex[msg] = (lst.find('em'), nrNodes)
            else:
                if (msgDex[msg][0] != lst.find('em')):
                    msgDex[msg] = (lst.find('em'), msgDex[msg][1])
                    print('link:', Link)
    print(len(pageBody.find_all('em')), nrNodes)

def AddEdge(u, v):
    edgeFile.write(str(u) + ' ' + str(v) + '\n')

def getDateFromList(s):
    idx = 0
    sLen = len(s)
    if ',' in s:
        while idx < sLen and s[idx] != ',':
            idx += 1
        idx += 2  # pass ', '
    else:
        while not isDigit(s[idx]):
            idx += 1
    dateStr = ''
    if ('-' in s) or ('+' in s):
        while idx < sLen and s[idx] != '-' and s[idx] != '+':
            dateStr += s[idx]
            idx += 1
        dateStr = dateStr[:-1]
        Date = datetime.strptime(dateStr, '%d %b %Y %H:%M:%S') + timedelta(hours=int(s[idx + 1:idx + 3]),
                                                                           minutes=int(s[idx + 3:idx + 5]))
    else:
        if not ('GMT' in s):
            print(s)
            s.replace('UTC', 'GMT')
        while (idx < sLen - 2) and (s[idx] != 'G' or s[idx + 1] != 'M' or s[idx + 2] != 'T'):
            dateStr += s[idx]
            idx += 1
        idx = len(dateStr) - 1
        while (idx > 0 and idx < len(dateStr) and dateStr[idx] == ' '):
            dateStr = dateStr[:-1]
            idx -= 1
        Date = datetime.strptime(dateStr, '%d %b %Y %H:%M:%S')

    return Date


def isDigit(a):
    return (ord(a) <= ord('9') and ord(a) >= ord('0'))


def isLetter(a):
    return (ord(a) <= ord('z') and ord(a) >= ord('a')) or (ord(a) <= ord('Z') and ord(a) >= ord('A'))


def getNameFromList(s):
    idx = 0
    sLen = len(s)
    name = ''
    s = s.replace('<li><em>From</em>:', '')

    while s[idx] != '&':
        if isLetter(s[idx]) or s[idx] == ' ':
            name += s[idx]
        idx += 1
    return name


def getIDFromEmail(s):
    idx = 0
    sLen = len(s)
    name = ''
    while s[idx] != '@':
        name += s[idx]
        idx += 1
    return name


for pageLink in pageLinks:
    nrNodes = 0
    BS = BeautifulSoup(getPageContent(pageLink), 'html.parser')
    CheckPage(BS)

for key in msgDex:
    # print(pref + key + '.html')
    BSi = BeautifulSoup(getPageContent(pref + key + '.html'), 'html.parser')
    # print(BSi.find_all(text=lambda text: (isinstance(text, Comment)) and 'X-Date' in text))
    allLists = BSi.find_all('li')
    ok1 = False
    ok2 = False
    msgDetails[key] = {}
    for lst in allLists:
        if ('Follow-Ups' in str(lst)):
            followUps = lst.find_all('a')
            for followUp in followUps:
                if ('name' in followUp.attrs):
                    AddEdge(followUp['name'], key)
                else:
                    print(followUp, '&&')
                    ok1 = True
                    ok2 = True
                    break
        elif ('References' in str(lst)):
            refs = lst.find_all('a')
            for ref in refs:
                if ('name' in ref.attrs):
                    AddEdge(key, ref['name'])
                else:
                    print(ref, '^^')
                    ok1 = True
                    ok2 = True
                    break

        Em = lst.find('em')
        if Em:
            Em = str(Em)
            if ('Date' in Em):
                if ('date' in msgDetails[key]) and (msgDetails[key]['date'] != None):
                    warningFile.write((str(lst) + '\n').encode())
                else:
                    msgDetails[key]['date'] = getDateFromList(str(lst))
            elif ('From' in Em):
                strList = str(lst)
                if ('email' in msgDetails[key]) and (msgDetails[key]['email'] != None):
                    warningFile.write((strList + '\n').encode())
                    continue
                msgDetails[key]['name'] = ''
                if (' &lt;' in strList):
                    msgDetails[key]['name'] = getNameFromList(str(strList))
                if not ('email' in msgDetails[key]):
                    msgDetails[key]['email'] = getIDFromEmail(lst.find('a')['href']).replace("mailto:", '')

    if msgDetails[key]['name'] and msgDetails[key]['name'] != '':
        if not (msgDetails[key]['name'] in emailOfName):
            emailOfName[msgDetails[key]['name']] = msgDetails[key]['email']
        else:
            msgDetails[key]['email'] = emailOfName[msgDetails[key]['name']]
    if not (msgDetails[key]['name'] in names):
        names[msgDetails[key]['name']] = msgDetails[key]['email']
        namesFile.write((str(msgDetails[key]['name']) + '/\\' + str(msgDetails[key]['email']) + '\n').encode())
    detailsFile.write((str(key) + '/\\' + str(msgDetails[key]['name']) + '/\\' + str(msgDetails[key]['email']) + '/\\'
                       + str(msgDetails[key]['date']) + '\n').encode())

    if ok1 and ok2:
        break

namesFile.close()
detailsFile.close()
warningFile.close()
errorFile.close()
edgeFile.close()
