# code to print modified file in a given time frame

from pydriller import RepositoryMining

import datetime as dt
import csv

dt1 = dt.datetime(2020,1,1, 0, 0)
dt2 = dt.datetime.now()

file1 = open("committerNames.txt", "w")
file2 = open("CommitterAuthorFiles.txt","w") 
file3 = open("FileNames.txt", "w")
file4 = open("AuthorNames.txt", "w")
commitData = open("commitData.txt", "w")

committerNames = {}
committerIdx = 0
authorIdx = 0
fileIdx = 0
authorNames = {}
fileNames = {}

Vis = {}

for commit in RepositoryMining('https://github.com/eclipse/eclipse.jdt.core', since=dt1, to=dt2).traverse_commits():
    commitData.write(str(commit.hash) + '/\\' + str(commit.msg) + '/\\\n')
    file2.write(str(commit.committer.name) + "/\\" + str(commit.author.name) + "/\\" + str(commit.hash) + "\n")
    if not(commit.committer.name in committerNames):
      committerIdx += 1
      committerNames[commit.committer.name] = committerIdx

    if not(commit.author.name in authorNames):
      authorIdx += 1
      authorNames[commit.author.name] = authorIdx
   
    for modifFile in commit.modifications:
      fileList = modifFile.filename.split('.')
      if (fileList[-1] == 'jar' or fileList[-1] == 'java' or fileList[-1] == 'class'):
        if (modifFile.new_path == None):
          file2.write("*" + str(modifFile.old_path) + ' ')
        else:
          file2.write(str(modifFile.new_path) + ' ')
        if not(modifFile.filename in fileNames):
          fileIdx += 1
          fileNames[modifFile.filename] = fileIdx
        
      file2.write("\n")

for Key in committerNames:
  file1.write(str(Key) + ":" + str(committerNames[Key]) + "\n")

for Key in authorNames:
  file4.write(str(Key) + ":" + str(authorNames[Key]) + "\n")

for Key in fileNames:
  file3.write(str(Key) + ":" + str(fileNames[Key]) + "\n")
file1.close()
file2.close()
file3.close()
file4.close()
commitData.close()
