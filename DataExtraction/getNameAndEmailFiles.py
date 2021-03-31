f = open('nameAndEmail.txt', 'r')
f1 = open('nameAndEmailUn.txt', 'w')
emailName = {}
emailWithoutDomain = {}
while True:
    crtLine = f.readline()
    if not crtLine:
        break

    if '<' in crtLine:
        crtLine = crtLine.rsplit('<', 1)
    elif ', ' in crtLine:
        crtLine = crtLine.split(', ')
    elif '(' in crtLine:
        crtLine = crtLine.split('(')
        aux = crtLine[0]
        crtLine[0] = crtLine[1]
        crtLine[1] = aux
    else:
        crtLine = ['', crtLine]

    assert (len(crtLine) == 2)
    crtLine[0].replace('\'', '')
    crtLine[0].replace('\"', '')
    if not (crtLine[1] in emailName):
        emailName[crtLine[1]] = [crtLine[0]]
    else:
        if emailName[crtLine[1]][0] != crtLine[0]:
            emailName[crtLine[1]].append(crtLine[0])

for email in emailName:
    emailUn = email.split('@')[0]
    if emailUn in emailWithoutDomain:
        print('Error for ', email)

    if (len(emailName[email]) != 1):
        f1.write(emailUn + '/\\' + emailName[email][1] + '\n')
    else:
        f1.write(emailUn + '/\\' + emailName[email][0] + '\n')
f1.close()
f.close()

f2 = open('nameAndEmailUn.txt', 'r')
f3 = open('nameAndEmailUsername.txt', 'w')

emailDict = {}
while True:
    crtL = f2.readline()
    if not crtL:
        break
    if crtL == '\n':
        continue
    lst = crtL.split('/\\')
    if lst[0] == '':
        continue
    lst[1] = lst[1].replace('\n', '')
    if lst[0] in emailDict:
      if len(lst[1]) > len(emailDict[lst[0]]):
        emailDict[lst[0]] = lst[1]
    else:
      emailDict[lst[0]] = lst[1]

for email in emailDict:
  f3.write(emailDict[email] + '/\\' + email + '\n')

f2.close()
f3.close()