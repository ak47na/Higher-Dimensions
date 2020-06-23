from perceval.backends.core.bugzilla import *
import datetime

hostname = 'https://bugs.eclipse.org//bugs//'

Bzilla = Bugzilla(url=hostname)

dateN = datetime.datetime(2020, 1, 1, 0, 0)
BugList = Bzilla.fetch(category='bug', from_date=dateN)
bugDex = [{}, {}]

nrProjects = 2

def Str(elem):
    if '\u010d' in elem:
        elem = elem.replace('\u010d', 'c')

    try:
        elemStr = str(elem).encode("utf-8").decode()
    except UnicodeEncodeError:
        strLen = len(elem)
        res = ''
        for i in range(strLen):
            if (ord(elem[i]) >= 128):
                res += '?'
            else:
                res += elem[i]
        return res
    else:
        return elemStr


af = [open("/AssigneeData2020.txt", "w"), open("/AssigneeData2020_1.txt", "w")]
baf = [open("/AssigneeData2020B.txt", "wb"), open("/AssigneeData2020B_1.txt", "wb")]

file1 = [open("/BugDex2020.txt", "w"), open("/BugDex2020_1.txt", "w")]
file2 = [open("/IssueEdges2020.txt", "w"), open("/IssueEdges2020_1.txt", "w")]
file3 = [open("/ReporterNames2020.txt", "w"), open("/ReporterNames2020_1.txt", "w")]
file4 = [open("/AssigneeNames2020.txt", "w"), open("/AssigneeNames2020_1.txt", "w")]
file5 = [open("/CCedNames2020.txt", "w"), open("/CCedNames2020_1.txt", "w")]
emailName = [open("/emailName2020B.txt", "w"), open("/emailName2020B_1.txt", "w")]
bfile1 = [open("/BugDex2020B.txt", "wb"), open("/BugDex2020B_1.txt", "wb")]
bfile2 = [open("/IssueEdges2020B.txt", "wb"), open("/IssueEdges2020B_1.txt", "wb")]
bfile3 = [open("/ReporterNames2020B.txt", "wb"), open("/ReporterNames2020B_1.txt", "wb")]
bfile4 = [open("/AssigneeNames2020B.txt", "wb"), open("/AssigneeNames2020B_1.txt", "wb")]
bfile5 = [open("/CCedNames2020B.txt", "wb"), open("/CCedNames2020B_1.txt", "wb")]
bemailName = [open("/emailName2020B.txt", "wb"), open("/emailName2020B_1.txt", "wb")]
bugComm = [open("/comments2020.txt", "w"), open("/comments2020_1.txt", "w")]
bugCommb = [open("/comments2020B.txt", "wb"), open("/comments2020B_1.txt", "wb")]


def isLetter(a):
    return (ord(a) <= ord('z') and ord(a) >= ord('a'))

def okTime(t):
    return (('2019' in t) or ('2020' in t))
repNames = [{}, {}]
assNames = [{}, {}]
ccNames = [{}, {}]
bugData = [{}, {}]

cnt = 0
for Bug in BugList:
    index = 0
    for bugid in Bug['data']['bug_id']:
        project = -1
        if ('jdt' in (str(Bug['data']['product'][index]).lower())) \
                and ('core' in (str(Bug['data']['component'][index]).lower())):
            project = 0
        if ('platform' in (str(Bug['data']['product'][index]).lower())) \
                and ('ide' in (str(Bug['data']['component'][index]).lower())):
            project = 1
        if project == -1 or bugid['__text__'] == None:
            continue
        s2 = str(bugid['__text__'])
        delim = '/\\'
        L = len(Bug['data']['delta_ts'])
        if len(Bug['data']['version']) != L or len(Bug['data']['creation_ts']) != L or len(
                Bug['data']['bug_status']) != L or len(Bug['data']['resolution']) != L:
            print(str(Bug['data']['resolution']), '*')

        for el in range(L):
            bugData[project][s2] = str(Bug['data']['version'][el]['__text__']) + delim + str(
                Bug['data']['creation_ts'][el]['__text__']) \
                                   + delim + str(Bug['data']['delta_ts'][el]['__text__']) + delim + \
                                   str(Bug['data']['bug_status'][el]['__text__']) + delim
            resolutionVal = 'unknown'
            if '__text__' in Bug['data']['resolution'][el]:
                resolutionVal = str(Bug['data']['resolution'][el]['__text__'])
            bugData[project][s2] += resolutionVal

        bugComm[project].write(s2 + '\n')
        bugCommb[project].write((s2 + '\n').encode())
        for elList in Bug['data']['long_desc']:
            for el in elList:
                if 'bug_when' in el and 'who' in el and 'name' in el['who'][index] and okTime(el['bug_when'][ '__text__']):
                    cstr = el['who']['name'] + '/\\' + el['bug_when']['__text__'] + '\n'
                    bugComm[project].write(Str(cstr))
                    bugCommb[project].write(cstr.encode('utf-8'))
        cstr = 'EOB1\n'
        bugComm[project].write(Str(cstr))
        bugCommb[project].write(cstr.encode('utf-8'))
        for el in Bug['data']['activity']:
            if 'When' in el and okTime(el['When']) and 'Who' in el and 'Added' in el and 'Removed' in el:
                cstr = el['Who'] + '/\\' + el['When'] + '/\\' + el['Added'] + '/\\' + el['Removed'] + '\n'
                bugComm[project].write(Str(cstr))
                bugCommb[project].write(cstr.encode('utf-8'))
        cstr = 'EOB2\n'
        bugComm[project].write(Str(cstr))
        bugCommb[project].write(cstr.encode('utf-8'))

        Time = str(Bug['data']['creation_ts'][index]['__text__'] + '/\\' + Bug['data']['delta_ts'][index]['__text__'])
        index += 1
        if not (s2 in bugDex[project]):
            bugDex[project][s2] = True
        for rep in Bug['data']['reporter']:
            if rep == None:
                continue
            if not ('name' in rep):
                if not ('__text__' in rep):
                    continue
                else:
                    s1 = str(rep['__text__'])
            else:
                s1 = str(rep['name'])
            s1 = (s1)
            file2[project].write("Reporter2Issue/\\" + Str(s1) + "/\\" + Str(s2) + "\n")
            bstr = "Reporter2Issue/\\" + s1 + "/\\" + s2 + "\n"
            bfile2[project].write(bstr.encode())

            if not (s1 in repNames[project]):
                if s1 != str(rep['__text__']):
                    bstr = s1 + "/\\" + str(rep['__text__']) + '\n'
                    emailName[project].write(Str(bstr))
                    bemailName[project].write(bstr.encode())
                repNames[project][s1] = True
        if 'assigned_to' in Bug['data'] and Bug['data']['assigned_to'] != None:
            for pers in Bug['data']['assigned_to']:
                if pers != None and ('name' in pers) and pers['name'] != None:
                    name = (str(pers['name']))
                    bstr = "Assignee2Issue/\\" + name + "/\\" + s2 + "\n"
                    file2[project].write(Str(bstr))
                    bfile2[project].write(bstr.encode())
                    if not (name in assNames[project]):
                        if not (name in repNames[project]):
                            bstr = (name + "/\\" + pers['__text__'] + "\n")
                            emailName[project].write(Str(bstr))
                            bemailName[project].write(bstr.encode())
                        assNames[project][name] = []
                    assNames[project][name].append((Time, s2))
        if not ('cc' in Bug['data']) or (Bug['data']['cc'] == None):
            continue
        for pers in Bug['data']['cc']:
            if '__text__' in pers:
                name = str(pers['__text__'])
                if not (name in ccNames):
                    ccNames[project][name] = True
                bstr = ("CC2Issue/\\" + name + "/\\" + s2 + "\n")
                file2[project].write(Str(bstr))
                bfile2[project].write(bstr.encode())

for i in range(nrProjects):
    fileName_i = 'bugData' + str(i) + '.txt'
    bugDataF = open(fileName_i, "w")
    for b in bugData[i]:
        bugDataF.write(b + '/\\' + bugData[b] + '\n')
    bugDataF.close()
    bugComm[i].close()
    bugCommb[i].close()
    idx = 0

    for Bug in bugDex[i]:
        idx += 1
        bstr = str(Bug) + '/\\' + str(idx) + '\n'
        file1[i].write(Str(bstr))
        bfile1[i].write(bstr.encode())
    idx = 0
    for name in repNames[i]:
        idx += 1
        bstr = str(name) + '/\\' + str(idx) + '\n'
        file3[i].write(Str(bstr))
        bfile3[i].write(bstr.encode())
    idx = 0
    for name in assNames[i]:
        idx += 1
        bstr = str(name) + '/\\' + str(idx) + '\n'
        file4[i].write(Str(bstr))
        bfile4[i].write(bstr.encode())
        bstr = str(name) + '/\\' + str(len(assNames[i][name])) + '\n'
        af[i].write(Str(bstr))
        baf[i].write(bstr.encode())
        for pair in assNames[i][name]:
            bstr = str(pair[0]) + '/\\' + str(pair[1]) + '\n'
            af[i].write(bstr)
            baf[i].write(bstr.encode())
    af[i].close()
    baf[i].close()
    idx = 0
    for name in ccNames[i]:
        idx += 1
        bstr = str(name) + '/\\' + str(idx) + '\n'
        file5[i].write(Str(bstr))
        bfile5[i].write(bstr.encode())

    emailName[i].close()
    bemailName[i].close()
    file1[i].close()
    file2[i].close()
    file3[i].close()
    file4[i].close()
    file5[i].close()
    bfile1[i].close()
    bfile2[i].close()
    bfile3[i].close()
    bfile4[i].close()
    bfile5[i].close()
