from pydriller import RepositoryMining

import datetime as dt

dt1 = dt.datetime(2020,1,1, 0, 0)
dt2 = dt.datetime(2020,5,23, 0, 0)




file1 = open("committerNames.txt", "w")
File1 = open("committerTimes.txt", "w")
file2 = open("CommitterAuthorFiles.txt","w") 
file3 = open("FileNames.txt", "w")
file4 = open("AuthorNames.txt", "w")
File4 = open("AuthorTimes.txt", "w")
commitData = open("commitData.txt", "w")

committerDates = {}
committerEmails = {}
committerIdx = 0
authorIdx = 0
fileIdx = 0
authorDates = {}
authorEmails = {}
fileNames = {}


for commit in RepositoryMining('https://github.com/eclipse/eclipse.jdt.core', since=dt1, to=dt2).traverse_commits():
    commitData.write(str(commit.hash) + '/\\' + str(commit.msg) + '/\\\n')
    file2.write(str(commit.committer.name) + "/\\" + str(commit.author.name) + "/\\" + str(commit.hash) + "\n")
    if not(commit.committer.name in committerDates):
      committerIdx += 1
      committerDates[commit.committer.name] = []
      committerEmails[commit.committer.name] = commit.committer.email
    committerDates[commit.committer.name].append(commit.committer_date)
    if not(commit.author.name in authorDates):
      authorIdx += 1
      authorDates[commit.author.name] = []
      authorEmails[commit.author.name] = commit.author.email
    authorDates[commit.author.name].append(commit.author_date)
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

idx = 0
for Key in committerDates:
  idx += 1
  file1.write(str(Key) + "/\\" + str(committerEmails[Key]) + '/\\' + str(idx) + "\n")
  File1.write(str(Key) + "/\\" + str(len(committerDates[Key])) + "\n")
  for el in committerDates[Key]:
    File1.write(str(el) + '\n')
File1.close()
idx = 0
for Key in authorDates:
  file4.write(str(Key) + "/\\" + str(authorEmails[Key]) + '/\\' + str(idx) + "\n")
  File4.write(str(Key) + "/\\" + str(len(authorDates[Key])) + "\n")
  for el in authorDates[Key]:
    File4.write(str(el) + '\n')
File4.close()
for Key in fileNames:
  file3.write(str(Key) + "/\\" + str(fileNames[Key]) + "\n")
file1.close()
file2.close()
file3.close()
file4.close()
commitData.close()
