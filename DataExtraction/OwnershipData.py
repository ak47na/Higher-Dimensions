from pydriller import RepositoryMining
import datetime as dt

file1 = open('OwnershipData.txt', 'w')
nrFiles = 0
fileDict = {}
listOfModif = {}
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

dt1 = dt.datetime(2020,1,1, 0, 0)
dt2 = dt.datetime(2020,5,23, 0, 0)

for commit in RepositoryMining('https://github.com/eclipse/eclipse.jdt.core', since=dt1, to=dt2).traverse_commits():
  for modification in commit.modifications:
    OldPath = modification.old_path
    NewPath = modification.new_path
    if not(NewPath in fileDict):
      nrFiles += 1
      listOfModif[nrFiles] = []
      fileDict[NewPath] = nrFiles

    id1 = fileDict[NewPath]
    modif = MyModif(commit.author.name, commit.author_date, commit.author_timezone, modification.added, modification.removed, modification.complexity)
    listOfModif[id1].append(modif)
  

for key in fileDict:
  if key == None or listOfModif[fileDict[key]] == None:
    continue
  file1.write(key + '/\\' + str(len(listOfModif[fileDict[key]])) + "\n")
  for modif in listOfModif[fileDict[key]]:
    file1.write(modif.ToString() + "\n")

file1.close()
