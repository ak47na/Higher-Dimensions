from pydriller import RepositoryMining
import datetime as dt

dt1 = dt.datetime(2020,1,1, 0, 0)
dt2 = dt.datetime(2020,5,23, 0, 0)

def Str(x):
  if x is None:
    return '*'
  return str(x)
class MyModif:
  def __init__(self, author_name_, author_date_, author_timezone_, add_, rem_, compl_):
    self.author_name = author_name_
    self.author_date = author_date_
    self.author_timezone = author_timezone_
    self.add = add_
    self.rem = rem_
    self.compl = compl_

  def ToString(self):
    retStr = Str(self.author_name) + '/\\' + Str(self.author_date) + '/\\' + Str(self.author_timezone) + '/\\' + Str(self.add) + '/\\' + Str(self.rem) + '/\\' + Str(self.compl)
    return retStr

class MyMethod:
  def __init__(self, name_, long_name_, start_ln_, end_ln_, filepath_):
    self.name = name_
    self.long_name = long_name_
    self.start_ln = start_ln_
    self.end_ln = end_ln_
    self.filepath = filepath_
  def __eq__(self, other):
    if other == None or self == None:
      return False
    return self.name == other.name and self.long_name == other.long_name and self.filepath == other.filepath
  def __lt__(self, other):
    return self.start_ln < other.start_ln
  def __ne__(self, other):
    if other == None and self == None:
      return False
    if other == None or self == None:
      return True
    if self.name == other.name and self.long_name != other.long_name:
      return True
    return self.name != other.name
  def __hash__(self):
    return hash((self.name, self.long_name))
    
ok = False

file1 = open('MethodOwnership.txt', 'w')
fileErr = open('MethodErrors.txt', 'w')

def addChangedInTmpDex(modification, commit):
  changedMethodList = []
  changedList = modification.changed_methods
  for meth in changedList:
    crtMethod = MyMethod(meth.name, meth.long_name, meth.start_line, meth.end_line, modification.old_path)
    changedMethodList.append(crtMethod)
    tmpDex[crtMethod] = MyModif(commit.author.name, commit.author_date, commit.author_timezone, 0, 0, 0)
  
methodDex = {}

for commit in RepositoryMining('https://github.com/eclipse/eclipse.jdt.core', since = dt1, to = dt2).traverse_commits():
  for modification in commit.modifications:
    tmpDex = {}
    addChangedInTmpDex(modification, commit)
    # make list of methods before
    myMethodList = []
    methodList = modification.methods_before
    for meth in methodList:
      crtMethod = MyMethod(meth.name, meth.long_name, meth.start_line, meth.end_line, modification.old_path)
      if crtMethod in tmpDex:
        myMethodList.append(crtMethod)
    
    myMethodList = sorted(myMethodList)
    idx = 0 
    nrMethods = len(myMethodList)
    for ln in modification.diff_parsed['deleted']:
      while idx < nrMethods and ln[0] > myMethodList[idx].end_ln:
        idx += 1
      if idx >= nrMethods:
        break
      if ln[0] >= myMethodList[idx].start_ln and ln[0] <= myMethodList[idx].end_ln:
        tmpDex[myMethodList[idx]].rem += 1
      

    myMethodList = []
    methodList = modification.methods
    for meth in methodList:
      crtMethod = MyMethod(meth.name, meth.long_name, meth.start_line, meth.end_line, modification.old_path)
      if not(crtMethod in tmpDex):
         continue
      myMethodList.append(crtMethod)

    fileErr.write('\n')
    for key in tmpDex:
        fileErr.write(key.name + ' ' + key.long_name + '\n')
    myMethodList = sorted(myMethodList)
    idx = 0 
    nrMethods = len(myMethodList)
    for ln in modification.diff_parsed['added']:
      while idx < nrMethods and ln[0] > myMethodList[idx].end_ln:
        idx += 1
      if idx >= nrMethods:
        break
      if ln[0] >= myMethodList[idx].start_ln and ln[0] <= myMethodList[idx].end_ln:
        tmpDex[myMethodList[idx]].add += 1


    for meth in tmpDex:
      if not(meth in methodDex):
        methodDex[meth] = []
      if tmpDex[meth].add > 0 or tmpDex[meth].rem > 0:
        methodDex[meth].append(tmpDex[meth])

    
for meth in methodDex:
  if meth == None or methodDex[meth] == None:
    continue
  if meth.filepath == None:
    continue
  file1.write(meth.filepath + '/\\' + meth.name + '/\\' + meth.long_name + '/\\' + str(len(methodDex[meth])) + "\n")
  for modif in methodDex[meth]:
    file1.write(modif.ToString() + "\n")

file1.close()
fileErr.close()
