#! /usr/bin/env python3
#cmd = "cd C:\\Program Files\\Git\\bin\\" + "\n" + "sh.exe\n"
#cmd += "eval `ssh-agent`" + "\n" + "ssh-add C:\\Users\\Maria\\firstKey.txt" + "\n"

import datetime
from perceval.backends.core.gerrit import Gerrit
from Settings import*

# hostname of the Gerrit instance
hostname = 'git.eclipse.org'
# user for sshing to the Gerrit instance
user = 'akapros'

projectName = getProjectName()

file1 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\ReviewEdges2020.txt", "w")
file2 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\UploaderNames2020.txt", "w")
file3 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\OwnerNames2020.txt", "w")
file4 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\CommentRevNames2020.txt", "w")
file5 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\ApproverNames2020.txt", "w")
file6 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\AuthorNames2020.txt", "w")
file8 = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\ReviewFilesFromComments.txt", "w")
reviewData = open("D:\\Ak_work2019-2020\\HigherDimensions\\jdtData\\ReviewData.txt", "w")

repo = Gerrit(hostname=hostname, user=user)
uploaderNames = {}
authorNames = {}
ownerNames = {}
reviewerNames = {}
approverNames = {}
uploaderIdx = 0
authorIdx = 0
ownerIdx = 0
reviewerIdx = 0
approverIdx = 0
dateN = datetime.datetime(2019, 12, 18, 0, 0)
dateLast = datetime.datetime(2020, 6, 23, 0, 0).timestamp()
def Str(elem):
    return str(elem).encode("utf-8").decode()

for review in repo.fetch(from_date=dateN):
    reviewProjectName = str(review['data']['project']).lower()
    if not(projectName in reviewProjectName):
        continue

    if (review['data']['createdOn']) > dateLast:
        continue
    reviewData.write(str(review['data']['project']) + '/\\' + Str(review['data']['number']) + '/\\' + Str(review['data']['id']) + '/\\' + Str(review['data']['subject'])
    + '/\\' + Str(review['updated_on']) + '/\\' + Str(review['data']['createdOn']) + '/\\' + Str(review['data']['status']) + '\n')
    ownerEmail = ''
    if 'email' in review['data']['owner']:
        ownerEmail = Str(review['data']['owner']['email'])
    if not ('name' in review['data']['owner']):
        ownerName = 'unknown'
    else:
        ownerName = Str(review['data']['owner']['name'])
    for patch in review['data']['patchSets']:
        if not ('email' in patch['author']):
            emailA = ''
        else:
            emailA = Str(patch['author']['email'])
        if not ('name' in patch['author']):
            name = 'unknown2'
        else:
            name = Str(patch['author']['name'])
        revId = Str(patch['revision'])
        file1.write("AuthorEdge" + "/\\" + revId + "/\\" + name + "\n")
        if name != None and (not(name in authorNames)):
            authorIdx += 1
            authorNames[name] = (authorIdx, emailA)
        if not ('email' in patch['uploader']):
            emailU = ''
        else:
            emailU = Str(patch['uploader']['email'])
        if not ('name' in patch['uploader']):
            name = 'unknown1'
        else:
            name = Str(patch['uploader']['name'])
        file1.write('Review2Commit/\\' + Str(review['data']['number']) + '/\\' + revId + "\n")
        file1.write("UploaderEdge" + "/\\" + revId + "/\\" + name + "\n")
        if name != None and (not (name in uploaderNames)):
            uploaderIdx += 1
            uploaderNames[name] = (uploaderIdx, emailU)
        if 'approvals' in patch:
            for approval in patch['approvals']:
                if not('name' in approval['by']):
                    continue
                name = Str(approval['by']['name'])
                file1.write("ApprovalEdge/\\" + revId + "/\\" + name + "\n")
                if name != None and (not (name in approverNames)):
                    approverIdx += 1
                    if not ('email' in approval['by']):
                        print(approval['by'])
                        approverNames[name] = (approverIdx, '')
                    else:
                        approverNames[name] = (approverIdx, Str(approval['by']['email']))

        file1.write("OwnerEdge" + "/\\" + revId + "/\\" + ownerName + "\n")
        if 'comments' in patch:
            for comment in patch['comments']:
                if not ('reviewer' in comment) or not('name' in comment['reviewer']):
                    continue
                nameC = Str(comment['reviewer']['name'])
                if ownerName != nameC:
                    file1.write("PCommentEdge" + "/\\" + ownerName + "/\\" + nameC + "\n")
                if not (nameC in reviewerNames):
                    reviewerIdx += 1
                    emailR = ''
                    if 'email' in comment['reviewer']:
                        emailR = Str(comment['reviewer']['email'])
                    reviewerNames[nameC] = (reviewerIdx, emailR)
                if 'file' in comment:
                    fileName = Str(comment['file'])
                    file8.write("CommentFileRelation/\\" + fileName + "/\\" + ownerName + "/\\" +
                                nameC + "/\\" + Str(review['data']['number']) + "/\\" + revId + "\n")

    if not(ownerName in ownerNames):
        ownerIdx += 1
        ownerNames[ownerName] = (ownerIdx, ownerEmail)

    for comment in review['data']['comments']:
        if not ('reviewer' in comment) or not ('name' in comment['reviewer']):
            continue
        if ownerName != name:
            file1.write("CommentEdge" + "/\\" + ownerName + "/\\" + name + "\n")
        if not (name in reviewerNames):
            reviewerIdx += 1
            emailR = ''
            if 'email' in comment['reviewer']:
                emailR = Str(comment['reviewer']['email'])
            reviewerNames[name] = (reviewerIdx, emailR)


for name in uploaderNames:
    file2.write(name + "/\\" + str(uploaderNames[name][1]) + "/\\" + str(uploaderNames[name][0]) + "\n")
for name in ownerNames:
    file3.write(name + "/\\" + str(ownerNames[name][1]) + "/\\" + str(ownerNames[name][0]) + "\n")
#reviewerNames represent the names of reviewers
for name in reviewerNames:
    file4.write(name + "/\\" + str(reviewerNames[name][1]) + "/\\" + str(reviewerNames[name][0]) + "\n")
for name in approverNames:
    file5.write(name + "/\\" + str(approverNames[name][1]) + "/\\" + str(approverNames[name][0]) + "\n")
for name in authorNames:
    file6.write(name + "/\\" + str(authorNames[name][1]) + "/\\" + str(authorNames[name][0]) + "\n")
file1.close()
file2.close()
file3.close()
file4.close()
file5.close()
file6.close()
file8.close()
reviewData.close()
