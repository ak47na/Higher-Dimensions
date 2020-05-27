from perceval.backends.core.bugzilla import *
import datetime

hostname = 'https://bugs.eclipse.org//bugs//'

Bzilla = Bugzilla(url=hostname)

dateN = datetime.datetime(2020, 1, 1, 0, 0)
BugList = Bzilla.fetch(category='bug', from_date=dateN)
bugDex = {}


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


file1 = open("/BugDex2020.txt", "w")
file2 = open("/IssueEdges2020.txt", "w")
file3 = open("/ReporterNames2020.txt", "w")
file4 = open("/AssigneeNames2020.txt", "w")
file5 = open("/CCedNames2020.txt", "w")
emailName = open("/emailName2020.txt", "w")
bfile1 = open("/BugDex2020B.txt", "wb")
bfile2 = open("/IssueEdges2020B.txt", "wb")
bfile3 = open("/ReporterNames2020B.txt", "wb")
bfile4 = open("/AssigneeNames2020B.txt", "wb")
bfile5 = open("/CCedNames2020B.txt", "wb")
bemailName = open("/emailName2020B.txt", "wb")

repNames = {}
assNames = {}
ccNames = {}

cnt = 0
for bug in BugList:
    if not ('JDT' in str(bug['data']['product'])) and not ('JDT' in str(bug['data']['component'])):
        continue
    for bugid in bug['data']['bug_id']:
        if bugid['__text__'] == None:
            continue
        s2 = Str(bugid['__text__'])
        if not (s2 in bugDex):
            bugDex[s2] = True
        for rep in bug['data']['reporter']:
            if rep == None:
                continue
            if not ('name' in rep):
                if not ('__text__' in rep):
                    continue
                else:
                    s1 = Str(rep['__text__'])
            else:
                s1 = Str(rep['name'])
            file2.write("Reporter2Issue/\\" + s1 + "/\\" + s2 + "\n")
            bstr = "Reporter2Issue/\\" + s1 + "/\\" + s2 + "\n"
            bfile2.write(bstr.encode())

            if not (s1 in repNames):
                if s1 != Str(rep['__text__']):
                    bstr = s1 + "/\\" + Str(rep['__text__']) + '\n'
                    emailName.write(bstr)
                    bemailName.write(bstr.encode())
                repNames[s1] = True
        if 'assigned_to' in bug['data'] and bug['data']['assigned_to'] != None:
            for pers in bug['data']['assigned_to']:
                if pers != None and ('name' in pers) and pers['name'] != None:
                    name = Str(pers['name'])
                    bstr = "Assignee2Issue/\\" + name + "/\\" + s2 + "\n"
                    file2.write(bstr)
                    bfile2.write(bstr.encode())
                    if not (name in assNames):
                        if not (name in repNames):
                            bstr = (name + "/\\" + pers['__text__'] + "\n")
                            emailName.write(bstr)
                            bemailName.write(bstr.encode())
                        assNames[name] = True
        if not ('cc' in bug['data']) or (bug['data']['cc'] == None):
            continue
        for pers in bug['data']['cc']:
            if '__text__' in pers:
                name = Str(pers['__text__'])
                if not (name in ccNames):
                    ccNames[name] = True
                bstr = ("CC2Issue/\\" + name + "/\\" + s2 + "\n")
                file2.write(bstr)
                bfile2.write(bstr.encode())

idx = 0
for bug in bugDex:
    idx += 1
    bstr = str(bug) + '/\\' + str(idx) + '\n'
    file1.write(bstr)
    bfile1.write(bstr.encode())
idx = 0
for name in repNames:
    idx += 1
    bstr = str(name) + '/\\' + str(idx) + '\n'
    file3.write(bstr)
    bfile3.write(bstr.encode())
idx = 0
for name in assNames:
    idx += 1
    bstr = str(name) + '/\\' + str(idx) + '\n'
    file4.write(bstr)
    bfile4.write(bstr.encode())

idx = 0
for name in ccNames:
    idx += 1
    bstr = str(name) + '/\\' + str(idx) + '\n'
    file5.write(bstr)
    bfile5.write(bstr.encode())

emailName.close()
bemailName.close()
file1.close()
file2.close()
file3.close()
file4.close()
file5.close()
bfile1.close()
bfile2.close()
bfile3.close()
bfile4.close()
bfile5.close()
