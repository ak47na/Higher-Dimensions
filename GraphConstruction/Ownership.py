from datetime import datetime
from datetime import timedelta
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import re

minPercentage = 5
class TimePair:
    def __init__(self, start_t_, end_t_):
        self.start_t = start_t_
        self.end_t = end_t_
    def __eq__(self, other):
        return (self.start_t == other.start_t and self.end_t == other.end_t)
    def __ne__(self, other):
        return not(self == other)
    def __lt__(self, other):
        return self.start_t < other.start_t

nrEpochs = 2
TimeList = []
dt1 = dt.datetime(2020,1,1, 0, 0)
dt2 = dt.datetime(2020, 2, 2, 0, 0)
dt3 = dt.datetime(2020,5,23, 0, 0)
TimeList.append(TimePair(dt1, dt2))
TimeList.append(TimePair(dt2, dt3))


def Str(x):
  if x is None:
    return '*'
  return str(x)

def isLetter(a):
    return (ord(a) <= ord('z') and ord(a) >= ord('a'))
def purifyName(name):
    nameLen = len(name)
    newName = ''
    for i in range(nameLen):
        crtSymbol = name[i].lower()
        if isLetter(crtSymbol):
            newName += crtSymbol
    return newName

class Modif:
  def __init__(self, author_name_, author_time_, add_, rem_, compl_):
    self.author_name = author_name_
    #self.author_date = author_date_
    self.author_time = author_time_
    self.add = add_
    self.rem = rem_
    self.compl = compl_

  def ToString(self):
      retStr = Str(self.author_name) + ' ' + Str(self.author_time) + ' ' + Str(
          self.add) + ' ' + Str(self.rem) + ' ' + Str(self.compl)
      return retStr
# an AuthorModif object holds a modification made by a specific author
class AuthorModif:
    def __init__(self, author_time_, add_, rem_, compl_):
        #self.author_time is the last time the author modified the component
        self.author_time = author_time_
        self.add = add_
        self.rem = rem_
        self.compl = compl_  # complexity of component
        self.sumAdd = add_
        self.sumRem = rem_
        self.nrCommits = 1

    def update(self, modif):
        if modif.author_time > self.author_time:
            self.author_time = self.author_time
            self.add = modif.add
            self.rem = modif.rem
            self.compl = modif.compl
        self.sumAdd += modif.add
        self.sumRem += modif.rem
        self.nrCommits += 1

class Ownership:
    def __init__(self, name_):
        self.name = name_
        # array of Dictionaries of (author, authorModifications) for each time frame
        self.authorDex = []
        self.lastModif = []
        self.lastModifier = []
        self.sumAdd = []
        self.sumRem = []
        self.nrCommits = []
        for i in range(nrEpochs + 1):
            self.authorDex.append({})
            self.lastModif.append(None)
            self.lastModifier.append('')
            self.sumAdd.append(0)
            self.sumRem.append(0)
            self.nrCommits.append(0)

    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return (self.name == other.name)
    def __ne__(self, other):
        return not (self == other)
    def addModif(self, modif):
        #Index 0 corresponds to all modifs.
        self.addModifAt(modif, 0)
        #binary search the index of epoch the modification belongs to
        p2 = 1
        index = -1
        while (p2 * 2) <= nrEpochs:
            p2 *= 2
        while p2 > 0:
            if index + p2 < nrEpochs and modif.author_time > TimeList[index + p2].end_t:
                index += p2
            p2 = p2 // 2

        index += 1
        if (index < nrEpochs and modif.author_time < TimeList[index].end_t and modif.author_time >= TimeList[index].start_t):
            self.addModifAt(modif, index + 1)

    def addModifAt(self, modif, idx):
        if not(modif.author_name in self.authorDex[idx]):
            self.authorDex[idx][modif.author_name] = AuthorModif(modif.author_time, modif.add, modif.rem, modif.compl)
        else:
            self.authorDex[idx][modif.author_name].update(modif)
        if self.lastModif[idx] == None or modif.author_time > self.lastModif[idx].author_time: #or (modif.author_date == self.lastModif.author_date and modif.author_timezone > self.lastModif.author_timezone):
            self.lastModif[idx] = modif
            self.lastModifier[idx] = modif.author_name

        self.sumAdd[idx] += modif.add
        self.sumRem[idx] += modif.rem
        self.nrCommits[idx] += 1

    def sumAROwner(self, idx):
        sum = 0
        name = ''
        for author in self.authorDex[idx]:
            if self.authorDex[idx][author].sumAdd + self.authorDex[idx][author].sumRem > sum:
                sum = self.authorDex[idx][author].sumAdd + self.authorDex[idx][author].sumRem
                name = author
        return name, sum
    def nrCommitsPercentage(self, idx):
        owner = self.nrCommitsOwner(idx)
        return (self.authorDex[idx][owner[0]].nrCommits / self.nrCommits[idx]) * 100
    def lastModifierOwner(self, idx):
        return self.lastModifier[idx]
    def nrCommitsOwner(self, idx):
        nrCommits = 0
        name = ''
        for author in self.authorDex[idx]:
            if self.authorDex[idx][author].nrCommits > nrCommits:
                nrCommits = self.authorDex[idx][author].nrCommits
                name = author
        return (name, nrCommits)
    #retruns minor, major
    def getMeasures(self, idx):
        nrMinor = 0
        nrMajor = 0
        for author in self.authorDex[idx]:
            p = (self.authorDex[idx][author].nrCommits / self.nrCommits[idx]) * 100
            if p <= minPercentage:
                nrMinor += 1
            else:
                nrMajor += 1
        return nrMinor, nrMajor

#file = open("D:\\Ak_work2019-2020\\HigherDimensions\\OwnershipMethods.txt")
def getTime(str1, str2):
    lst = re.split('\+|\-', str2)
    if not (':' in lst[1]):
        lst[1] = lst[1][:2] + ':' + lst[1][2:]
    str3 = lst[1].split(':')
    if '+' in str2:
        dateTime = datetime.strptime(str1 + ' ' + lst[0], '%Y-%m-%d %H:%M:%S') + timedelta(hours = int(str3[0]), minutes = int(str3[1]))
    else:
        dateTime = datetime.strptime(str1 + ' ' + lst[0], '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(str3[0]),
                                                                                           minutes=int(str3[1]))

    return dateTime

OwnershipDex = {}
def getModifFromLine(nxtL):
    AuthorName = purifyName(nxtL[0])
    dateLn = nxtL[1].split(' ')
    Time = getTime(dateLn[0], dateLn[1])
    compl = 0
    nxtL[5] = nxtL[5].replace('\n', '')
    if nxtL[5] != '*':
        compl = int(nxtL[5])
    return Modif(AuthorName, Time, int(nxtL[3]), int(nxtL[4]), compl)

def plotOwnershipHistogram(x, Name):
    yTicks = []
    cnt = 0
    for i in x:
        if i == 50:
            cnt += 1
    print(cnt)
    for i in range(0, 600, 20):
        yTicks.append(i)

    x = sorted(x)
    print(x[len(x) - 1])
    fig, ax = plt.subplots()
    ax.hist(x, bins=100)
    ax.set_ylim([0, 600])
    plt.yticks(yTicks)
    ax.set_xlabel('Ownership percentage')
    ax.set_ylabel('Number of compoonents')
    plt.savefig(Name)
    plt.show()
def plotOwnershipPercent(x, Name):
    xTicks = []  
    for i in range(0, 20):
        xTicks.append(i)
        print(i)
    x = sorted(x)
    fig, ax = plt.subplots()
    ax.set_ylim([0, 100])
    ax.hist(x, bins=100)
    ax.set_ylabel('Ownership percentage')
    ax.set_xlabel('Number of compoonent')
    plt.savefig(Name)
    plt.show()
