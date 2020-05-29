from perceval.backends.core.bugzilla import *
import datetime

def Str(elem): 
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

hostname = 'https://bugs.eclipse.org//bugs//'

Bzilla = Bugzilla(url=hostname)
dateN = datetime.datetime(2020, 1, 1, 0, 0)
BugList = Bzilla.fetch(category='bug', from_date=dateN)
bugDex = {}

af = open("/AssigneeData2020.txt", "w")
baf = open("/AssigneeData2020B.txt", "wb")
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
bugComm = open("/comments2020.txt", "w")
bugCommb = open("/comments2020B.txt", "wb")


repNames = {}
assigneeNames = {}
ccNames = {}

for bug in BugList:
    index = 0
    for bugid in bug['data']['bug_id']:
        if not ('jdt' in (str(bug['data']['product'][index]).lower())) or not (
                'core' in (str(bug['data']['component'][index]).lower())):
            continue
        if bugid['__text__'] == None:
            continue
        s2 = str(bugid['__text__'])
        bugComm.write(s2 + '\n')
        bugCommb.write((s2 + '\n').encode())
        for elList in bug['data']['long_desc']:
            for el in elList:
                if 'bug_when' in el and 'who' in el and 'name' in el['who'][index] and '2020' in el['bug_when'][
                    '__text__']:
                    cstr = el['who']['name'] + '/\\' + el['bug_when']['__text__'] + '\n'
                    bugComm.write(Str(cstr))
                    bugCommb.write(cstr.encode('utf-8'))
        cstr = 'EOB1\n'
        bugComm.write(Str(cstr))
        bugCommb.write(cstr.encode('utf-8'))
        for el in bug['data']['activity']:
            if 'When' in el and '2020' in el['When'] and 'Who' in el and 'Added' in el and 'Removed' in el:
                cstr = el['Who'] + '/\\' + el['When'] + '/\\' + el['Added'] + '/\\' + el['Removed'] + '\n'
                bugComm.write(Str(cstr))
                bugCommb.write(cstr.encode('utf-8'))
        cstr = 'EOB2\n'
        bugComm.write(Str(cstr))
        bugCommb.write(cstr.encode('utf-8'))

        Time = str(bug['data']['creation_ts'][index]['__text__'] + '/\\' + bug['data']['delta_ts'][index]['__text__'])
        index += 1
        if not (s2 in bugDex):
            bugDex[s2] = True
        for rep in bug['data']['reporter']:
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
            file2.write("Reporter2Issue/\\" + Str(s1) + "/\\" + Str(s2) + "\n")
            bstr = "Reporter2Issue/\\" + s1 + "/\\" + s2 + "\n"
            bfile2.write(bstr.encode())

            if not (s1 in repNames):
                if s1 != str(rep['__text__']):
                    bstr = s1 + "/\\" + str(rep['__text__']) + '\n'
                    emailName.write(Str(bstr))
                    bemailName.write(bstr.encode())
                repNames[s1] = True
        if 'assigned_to' in bug['data'] and bug['data']['assigned_to'] != None:
            for pers in bug['data']['assigned_to']:
                if pers != None and ('name' in pers) and pers['name'] != None:
                    name = (str(pers['name']))
                    bstr = "Assignee2Issue/\\" + name + "/\\" + s2 + "\n"
                    file2.write(Str(bstr))
                    bfile2.write(bstr.encode())
                    if not (name in assigneeNames):
                        if not (name in repNames):
                            bstr = (name + "/\\" + pers['__text__'] + "\n")
                            emailName.write(Str(bstr))
                            bemailName.write(bstr.encode())
                        assigneeNames[name] = []
                    assigneeNames[name].append((Time, s2))
        if not ('cc' in bug['data']) or (bug['data']['cc'] == None):
            continue
        for pers in bug['data']['cc']:
            if '__text__' in pers:
                name = str(pers['__text__'])
                if not (name in ccNames):
                    ccNames[name] = True
                bstr = ("CC2Issue/\\" + name + "/\\" + s2 + "\n")
                file2.write(Str(bstr))
                bfile2.write(bstr.encode())

bugComm.close()
bugCommb.close()
idx = 0
for bug in bugDex:
    idx += 1
    bstr = str(bug) + '/\\' + str(idx) + '\n'
    file1.write(Str(bstr))
    bfile1.write(bstr.encode())
idx = 0
for name in repNames:
    idx += 1
    bstr = str(name) + '/\\' + str(idx) + '\n'
    file3.write(Str(bstr))
    bfile3.write(bstr.encode())
idx = 0
for name in assigneeNames:
    idx += 1
    bstr = str(name) + '/\\' + str(idx) + '\n'
    file4.write(Str(bstr))
    bfile4.write(bstr.encode())
    bstr = str(name) + '/\\' + str(len(assigneeNames[name])) + '\n'
    af.write(Str(bstr))
    baf.write(bstr.encode())
    for pair in assigneeNames[name]:
        bstr = str(pair[0]) + '/\\' + str(pair[1]) + '\n'
        af.write(bstr)
        baf.write(bstr.encode())
af.close()
baf.close()
idx = 0
for name in ccNames:
    idx += 1
    bstr = str(name) + '/\\' + str(idx) + '\n'
    file5.write(Str(bstr))
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
